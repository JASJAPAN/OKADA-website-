# -*- coding: utf-8 -*-
"""三島畜産 鹿児島中央駅店 サイトのビルド。  python3 build.py → ../../dist/mishima/"""
import html, json, os, shutil
from content import *

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "..", "dist", STORE_ID)
e = lambda s: html.escape(s, quote=True)
yen = lambda n: f'{n:,}<small>円（税込）</small>'
NAV = [("", "トップ"), ("course/", "コース"), ("menu/", "お品書き"), ("private-room/", "個室・宴会"), ("access/", "アクセス"), ("faq/", "よくある質問")]
TITLES = dict(NAV)


def restaurant_ld():
    return {"@context": "https://schema.org", "@type": "Restaurant", "@id": SITE_URL + "/#restaurant",
            "name": FULL, "alternateName": [NAME, "三島畜産", "Mishima Chikusan Kagoshima-Chuo Station"],
            "url": SITE_URL + "/", "telephone": TEL_INTL,
            "address": {"@type": "PostalAddress", "postalCode": ZIP, "addressRegion": "鹿児島県", "addressLocality": "鹿児島市",
                        "streetAddress": "中央町7-1 地下1階", "addressCountry": "JP"},
            "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "16:00", "closes": "24:00"}],
            "servesCuisine": ["鹿児島郷土料理", "居酒屋", "黒豚しゃぶしゃぶ", "地鶏料理", "藁焼き"],
            "priceRange": "¥3,000〜¥4,000", "acceptsReservations": True, "hasMenu": SITE_URL + "/menu/",
            "paymentAccepted": "現金, クレジットカード, 電子マネー, QRコード決済", "currenciesAccepted": "JPY",
            "maximumAttendeeCapacity": 150,
            "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in ("個室", "掘りごたつ", "貸切", "飲み放題", "英語メニュー")],
            "description": "JR鹿児島中央駅から徒歩約3分。全150席、掘りごたつの個室で、薩摩地鶏・黒豚・きびなご・枕崎産かつおの藁焼きなど鹿児島の郷土料理を出す居酒屋。2.5時間飲み放題付きコースは3,500円（税込）から。"}


