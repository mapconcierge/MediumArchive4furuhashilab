# MediumArchive4furuhashilab

古橋研究室公式のMedium ([medium.com/furuhashilab](https://medium.com/furuhashilab)) に投稿された記事を、GitHub Actionsで定期的にMarkdown形式でアーカイブし、GitHub Pagesで公開するサービス。

## 概要

- **トラックA（自動・継続）**: GitHub ActionsがMedium公式RSSフィードを毎日ポーリングし、新着・更新記事を自動でMarkdown化して `posts/` に追加、画像は `assets/images/` にダウンロードして保存する
- **トラックB（半自動・初回のみ）**: RSSは最新10件までしか取得できないMedium側の制約があるため、過去記事はユーザーの実ブラウザセッション（Chrome DevToolsコンソール）で収集したデータを取り込んでバックフィルする

詳細な設計・技術的制約の調査結果は [SPEC.md](SPEC.md) を参照。

## 使い方

```bash
pip install -r requirements.txt

# 新着記事の取得・Markdown化（RSSベース、トラックA）
python scripts/archive.py

# GitHub Pages用の記事一覧(data/index.json)を再生成
python scripts/build_index.py
```

GitHub Actions (`.github/workflows/archive.yml`) がこの2ステップを毎日自動実行し、差分があればコミット・pushする。

### 過去記事のバックフィル（トラックB）

RSSでは取得できない過去記事は、実ブラウザセッションで収集する（GitHub Actionsからは実行不可 — Medium側のボット対策でブロックされるため。詳細は [SPEC.md](SPEC.md) 参照）。

1. Chromeで https://medium.com/furuhashilab/all を開く
2. DevTools（Cmd+Option+J）> Console を開き、[`scripts/browser_backfill.js`](scripts/browser_backfill.js) の中身を丸ごと貼り付けて実行
3. 画面右下にカウンターが出るので、マウス/トラックパッドで実際にページを下にスクロールし続ける（無限スクロールの読み込みは本物の操作でないと発火しないため、スクリプトによる自動スクロールはできない）。カウンターが15〜20秒増えなくなったら最古の記事まで到達
4. コンソールで `downloadPostList()` を実行（記事一覧のJSONをダウンロード）
5. コンソールで `await fetchAllContent()` を実行（全記事の本文を取得してJSONをダウンロード。数百記事あると数分かかる）
6. ダウンロードした `furuhashilab_full_content.json` を使って:
   ```bash
   python scripts/import_export.py /path/to/furuhashilab_full_content.json
   python scripts/build_index.py
   ```

## データソース・ライセンス

- コード: MIT License ([LICENSE](LICENSE))
- アーカイブされた記事本文・画像: 原則 CC BY 4.0（詳細は [CONTENT_LICENSE.md](CONTENT_LICENSE.md)）。原文は各記事frontmatterの `medium_url` から参照可能
- 記事データの取得元: [medium.com/furuhashilab](https://medium.com/furuhashilab) 公式RSSフィード

## 著者

青山学院大学 地球社会共生学部 古橋研究室 (Furuhashi Lab)

## 関連リンク

- [medium.com/furuhashilab](https://medium.com/furuhashilab)（原文）
