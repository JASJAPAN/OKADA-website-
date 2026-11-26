# -*- coding: utf-8 -*-
"""いずみ精肉店 天文館店 サイトの組み立て（2版：6ページ×5言語）。
  python3 build.py           → ../../dist/izumi/    本番用（ルートからのURL、hreflang、構造化データ、サイトマップ）
  python3 build.py preview   → ../../preview/izumi/ 確認用（相対パス。どこに置いても開ける）
"""
import html, json, os, shutil, sys
from content import *

ROOT = os.path.dirname(os.path.abspath(__file__))
MODE = "preview" if len(sys.argv) > 1 and sys.argv[1] == "preview" else "site"
OUT = os.path.join(ROOT, "..", "..", "preview" if MODE == "preview" else "dist", STORE_ID)
PAGES = ["top", "course", "rooms", "kagoshima", "access", "guide"]
PATH = {"top": "", "course": "course/", "rooms": "rooms/", "kagoshima": "kagoshima/", "access": "access/", "guide": "guide/"}
NAV = ["course", "rooms", "kagoshima", "access", "guide"]
IMGS = ["tsubo", "room", "room2", "counter", "plates", "horumon", "spread", "drinks"]
CI = {c["id"]: n for n, c in enumerate(COURSES)}


def e(s):
    return html.escape(s, quote=True)


