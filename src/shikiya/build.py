# -*- coding: utf-8 -*-
"""四季家 天文館店サイトのビルド。  cd src/shikiya && python3 build.py  →  dist/shikiya/
ページ：トップ／コース・メニュー／宴会・忘年会／個室／野菜巻き串／アクセス"""
import html, json, os, shutil
from content import *

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "..", "dist", STORE_ID)
PATH = {"top": "/", "maki": "/yasaimaki/", "course": "/course/", "enkai": "/enkai/", "room": "/private-room/", "access": "/access/"}
NAV = [("maki", "野菜巻き串"), ("course", "コース・メニュー"), ("enkai", "宴会・忘年会"), ("room", "個室"), ("access", "アクセス")]
LABEL = dict(NAV, top="トップ")
SEASON = "忘年会・新年会"  # 宴会ページの見出しに入れる季節の言葉。3月は「歓送迎会」などに替える
ALT = {
    "course": "四季家 天文館店の冬コース。せいろ蒸しご飯、お造り、炭火焼き、天ぷらが並ぶ卓",
    "maki": "鹿児島県産黒豚で野菜を巻いた、四季家の野菜巻き串の盛り合わせ",
    "makibox": "トマト・レタス・オクラ・にらなどの野菜巻き串を並べた木箱",
    "kushishabu": "せいろに盛った野菜巻き串の串しゃぶセット",
    "kushishabu2": "野菜巻き串の串しゃぶ。レタス巻き、えのき巻き、水菜巻きなどの串",
    "fondue": "野菜巻き串のチーズフォンデュ。赤い鍋のチーズを囲むトマト巻き、オクラ巻き、レタス巻き",
    "seiro": "地鶏と彩り根菜のせいろ蒸しご飯",
    "seiro-kanpachi": "かんぱちといくらのせいろ蒸しご飯",
    "seiro-kani": "ズワイガニとうに・いくらのせいろ蒸しご飯",
    "nabe": "和牛もつ鍋と黒豚しゃぶしゃぶが並ぶ、鍋ありの冬コース",
    "nabe6000": "6,000円 冬錦コース（鍋あり）。もつ鍋、黒豚しゃぶしゃぶ、せいろ、馬刺しが並ぶ卓",
    "yogan-buta": "黒豚の溶岩焼き",
    "yogan-jidori": "鹿児島県産地鶏の溶岩焼き",
    "sanshu": "牛・豚・鶏の鹿児島三味串盛り合わせ",
    "room4": "掘りごたつの個室（少人数用）",
    "room10": "テーブルをつなげた個室（10名様前後）",
    "hero-maki": "鹿児島県産黒豚で巻いた野菜巻き串の盛り合わせ。えのき、レタス、水菜、にんじん、ねぎ",
    "hero-table": "冬コースの卓。もつ鍋、黒豚しゃぶしゃぶ、せいろ蒸しご飯、お造り、馬刺しが並ぶ",
    "table": "冬コースの卓。もつ鍋、黒豚しゃぶしゃぶ、せいろ蒸しご飯、お造り、馬刺しが並ぶ",
    "seiro-kabocha": "かぼちゃと地鶏そぼろのせいろ蒸しご飯（4,000円 冬灯りコース）",
    "seiro-wagyu": "A5黒毛和牛といくらのせいろ蒸しご飯",
}
for _g, _items in MAKI:
    for _k, _n, _p in _items:
        ALT["maki-" + _k] = f"四季家の鹿児島県産黒豚の{_n}串（焼く前）"
SMALL = {"room4": 238, "room10": 198}
WIDE = {"hero-maki": (1200, 750), "hero-table": (1400, 875)}
e = lambda s: html.escape(s, quote=True)
yen = lambda n: f"{n:,}円"
tel_btn = f'<a class="btn solid" href="tel:{TEL_INTL}">電話で予約 <span class="num">&nbsp;{TEL}</span></a>'


def img(k, eager=False):
    w = SMALL.get(k, 640 if k.startswith("maki-") else 1200)
    w, h = WIDE.get(k, (w, w))
    return f'<img src="/assets/img/{k}.jpg" alt="{e(ALT[k])}" width="{w}" height="{h}"{"" if eager else " loading=lazy"} decoding="async">'


