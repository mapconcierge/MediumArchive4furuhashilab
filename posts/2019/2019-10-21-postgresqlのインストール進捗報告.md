---
title: "Postgresqlのインストール・進捗報告"
author: "Kouki Takesue"
medium_url: "https://medium.com/furuhashilab/postgresql%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB-%E9%80%B2%E6%8D%97%E5%A0%B1%E5%91%8A-1cc8d15f4d3d"
medium_guid: "1cc8d15f4d3d"
published_at: "2019-10-21T03:06:33.977000+00:00"
updated_at: "2026-08-17T08:48:41+09:00"
archived_at: "2026-08-17T08:48:41+09:00"
tags: ["report", "kouki-takesue"]
---

### Postgresqlのインストール・進捗報告

_環境構築を記事にしてみました。_

![](../../assets/images/2019-10-21-postgresqlのインストール進捗報告/001.png)

![](../../assets/images/2019-10-21-postgresqlのインストール進捗報告/002.png)

こんにちは、二期生の武末です。11月の国際会議に参加することとなり、visaの申請やスライドの作成などに追われ忙しい毎日を過ごしております。

そのため進捗らしい進捗が生まれず、ブログ更新を放置していました。10月未更新は流石にやばいだろうということで、とりあえずひとつだけ形になるものを書き込んでまいりました。

[MacOS CatalinaでPostgresqlをインストール・初期操作 - Qiita
卒業制作の関係でWEBアプリを制作しており、レンタルサーバーでsqliteが使えないことが判明しPostgresqlをインストールしようとしたら記事がバラバラで死ぬほど時間がかかったので備忘録。…qiita.com](https://qiita.com/kouki-T/items/d6444b81ce65d6412146)

以前より、Postgresqlの環境構築をするぞ！するぞ！と言ってはいたものの、様々な問題からエラー多発で泣いていたのですが、今回１から環境を見直すことで無事インストールに成功しました。

参考となるブログが３年、５年前のが多く、環境構築の資料としては問題だった点、SIPの解除やchown、PATHの通し方など広い範囲での検索が必要になる点などを考慮し、新しくQiitaの記事としてまとめてみました。

うちのゼミでデータベースを使う子は少ないと思いますが、OSSであるPostgresqlを知るというのは意外と必要かも。(OSMもPostgres使ってますしね)

ぜひともチャレンジしてみてください。
