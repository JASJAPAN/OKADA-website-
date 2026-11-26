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
}
for _g, _items in MAKI:
    for _k, _n, _p in _items:
        ALT["maki-" + _k] = f"四季家の鹿児島県産黒豚の{_n}串（焼く前）"
SMALL = {"room4": 238, "room10": 198}
e = lambda s: html.escape(s, quote=True)
yen = lambda n: f"{n:,}円"
tel_btn = f'<a class="btn solid" href="tel:{TEL_INTL}">電話で予約 <span class="num">&nbsp;{TEL}</span></a>'


def img(k, eager=False):
    w = SMALL.get(k, 640 if k.startswith("maki-") else 1200)
    return f'<img src="/assets/img/{k}.jpg" alt="{e(ALT[k])}" width="{w}" height="{w}"{"" if eager else " loading=lazy"} decoding="async">'


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
    return f'''<footer class="ft"><div class="wrap">
<p class="name">四季家 天文館店</p>
<p>{TAG}<br>〒{ZIP} {ADDR}<br><span class="num">{TEL}</span></p>
<div class="links">{links}</div>
<small>料理写真はイメージです。内容・価格は仕入れにより変わることがあります。価格はすべて税込です。</small>
</div></footer>
<nav class="bar" aria-label="予約"><a href="/enkai/">宴会コースを見る</a><a class="main" href="tel:{TEL_INTL}">電話で予約 {TEL}</a></nav>'''


def reserve():
    return f'''<section class="sec green rsv" id="reserve"><div class="wrap">
<span class="kicker">RESERVATION</span><h2>ご予約・お問い合わせ</h2>
<p class="intro" style="margin-inline:auto">ご予約はお電話で承ります。人数、ご予算、鍋のあり・なし、お祝いのデザートプレートなど、お気軽にご相談ください。</p>
<a class="tel num" href="tel:{TEL_INTL}">{TEL}</a>
<p class="sub">営業時間 16:00〜（年中無休）</p>
<p class="policy">{CANCEL}</p>
</div></section>'''


def faq(items):
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items) + "</div>"


def rows(items):
    return '<div class="rows">' + "".join(f'<div class="row"><h3>{a}</h3><p class="p">{b}</p><p class="d">{e(c)}</p></div>' for a, b, c in items) + "</div>"


def hours_html():
    return "<br>".join(f"{d}　<b class=num>{h}</b><br><small>{lo}</small>" for d, h, lo in HOURS)


def badge(c):
    return (f'<span class="badge">{c["badge"]}</span> ' if c.get("badge") else "") + (f'<span class="badge lim">{c["limit"]}</span>' if c.get("limit") else "")


def compare():
    """宴会ページのコース比較。PCは表、スマホは同じ表を1コース1枚のカードに組み替える（CSS）。"""
    body = ""
    for c in COURSES:
        s, m, f = COMPARE[c["id"]]
        body += f'''<tr><th scope="row"><a href="/course/#{c["id"]}">{c["name"]}</a>{badge(c)}</th>
<td data-l="料金" class="pr num">{yen(c["price"])}</td><td data-l="品数" class="num">鍋なし {c["n"][0]}品／鍋あり {c["n"][1]}品</td>
<td data-l="お造り">{s}</td><td data-l="主な料理">{e(m)}</td><td data-l="鍋なしの締め">{e(f)}</td><td data-l="鍋ありの鍋・締め">{e(NABE_SHIME[c["id"]])}</td></tr>'''
    return f'''<div class="cmpwrap"><table class="cmp"><thead><tr><th scope="col">コース</th><th scope="col">料金（税込）</th><th scope="col">品数</th><th scope="col">お造り</th><th scope="col">主な料理</th><th scope="col">鍋なしの締め</th><th scope="col">鍋あり（鍋・締め）</th></tr></thead><tbody>{body}</tbody></table></div>'''


def strip(n=None):
    items = [(k, nm) for _, g in MAKI for k, nm, _ in g][:n]
    return '<div class="strip">' + "".join(f'<figure>{img("maki-" + k)}<figcaption>{nm}</figcaption></figure>' for k, nm in items) + "</div>"