def header(page):
    nav = "".join(f'<a href="{PATH[p]}"{" aria-current=page" if p == page else ""}>{t}</a>' for p, t in NAV)
    return f'''<a class="skip" href="#main">本文へ</a>
<header class="hd"><div class="wrap">
<a class="brand" href="/"><b>四季家</b><span>{TAG}　天文館店</span></a>
<nav class="nav" aria-label="メニュー">{nav}</nav>
<a class="tel num" href="tel:{TEL_INTL}">{TEL}</a>
<button class="burger" type="button" aria-label="メニューを開く" aria-expanded="false" aria-controls="drawer"><i></i><i></i><i></i></button>
</div>
<nav class="drawer" id="drawer" aria-label="メニュー" hidden><a href="/">トップ</a>{nav}<a class="t num" href="tel:{TEL_INTL}">電話で予約　{TEL}</a></nav>
</header>'''


def footer():
    links = '<a href="/">トップ</a>' + "".join(f'<a href="{PATH[p]}">{t}</a>' for p, t in NAV)
    return f"""<footer class="ft"><div class="wrap">
<p class="name">四季家 天文館店</p>
<p>{TAG}<br>〒{ZIP} {ADDR}<br><span class="num">{TEL}</span></p>
<div class="links">{links}</div>
<small>料理写真はイメージです。内容・価格は仕入れにより変わることがあります。価格はすべて税込です。</small>
</div></footer>
<nav class="bar" aria-label="予約"><a href="/course/">コースを見る</a><a class="main" href="tel:{TEL_INTL}">電話で予約 {TEL}</a></nav>"""


def reserve(policy=False):
    pol = f'<p class="policy">{CANCEL}</p>' if policy else ""
    return f"""<section class="sec tint rsv" id="reserve"><div class="wrap">
<h2>ご予約はお電話で</h2>
<a class="num-big num" href="tel:{TEL_INTL}">{TEL}</a>
<p>営業時間中（16:00〜）に承ります。年中無休</p>{pol}
</div></section>"""


def faq(items):
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items) + "</div>"


def tiles():
    out = ""
    for c in COURSES:
        d = f'<span class="d lim">{c["limit"]}</span>' if c.get("limit") else '<span class="d">毎日</span>'
        out += f'<a class="tile" href="/course/#{c["id"]}">{img(COURSE_IMG[c["id"]])}<span class="p num">{yen(c["price"])}</span><span class="n">{c["name"]}　{c["n"][0]}品</span>{d}</a>'
    return f'<div class="tiles">{out}</div>'


def grid(items, cls=""):
    return f'<div class="grid {cls}">' + "".join(f'<figure>{img(k)}<figcaption>{n}{f"<span>{p}</span>" if p else ""}</figcaption></figure>' for k, n, p in items) + "</div>"


def info_block():
    info = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in (
        ("店名", FULL), ("住所", f"〒{ZIP} {ADDR}"), ("電話", f'<a class="num" href="tel:{TEL_INTL}">{TEL}</a>'),
        ("営業時間", "<br>".join(f"{d}　{h}<br><small>{lo}</small>" for d, h, lo in HOURS)), ("定休日", "なし"),
        ("アクセス", ACCESS + "。駐車場なし"), ("お支払い", "現金・クレジットカード（銀聯含む）・交通系IC・iD・QUICPay・PayPay・楽天ペイ・au PAY・Alipay・WeChat Pay")))
    mapq = "https://www.google.com/maps/search/?api=1&query=%E5%9B%9B%E5%AD%A3%E5%AE%B6+%E5%A4%A9%E6%96%87%E9%A4%A8%E5%BA%97+%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82%E6%9D%B1%E5%8D%83%E7%9F%B3%E7%94%BA1-26"
    return f"""<div class="info"><dl class="rows">{info}</dl>
<div class="map"><p class="status" data-status><i></i><span>16:00〜</span></p><p class="addr">{ADDR}</p><p class="note">{ACCESS}。エレベーターで7階へ</p>
<div class="btns"><a class="btn" href="{mapq}" target="_blank" rel="noopener">Googleマップで開く</a></div></div></div>"""