def crumbs_ld(path):
    items = [("トップ", SITE_URL + "/")] + ([(TITLES[path], SITE_URL + "/" + path)] if path else [])
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def page(path, title, desc, body, ld=(), lang="ja", alt=None):
    nav = "".join(f'<a href="/{p}"{" aria-current=\"page\"" if p == path else ""}>{t}</a>' for p, t in NAV)
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    url = SITE_URL + "/" + path
    alts = ""
    if alt:
        alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE_URL}/{p}">\n' for l, p in alt)
    en = lang == "en"
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{alts}<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(NAME)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{"en_US" if en else "ja_JP"}">
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#f5f2eb">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
{lds}</head>
<body>
<a class="skip" href="#main">{"Skip to content" if en else "本文へ"}</a>
<header class="hd"><div class="wrap">
<a class="brand" href="/">三島畜産<span>鹿児島中央駅店</span></a>
<nav class="nav" aria-label="メニュー">{nav}<a href="/en/" lang="en"{" aria-current=\"page\"" if en else ""}>English</a></nav>
<a class="tel num" href="tel:{TEL_INTL}">{TEL}</a>
</div></header>
<main id="main">
{body}
</main>
<footer class="ft"><div class="wrap">
<p class="name">{NAME}</p>
<p>〒{ZIP} {ADDR}<br>電話 <a class="num" href="tel:{TEL_INTL}">{TEL}</a>　営業 {HOURS}（定休日なし）</p>
<div class="links">{"".join(f'<a href="/{p}">{t}</a>' for p, t in NAV)}<a href="/en/" lang="en">English</a></div>
<p><small>正式な店名：{FULL}<br>運営：{OPERATOR}　価格はすべて税込です。内容は仕入れにより変わることがあります。</small></p>
</div></footer>
<nav class="bar" aria-label="{"Quick links" if en else "すぐ使う"}">
<a href="/course/">{"Courses" if en else "コース"}</a><a class="main num" href="tel:{TEL_INTL}">{TEL}</a><a href="/access/">{"Access" if en else "アクセス"}</a>
</nav>
</body>
</html>
'''


def oshi(items):
    return '<ul class="oshi">' + "".join(f'<li><span>{e(n)}</span><span class="p num">{p}<small>円</small></span></li>' for n, p in items) + "</ul>"


def kondate(menu):
    return "<dl>" + "".join(f"<dt>{e(c)}</dt><dd>{'<br>'.join(e(i) for i in items)}</dd>" for c, items in menu) + "</dl>"


def call_btn(label="電話で予約する"):
    return f'<a class="btn call" href="tel:{TEL_INTL}"><small>{label}</small><span class="num">{TEL}</span></a>'


# ------------------------------------------------------------ トップ
def price_rows(link=True):
    out = ""
    for c in COURSES:
        nm = f'<a href="/course/#{c["id"]}">{c["name"]}</a>' if link else c["name"]
        pop = '<span class="pop">一番人気</span>' if c.get("popular") else ""
        note = "・" + c["note"] if c["note"] else ""
        out += (f'<li><p class="pp num">{c["price"]:,}<small>円</small></p><div><h3>{nm}{pop}</h3>'
                f'<p>{e(c["lead"])}</p><p class="sub">{c["count"]}・2.5時間飲み放題付き{note}</p></div></li>')
    return f'<ol class="prices">{out}</ol><p class="taxnote">価格はお一人様・税込です。どのコースも鍋なし・鍋ありを選べます。ご予約は2名様から。</p>'


def telbig(label="ご予約・お問い合わせ"):
    return f'<p class="telbig"><span>{label}</span><a class="num" href="tel:{TEL_INTL}">{TEL}</a></p>'


def closing():
    return ('<section class="closing"><div class="wrap"><h2>ご予約はお電話で</h2>'
            '<p>毎日 16:00〜24:00　当日のご予約もお受けします</p>' + telbig("三島畜産 鹿児島中央駅店") + '</div></section>')


def top():
    faq = "".join(f"<div><h3>{e(q)}</h3><p>{e(a)}</p></div>" for q, a in FAQ[:5])
    body = f"""<section class="hero"><div class="wrap hero-in">
<div>
<h1><span>鹿児島の郷土料理を、</span><span>掘りごたつの個室で。</span></h1>
<p class="lead">薩摩地鶏の刺身と炭火のたたき、黒豚のしゃぶしゃぶ、わらの火で焼く枕崎のかつお、ご注文を受けてから炊く釜飯。鹿児島中央駅から歩いて3分の店で、2名様の個室からお出ししています。</p>
<p class="meta"><span>鹿児島中央駅 <b>徒歩3分</b></span><span>毎日 <b class="num">16:00〜24:00</b></span><span>コース <b class="num">3,500〜10,000円</b></span></p>
{telbig()}
</div>
<p class="yago">三島畜産<small>鹿児島中央駅店</small></p>
</div></section>

<section class="sec tone" id="meibutsu"><div class="wrap">
<h2>鹿児島の名物を、ひと通り</h2>
<p>旅行や出張で鹿児島に来た方が、食べておきたいと思う料理を一軒で。</p>
<div class="rows block">
<div><h3>薩摩地鶏と黒豚</h3><p>薩摩地鶏は朝引きを刺身と炭火のたたきで、甘い醤油を添えて。黒豚はしゃぶしゃぶ、角煮、軟骨の味噌煮、知覧茶を使った溶岩焼きでお出しします。</p></div>
<div><h3>藁焼きと鮮魚</h3><p>枕崎産のかつおは、わらの火で一気に焼いてたたきに。きびなごはお造りとフライで。鮮魚のお造りは三種盛りと五種盛りがあります。</p></div>
<div><h3>釜飯と鍋、締め</h3><p>釜飯はご注文を受けてから炊き上げます。鍋は和牛もつ鍋と黒豚のしゃぶしゃぶ。締めはさつまうどん、甘味は鹿児島のかき氷「しろくま」。</p></div>
</div>
<p class="more"><a class="link" href="/menu/">お品書きを見る</a></p>
</div></section>

<section class="sec" id="course"><div class="wrap">
<h2>コース</h2>
<p>鹿児島の料理を組んだ、2.5時間の飲み放題付きのコースです。</p>
<div class="block">{price_rows()}</div>
<p class="more"><a class="link" href="/course/">献立と条件を見る</a></p>
</div></section>

<section class="sec tone" id="room"><div class="wrap">
<h2>個室について</h2>
<p>席はすべて掘りごたつの個室です。足を伸ばして座れます。全150席、2名様から着席で最大150名様までお受けします。</p>
<div class="rows block">
<div><h3>2名様・4名様・6名様</h3><p>接待や会食、ご家族でのお食事、旅行中の夕食に。8,000円と10,000円のコースは、お一人ずつ盛り付けてお出しします。</p></div>
<div><h3>8名様・10名様</h3><p>部署の飲み会、歓送迎会、同窓会に。人数に合わせて部屋をご用意します。</p></div>
<div><h3>それ以上・貸切</h3><p>着席で最大150名様まで。会社のご宴会は請求書払いもご相談いただけます。</p></div>
</div>
<p class="more"><a class="link" href="/private-room/">個室・宴会について</a></p>
</div></section>

<section class="sec" id="access"><div class="wrap two">
<div><h2>店舗情報</h2>
<dl class="dl2">
<div><dt>店名</dt><dd>{NAME}</dd></div>
<div><dt>住所</dt><dd>〒{ZIP}<br>{ADDR}</dd></div>
<div><dt>電話</dt><dd><a class="num" href="tel:{TEL_INTL}">{TEL}</a></dd></div>
<div><dt>営業時間</dt><dd><span class="num">{HOURS}</span>（毎日）<br>ラストオーダー {LO}</dd></div>
<div><dt>行き方</dt><dd>JR鹿児島中央駅から徒歩約3分<br>市電 高見橋電停から徒歩約3分</dd></div>
</dl>
<p class="more links-row"><a class="link" href="/access/">アクセス・お支払い方法</a><a class="link" href="{MAP}" target="_blank" rel="noopener">Googleマップで開く</a></p></div>
<div><h2>よくある質問</h2><div class="faq">{faq}</div>
<p class="more"><a class="link" href="/faq/">質問をすべて見る</a></p></div>
</div></section>
{closing()}"""
    return page("", f"{NAME}｜鹿児島中央駅 徒歩3分の個室居酒屋・鹿児島郷土料理",
                "JR鹿児島中央駅から徒歩約3分。掘りごたつの個室で、薩摩地鶏・黒豚しゃぶしゃぶ・きびなご・かつおの藁焼きなど鹿児島の郷土料理をお出しします。全150席、2名様から最大150名様まで。2.5時間飲み放題付きコースは3,500円（税込）から。",
                body, [restaurant_ld()], alt=[("ja", ""), ("en", "en/"), ("x-default", "")])


# ------------------------------------------------------------ コース
def course():
    arts = ""
    for c in COURSES:
        ari = kondate(c["ari"]) if c["ari"] else f'<p class="tel-note">{c["ari_text"]}<br><a class="num" href="tel:{TEL_INTL}">{TEL}</a></p>'
        cond = f'<p class="cond">税込・お一人様　{c["count"]}・2.5時間飲み放題付き・2名様から{"・" + c["note"] if c["note"] else ""}</p>'
        arts += f'''<article class="course" id="{c["id"]}"><header><h2>{c["name"]}</h2><p class="pr num">{c["price"]:,}<small>円</small></p></header>
{cond}<p class="desc">{e(c["lead"])}</p>
<div class="kon"><div><h3>鍋なし</h3>{kondate(c["nashi"])}</div><div><h3>鍋あり</h3>{ari}</div></div></article>'''
    nomi = "".join(f"<div><dt>{k}</dt><dd>{e(v)}</dd></div>" for k, v in NOMIHO)
    body = f'''<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ コース</p>
