---
title: "satoaki報告_Blenderハッカソン"
author: "SATOAKI"
medium_url: "https://medium.com/furuhashilab/satoaki%E5%A0%B1%E5%91%8A-blender%E3%83%8F%E3%83%83%E3%82%AB%E3%82%BD%E3%83%B3-b34e44225407"
medium_guid: "b34e44225407"
published_at: "2025-01-31T14:20:35.629000+00:00"
updated_at: "2026-08-17T08:14:39+09:00"
archived_at: "2026-08-17T08:14:39+09:00"
tags: ["furuhashilab", "blender"]
---

### satoaki報告_Blenderハッカソン

[blenderhackathon2025jan/data/satoaki at main · furuhashilab/blenderhackathon2025jan
Blenderハッカソン2025 成果物置き場. Contribute to furuhashilab/blenderhackathon2025jan development by creating an account on…github.com](https://github.com/furuhashilab/blenderhackathon2025jan/tree/main/data/satoaki)

佐藤愛妃（satoaki）です。今回は、ブレンダーを用いて相模原キャンパス内のオブジェクトを3Dモデリングしました。

### 芝生エリア内にある池近くの背の低い街灯

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/001.png)

今回は、芝生エリア内にある池近くの背の低い街灯をモデリングしました。ポリゴン数に制限があったので、細分化し過ぎず、表面が滑らかになるように工夫しました。

元の画像↓

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/002.jpeg)

### 作業概要

### body部分

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/003.png)

まず、構造物は円柱（シリンダー）を選択して設置します。 それから、Add ModifierのSubdivisionでオブジェクトを10に分割し、円柱を滑らかにします。

s z 4で縦（+z軸方向）に4倍（×4拡大）します。これで、街灯らしくなります。

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/004.png)

### ライト部分

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/005.png)

ループカット多めに入れて凹凸を再現します。ループカット→辺を選択→スケールでxとy軸方向に同間隔で調整します。 ここら辺は集中して作業したのでスクリーンショット撮り忘れました。この段階での完成物はこんなかんじでした。

### 色付け

色も付けました。今回はシンプルなので、3色です。

### ポリゴン数削除

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/006.png)

今回はポリゴン数が1000以下と指定ですが、細分化した状態では3000近くなってしまうので、メッシュを荒くしていきます。 ↓修正前はこんなかんじです。

↓ポリゴン数を減らすため、Add modifier→Decimateを選択します。

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/007.png)

Ratioを調節し、984まで落としました。所感として、800以下にすると、街灯上部分がカクカクし始めます。

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/008.png)

### 完成形

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/009.png)

完成形です。エクスポート後に3Dビューワーで見てみました。

ライトの色変えて遊んでみました。

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/010.png)

### 感想

今回の作業では、最後にポリゴン数が1000よりオーバーしていると気づき、修正をいれました。ただ、初めから少ないポリゴン数で作業するより、細分化しておいた方が調整が楽でした。形を調節するときは丁寧に作業を進めたので、出来上がったときに達成感がありました。本物と比率や頭身が若干違うところもあるので、次は細かいところもクリアしていきたいです。ショートカットキーもマスターして、作業を楽に進められるようにしたいです。

![](../../assets/images/2025-01-31-satoaki報告-blenderハッカソン/011.jpeg)
