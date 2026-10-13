---
title: "Claude Codeを使ってPanoramaxにアップロードした写真を地図上に反映してみた！"
author: "Fuka Okamura"
medium_url: "https://medium.com/furuhashilab/panoramax%E4%BD%BF%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%9F-5a96531521d7"
medium_guid: "5a96531521d7"
published_at: "2026-10-12T21:55:16+00:00"
updated_at: "2026-10-13T10:11:24+00:00"
archived_at: "2026-10-13T10:11:24+00:00"
tags: []
---

こんにちは。岡村です。  
SoTM Asia OsakaのNANBA Wheelchair Mapping Party でMapilally以外にも、Panoramaxがあることを知ったので、今回試しに、使ってみました。  
成果物（Claude Codeを使ってPanoramaxにアップロードした写真を地図上に反映した）は、GitHub Pages として公開しています。  
GitHub：[furuhashilab/Hackathon\_Oct\_FukaOkamura](https://github.com/furuhashilab/Hackathon_Oct_FukaOkamura)  
成果物：[撮影シーケンス一覧](https://furuhashilab.github.io/Hackathon_Oct_FukaOkamura/)

#### Panoramaxとは何か

Panoramaxは、誰でも参加できるオープンな「ストリートビュー」プラットフォームです。Google ストリートビューのように、実際の道路や風景を写した写真を地図と連動して閲覧できますが、決定的な違いが2つあります。**撮影者は市民や自治体など誰でもよく**、**写真はすべてオープンライセンスで公開**されます。

[Panoramax — The free alternative to photo-mapping territories](https://panoramax.fr/)

#### 誕生の背景

Panoramaxは2022年、フランス国立地理院（IGN）とフランスのOpenStreetMapコミュニティが共同で立ち上げました。発端は2021年にさかのぼります。IGNが「ジオコモンズ（地理情報の公共財）」をテーマにパートナーを募ったとき、OpenStreetMap Franceがオープンな路面写真データベースの創設を提案し、採択されたのです。

当初の動機は実用的なものでした。フランスの地方自治体が道路設備の台帳更新や道路インフラの管理に使えるツールが必要とされていました。プロジェクト名「Panoramax」は、48人のコミュニティメンバーによる提案と投票を経て決まっています。予算は50万ユーロ、2024年3月時点のチーム規模は6名という、スモールスタートのプロジェクトです。

#### 使い始めてびっくり！

**フェデレーション（分散）方式**を採用していていること！個人や組織が独自のインスタンス（サーバー）を運営でき、それらが連携してひとつの大きなネットワークを構成していた。

つまり、写真をアップロードするときに、どこにアップロードするか選ぶ必要がある。

今回、私は、OSM-FRから写真をアップロードしました。  
ちなみにアプリもありますが、今回は、Iphoneのノーマルカメラで写真を撮り、その写真をブラウザからアップロードしました。

![](../../assets/images/2026-10-12-claude-codeを使ってpanoramaxにアップロードした写真を地図上に反映してみた/001.png)![](../../assets/images/2026-10-12-claude-codeを使ってpanoramaxにアップロードした写真を地図上に反映してみた/002.png)

#### 使ってみた感想

私は、この一週間イタリアを観光していたので、歩きながらでも簡単にできるPanoramaxはよかった。ノーマルカメラで風景を撮影しておけば、あとからアップロードすればよいので、手軽に使えた。

#### Claude Codeを使用してGitHubを更新した感想

Panoramaxに写真をアップロードした後、CSV形式でダウンロードし、Claude Codeに地図を作ってもらったが、あっというまにできあがった。  
GitHub Pagesの設定はClaude自体ではできなかったため、手動で設定する必要があった。やり方が分からなくても、その状況を説明したり、スクリーンショットを送ったりすると、エラーの原因やその解決方法を提示してくれるのでその方法でお願いすると解決した。必ず、提案した内容で実行（マージ）するか確認してから実行するので安心。GitHubの仕組みを理解していなくても、作れてしまうのはすごい簡単で便利だけど、最後には、それがあっているか確認できる知識は必要だと思った。

#### グラレコ

![](../../assets/images/2026-10-12-claude-codeを使ってpanoramaxにアップロードした写真を地図上に反映してみた/003.png)![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=5a96531521d7)

---

[Claude Codeを使ってPanoramaxにアップロードした写真を地図上に反映してみた！](https://medium.com/furuhashilab/panoramax%E4%BD%BF%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%9F-5a96531521d7) was originally published in [Furuhashi(mapconcierge)Lab.](https://medium.com/furuhashilab) on Medium, where people are continuing the conversation by highlighting and responding to this story.