class R:
    def __init__(self, lang, page):
        self.lang, self.page = lang, page
        self.i = LANGS.index(lang)

    def t(self, k):
        return T[k][self.i]

    def x(self, tup):
        return tup[self.i]

    # ---- URL
    def rel(self, lang=None, page=None):
        lang = lang or self.lang
        page = self.page if page is None else page
        return ("" if lang == "ja" else lang + "/") + PATH[page]

    def url(self, lang=None, page=None, anchor=""):
        target = self.rel(lang, page)
        a = f"#{anchor}" if anchor else ""
        if MODE == "site":
            return "/" + target + a
        return "../" * self.rel().count("/") + target + "index.html" + a

    def asset(self, f):
        if MODE == "site":
            return "/assets/" + f
        return "../" * self.rel().count("/") + "assets/" + f

    def abs(self, lang=None, page=None):
        return SITE_URL + "/" + self.rel(lang, page)

    def yen(self, n):
        s = f"{n:,}"
        return {"ja": f"<b>{s}</b><small>円</small>", "en": f"<small>¥</small><b>{s}</b>",
                "zh-cn": f"<b>{s}</b><small>日元</small>", "zh-tw": f"<b>{s}</b><small>日圓</small>",
                "ko": f"<b>{s}</b><small>엔</small>"}[self.lang]

    def cname(self, c):
        """日本語ページは方言名が主役、外国語ページは中身の名前が主役。"""
        lab = self.x(LABEL[c["id"]])
        if self.lang == "ja":
            return f'<span class="cn">{c["ja"]}</span><span class="cj">{lab}</span>'
        return f'<span class="cn">{lab}</span><span class="cj"><span lang="ja">{c["ja"]}</span>（{c["roma"]}）</span>'

    def cshort(self, c):
        return c["ja"] if self.lang == "ja" else self.x(LABEL[c["id"]])

    def img(self, key, w, h, eager=False, cls=""):
        load = ' fetchpriority="high"' if eager else ' loading="lazy"'
        c = f' class="{cls}"' if cls else ""
        return f'<img{c} src="{self.asset("img/" + key + ".jpg")}" alt="{e(self.t("alt_" + key))}" width="{w}" height="{h}"{load} decoding="async">'

    # ---- 共通パーツ
    def header(self):
        t = self.t
        cur = lambda p: ' aria-current="page"' if p == self.page else ""
        langs = "".join(
            f'<li><a href="{self.url(lang=l)}" hreflang="{HTML_LANG[l]}" lang="{HTML_LANG[l]}"'
            + (' aria-current="true"' if l == self.lang else "") + f'>{LANG_LABEL[l]}</a></li>' for l in LANGS)
        nav = "".join(f'<a href="{self.url(page=p)}"{cur(p)}>{t("nav_" + p)}</a>' for p in NAV)
        return f'''<a class="skip" href="#main">{t("skip")}</a>
<header class="hd"><div class="wrap">
<a class="brand" href="{self.url(page="top")}"><b>{e(self.x(STORE["short"]))}</b><span>{e(self.x(STORE["tag"]))}</span></a>
<nav class="nav" aria-label="main">{nav}<a class="tel" href="tel:{TEL_INTL}">{TEL}</a></nav>
<details class="langsel"><summary aria-label="{t("lang")}">{LANG_LABEL[self.lang]}</summary><ul>{langs}</ul></details>
</div></header>'''

    def footer(self):
        t = self.t
        links = "".join(f'<a href="{self.url(page=p)}">{t("nav_" + p)}</a>' for p in ["top"] + NAV)
        return f'''<footer class="ft"><div class="wrap">
<p class="name">{e(self.x(STORE["name"]))}</p>
<p>{e(self.x(STORE["addr"]))}<br><span class="num">{TEL}</span>（{TEL_INTL}）</p>
<p>{t("a_h1")}<br>{t("a_h2")}</p>
<p class="links">{links}</p>
<p class="sis"><a href="{SISTER_URL}{"/" if self.lang == "ja" else "/" + self.lang + "/"}">{t("sister")}</a></p>
<p class="fine">{t("foot_note")}<br>{t("foot_op")}</p>
</div></footer>
<nav class="bar" aria-label="quick">
<a href="{self.url(page="course")}">{t("nav_course")}</a>
<a class="main" href="tel:{TEL_INTL}">{t("cta_call")} {TEL}</a>
</nav>'''

    def phead(self, h1, lead):
        return f'''<section class="phead"><div class="wrap">
<p class="crumb"><a href="{self.url(page="top")}">{e(self.x(STORE["short"]))}</a> / {self.t("nav_" + self.page)}</p>
<h1>{h1}</h1><p class="lead">{lead}</p>
</div></section>'''

    def ladder(self, detail=False):
        t, rows = self.t, []
        for n, c in enumerate(COURSES):
            badge = f'<span class="badge">{t("popular")}</span>' if c["popular"] else ""
            body = ""
            if n:
                body += f'<p class="inc">{e(t("c_includes").format(self.cshort(COURSES[n - 1])))}</p>'
            if detail:
                if c["adds"]:
                    body += f'<p class="add"><span>＋ {t("adds")}</span>{e(self.x(c["adds"]))}</p>'
                else:
                    body += '<dl class="base">' + "".join(
                        f'<div><dt>{e(self.x(k))}</dt><dd>{e(self.x(v))}</dd></div>' for k, v in BASE) + "</dl>"
            else:
                body += f'<p class="hd2">{e(self.x(c["head"]))}</p>'
            rows.append(f'''<li class="tag{" pop" if c["popular"] else ""}" id="{c["id"]}" style="--i:{n}">
<div class="tn"><p class="nm">{self.cname(c)}</p>{badge}<p class="mean">{e(self.x(c["mean"]))}</p></div>
<div class="tb">{body}</div>
<p class="pr num">{self.yen(c["price"])}</p></li>''')
        return f'<ol class="ladder{" detail" if detail else ""}">' + "".join(rows) + "</ol>"

    def matrix(self):
        t = self.t
        head = "".join(f'<th scope="col"><span>{self.cshort(c)}</span><b class="num">{c["price"]:,}</b></th>' for c in COURSES)
        body = ""
        for name, start in MATRIX:
            cells = "".join(f'<td>{"<i>○</i>" if n >= start else "<s>—</s>"}</td>' for n in range(len(COURSES)))
            body += f'<tr><th scope="row">{e(self.x(name))}</th>{cells}</tr>'
        return f'''<div class="mx-wrap" tabindex="0"><table class="mx"><thead><tr><th scope="col">{t("cmp_item")}</th>{head}</tr></thead><tbody>{body}</tbody></table></div>
<p class="note">{t("cmp_note")} {t("tax")}</p>'''

    def faqs(self, page=None):
        items = [(q, a) for p, q, a in FAQ2 if p == (page or self.page)]
        return items

    def faq_block(self, more=False):
        items = self.faqs()
        if not items:
            return ""
        li = "".join(f'<details><summary>{e(self.x(q))}</summary><p>{e(self.x(a))}</p></details>' for q, a in items)
        m = f'<p class="more"><a class="btn line" href="{self.url(page="guide")}">{self.t("more_faq")}</a></p>' if more else ""
        return f'''<section class="sec" id="faq"><div class="wrap narrow">
<h2>{self.t("s_faq")}</h2><div class="faq">{li}</div>{m}
</div></section>'''

    def reserve(self):
        t = self.t
        return f'''<section class="rsv" id="reserve"><div class="wrap">
<h2>{t("s_reserve")}</h2>
<p>{t("reserve_p")}</p>
<p class="big"><a class="num" href="tel:{TEL_INTL}">{TEL}</a></p>
<p class="abroad">{t("reserve_from_abroad")} <span class="num">{TEL_INTL}</span></p>
</div></section>'''

    def thumbs(self, keys):
        return '<div class="thumbs">' + "".join(f'<figure>{self.img(k, 480, 480)}<figcaption>{e(self.t("alt_" + k))}</figcaption></figure>' for k in keys) + "</div>"

    # ---- トップ
    def top(self):
        t = self.t
        chips = "".join(f"<li>{t(k)}</li>" for k in ("chip1", "chip2", "chip3"))
        visit = "".join(f"<li>{t(k)}</li>" for k in ("v1", "v2", "v3", "v4"))
        cards = ""
        for p, img, k in (("rooms", "room", "card_rooms"), ("kagoshima", "plates", "card_kago"), ("guide", "spread", "card_guide")):
            cards += f'''<a class="door" href="{self.url(page=p)}">{self.img(img, 480, 480)}
<span class="dt"><b>{t("nav_" + p)}</b><span>{t(k)}</span><i>{t("see")} →</i></span></a>'''
        return f'''<section class="hero"><div class="wrap">
<div class="ht">
<p class="eyebrow">{e(self.x(STORE["name"]))}</p>
<h1>{t("h1")}</h1>
<p class="sub">{t("h_sub")}</p>
<ul class="chips">{chips}</ul>
<p class="cta"><a class="btn red" href="{self.url(page="course")}">{t("cta_course")}</a><a class="btn ghost" href="tel:{TEL_INTL}">{t("cta_tel")}<span class="num">{TEL}</span></a></p>
</div>
<div class="pt">
<div class="ticket"><p class="tk">{t("tag_k")}</p><p class="tp num">{self.yen(2980)}<em>{t("tag_from")}</em></p><p class="tx">{t("tax")}</p></div>
<div class="strip">{self.img("tsubo", 724, 724, eager=True)}{self.img("plates", 480, 480)}{self.img("horumon", 480, 480)}</div>
</div>
</div></section>

<section class="sec" id="courses"><div class="wrap">
<h2>{t("s_course")}</h2>
<p class="note">{t("s_course_note")} <span class="taxn">{t("tax")}</span></p>
{self.ladder()}
<p class="more"><a class="btn line" href="{self.url(page="course")}">{t("more_course")}</a></p>
</div></section>

<section class="sec alt"><div class="wrap">
<h2>{t("s_more")}</h2>
<div class="doors">{cards}</div>
</div></section>

<section class="visit"><div class="wrap">
<h2>{t("s_visit")}</h2>
<ul>{visit}</ul>
<p><a class="btn cream" href="{self.url(page="guide")}">{t("more_guide")}</a></p>
</div></section>

<section class="sec" id="access"><div class="wrap">
<h2>{t("s_access_short")}</h2>
{self.info(short=True)}
<p class="more"><a class="btn line" href="{self.url(page="access")}">{t("more_access")}</a></p>
</div></section>
{self.faq_block(more=True)}
{self.reserve()}'''

    def info(self, short=False):
        t = self.t
        ja_addr = "" if self.lang == "ja" else f'<p class="taxi"><span>{t("taxi")}</span><b lang="ja">{ADDR_JA}</b></p>'
        rows = [(t("a_addr"), f'<span>{e(self.x(STORE["addr"]))}</span>{ja_addr}<p class="acts"><a class="btn line sm" href="{MAP_URL}" rel="noopener">{t("map_open")}</a><button class="btn line sm" type="button" data-copy="{e(ADDR_JA)}" data-done="{e(t("map_copied"))}">{t("map_copy")}</button></p>'),
                (t("a_hours"), f'{t("a_h1")}<br>{t("a_h2")}'),
                (t("a_tel"), f'<a class="num" href="tel:{TEL_INTL}">{TEL}</a>（{TEL_INTL}）')]
        if not short:
            rows += [(t("a_closed"), t("a_closed_v")), (t("a_park"), t("a_park_v")), (t("a_pay"), t("a_pay_v"))]
        return '<dl class="info">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows) + "</dl>"

    # ---- コースと料金
    def course(self):
        t = self.t
        rules = "".join(f"<li>{t(k)}</li>" for k in ("r1", "r2", "r3", "r4", "r5", "r6"))
        return f'''{self.phead(t("c_h1"), t("c_lead"))}
<section class="sec"><div class="wrap">
<h2>{t("cmp_h")}</h2>
{self.matrix()}
</div></section>
<section class="sec alt"><div class="wrap">
<h2>{t("detail_h")}</h2>
{self.ladder(detail=True)}
</div></section>
<section class="sec"><div class="wrap two">
<div><h2>{t("c_drink_h")}</h2><p>{t("c_drink_p")}</p><figure class="sm">{self.img("drinks", 480, 480)}</figure></div>
<div><h2>{t("c_rule_h")}</h2><ul class="rules">{rules}</ul></div>
</div></section>
{self.faq_block()}
{self.reserve()}'''

    # ---- 個室
    def rooms(self):
        t = self.t
        types = "".join(f'<div><dt>{t(a)}</dt><dd class="num">{t(b)}</dd></div>' for a, b in (("r_t1", "r_t1n"), ("r_t2", "r_t2n"), ("r_t3", "r_t3n")))
        notes = "".join(f"<li>{t(k)}</li>" for k in ("r_n1", "r_n2", "r_n3"))
        return f'''{self.phead(t("r_h1"), t("r_lead"))}
<section class="sec"><div class="wrap two">
<div><h2>{t("r_type")}</h2><dl class="types">{types}</dl><p class="small">{t("r_sunken")}</p></div>
<div><ul class="rules">{notes}</ul></div>
</div></section>
<section class="sec alt"><div class="wrap">{self.thumbs(["room", "room2", "counter"])}</div></section>
{self.faq_block()}
{self.reserve()}'''

    # ---- 鹿児島の味
    def kagoshima(self):
        t = self.t
        cards = ""
        for cid, name, desc in DISHES:
            c = COURSES[CI[cid]]
            raw = " raw" if name[0] == "鶏刺し" else ""
            cards += f'''<article class="dish{raw}"><p class="from">{e(t("k_from").format(self.cshort(c)))} <span class="num">{c["price"]:,}</span></p>
<h2>{e(self.x(name))}</h2><p>{e(self.x(desc))}</p></article>'''
        return f'''{self.phead(t("k_h1"), t("k_lead"))}
<section class="sec"><div class="wrap"><div class="dishes">{cards}</div></div></section>
<section class="sec alt"><div class="wrap">{self.thumbs(["plates", "tsubo", "horumon"])}</div></section>
{self.faq_block()}
{self.reserve()}'''

    # ---- アクセス
    def access(self):
        t = self.t
        route = "".join(f"<li>{t(k)}</li>" for k in ("ac_r1", "ac_r2", "ac_r3", "ac_r4"))
        return f'''{self.phead(t("ac_h1"), t("ac_lead"))}
<section class="sec"><div class="wrap two">
<div>{self.info()}</div>
<div><h2>{t("ac_route_h")}</h2><ol class="route">{route}</ol>
<div class="box"><h3>{t("ac_cruise_h")}</h3><p>{t("ac_cruise_p")}</p></div></div>
</div></section>
{self.faq_block()}
{self.reserve()}'''

    # ---- ご利用の流れ
    def guide(self):
        t = self.t
        steps = "".join(f'<li><h2>{t(f"g{n}_h")}</h2><p>{t(f"g{n}_p")}</p></li>' for n in range(1, 6))
        rules = "".join(f"<li>{t(k)}</li>" for k in ("r1", "r2", "r3", "r4", "r5"))
        visit = "".join(f"<li>{t(k)}</li>" for k in ("v1", "v2", "v3"))
        show = ""
        if self.lang != "ja":
            rows = "".join(f'<li><b lang="ja">{c["ja"]}</b><span>{e(self.x(LABEL[c["id"]]))}</span><i class="num">{c["price"]:,}円</i></li>' for c in COURSES)
            show = f'''<section class="sec alt"><div class="wrap narrow">
<h2>{t("g_show_h")}</h2><p class="note">{t("g_show_p")}</p>
<div class="show"><p lang="ja">{T["g_show_line"][0]}</p><ul>{rows}</ul></div>
</div></section>'''
        return f'''{self.phead(t("g_h1"), t("g_lead"))}
<section class="sec"><div class="wrap narrow"><ol class="steps">{steps}</ol></div></section>
{show}
<section class="sec"><div class="wrap two">
<div><h2>{t("c_rule_h")}</h2><ul class="rules">{rules}</ul></div>
<div><h2>{t("s_visit")}</h2><ul class="rules">{visit}</ul></div>
</div></section>
{self.faq_block()}
{self.reserve()}'''

    # ---- 構造化データ
    def ld(self):
        out = [{
            "@context": "https://schema.org", "@type": "Restaurant", "@id": SITE_URL + "/#restaurant",
            "name": STORE["name"][0],
            "alternateName": ["完全個室 焼肉食べ放題 いずみ精肉店 天文館店", "Izumi Seinikuten Tenmonkan", "Izumi精肉店 天文館店"],
            "description": T["d_top"][self.i], "url": self.abs(page="top"), "telephone": TEL_INTL,
            "image": [SITE_URL + f"/assets/img/{k}.jpg" for k in ("tsubo", "plates", "room")],
            "address": {"@type": "PostalAddress", "postalCode": "892-0843", "addressCountry": "JP", "addressRegion": "鹿児島県",
                        "addressLocality": "鹿児島市", "streetAddress": "千日町3-5 くらかわビル地下1階"},
            "servesCuisine": ["焼肉", "焼肉食べ放題", "Yakiniku", "Japanese BBQ"],
            "priceRange": "¥2,980〜¥5,980", "acceptsReservations": True, "currenciesAccepted": "JPY",
            "paymentAccepted": "Cash, Visa, Mastercard, JCB, American Express, Diners Club, Discover, UnionPay, Alipay, WeChat Pay, PayPay",
            "openingHoursSpecification": [
                {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "16:00", "closes": "00:00"},
                {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Friday", "Saturday"], "opens": "16:00", "closes": "02:00"}],
            "hasMenu": self.abs(page="course"), "sameAs": SAME_AS, "availableLanguage": ["ja", "en", "zh"],
            "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": "Private rooms", "value": True}],
        }]
        items = self.faqs()
        if items:
            out.append({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": HTML_LANG[self.lang],
                        "mainEntity": [{"@type": "Question", "name": self.x(q),
                                        "acceptedAnswer": {"@type": "Answer", "text": self.x(a)}} for q, a in items]})
        if self.page == "course":
            mi = [{"@type": "MenuItem", "name": f'{c["ja"]}（{self.x(LABEL[c["id"]])}）',
                   "description": self.x(c["head"]) + (" ／ " + self.x(c["adds"]) if c["adds"] else ""),
                   "offers": {"@type": "Offer", "price": c["price"], "priceCurrency": "JPY"}} for c in COURSES]
            out.append({"@context": "https://schema.org", "@type": "Menu", "name": self.t("c_h1"), "inLanguage": HTML_LANG[self.lang],
                        "url": self.abs(page="course"), "hasMenuSection": {"@type": "MenuSection", "name": self.t("c_h1"), "hasMenuItem": mi}})
        if self.page != "top":
            out.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": self.x(STORE["name"]), "item": self.abs(page="top")},
                {"@type": "ListItem", "position": 2, "name": self.t("nav_" + self.page), "item": self.abs()}]})
        return "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>\n' for o in out)

    def render(self):
        t = self.t
        title, desc = t("t_" + self.page), t("d_" + self.page)
        alts = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{self.abs(lang=l)}">' for l in LANGS)
        alts += f'<link rel="alternate" hreflang="x-default" href="{self.abs(lang="en")}">'
        body = getattr(self, self.page)()
        return f'''<!DOCTYPE html>
<html lang="{HTML_LANG[self.lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{self.abs()}">
{alts}
<meta property="og:type" content="restaurant">
<meta property="og:site_name" content="{e(self.x(STORE["name"]))}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{self.abs()}">
<meta property="og:image" content="{SITE_URL}/assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f0d0c">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="{self.asset("favicon.svg")}" type="image/svg+xml">
<link rel="stylesheet" href="{self.asset("site.css")}">
{self.ld()}</head>
<body class="p-{self.page}">
{self.header()}
<main id="main">
{body}
</main>
{self.footer()}
<script src="{self.asset("site.js")}" defer></script>
</body>
</html>
'''


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets", "img"))
    for k in IMGS + ["og"]:
        shutil.copy(os.path.join(ROOT, "img", f"{k}.jpg"), os.path.join(OUT, "assets", "img", f"{k}.jpg"))
    for f in ("site.css", "site.js", "favicon.svg"):
        shutil.copy(os.path.join(ROOT, f), os.path.join(OUT, "assets", f))
    urls = []
    for lang in LANGS:
        for page in PAGES:
            r = R(lang, page)
            d = os.path.join(OUT, r.rel())
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
                f.write(r.render())
            urls.append(r.abs())
    if MODE == "site":
        with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                    + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
        with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(MODE, "→", os.path.normpath(OUT), len(urls), "pages")


if __name__ == "__main__":
    main()