# ------------------------------------------------------------------ トップ
def top():
    cards = "".join(f'''<a class="card" href="/course/#{c["id"]}">{badge(c)}<h3>{c["name"]}</h3>
<p class="price num">{yen(c["price"])}<small>税込・飲み放題付き</small></p><p class="meta">鍋なし 全{c["n"][0]}品／鍋あり 全{c["n"][1]}品</p><p class="lead">{e(c["lead"])}</p></a>''' for c in COURSES)
    return f'''<section class="hero"><div class="wrap">
<div class="hg"><div><span class="kicker">鹿児島・天文館通電停から徒歩2分</span>
<h1><span>{HERO_H[0]}</span><span>{"".join(f"<em>{x}</em>" for x in HERO_H[1].replace("、","、|").split("|"))}</span></h1>
<p class="lead">{HERO_P}</p>
<div class="btns">{tel_btn}<a class="btn" href="/yasaimaki/">野菜巻き串を見る</a></div></div>
<figure>{img("maki", eager=True)}</figure></div>
<a class="ribbon" href="/enkai/"><b>冬の{SEASON}・会社の宴会</b><span>飲み放題付き3,500円〜／個室は最大70名様まで</span><i>宴会コースを見る</i></a>
<dl class="facts"><div><dt>お席</dt><dd>全席 扉付き完全個室</dd></div><div><dt>人数</dt><dd>2名〜最大70名様</dd></div><div><dt>コース</dt><dd>3,500円〜（飲み放題付き）</dd></div><div><dt>アクセス</dt><dd>天文館通電停 徒歩2分</dd></div></dl>
</div></section>

<section class="sec" id="about"><div class="wrap narrow">
<span class="kicker">ABOUT</span><h2>四季家 天文館店について</h2>
<p class="define">{DEFINITION}</p>
</div></section>

<section class="sec alt" id="yasaimaki"><div class="wrap">
<span class="kicker">SIGNATURE</span><h2>看板は、黒豚の野菜巻き串</h2>
<p class="intro">鹿児島県産黒豚のバラ肉で、野菜を一本ずつ巻いて焼きます。葉もの、きのこ、実もの、チーズ入りまで13種。トマト巻き・レタス巻きなどは1本418円（税込）です。</p>
{strip()}
<div class="duo" style="margin-top:44px"><figure>{img("kushishabu")}</figure>
<div><h3 class="h3">焼くだけでなく、串しゃぶでも</h3><p class="intro">野菜巻き串5種を、だしにさっとくぐらせて食べる鍋です（1人前2,178円・2人前から）。同じ串をチーズにつけるチーズフォンデュもあります。</p>
<p class="more"><a class="btn" href="/yasaimaki/">野菜巻き串 13種を見る</a></p></div></div>
</div></section>

<section class="sec" id="courses"><div class="wrap">
<span class="kicker">COURSE</span><h2>飲み放題付きの冬コース</h2>
<p class="intro">すべてのコースに飲み放題が付きます。日曜〜木曜は時間無制限、金曜・土曜・祝前日は2時間制です。どの価格にも「鍋なし」と「鍋あり」があり、2名様からご予約いただけます。</p>
<div class="duo" style="margin-top:28px"><figure>{img("course")}<figcaption>鍋なし：締めはせいろ蒸しご飯</figcaption></figure><figure>{img("nabe")}<figcaption>鍋あり：和牛もつ鍋か黒豚しゃぶしゃぶ</figcaption></figure></div>
<div class="cards">{cards}</div>
<p class="note">価格はお一人様・税込です。12月26日〜1月3日は年末年始料金としてお一人様500円を加算します。</p>
<p class="more btns"><a class="btn" href="/course/">全コースの献立を見る</a><a class="btn" href="/enkai/">コースを比べる（宴会・忘年会）</a></p>
</div></section>

<section class="sec green" id="room"><div class="wrap">
<span class="kicker">PRIVATE ROOM</span><h2>全席、扉付きの完全個室。人数に合わせてご用意します</h2>
{rows(ROOMS)}
<p class="more"><a class="btn inv" href="/private-room/">個室のご案内</a></p>
</div></section>

<section class="sec alt" id="access"><div class="wrap">
<span class="kicker">INFORMATION</span><h2>店舗情報・アクセス</h2>
{info_block()}
<p class="more"><a class="btn" href="/access/">行き方をくわしく見る</a></p>
</div></section>

<section class="sec" id="faq"><div class="wrap narrow">
<span class="kicker">Q&amp;A</span><h2>よくあるご質問</h2>
{faq(FAQ)}
</div></section>
{reserve()}'''