<h1>コース</h1>
<p class="lead">鹿児島の郷土料理を組んだ、2.5時間飲み放題付きのコースです。3,500円から10,000円まで七つの価格があり、どれも鍋なしと鍋ありを選べます。価格はお一人様・税込、ご予約は2名様から承ります。</p>
{telbig()}
</div></section>
<section class="sec tone"><div class="wrap">
<h2>価格で選ぶ</h2>
<div class="block">{price_rows().replace("/course/#", "#")}</div>
</div></section>
<section class="sec" style="padding-top:0;border-top:0"><div class="wrap">
{arts}
<article class="course" id="sandai"><header><h2>{SANDAI["name"]}</h2><p class="pr num">{SANDAI["price"]:,}<small>円</small></p></header>
<p class="cond">税込・お一人様　2.5時間飲み放題付き・2名様から・鍋あり（黒豚しゃぶしゃぶ）</p><p class="desc">{e(SANDAI["lead"])}</p>
<div class="kon"><div><h3>献立</h3>{kondate(SANDAI["menu"])}</div></div></article>
</div></section>
<section class="sec tone" id="rules"><div class="wrap two">
<div><h2>コースの決まりごと</h2>
<ul class="notes">
<li>コースのお時間は2時間30分です。金曜・土曜・祝前日は2時間制になります。</li>
<li>飲み放題のラストオーダーは終了の30分前です。</li>
<li>30分の延長は、お一人様＋500円で承ります。</li>
<li>料理のみ（飲み放題なし）の場合は、コース料金から1,000円引きです。</li>
<li>12月26日〜1月3日は、コース料金がお一人様＋500円になります。</li>
<li>3,500円の冬宵コースは日〜木曜・祝日限定です。</li>
<li>鍋を選べるコースでご指定がない場合は、もつ鍋をご用意します。釜飯を選べるコースでご指定がない場合は、黒毛和牛の釜飯をご用意します。</li>
<li>献立は仕入れにより変わることがあります。</li>
<li>会社のご宴会は請求書払いもご相談ください。</li>
</ul>
<h3 style="margin-top:30px">キャンセルについて</h3>
<ul class="notes"><li>コースのご予約：前日のキャンセルはコース料金の50%、当日は100%を申し受けます。</li><li>お席のみのご予約：当日のキャンセルはお一人様4,000円を申し受けます。</li><li>10名様以上・貸切のご予約は、別の定めがあります。ご予約の際にご案内します。</li></ul>
</div>
<div id="nomihodai"><h2>飲み放題の内容</h2>
<dl class="dl2">{nomi}</dl>
<p style="margin-top:16px;font-size:14.5px">＋500円のプラチナ飲み放題：{e(PLATINUM)}が加わります。</p>
<h3 style="margin-top:30px">飲み放題だけ・二次会</h3>
<ul class="oshi"><li><span>2時間 単品飲み放題</span><span class="p num">2,000<small>円</small></span></li><li><span>二次会プラン（料理3品＋飲み放題）</span><span class="p num">2,500<small>円</small></span></li></ul>
</div></div></section>
{closing()}'''
    offers = [{"@type": "Offer", "name": c["name"] + "（2.5時間飲み放題付き）", "price": c["price"], "priceCurrency": "JPY", "url": SITE_URL + "/course/#" + c["id"]} for c in COURSES]
    ld = {"@context": "https://schema.org", "@type": "Restaurant", "@id": SITE_URL + "/#restaurant", "name": FULL, "url": SITE_URL + "/", "makesOffer": offers}
    return page("course/", f"コース（2.5時間飲み放題付き 3,500円〜）｜{NAME}",
                "三島畜産 鹿児島中央駅店のコース。2.5時間飲み放題付きで3,500円・4,000円・4,500円・5,000円・6,000円・8,000円・10,000円（税込）。鍋なし・鍋ありを選べ、個室でご利用いただけます。献立と条件を掲載。",
                body, [ld, crumbs_ld("course/")])


# ------------------------------------------------------------ お品書き
def menu():
    jump = "".join(f'<li><a href="#m{i}">{e(c)}</a></li>' for i, (c, _, _) in enumerate(MENU))
    secs = "".join(f'<section class="menu-sec" id="m{i}"><h2>{e(c)}</h2>{f"<p class=cap>{e(cap)}</p>" if cap else ""}{oshi(items)}</section>' for i, (c, cap, items) in enumerate(MENU))
    body = f'''<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ お品書き</p>