def ph(page, h1, lead, jump=""):
    return f"""<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ {LABEL[page]}</p>
<h1>{h1}</h1><p class="lead">{lead}</p>{jump}
</div></section>"""


MAKI6 = [("maki-tomato", "トマト巻き", "418円"), ("maki-lettuce", "レタス巻き", "418円"), ("maki-enoki", "えのき巻き", "418円"),
         ("maki-okra", "オクラ巻き", ""), ("maki-shiso-cheese", "しそチーズ巻き", ""), ("maki-ninjin", "にんじん巻き", "418円")]


# ------------------------------------------------------------------ トップ
def top():
    return f"""<section class="hero">
<figure>{img("hero-maki", eager=True)}</figure>
<div class="txt wrap"><h1><em>天文館の</em><em>完全個室居酒屋</em> <em>四季家</em></h1>
<p class="sub">黒豚の野菜巻き串と、飲み放題付きコース。</p>
<ul class="facts"><li>天文館通電停<b>徒歩2分</b></li><li>個室<b>2〜70名</b></li><li>コース<b>3,500円〜</b></li></ul>
<div class="btns"><a class="btn tel" href="tel:{TEL_INTL}">電話で予約 {TEL}</a></div></div>
</section>

<section class="sec" id="yasaimaki"><div class="wrap">
<h2>看板料理は、黒豚の野菜巻き串</h2>
<p class="lead"><b>1本418円〜</b>　鹿児島県産黒豚で巻いた13種類</p>
{grid(MAKI6, "c3")}
<p class="more"><a class="link" href="/yasaimaki/">13種類すべて見る</a></p>
</div></section>

<section class="sec tint"><div class="wrap">
<h2>串しゃぶ</h2>
<p class="lead">野菜巻き串を、だしにくぐらせて。<b>1人前2,178円</b>（2人前〜）</p>
<figure class="full">{img("kushishabu")}</figure>
</div></section>

<section class="sec" id="courses"><div class="wrap">
<h2>飲み放題付き 冬コース</h2>
<p class="lead">飲み放題は<b>日〜木 時間無制限</b>／金・土・祝前日 2時間</p>
{tiles()}
<p class="more"><a class="link" href="/enkai/">宴会・忘年会のご案内</a></p>
</div></section>

<section class="sec tint" id="room"><div class="wrap">
<h2>全席、扉付きの個室</h2>
<div class="nums"><div><b>4・6・8名</b><span>少人数の個室</span></div><div><b>10〜30名</b><span>宴会</span></div><div><b>最大70名</b><span>大人数</span></div></div>
<div class="rooms"><figure>{img("room4")}<figcaption>掘りごたつ個室</figcaption></figure><figure>{img("room10")}<figcaption>10名様前後</figcaption></figure></div>
<p class="more"><a class="link" href="/private-room/">個室のご案内</a></p>
</div></section>

<section class="sec"><div class="wrap">
<h2>ほかにも</h2>
{grid([("fondue", "野菜巻き串のチーズフォンデュ", "1人前2,178円"), ("seiro-kanpachi", "せいろ蒸しご飯", "コースの締め"), ("yogan-buta", "知覧茶薫る黒豚の溶岩焼き", "2,728円"), ("sanshu", "鹿児島三味串盛り合わせ", "1,078円")])}
<p class="more"><a class="link" href="/course/#alacarte">メニューと価格</a></p>
</div></section>

<section class="sec tint" id="access"><div class="wrap">
<h2>店舗情報</h2>
{info_block()}
</div></section>

<section class="sec" id="faq"><div class="wrap">
<h2>よくあるご質問</h2>
{faq(FAQ)}
</div></section>
{reserve()}"""