def info_block():
    info = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in (
        ("店名", FULL), ("住所", f"〒{ZIP}<br>{ADDR}"), ("電話", f'<a class="num" href="tel:{TEL_INTL}">{TEL}</a>'),
        ("営業時間", hours_html()), ("定休日", "なし（年中無休）"), ("アクセス", ACCESS + "。駐車場はありません（近くにコインパーキングあり）"),
        ("お席", "全席扉付きの完全個室（掘りごたつ・テーブル）。2名様〜最大70名様"), ("ご予算", "コース 3,500円〜8,000円（税込・飲み放題付き）"),
        ("お支払い", PAY + "。請求書払いはお電話でご相談ください")))
    mapq = "https://www.google.com/maps/search/?api=1&query=%E5%9B%9B%E5%AD%A3%E5%AE%B6+%E5%A4%A9%E6%96%87%E9%A4%A8%E5%BA%97+%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82%E6%9D%B1%E5%8D%83%E7%9F%B3%E7%94%BA1-26"
    return f'''<div class="info"><dl>{info}</dl>
<div class="mapbox"><p class="status" data-status><i></i><span>営業時間 16:00〜</span></p>
<p class="addr">{ADDR}</p><p class="hint">{ACCESS}。エレベーターで7階へお上がりください。</p>
<div class="btns"><a class="btn" href="{mapq}" target="_blank" rel="noopener">Googleマップで開く</a></div></div></div>'''


def ph(page, kicker, h1, lead, extra=""):
    return f'''<section class="ph"><div class="wrap">
<p class="crumb"><a href="/">トップ</a> ／ {LABEL[page]}</p>
<span class="kicker">{kicker}</span><h1>{h1}</h1>
<p>{lead}</p>{extra}
</div></section>'''


