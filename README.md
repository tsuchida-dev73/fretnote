# フレットノート

ギターコードの押さえ方図解・カポ計算・定番コード進行・コード譜プレイヤーの無料サイト。

- 公開: GitHub Pages（main / root）
- ページ生成: `python3 tools/build.py`（コード辞典・コード進行・カポ・トップ・sitemap.xml・robots.txt・llms.txt を書き出す）
- 曲プレイヤー: `player/index.html`（手書き。歌詞はパブリックドメインとオリジナル曲のみ）
- 独自ドメイン移行時: `tools/build.py` の `SITE` を書き換えて再ビルド
- アフィリエイト: `tools/build.py` の `AMAZON_TAG` にトラッキングIDを入れて再ビルド