# ------------------------------------------------------------------ 野菜巻き串
def maki():
    groups = "".join(f'<h3 style="font-size:16px;margin-top:30px">{g}</h3>' + grid([("maki-" + k, n, p) for k, n, p in items], "c3") for g, items in MAKI)
    return ph("maki", "黒豚の野菜巻き串", "鹿児島県産黒豚のバラ肉で、野菜を一本ずつ巻いて焼きます。<b>1本418円〜</b>") + f"""
<section class="sec" style="padding-top:22px"><div class="wrap">
<figure class="full" style="margin-top:0">{img("makibox", eager=True)}</figure>
</div></section>

<section class="sec tint" id="list" style="padding-top:40px"><div class="wrap">
<h2>13種類</h2>
<p class="lead">価格の表示がない串は、店頭のメニューでご確認ください。写真は焼く前です。</p>
{groups}
</div></section>

<section class="sec" id="kushishabu"><div class="wrap">
<h2>串しゃぶ・チーズフォンデュ</h2>
<div class="pair">
<figure>{img("kushishabu2")}<h3>串しゃぶ</h3><p>だしにくぐらせて、ポン酢と胡麻だれで。<b>1人前2,178円</b>（2人前〜）</p></figure>
<figure>{img("fondue")}<h3>チーズフォンデュ</h3><p>温めたチーズにつけて。<b>1人前2,178円</b>（2人前〜）</p></figure>
</div>
<p class="note">冬コース6種すべてに野菜巻き串が入ります。串しゃぶのコース（5,000円）、チーズフォンデュの女子会コース（4,000円）もあります。</p>
<p class="more"><a class="link" href="/course/">コースを見る</a></p>
</div></section>

<section class="sec tint" id="faq"><div class="wrap">
<h2>よくあるご質問</h2>
{faq(FAQ_MAKI)}
</div></section>
{reserve()}"""


# ------------------------------------------------------------------ コース・メニュー
def course():
    blocks = ""
    for c in COURSES:
        s, m, f = COMPARE[c["id"]]
        tags = [f"お造り {s}"] + m.split("／") + [f.split("（")[0]]
        dl = "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in c["menu"])
        lim = f'<span class="d">{c["limit"]}</span>' if c.get("limit") else ""
        blocks += f"""<article class="course" id="{c["id"]}">{img(COURSE_IMG[c["id"]])}
<div><h3>{c["name"]}{lim}</h3><p class="p num">{yen(c["price"])}<small>税込・飲み放題付き</small></p>
<p class="note" style="margin-top:2px">鍋なし {c["n"][0]}品／鍋あり {c["n"][1]}品</p>
<ul class="main">{"".join(f"<li>{e(t)}</li>" for t in tags)}</ul>
<details class="menu"><summary>献立を見る（鍋なし）</summary><dl>{dl}</dl><p class="nabe">鍋あり：{e(c["nabe"])}</p></details></div></article>"""
    sp = "".join(f'<div><span class="k">{p}</span><span><b>{n}</b>　{k}</span></div>' for n, p, k, d in SPECIAL)
    alc = "".join(f"<div><h3>{h}</h3><ul>" + "".join(f"<li><span>{e(n)}</span><span class=num>{p}</span></li>" for n, p in items) + "</ul></div>" for h, items in ALC)
    jump = '<div class="jump">' + "".join(f'<a href="#{c["id"]}">{yen(c["price"])}</a>' for c in COURSES) + '<a href="#special">串しゃぶほか</a><a href="#alacarte">単品</a></div>'
    return ph("course", "コース・メニュー", "すべて飲み放題付き・2名様から。飲み放題は<b>日〜木 時間無制限</b>／金・土・祝前日 2時間", jump) + f"""
<section class="sec" style="padding-top:20px"><div class="wrap">
{blocks}
<p class="note">価格はお一人様・税込。12月26日〜1月3日はお一人様500円加算。鍋のご指定がない場合はもつ鍋でご用意します。</p>
</div></section>

<section class="sec tint" id="special"><div class="wrap">
<h2>串しゃぶ・女子会・飲み放題</h2>
<div class="rows">{sp}</div>
</div></section>

<section class="sec" id="alacarte"><div class="wrap">
<h2>単品メニュー</h2>
<div class="alc">{alc}</div>
<p class="note">価格は税込。抜粋です。</p>
</div></section>
{reserve()}"""