# ------------------------------------------------------------------ 野菜巻き串
def maki():
    groups = ""
    for g, items in MAKI:
        figs = "".join(f'<figure>{img("maki-" + k)}<figcaption><b>{n}</b>{f"<span class=num>{p}</span>" if p else ""}</figcaption></figure>' for k, n, p in items)
        groups += f'<h3 class="gh">{g}</h3><div class="makigrid">{figs}</div>'
    courses = "".join(f'<div class="row"><h3><a href="/course/#{c["id"]}">{c["name"]}</a></h3><p class="p num">{yen(c["price"])}（税込・飲み放題付き）</p><p class="d">{e(v)}</p></div>' for c, v in zip(COURSES, (
        "黒豚の野菜巻き串 1本", "黒豚の冬野菜巻き串 1本", "黒豚の冬野菜巻き串 1本", "黒豚の冬野菜巻き串 2本", "黒豚の冬野菜巻き串 三種", "黒豚の冬野菜巻き串 三種")))
    return ph("maki", "YASAIMAKI", "鹿児島県産黒豚の野菜巻き串",
              "四季家 天文館店の看板料理です。鹿児島県産黒豚のバラ肉で、トマト、レタス、えのき、オクラなど13種の野菜を一本ずつ巻き、炭火で焼きます。トマト巻き・レタス巻き・えのき巻き・にんじん巻き・水菜巻きは1本418円（税込）。全席扉付きの個室で、単品でもコースでもお出ししています。",
              '<div class="anchors"><a href="#list">13種の一覧</a><a href="#kushishabu">串しゃぶ・チーズフォンデュ</a><a href="#course">野菜巻き串が入るコース</a><a href="#other">串焼き・溶岩焼き</a><a href="#faq">よくあるご質問</a></div>') + f'''
<section class="sec" style="padding-top:36px"><div class="wrap duo">
<figure>{img("maki", eager=True)}</figure>
<div><span class="kicker">ABOUT</span><h2>四季家の野菜巻き串とは</h2>
<p class="intro">野菜を豚バラ肉で巻いて串に刺し、焼き上げる串料理です。四季家では鹿児島県産の黒豚を使い、野菜の種類ごとに一本ずつ巻いています。焼くと黒豚の脂が野菜に回り、レタスや水菜はしゃきっと、トマトは熱くてみずみずしく仕上がります。</p>
<p class="intro">盛り合わせなら「旬の朝採れ野菜串盛り」1,628円（税込）。牛・豚・鶏を一皿にした「鹿児島三味串盛り合わせ」1,078円（税込）もあります。</p></div>
</div></section>

<section class="sec alt" id="list"><div class="wrap">
<span class="kicker">13 KINDS</span><h2>野菜巻き串 13種</h2>
<p class="intro">写真は焼く前の串です。価格の表示がない串は、季節や仕入れでご用意が変わるため、店頭のメニューでご確認ください。</p>
{groups}
</div></section>

<section class="sec" id="kushishabu"><div class="wrap">
<span class="kicker">KUSHI-SHABU</span><h2>野菜巻き串を、串しゃぶとチーズフォンデュで</h2>
<div class="sig">
<article>{img("kushishabu2")}<div class="tx"><h3>野菜巻き串の串しゃぶ</h3><p class="pr">1人前 2,178円（税込・2人前から）</p><p>野菜巻き串5種を、だしにさっとくぐらせて、ポン酢と胡麻だれで食べる鍋です。焼いた串より軽く、野菜の甘みがそのまま出ます。コースでは「黒豚の野菜巻き串しゃぶしゃぶコース」5,000円（飲み放題付き・全11品）でお出ししています。</p></div></article>
<article>{img("fondue")}<div class="tx"><h3>野菜巻き串のチーズフォンデュ</h3><p class="pr">1人前 2,178円（税込・2人前から）</p><p>野菜巻き串5種を、温めたチーズにつけて食べます。女子会コース（4,000円・飲み放題付き・全10品）にも入っています。</p></div></article>
</div></div></section>

<section class="sec green" id="course"><div class="wrap">
<span class="kicker">COURSE</span><h2>野菜巻き串が入る、飲み放題付きコース</h2>
<p class="intro">冬コースは6種類すべてに野菜巻き串が入ります。日曜〜木曜は飲み放題が時間無制限、金曜・土曜・祝前日は2時間制です。</p>
<div class="rows">{courses}</div>
<p class="more"><a class="btn inv" href="/enkai/">宴会・忘年会のコースを比べる</a></p>
</div></section>

<section class="sec alt" id="other"><div class="wrap">
<span class="kicker">GRILL</span><h2>串焼き・溶岩焼き・藁焼き</h2>
<div class="tri">
<figure>{img("sanshu")}<figcaption><b>鹿児島三味串盛り合わせ（牛・豚・鶏）</b><span class="num">1,078円</span></figcaption></figure>
<figure>{img("yogan-buta")}<figcaption><b>知覧茶薫る黒豚の溶岩焼き</b><span class="num">2,728円</span></figcaption></figure>
<figure>{img("yogan-jidori")}<figcaption><b>鹿児島県産地鶏の溶岩焼き</b><span class="num">1,518円</span></figcaption></figure>
</div>
<p class="note">価格は税込です。藁焼きカツオのたたき 1,078円、30日間熟成国産牛の藁焼き 2,728円もあります。</p>
<p class="more"><a class="btn" href="/course/#alacarte">単品メニューと価格</a></p>
</div></section>

<section class="sec" id="faq"><div class="wrap narrow">
<span class="kicker">Q&amp;A</span><h2>野菜巻き串についてのご質問</h2>
{faq(FAQ_FOOD + [("野菜巻き串はコースでも食べられますか。", "はい。冬コース6種類すべてに野菜巻き串が入ります。3,500円〜4,500円のコースは1本、5,000円は2本、6,000円と8,000円は三種です。"), ("野菜巻き串を個室で食べられますか。", "はい。四季家 天文館店は全席が扉付きの完全個室です。4名様用の個室から最大70名様までご利用いただけます。")])}
</div></section>
{reserve()}'''