<h1>お品書き</h1>
<p class="lead">単品の料理です。価格はすべて税込。黒豚、薩摩地鶏、きびなご、さつま揚げ、かつおの藁焼きなど、鹿児島の料理を中心に揃えています。</p>
</div></section>
<section class="sec" style="padding-top:0;border-top:0"><div class="wrap">
<ul class="jump">{jump}</ul>
<div class="menu-cols">{secs}</div>
<p style="font-size:14px;color:var(--soft)">仕入れにより、内容と価格が変わることがあります。英語を併記したメニューブックを店内にご用意しています。</p>
</div></section>
{closing()}'''
    ld = {"@context": "https://schema.org", "@type": "Menu", "name": NAME + " お品書き", "url": SITE_URL + "/menu/", "inLanguage": "ja",
          "hasMenuSection": [{"@type": "MenuSection", "name": c, "hasMenuItem": [
              {"@type": "MenuItem", "name": n, "offers": {"@type": "Offer", "price": int(p.replace(",", "")), "priceCurrency": "JPY"}} for n, p in items]} for c, _, items in MENU]}
    return page("menu/", f"お品書き（単品メニューと価格）｜{NAME}",
                "三島畜産 鹿児島中央駅店の単品メニューと税込価格。藁焼きカツオのたたき、薩摩地鶏刺し、黒豚のしゃぶしゃぶ、きびなご、さつま揚げ、溶岩焼き、釜飯、さつまうどん、しろくま。",
                body, [ld, crumbs_ld("menu/")])


# ------------------------------------------------------------ 個室・宴会
def room():
    body = f'''<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ 個室・宴会</p>