# ------------------------------------------------------------------ 宴会・忘年会
def enkai():
    return f"""<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ {LABEL["enkai"]}</p>
<h1>天文館の{SEASON}・宴会</h1>
<p class="lead">全席扉付きの個室で、2名様から最大70名様まで。飲み放題付きコース3,500円〜</p></div>
<div class="wrap"><figure class="full">{img("table", eager=True)}</figure></div></section>

<section class="sec" id="courses"><div class="wrap">
<h2>コースは6種類</h2>
<p class="lead">どの価格も<b>鍋なし</b>（締めはせいろ蒸しご飯）か<b>鍋あり</b>（もつ鍋か黒豚しゃぶ）</p>
{tiles()}
</div></section>

<section class="sec tint"><div class="wrap">
<h2>人数</h2>
<div class="nums"><div><b>2〜8名</b><span>4・6・8名用の個室</span></div><div><b>10〜30名</b><span>人数に合わせた個室</span></div><div><b>最大70名</b><span>部屋の組み方はお電話で</span></div></div>
<h2 style="margin-top:44px">飲み放題</h2>
<div class="nums"><div><b>時間無制限</b><span>日〜木・祝日</span></div><div><b>2時間</b><span>金・土・祝前日</span></div><div><b>約80種</b><span>生ビール・焼酎ほか</span></div></div>
</div></section>

<section class="sec"><div class="wrap">
<h2>幹事様へ</h2>
<dl class="rows">
<div><dt>ご予約</dt><dd>お電話で。日時・人数・コース・鍋のあり／なしをお伝えください</dd></div>
<div><dt>お支払い</dt><dd>請求書払いにも対応しています</dd></div>
<div><dt>お祝い</dt><dd>メッセージ入りのデザートプレートをご用意できます</dd></div>
</dl>
<p class="note">{CANCEL}　12月26日〜1月3日はお一人様500円加算。</p>
</div></section>

<section class="sec tint" id="faq"><div class="wrap">
<h2>よくあるご質問</h2>
{faq(FAQ_ENKAI)}
</div></section>
{reserve()}"""


# ------------------------------------------------------------------ 個室
def room():
    rows = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b, _ in ROOMS)
    return ph("room", "個室", "全席、扉付きの完全個室。掘りごたつとテーブルがあります。") + f"""
<section class="sec" style="padding-top:22px"><div class="wrap">
<div class="nums"><div><b>4・6・8名</b><span>少人数の個室</span></div><div><b>10〜30名</b><span>宴会</span></div><div><b>最大70名</b><span>大人数</span></div></div>
<div class="rooms">{img("room4", eager=True)}{img("room10")}</div>
<dl class="rows" style="margin-top:28px">{rows}</dl>
<p class="more"><a class="link" href="/enkai/">宴会・忘年会のご案内</a></p>
</div></section>

<section class="sec tint"><div class="wrap">
<h2>よくあるご質問</h2>
{faq(FAQ_ROOM)}
</div></section>
{reserve()}"""


# ------------------------------------------------------------------ アクセス
def access():
    return ph("access", "アクセス・営業時間", f"{ACCESS}。フォリス観光ビル天文館の7階です。") + f"""
<section class="sec" style="padding-top:22px"><div class="wrap">
{info_block()}
<dl class="rows" style="margin-top:32px">
<div><dt>市電</dt><dd>「天文館通」で降りて徒歩2分。鹿児島中央駅からは駅前の電停から市電で</dd></div>
<div><dt>ビル</dt><dd>フォリス観光ビル天文館のエレベーターで7階へ</dd></div>
<div><dt>お車</dt><dd>専用駐車場はありません。近くのコインパーキングをご利用ください</dd></div>
<div><dt>タクシー</dt><dd>「東千石町のフォリス観光ビル天文館」とお伝えください</dd></div>
</dl></div></section>

<section class="sec tint"><div class="wrap">
<h2>よくあるご質問</h2>
{faq(FAQ_ACCESS)}
</div></section>
{reserve()}"""


PAGES = {"top": top, "maki": maki, "course": course, "enkai": enkai, "room": room, "access": access}
PAGE_FAQ = {"top": FAQ, "maki": FAQ_MAKI, "enkai": FAQ_ENKAI, "room": FAQ_ROOM, "access": FAQ_ACCESS}