# ------------------------------------------------------------------ コース・メニュー
def course():
    blocks = ""
    for c in COURSES:
        dl = "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in c["menu"])
        blocks += f'''<article class="menu" id="{c["id"]}">{badge(c)}
<header><h3>{c["name"]}</h3><p class="price num">{yen(c["price"])}<small>税込・飲み放題付き／鍋なし 全{c["n"][0]}品</small></p></header>
<p class="lead">{e(c["lead"])}</p><dl>{dl}</dl>
<p class="nabe"><b>鍋あり</b>　{e(c["nabe"])}</p></article>'''
    sp = "".join(f'<div class="row"><h3>{n}</h3><p class="p">{p}（税込）／{k}</p><p class="d">{e(d)}</p></div>' for n, p, k, d in SPECIAL)
    alc = "".join(f"<div><h3>{h}</h3><ul>" + "".join(f"<li><span>{e(n)}</span><span class=num>{p}</span></li>" for n, p in items) + "</ul></div>" for h, items in ALC)
    anchors = "".join(f'<a href="#{c["id"]}">{yen(c["price"])} {c["name"]}</a>' for c in COURSES) + '<a href="#special">串しゃぶ・女子会ほか</a><a href="#alacarte">単品メニュー</a>'
    return ph("course", "COURSE &amp; MENU", "コース・メニュー",
              "四季家 天文館店のコースは、すべて飲み放題付き・2名様からです。飲み放題は日曜〜木曜が時間無制限、金曜・土曜・祝前日が2時間制。生ビール、ハイボール、焼酎、カクテルなど約80種類からお選びいただけます。",
              f'<div class="anchors">{anchors}</div>') + f'''
<section class="sec" id="winter" style="padding-top:36px"><div class="wrap">
<span class="kicker">WINTER COURSE</span><h2>冬コースの献立（鍋なし／鍋あり）</h2>
<p class="intro">献立は鍋なしの内容です。鍋ありを選ぶと、後半の数品が鍋と〆に替わります。鍋のご指定がない場合は、もつ鍋でご用意します。6種類を横に比べたい方は<a href="/enkai/#compare">コース比較表</a>をご覧ください。</p>
<div class="duo" style="margin-top:24px"><figure>{img("seiro-kanpachi", eager=True)}<figcaption>かんぱちといくらのせいろ蒸しご飯（5,000円 冬椿コース）</figcaption></figure><figure>{img("seiro-kani")}<figcaption>ズワイガニとうに・いくらのせいろ蒸しご飯（8,000円 冬銀コース）</figcaption></figure></div>
{blocks}
<p class="note">価格はお一人様・税込です。仕入れにより内容が変わることがあります。12月26日〜1月3日は年末年始料金としてお一人様500円を加算します。食物アレルギーのある方は、ご予約の際にお知らせください。</p>
<p class="more">{tel_btn}</p>
</div></section>

<section class="sec green" id="special"><div class="wrap">
<span class="kicker">SPECIAL</span><h2>串しゃぶ・女子会・単品飲み放題</h2>
<div class="rows">{sp}</div>
</div></section>

<section class="sec alt" id="alacarte"><div class="wrap">
<span class="kicker">A LA CARTE</span><h2>単品メニュー（抜粋）</h2>
<p class="intro">お席のみのご予約でも、単品でご注文いただけます。野菜巻き串の13種は<a href="/yasaimaki/">野菜巻き串のページ</a>に写真があります。</p>
<div class="alc">{alc}</div>
<p class="note">価格は税込です。このほかにもサラダ、揚げ物、一品料理をご用意しています。生の肉・魚料理は、お子様やご高齢の方、体調のすぐれない方はお控えください。</p>
</div></section>
{reserve()}'''


