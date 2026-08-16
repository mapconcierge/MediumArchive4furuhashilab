# MediumArchive4furuhashilab 仕様書 (Draft v1)

古橋研究室公式Medium (`https://medium.com/furuhashilab`) の全記事を、GitHub Actionsで定期的にMarkdown形式でアーカイブし、GitHub Pagesで閲覧できるようにするサービスの設計仕様。

## 0. 技術的制約の事前調査結果（重要）

設計前に実機で確認した事実。これが全体構成を決定づける。

| エンドポイント | 結果 | 備考 |
|---|---|---|
| `https://medium.com/feed/furuhashilab` (RSS) | **200 OK** (`curl`で取得可) | 最新 **10件のみ**、`content:encoded`に本文フルHTML入り |
| `https://medium.com/furuhashilab` (公開トップ) | **403** (`Just a moment...` Cloudflareチャレンジ) | 通常のUser-Agent付きcurlでも弾かれる |
| `https://medium.com/furuhashilab/archive` | **403** (同上) | 過去記事一覧ページ |
| 個別記事URL (RSSから抽出したもの) | **403** (同上) | 記事本体HTMLも同様にブロック |
| `https://medium.com/_/graphql` | **403** (同上) | 非公式内部APIも同様 |
| `robots.txt` | `User-Agent: *` は記事ページを明示的に禁止していない。一方 `ClaudeBot`, `GPTBot`, `Bytespider` 等AIクローラー名指しで全面 `Disallow: /` | ポリシー上はグレーだが、実際はCloudflareのボット検知（TLS/JS fingerprint）で技術的にブロックされている |

**結論**: GitHub Actions（サーバー/データセンターIP、非ブラウザ実行環境）から安定して取得できるのは **RSSフィードのみ**。個別記事ページ・アーカイブ一覧ページはCI環境からは事実上取得不可。

この制約により、本サービスは **2トラック構成** とする。

- **トラックA（自動・継続）**: GitHub Actionsが定期的にRSSを見に行き、新着記事だけを自動アーカイブする。ToS的にもクリーン（RSSはMedium公式の配信用途）。
- **トラックB（半自動・初回のみ）**: RSSの範囲外にある過去記事（既存の全投稿）は、CI環境では取得できないため、人間のブラウザセッションを使った一度きりのバックフィル作業として別途行う。

## 1. トラックA: 継続的な新着記事アーカイブ（GitHub Actions）

### 1.1 処理フロー
1. `.github/workflows/archive.yml` がスケジュール実行（例: 毎日 JST 12:00 = UTC 03:00）+ `workflow_dispatch` で手動実行も可能にする
2. `scripts/fetch_feed.py` が `https://medium.com/feed/furuhashilab` を取得
3. 各 `<item>` について `guid`（記事の一意ID）を `data/archived_posts.json` の既存レコードと照合し、未アーカイブのものだけ処理
4. `content:encoded` のHTMLを取得し、`scripts/html_to_md.py` でMarkdownに変換
   - 変換ライブラリ: Python `markdownify`
   - 本文中の `<img>` タグを検出し、画像をダウンロードして `assets/images/{post-slug}/` に保存、Markdown内の参照をローカルパスに書き換える（ユーザー確認済み: 画像はローカル保存方針）
5. Frontmatter付きMarkdownを `posts/{YYYY}/{YYYY-MM-DD}-{slug}.md` として書き出し
6. `data/archived_posts.json` を更新（guid, 記事URL, ローカルパス, 取得日時, コンテンツハッシュ）
7. `scripts/build_index.py` で `index.json`（サイト表示用の記事一覧）を再生成
8. 差分があれば `git commit` + `git push`（`GITHUB_TOKEN` に contents:write 権限が必要 → リポジトリ Settings > Actions > General > Workflow permissions を "Read and write" に設定する必要あり。**これはユーザー側の初期設定作業**）

### 1.2 更新検知（編集された記事への対応）
Mediumでは公開後に記事が編集されることがある。`content:encoded` のハッシュ値を `archived_posts.json` に保存しておき、既存記事でもハッシュが変化していれば再アーカイブ（上書き）し、`updated_at` を記録する。

### 1.3 実行頻度に関する注意
RSSは最新10件までしか含まないため、**1回の実行間隔中に11件以上新規投稿されると取りこぼす**。研究室の投稿頻度なら毎日実行で十分安全マージンがあるはずだが、念のため運用開始後に投稿頻度を確認する。

## 2. トラックB: 初回バックフィル（過去の全記事）

CI環境からは取得できないため、以下いずれかを選択する（**要ユーザー判断**）。

### 案1: 公式エクスポート（採用・確定）
`medium.com/furuhashilab` の管理者アカウントの設定 → "Download your information" から、公開済み全記事の公式データエクスポート（HTML/JSON）を取得してもらう。これを取り込むワンショットスクリプト (`scripts/import_export.py`) を用意し、トラックAと同じMarkdown形式・frontmatter仕様に正規化する。ToS完全準拠。管理者による手動操作が1回必要。

**2026-08-16 決定**: バックフィルはこの案1で進める。管理者によるエクスポート取得を待つ間、トラックA（RSSベースの継続自動アーカイブ）とサイト表示まわりの実装を先行して進める。エクスポートのZIPが届き次第 `import_export.py` を実データに合わせて調整する（Mediumの公式エクスポートの内部フォーマットは未確認のため、実データ到着後に構造を検証してからパーサーを確定させる）。