def jsonld(page):
    url = SITE_URL + PATH[page]
    rest = {
        "@context": "https://schema.org", "@type": "Restaurant", "@id": SITE_URL + "/#restaurant",
        "name": NAME, "alternateName": [FULL, "四季家", "しきや", "Shikiya Tenmonkan"], "description": DEFINITION,
        "url": SITE_URL + "/", "telephone": TEL_INTL,
        "image": [SITE_URL + f"/assets/img/{k}.jpg" for k in ("maki", "course", "nabe")],
        "address": {"@type": "PostalAddress", "postalCode": ZIP, "addressCountry": "JP", "addressRegion": "鹿児島県",
                    "addressLocality": "鹿児島市", "streetAddress": "東千石町1-26 フォリス観光ビル天文館7階"},
        "servesCuisine": ["居酒屋", "野菜巻き串", "串焼き", "鹿児島郷土料理", "黒豚しゃぶしゃぶ", "もつ鍋"],
        "priceRange": "¥3,500〜¥8,000", "acceptsReservations": True, "currenciesAccepted": "JPY",
        "paymentAccepted": "Cash, Visa, Mastercard, JCB, American Express, Diners Club, Discover, UnionPay, PayPay, Rakuten Pay, au PAY, Alipay, WeChat Pay",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "16:00", "closes": "24:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Friday", "Saturday"], "opens": "16:00", "closes": "02:00"}],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": "全席扉付き完全個室", "value": True},
                           {"@type": "LocationFeatureSpecification", "name": "飲み放題付きコース", "value": True}],
        "hasMenu": SITE_URL + PATH["course"],
        "sameAs": ["https://www.hotpepper.jp/strJ003582117/", "https://r.gnavi.co.jp/fbxc601/"],
    }
    out = [rest]
    if page != "top":
        out.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "トップ", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": LABEL[page], "item": url}]})
    if page == "course":
        out.append({"@context": "https://schema.org", "@type": "Menu", "name": "四季家 天文館店 コース・メニュー", "url": url, "inLanguage": "ja", "hasMenuSection": [
            {"@type": "MenuSection", "name": "冬コース（飲み放題付き）", "hasMenuItem": [
                {"@type": "MenuItem", "name": c["name"], "description": c["lead"], "offers": {"@type": "Offer", "price": c["price"], "priceCurrency": "JPY"}} for c in COURSES]},
            *[{"@type": "MenuSection", "name": h, "hasMenuItem": [{"@type": "MenuItem", "name": n, "description": p} for n, p in items]} for h, items in ALC]]})
    if page == "maki":
        out.append({"@context": "https://schema.org", "@type": "Menu", "name": "四季家 天文館店 黒豚の野菜巻き串", "url": url, "inLanguage": "ja", "hasMenuSection": [
            {"@type": "MenuSection", "name": g, "hasMenuItem": [dict({"@type": "MenuItem", "name": "黒豚の" + n, "image": SITE_URL + f"/assets/img/maki-{k}.jpg"},
                                                                  **({"offers": {"@type": "Offer", "price": 418, "priceCurrency": "JPY"}} if p else {})) for k, n, p in items]} for g, items in MAKI]})
    if page in PAGE_FAQ:
        out.append({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "ja",
                    "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in PAGE_FAQ[page]]})
    return "\n".join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>" for o in out)


def document(page):
    title, desc = META[page]
    url = SITE_URL + PATH[page]
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="restaurant">
<meta property="og:site_name" content="四季家 天文館店">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#faf6ee">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
{jsonld(page)}
</head>
<body>
{header(page)}
<main id="main">
{PAGES[page]()}
</main>
{footer()}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "assets", "img"))
    for f in os.listdir(os.path.join(ROOT, "img")):
        shutil.copy(os.path.join(ROOT, "img", f), os.path.join(OUT, "assets", "img", f))
    for f in ("site.css", "site.js", "favicon.svg"):
        shutil.copy(os.path.join(ROOT, f), os.path.join(OUT, "assets", f))
    for page, path in PATH.items():
        d = os.path.join(OUT, path.strip("/"))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(document(page))
    with open(os.path.join(OUT, "robots.txt"), "w") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 + "".join(f"<url><loc>{SITE_URL}{p}</loc></url>\n" for p in PATH.values()) + "</urlset>\n")
    print("built", OUT)


if __name__ == "__main__":
    main()
