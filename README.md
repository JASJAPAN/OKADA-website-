# きりしま牧場 天文館店 サイト

- `dist/` 公開しているページ（5言語 × 3ページ）。Render の静的サイト `kirishima-bokujo` が配信
- `api/server.js` 予約リクエストの受け口。Render の Web サービス `kirishima-reserve` で動かし、トークノートのノートへ投稿する
- `src/` 元データ。文言・価格は `content.py`、見た目は `site.css`。直したら `cd src && python3 build.py` を実行し、できた `dist/` をコミットする

## 予約リクエストを有効にする
`kirishima-reserve` の環境変数に次の2つを入れると、サイトのフォームが表示される（未設定の間は電話の案内だけが出る）。

- `TALKNOTE_TOKEN` トークノート外部公開APIのアクセストークン
- `TALKNOTE_GROUP_ID` 投稿先ノートのID

トークンの出し方は https://developer.talknote.com/doc/ の「ご利用方法」。トークンはリポジトリに書かない。
