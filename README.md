# 店舗サイト（1店舗目：きりしま牧場 天文館店）

店ごとに静的なサイトを作り、同じ型で増やしていくためのリポジトリ。

- `dist/<店の識別名>/` 公開しているページ。店ごとに Render の静的サイトを1つ作り、このフォルダを公開先に指定する
  - `dist/kirishima/` きりしま牧場 天文館店（5言語 × 3ページ）
  - `dist/mishima/` 三島畜産 鹿児島中央駅店（日本語6ページ＋英語1ページ）
- `api/server.js` 全店共通の予約リクエストの受け口。Render の Web サービス `store-reserve-api` で動かし、店ごとのトークノートのノートへ投稿する
- `src/` 元データ。文言・価格・店舗情報は `content.py`、見た目は `site.css`、組み立ては `build.py`
  - 直したら `cd src && python3 build.py` を実行し、できた `dist/` をコミットする（push すると自動で公開される）

## 予約リクエストを有効にする
`store-reserve-api` の環境変数に次を入れると、その店のフォームが表示される（未設定の間は電話の案内だけが出る）。

- `TALKNOTE_TOKEN` トークノート外部公開APIのアクセストークン（全店共通）
- `TALKNOTE_GROUP_ID_KIRISHIMA` きりしま牧場の投稿先ノートのID
- `ALLOW_ORIGIN` 各店サイトのURL（カンマ区切り）

トークンの出し方は https://developer.talknote.com/doc/ の「ご利用方法」。トークンはリポジトリに書かない。

## 店を増やすとき
1. `src/content.py` をその店の内容で用意する（`STORE_ID`、店名、住所、コース、写真）
2. `api/server.js` の `STORES` に1行足し、環境変数 `TALKNOTE_GROUP_ID_<識別名>` を入れる
3. Render に静的サイトを1つ追加し、公開先を `dist/<識別名>` にする

## 三島畜産 鹿児島中央駅店（2店舗目）
- 元データは `stores/mishima/`（`content.py` 文言・価格、`site.css` 見た目、`build.py` 組み立て）。直したら `cd stores/mishima && python3 build.py`
- 公開先は Render の静的サイト `mishima-chikusan`（公開フォルダ `dist/mishima`）。独自ドメインは `mishima-chikusan.jp` を予定。取得したら `content.py` の `SITE_URL` を差し替えて作り直す
- 事実の出どころ：ホットペッパー（店舗・コース・料理ページ、2026-11-26 時点）、ぐるなび（駅からの徒歩分数、8名個室）。電話番号はホットペッパー提供データ（NAVITIME 掲載）
- 写真は未掲載。料理・個室の写真が入り次第、トップと各ページに追加する
- きりしま牧場の元データは従来どおり `src/` にある（3店舗目のときに `stores/kirishima/` へ移す）