# ------------------------------------------------------------------ 宴会・忘年会
def enkai():
    return ph("enkai", "PARTY", f"天文館の{SEASON}・会社の宴会",
              "天文館で忘年会・会社の宴会をお考えの幹事様へ。四季家 天文館店は全席が扉付きの個室で、2名様から最大70名様まで、人数に合わせてお部屋をご用意します。コースはすべて飲み放題付きで、3,500円（日曜〜木曜限定）から8,000円までの6種類。どの価格も、締めがせいろ蒸しご飯の「鍋なし」と、和牛もつ鍋か黒豚しゃぶしゃぶの「鍋あり」を選べます。天文館通電停から徒歩2分です。",
              '<div class="anchors"><a href="#people">人数で探す</a><a href="#compare">コースを比べる</a><a href="#drink">飲み放題</a><a href="#kanji">幹事様へ</a><a href="#faq">よくあるご質問</a></div>') + f'''
<section class="sec" id="people" style="padding-top:36px"><div class="wrap duo">
<div><span class="kicker">PEOPLE</span><h2>人数で探す</h2>
{rows(ROOMS)}
<p class="more"><a class="btn" href="/private-room/">個室のご案内</a></p></div>
<figure>{img("nabe6000", eager=True)}<figcaption>6,000円 冬錦コース（鍋あり）</figcaption></figure>
</div></section>

<section class="sec alt" id="compare"><div class="wrap">
<span class="kicker">COMPARE</span><h2>飲み放題付きコース 6種を比べる</h2>
<p class="intro">価格が上がるほど、お造りの種類が増え、主な料理が鶏から黒豚・黒毛和牛・海の幸へ変わります。コース名を押すと全献立が開きます。</p>
{compare()}
<p class="note">価格はお一人様・税込、2名様から。12月26日〜1月3日は年末年始料金としてお一人様500円を加算します。</p>
<div class="two">
<div class="box"><h3>鍋なしを選ぶと</h3><p>締めは卓上で蒸し上げるせいろ蒸しご飯です（3,500円コースは混ぜご飯）。焼物や煮物まで一品ずつお出しします。</p></div>
<div class="box"><h3>鍋ありを選ぶと</h3><p>後半の数品が、黄金だしの和牛もつ鍋か薩摩黒豚のしゃぶしゃぶに替わります（3,500円コースはもつ鍋）。締めはさつまうどん。ご指定がない場合はもつ鍋でご用意します。</p></div>
</div>
<p class="more btns"><a class="btn" href="/course/">全コースの献立を見る</a>{tel_btn}</p>
</div></section>

<section class="sec" id="drink"><div class="wrap narrow">
<span class="kicker">DRINK</span><h2>飲み放題は、日曜〜木曜が時間無制限</h2>
<div class="rows">
<div class="row"><h3>日曜〜木曜・祝日</h3><p class="p">時間無制限</p><p class="d">コースの飲み放題に時間の区切りがありません。平日の忘年会や、ゆっくり話したい集まりに向いています。</p></div>
<div class="row"><h3>金曜・土曜・祝前日</h3><p class="p">2時間制</p><p class="d">ラストオーダーは終了の30分前です。</p></div>
<div class="row"><h3>内容</h3><p class="p">約80種類</p><p class="d">生ビール、ハイボール、焼酎、カクテル、ソフトドリンクなど。＋500円で銘柄の増えるプラチナ飲み放題に変更できます。</p></div>
</div></div></section>

<section class="sec green" id="kanji"><div class="wrap">
<span class="kicker">FOR ORGANIZERS</span><h2>幹事様へ</h2>
<div class="rows">
<div class="row"><h3>ご予約</h3><p class="d">お電話（<a class="num" href="tel:{TEL_INTL}">{TEL}</a>）で、営業時間中（16:00〜）に承ります。<br>お伝えいただくこと：日時、人数、コース（価格）、鍋のあり・なしと鍋の種類、お祝いのデザートプレートの有無、食物アレルギーの有無、請求書払いの希望。</p></div>
<div class="row"><h3>人数の変更・キャンセル</h3><p class="d">{CANCEL}</p></div>
<div class="row"><h3>お支払い</h3><p class="d">{PAY}。請求書払いにも対応していますので、お電話でご相談ください。</p></div>
<div class="row"><h3>お祝い・送別</h3><p class="d">メッセージ入りのデザートプレートをご用意できます。ご予約の際にお申し付けください。</p></div>
<div class="row"><h3>年末年始</h3><p class="d">定休日はありません。12月26日〜1月3日は年末年始料金としてお一人様500円を加算します。</p></div>
</div></div></section>

<section class="sec" id="faq"><div class="wrap narrow">
<span class="kicker">Q&amp;A</span><h2>宴会についてのご質問</h2>
{faq(FAQ_PARTY)}
</div></section>
{reserve()}'''