<h1>個室・宴会</h1>
<p class="lead">席は掘りごたつの個室です。2名様から、着席で最大150名様までお受けできます。鹿児島中央駅から徒歩約3分なので、新幹線で来られる方との会食や、駅周辺に泊まる方のご宴会にも便利です。</p>
{telbig("人数と日にちのご相談")}
</div></section>
<section class="sec"><div class="wrap">
<h2>人数に合わせた部屋</h2>
<dl class="dl2">
<div><dt>2名様</dt><dd>お二人用の個室。旅行中の夕食、記念日のお食事に。</dd></div>
<div><dt>4名様・6名様</dt><dd>接待や会食、ご家族でのお食事、少人数の飲み会に。</dd></div>
<div><dt>8名様・10名様</dt><dd>部署の飲み会、歓送迎会、同窓会に。</dd></div>
<div><dt>それ以上</dt><dd>人数に合わせて部屋をご用意します。着席で最大150名様まで、貸切もご相談ください。</dd></div>
<div><dt>総席数</dt><dd>150席（掘りごたつ・個室）</dd></div>
</dl>
</div></section>
<section class="sec tone"><div class="wrap">
<h2>こんな席に</h2>
<div class="rows block">
<article><h3>会社の宴会</h3><p>忘年会、新年会、歓送迎会、懇親会。2.5時間飲み放題付きのコースは3,500円（税込）から。請求書払いもご相談いただけます。</p></article>
<article><h3>接待・会食</h3><p>8,000円と10,000円のコースは、お一人ずつ盛り付けてお出しします。県外からのお客様には、鹿児島の名物を揃えたコースを。</p></article>
<article><h3>旅行・出張の夕食</h3><p>駅から近く、24時まで営業しています。鹿児島の郷土料理をひと通り召し上がれる「鹿児島三大名物堪能コース」があります。</p></article>
</div>
<p class="more"><a class="link" href="/course/">コースを見る</a></p>
</div></section>
<section class="sec"><div class="wrap">
<h2>ご宴会の前に</h2>
<ul class="notes">
<li>コースのご予約は2名様から承ります。</li>
<li>コースのお時間は2時間30分、金曜・土曜・祝前日は2時間制です。</li>
<li>お祝いやサプライズのご相談も承ります。ご予約の際にお知らせください。</li>
<li>お子様連れでもご利用いただけます。</li>
<li>店内は分煙で、喫煙スペースがあります。</li>
<li>専用の駐車場はありません。近くのコインパーキングをご利用ください。</li>
</ul>
</div></section>
{closing()}'''
    return page("private-room/", f"個室・宴会（2名〜最大150名）｜{NAME}",
                "三島畜産 鹿児島中央駅店は掘りごたつの個室。2名・4名・6名・8名・10名用の部屋があり、着席で最大150名様の宴会、貸切に対応。鹿児島中央駅から徒歩約3分。忘年会、歓送迎会、接待、旅行の夕食に。",
                body, [crumbs_ld("private-room/")])


# ------------------------------------------------------------ アクセス
def access():
    pay = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in PAY)
    body = f'''<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ アクセス</p>