### 案2: 実ブラウザセッションでの半自動収集
ユーザーの手元のブラウザ（Claude in Chromeや手動操作）で `medium.com/furuhashilab/archive` にアクセスし、記事URL一覧を収集 → 各記事ページを実ブラウザで開いてHTML取得 → ローカルで同じ変換パイプラインにかける。人間の通常利用と区別がつかないため技術的には通るはずだが、CI化はできない（毎回人手が必要）。今回、この方針を試すため実際にClaude in Chromeでの動作確認を試みたが、**このセッションではブラウザ拡張が未接続で検証できなかった**。拡張を接続すれば再テスト可能。

### 案3: バックフィルなし
今後の新着のみ自動アーカイブし、過去記事は対象外とする。

**現状の推奨は案1**。案2は追加検証が必要、案3は「すべての記事をアーカイブする」という当初要件を満たさない。

## 3. リポジトリ構成案

```
MediumArchive4furuhashilab/
├── README.md
├── LICENSE                    # コード: MIT（既存）
├── CONTENT_LICENSE.md         # コンテンツ: CC BY 4.0 + Medium原文へのクレジット
├── SPEC.md                    # 本ファイル
├── .github/
│   └── workflows/
│       └── archive.yml        # スケジュール実行 + 手動実行
├── scripts/
│   ├── fetch_feed.py          # RSS取得・差分検出
│   ├── html_to_md.py          # HTML→Markdown変換・画像DL
│   ├── build_index.py         # index.json 再生成
│   └── import_export.py       # (案1採用時) 公式エクスポート取込み
├── posts/
│   └── 2026/
│       └── 2026-08-10-example-slug.md
├── assets/
│   └── images/
│       └── 2026-08-10-example-slug/
│           └── 001.png
├── data/
│   └── archived_posts.json    # guid → ローカルパス・ハッシュ・タイムスタンプ の索引
├── index.html                 # GitHub Pagesエントリ（一覧）
├── post.html                  # 個別記事表示テンプレート（クエリパラメータでMarkdownを指定）
└── assets/js/
    └── render.js              # marked.js等でクライアントサイドMarkdownレンダリング
```

## 4. Markdownファイル仕様

```markdown
---
title: "記事タイトル"
subtitle: "副題（あれば、なければ省略）"
author: "著者名"
medium_url: "https://medium.com/furuhashilab/xxxx-xxxxxxxxxxxx"
medium_guid: "xxxxxxxxxxxx"
published_at: "2026-08-10T09:00:00+09:00"
updated_at: "2026-08-10T09:00:00+09:00"
archived_at: "2026-08-16T12:00:00+09:00"
tags: ["OpenStreetMap", "ドローン測量"]
---

(本文Markdown。画像はローカル相対パス `../../assets/images/.../001.png` を参照)
```

## 5. サイト構成（GitHub Pages）

ユーザー選択: **静的HTML + クライアントサイドMarkdownレンダリング**（Jekyllビルド不要）。

- `index.html`: `data/index.json`（記事メタデータ一覧）を fetch → タイトル・日付・タグでカード一覧表示
- `post.html?slug=xxx`: 該当Markdownをfetchし、marked.js等でレンダリング。frontmatterはJS側でパースして見出し情報として表示
- `data/index.json` は `build_index.py` がworkflow内で自動生成（`archived_posts.json` から必要フィールドを抽出した軽量版）
- GitHub Pagesの設定: リポジトリ Settings > Pages でソースを `main` ブランチ `/ (root)` に設定（**ユーザー側の初期設定作業**）

## 6. ライセンス・著作権表記

CLAUDE.mdの原則に従い:
- コード（`scripts/`, `*.js`, ワークフロー等）: MIT License（既存LICENSEファイル）
- アーカイブされたコンテンツ（Markdown化された記事本文）: 原記事が研究室公式Mediumのものであるため、CC BY 4.0を提案。ただし記事によっては共著者・引用画像の権利関係が異なる可能性があるため、`CONTENT_LICENSE.md` に「原則CC BY 4.0、個別記事の権利は原著者に帰属し、詳細は各記事のMedium原文を参照」と明記し、各Markdownファイルにも `medium_url` で原文への出典リンクを必須とする

## 7. 状態管理・重複検出

`data/archived_posts.json`:
```json
{
  "xxxxxxxxxxxx": {
    "path": "posts/2026/2026-08-10-example-slug.md",
    "medium_url": "https://medium.com/furuhashilab/...",
    "content_hash": "sha256:...",
    "published_at": "2026-08-10T09:00:00+09:00",
    "archived_at": "2026-08-16T12:00:00+09:00",
    "updated_at": "2026-08-16T12:00:00+09:00"
  }
}
```

## 8. 運用・初期設定チェックリスト（ユーザー側で必要な作業）

- [ ] リポジトリ Settings > Actions > General > Workflow permissions を "Read and write permissions" に変更（Actionsからのpushに必要）
- [ ] リポジトリ Settings > Pages でソースを設定（`main` / root）
- [ ] リポジトリの公開設定を確認（研究室の原則は基本パブリック。既にpublicか要確認）
- [x] バックフィル方針: 案1（公式エクスポート）に決定(2026-08-16)
- [ ] `medium.com/furuhashilab` 管理者による公式エクスポートの取得・提供（届き次第 `import_export.py` を実データに合わせて調整）

## 9. 未解決事項

- Medium公式エクスポートの内部フォーマット（ファイル構成・HTML構造）は未確認。実データ到着後に `import_export.py` を検証・調整する
- 画像の著作権（記事中の図表・写真がCC由来か、研究室独自作成かで表記が変わりうる。全件確認は非現実的なため、包括的な出典明記に留めるのが現実的）
- Medium GraphQL API経由の非公式取得は今回不採用（Cloudflareにブロックされ、かつToSグレーゾーンのため）