# ------------------------------------------------------------------ 個室
def room():
    return ph("room", "PRIVATE ROOM", "個室のご案内",
              "四季家 天文館店は、全席が扉付きの完全個室です。4名・6名・8名様用の掘りごたつ・テーブル個室から、最大70名様までの個室まで、人数に合わせてお部屋をご用意します。天文館通電停から徒歩2分、フォリス観光ビル天文館の7階です。") + f'''
<section class="sec" style="padding-top:36px"><div class="wrap duo">
<div><span class="kicker">ROOMS</span><h2>人数に合わせたお部屋</h2>
{rows(ROOMS)}</div>
<div><div class="rooms"><figure>{img("room4", eager=True)}<figcaption>掘りごたつの個室</figcaption></figure><figure>{img("room10")}<figcaption>10名様前後の個室</figcaption></figure></div>
<p class="note">お部屋はどれも扉で仕切られています。掘りごたつ・テーブルのご希望や、お子様連れ、ご年配の方がいらっしゃる場合は、ご予約の際にお知らせください。</p></div>
</div></section>

<section class="sec alt"><div class="wrap">
<span class="kicker">SCENE</span><h2>個室でのご利用</h2>
<div class="rows">
<div class="row"><h3>ご家族・お子様連れ</h3><p class="d">周りを気にせず過ごせます。黒豚、地鶏、かつおの藁焼き、さつま揚げなど、鹿児島の味を単品でもコースでもどうぞ。</p></div>
<div class="row"><h3>接待・会食</h3><p class="d">扉付きの個室ですので、お話に集中していただけます。6,000円の冬錦コース、お一人ずつ盛り付ける8,000円の冬銀コースがあります。</p></div>
<div class="row"><h3>女子会・誕生日</h3><p class="d">野菜巻き串の串しゃぶコース（5,000円）、チーズフォンデュの女子会コース（4,000円）があります。メッセージ入りのデザートプレートは、ご予約の際にお申し付けください。</p></div>
<div class="row"><h3>会社の宴会・忘年会</h3><p class="d">人数別のご案内、コースの比較、キャンセル規定は<a href="/enkai/">宴会・忘年会のページ</a>にまとめています。</p></div>
</div>
<p class="more btns"><a class="btn" href="/enkai/">宴会・忘年会のご案内</a><a class="btn" href="/course/">コース・メニュー</a></p>
</div></section>

<section class="sec"><div class="wrap narrow">
<span class="kicker">Q&amp;A</span><h2>個室についてのご質問</h2>
{faq(FAQ_ROOM + FAQ_PARTY[:4])}
</div></section>
{reserve()}'''


# ------------------------------------------------------------------ アクセス
def access():
    return ph("access", "ACCESS", "アクセス・営業時間",
              "四季家 天文館店は、鹿児島市東千石町1-26 フォリス観光ビル天文館の7階にあります。鹿児島市電「天文館通」電停から徒歩2分。営業は16時から、定休日はありません。") + f'''
<section class="sec" style="padding-top:36px"><div class="wrap">
{info_block()}
</div></section>

<section class="sec alt"><div class="wrap narrow">
<span class="kicker">ROUTE</span><h2>行き方</h2>
<div class="rows">
<div class="row"><h3>市電で</h3><p class="d">鹿児島市電「天文館通」電停で降りて、徒歩2分です。鹿児島中央駅からは、駅前の電停から市電に乗り「天文館通」で降ります。</p></div>
<div class="row"><h3>ビルに着いたら</h3><p class="d">フォリス観光ビル天文館のエレベーターで7階へお上がりください。</p></div>
<div class="row"><h3>お車で</h3><p class="d">専用の駐車場はありません。近くのコインパーキングをご利用ください。お酒を召し上がる方は、公共交通機関かタクシーでお越しください。</p></div>
<div class="row"><h3>タクシーで</h3><p class="d">運転手さんには「東千石町のフォリス観光ビル天文館」とお伝えください。</p></div>
</div></div></section>

<section class="sec"><div class="wrap narrow">
<span class="kicker">Q&amp;A</span><h2>アクセス・営業についてのご質問</h2>
{faq(FAQ_ACCESS)}
</div></section>
{reserve()}'''


PAGES = {"top": top, "maki": maki, "course": course, "enkai": enkai, "room": room, "access": access}
PAGE_FAQ = {"top": FAQ, "maki": FAQ_FOOD, "enkai": FAQ_PARTY, "room": FAQ_ROOM + FAQ_PARTY[:4], "access": FAQ_ACCESS}


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