<h1>アクセス・店舗情報</h1>
<p class="lead">JR鹿児島中央駅から徒歩約3分、市電の高見橋電停から徒歩約3分です。店は建物の地下1階にあります。</p>
<p class="more" style="margin-top:40px"><a class="link" href="{MAP}" target="_blank" rel="noopener">Googleマップで開く</a></p>{telbig()}
</div></section>
<section class="sec"><div class="wrap two">
<div><h2>店舗情報</h2>
<dl class="dl2">
<div><dt>店名</dt><dd>{NAME}<br><span style="font-size:13.5px;color:var(--soft)">{FULL}</span></dd></div>
<div><dt>住所</dt><dd>〒{ZIP}<br>{ADDR}</dd></div>
<div><dt>電話</dt><dd><a class="num" href="tel:{TEL_INTL}">{TEL}</a></dd></div>
<div><dt>営業時間</dt><dd><span class="num">{HOURS}</span>（毎日）<br>ラストオーダー {LO}</dd></div>
<div><dt>定休日</dt><dd>なし<br>年末年始の営業はお電話でご確認ください。</dd></div>
<div><dt>席数</dt><dd>150席（掘りごたつ・個室）</dd></div>
<div><dt>予算の目安</dt><dd>お一人様 3,000円〜4,000円</dd></div>
<div><dt>喫煙</dt><dd>分煙（喫煙スペースあり）</dd></div>
<div><dt>駐車場</dt><dd>なし（近くにコインパーキングがあります）</dd></div>
<div><dt>お子様</dt><dd>お子様連れでご利用いただけます</dd></div>
<div><dt>外国語</dt><dd>英語を併記したメニューブックがあります</dd></div>
</dl></div>
<div><h2>行き方</h2>
<dl class="dl2">
<div><dt>JR・新幹線</dt><dd>鹿児島中央駅から徒歩約3分</dd></div>
<div><dt>市電</dt><dd>高見橋電停から徒歩約3分</dd></div>
<div><dt>お車</dt><dd>専用駐車場はありません。近くのコインパーキングをご利用ください。</dd></div>
</dl>
<h2 style="margin-top:96px">お支払い方法</h2>
<dl class="dl2">{pay}
<div><dt>請求書払い</dt><dd>会社のご宴会はご相談ください</dd></div></dl>
</div></div></section>
{closing()}'''
    return page("access/", f"アクセス・営業時間・お支払い方法｜{NAME}",
                "三島畜産 鹿児島中央駅店は鹿児島市中央町7-1 地下1階。JR鹿児島中央駅から徒歩約3分、市電 高見橋電停から徒歩約3分。営業時間16:00〜24:00、定休日なし。電話099-813-8722。使えるカード・電子マネー・QR決済を掲載。",
                body, [restaurant_ld(), crumbs_ld("access/")])


# ------------------------------------------------------------ よくある質問
def faq():
    items = "".join(f"<div><h3>{e(q)}</h3><p>{e(a)}</p></div>" for q, a in FAQ)
    body = f'''<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ よくある質問</p>
<h1>よくある質問</h1>
<p class="lead">場所、個室、コース、飲み放題、お支払いについて、よくいただく質問にお答えします。</p>
</div></section>
<section class="sec" style="padding-top:0;border-top:0"><div class="wrap"><div class="faq">{items}</div></div></section>
{closing()}'''
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    return page("faq/", f"よくある質問｜{NAME}",
                "三島畜産 鹿児島中央駅店へのよくある質問。駅からの行き方、個室の人数、最大宴会人数、コースの価格、飲み放題の時間、選べる鍋、支払い方法、駐車場、喫煙、英語メニュー。",
                body, [ld, crumbs_ld("faq/")])


# ------------------------------------------------------------ English
def english():
    rows = "".join(f'<li><span>{n}</span><span class="p num">¥{c["price"]:,}</span></li>' for n, c in zip(
        ["Fuyuyoi course (10 dishes, Sun–Thu and holidays only)", "Fuyukaze course (11 dishes)", "Fuyuutage course (12 dishes, most popular)",
         "Minori course (12 dishes, with seared wagyu)", "Irodori course (13 dishes)", "Kaori course (14 dishes, individually plated)", "Kiwami course (15 dishes, individually plated)"], COURSES))
    body = f'''<section class="ph"><div class="wrap">
