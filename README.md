# MediumArchive4furuhashilab

古橋研究室公式のMedium ([medium.com/furuhashilab](https://medium.com/furuhashilab)) に投稿された記事を、GitHub Actionsで定期的にMarkdown形式でアーカイブし、GitHub Pagesで公開するサービス。

## 概要

- **トラックA（自動・継続）**: GitHub ActionsがMedium公式RSSフィードを毎日ポーリングし、新着・更新記事を自動でMarkdown化して `posts/` に追加、画像は `assets/images/` にダウンロードして保存する
- **トラックB（半自動・初回のみ）**: RSSは最新10件までしか取得できないMedium側の制約があるため、過去記事は管理者による公式データエクスポート（Medium account settings > Download your information）を取り込んでバックフィルする

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

過去記事のバックフィル（トラックB）は、公式エクスポートを取得後に `scripts/import_export.py` を実データに合わせて実装してから実行する（現状未実装、[SPEC.md](SPEC.md) 参照）。

## データソース・ライセンス

- コード: MIT License ([LICENSE](LICENSE))
- アーカイブされた記事本文・画像: 原則 CC BY 4.0（詳細は [CONTENT_LICENSE.md](CONTENT_LICENSE.md)）。原文は各記事frontmatterの `medium_url` から参照可能
- 記事データの取得元: [medium.com/furuhashilab](https://medium.com/furuhashilab) 公式RSSフィード

## 著者

青山学院大学 地球社会共生学部 古橋研究室 (Furuhashi Lab)

## 関連リンク

- [medium.com/furuhashilab](https://medium.com/furuhashilab)（原文）
