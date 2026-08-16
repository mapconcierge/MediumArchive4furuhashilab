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

### 案1: 公式エクスポート（不採用に変更）
`medium.com/furuhashilab` の管理者アカウントの設定 → "Download your information" から取得できる公式データエクスポートを検討したが、**Medium公式ヘルプ（[Export your account data](https://help.medium.com/hc/en-us/articles/115004745787-Export-your-account-data)）によるとこの機能は「ログイン中のアカウント本人が書いた記事のみ」をエクスポートする個人アカウント単位の機能であり、publication単位の全記事エクスポートではない**ことが判明。実際、直近10記事だけでも著者が8名（SAKURA NAKAMIZO, INOUE RENSEI, Kanoko Fujiwara, Moe Anjo, REARA KATO, SATOAKI, Shota Arakawa, USUI CHIHANA）に分かれており、研究室公式アカウント（仮に存在しても）のエクスポートだけでは全記事をカバーできない。全執筆者（卒業生含む）に個別エクスポートを依頼するのは非現実的なため、**2026-08-17 不採用に変更**。

### 案2: 実ブラウザセッションでの半自動収集（採用・確定・実装済み）
Claude in Chromeで実際に検証し、以下が判明・実装済み。

- `medium.com/furuhashilab/all`（`/archive` はここへリダイレクトされる）は実ブラウザセッションなら403にならず閲覧できる
- ただし無限スクロールによる追加記事の読み込みは、**本物のマウスホイール/トラックパッド入力でないと発火しない**。`window.scrollTo()`や合成`WheelEvent`のdispatchなど、スクリプトから生成した非trustedなイベントでは追加読み込みが起きない（実機比較で確認済み）。これはDevToolsコンソールに貼り付けて実行するスクリプトにも同じ制約が及ぶ（コンソールもページのJSコンテキストで動くため、CDP経由の合成入力のような特権はない）
- 一方、記事本文の取得は問題なし。ページが読み込まれた状態からの**同一オリジン`fetch()`（`credentials: "include"`）は個別記事URLに対して403にならず200 OKでHTMLを取得できる**。取得したHTML内の `window.__APOLLO_STATE__` に、Mediumの内部リッチテキストモデル（Paragraph配列: type/text/markups/metadata等）が完全な形で埋め込まれている
- 画像は `miro.medium.com`（記事本文とは別ドメイン）から配信されており、こちらはCloudflareの対象外でPython `requests` から直接ダウンロード可能（Track Aで検証済みと同じ）

このため実装は「収集」と「変換」を分離した:
1. **収集**: `scripts/browser_backfill.js` をユーザーがChrome DevToolsコンソールに貼り付けて実行する。ユーザー自身が実際にマウス/トラックパッドでページをスクロールして無限読み込みを進め（スクリプトはApolloキャッシュを1秒おきにポーリングして件数を画面オーバーレイ表示するのみ）、`downloadPostList()` で記事一覧、`await fetchAllContent()` で全記事の本文（Paragraphモデル）をJSONとしてダウンロードする
2. **変換**: `scripts/import_export.py <ダウンロードしたJSON>` が、Paragraphモデルを `scripts/paragraphs_to_md.py` でMarkdownに変換し、画像をダウンロードし、Track Aと同じ `posts/`・`assets/images/`・`data/archived_posts.json` の形式で書き出す（サンプルデータでのローカル動作確認済み、2026-08-17）

**2026-08-17 決定**: バックフィルは案2で進める。収集スクリプトと変換スクリプトを実装済み。次はユーザーに `scripts/browser_backfill.js` を実行してもらい、実データで全件バックフィルする。

### 案3: バックフィルなし
今後の新着のみ自動アーカイブし、過去記事は対象外とする。不採用（「すべての記事をアーカイブする」という当初要件を満たさないため）。

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
│   ├── browser_backfill.js    # (Track B) DevToolsコンソール実行用の収集スクリプト
│   ├── paragraphs_to_md.py    # (Track B) MediumのParagraphモデル→Markdown変換
│   └── import_export.py       # (Track B) browser_backfill.jsの出力を取り込みMarkdown化
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
- [x] バックフィル方針: 案1（公式エクスポート）は不採用と判明(2026-08-17)。案2（実ブラウザセッションでの半自動収集）に変更
- [x] 収集スクリプト(`scripts/browser_backfill.js`)・変換スクリプト(`scripts/paragraphs_to_md.py`, `scripts/import_export.py`)を実装・サンプルデータで動作確認(2026-08-17)
- [ ] ユーザーが `scripts/browser_backfill.js` を実行して全記事を収集し、`python scripts/import_export.py <JSON>` で実データをバックフィル

## 9. 未解決事項

- `scripts/paragraphs_to_md.py` はサンプルデータでの動作確認のみ。実データ全件（数百記事）でMarkdown崩れがないか、Track Bの初回実行後に目視サニティチェックが必要
- Paragraph `type` の網羅性: 確認できたのは H2/H3/P/ULI/IMG/MIXTAPE_EMBED のみ。PRE(コードブロック)/IFRAME(埋め込み動画等)/OLI(番号リスト)は未確認の型のためフォールバック実装（プレーンテキスト化）に留まっており、実データで遭遇したら都度調整する
- 画像の著作権（記事中の図表・写真がCC由来か、研究室独自作成かで表記が変わりうる。全件確認は非現実的なため、包括的な出典明記に留めるのが現実的）
- Medium GraphQL API経由の非公式取得は今回不採用（Cloudflareにブロックされ、かつToSグレーゾーンのため）。ただし同一オリジンfetch()経由の`__APOLLO_STATE__`取得は「実ブラウザで公開ページを閲覧する」ことの範囲内と整理し、Track Bで採用した