<p class="crumb"><a href="/" lang="ja">トップ</a> ／ English</p>
<h1 style="letter-spacing:.02em">Mishima Chikusan, Kagoshima-Chuo Station</h1>
<p class="lead">A Kagoshima-cuisine izakaya with private rooms, about three minutes on foot from JR Kagoshima-Chuo Station. Every table is in a private room with sunken (horigotatsu) seating, for two guests up to parties of 150.</p>
<p class="telbig"><span>Reservations by phone</span><a class="num" href="tel:{TEL_INTL}">+81-99-813-8722</a></p><p class="more" style="margin-top:32px"><a class="link" href="{MAP}" target="_blank" rel="noopener">Open in Google Maps</a></p>
</div></section>
<section class="sec"><div class="wrap two">
<div><h2 style="letter-spacing:.02em">What we serve</h2>
<p style="margin-top:28px">Local dishes of Kagoshima: Satsuma jidori chicken as sashimi and charcoal-seared tataki, Kurobuta black pork shabu-shabu and braised pork, kibinago (silver-stripe herring) as sashimi or fried, satsuma-age fish cakes, and bonito from Makurazaki seared over burning straw. Rice is cooked to order in individual kama pots. Shochu from Kagoshima is on the drinks list.</p>
<p style="margin-top:20px">A menu book with English is available in the restaurant. Please note that several local specialities are served raw (chicken, fish, horse meat); tell the staff if you prefer cooked dishes only.</p>
<h2 style="letter-spacing:.02em;margin-top:96px">Set courses</h2>
<p>All courses include 2.5 hours of all-you-can-drink (2 hours on Fridays, Saturdays and days before holidays). Prices are per person, tax included, for two or more guests. Each price is offered with or without a hot pot. Without drinks, each course is ¥1,000 less.</p>
<ul class="oshi" style="margin-top:12px">{rows}<li><span>Kagoshima Three Specialities course (with Kurobuta shabu-shabu)</span><span class="p num">¥5,000</span></li></ul>
<p style="margin-top:12px;font-size:14.5px">From 26 December to 3 January, courses are ¥500 more per person. Single dishes start at about ¥500; see the <a href="/menu/" lang="ja">à la carte menu (Japanese)</a>.</p></div>
<div><h2 style="letter-spacing:.02em">Hours and access</h2>
<dl class="dl2">
<div><dt>Hours</dt><dd>16:00–24:00 daily<br>Last order: food 23:00, drinks 23:30</dd></div>
<div><dt>Closed</dt><dd>No regular closing day. Please call about the New Year period.</dd></div>
<div><dt>Address</dt><dd>{ADDR_EN}<br><span lang="ja">〒{ZIP} {ADDR}</span></dd></div>
<div><dt>Access</dt><dd>About 3 minutes on foot from JR Kagoshima-Chuo Station (Shinkansen). About 3 minutes from Takamibashi tram stop.</dd></div>
<div><dt>Seats</dt><dd>150, all in private rooms with sunken seating</dd></div>
<div><dt>Payment</dt><dd>Cash; Visa, Mastercard, JCB, American Express, Diners Club, Discover, UnionPay; Alipay, WeChat Pay, PayPay; transit IC cards</dd></div>
<div><dt>Smoking</dt><dd>Separate smoking area</dd></div>
<div><dt>Children</dt><dd>Welcome</dd></div>
<div><dt>Parking</dt><dd>None. Coin-operated car parks are nearby.</dd></div>
<div><dt>Booking</dt><dd>By phone: <a class="num" href="tel:{TEL_INTL}">+81-99-813-8722</a> (from Japan: {TEL})</dd></div>
</dl></div>
</div></section>'''
    ld = restaurant_ld(); ld["description"] = "Kagoshima-cuisine izakaya with private rooms, about 3 minutes on foot from JR Kagoshima-Chuo Station. Satsuma chicken, Kurobuta pork shabu-shabu, straw-seared bonito. Courses with 2.5 hours of all-you-can-drink from ¥3,500."
    return page("en/", "Mishima Chikusan Kagoshima-Chuo Station | Private-room izakaya, Kagoshima local cuisine",
                "Private-room izakaya 3 minutes from JR Kagoshima-Chuo Station serving Kagoshima local cuisine: Satsuma chicken, Kurobuta pork shabu-shabu, straw-seared bonito. Open 16:00–24:00 daily. Courses with all-you-can-drink from ¥3,500.",
                body, [ld], lang="en", alt=[("ja", ""), ("en", "en/"), ("x-default", "")])


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    pages = {"": top(), "course/": course(), "menu/": menu(), "private-room/": room(), "access/": access(), "faq/": faq(), "en/": english()}
    for path, htm in pages.items():
        d = os.path.join(OUT, path)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(htm)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "site.css"), os.path.join(OUT, "assets", "site.css"))
    open(os.path.join(OUT, "assets", "favicon.svg"), "w", encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#252a27"/><text x="32" y="45" font-size="38" text-anchor="middle" fill="#f4f1e8" font-family="serif">三</text></svg>')
    sm = "".join(f"<url><loc>{SITE_URL}/{p}</loc></url>" for p in pages)
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("built", len(pages), "pages →", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
