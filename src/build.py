# -*- coding: utf-8 -*-
"""きりしま牧場サイトのビルド。
  python3 build.py  →  dist/   本番用（言語ごとのURL、hreflang、構造化データ、Netlify設定）
                       preview.html  デザイン確認用の1ファイル（全言語・全ページを内蔵）
"""
import base64, html, json, os, shutil, sys
from content import *

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "dist")
PAGES = ["top", "course", "anniv"]
PATH = {"top": "", "course": "course/", "anniv": "celebrations/"}
IMGS = ["steak", "sushi", "aburi", "rossini", "spread", "dessert", "room", "table"]
PX = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="


def e(s):
    return html.escape(s, quote=True)


class R:
    """1言語・1ページ分のレンダラ。mode は 'site' か 'preview'。"""

    def __init__(self, lang, page, mode):
        self.lang, self.page, self.mode = lang, page, mode
        self.i = LANGS.index(lang)

    def t(self, k):
        return T[k][self.i]

    def x(self, tup):
        return tup[self.i]

    def base(self, lang=None):
        lang = lang or self.lang
        return "/" if lang == "ja" else f"/{lang}/"

    def href(self, page=None, anchor="", lang=None):
        page = page or self.page
        lang = lang or self.lang
        url = self.base(lang) + PATH[page] + (f"#{anchor}" if anchor else "")
        if self.mode == "preview":
            return f'href="#{lang}-{page}" data-go="{lang}:{page}:{anchor}"'
        return f'href="{url}"'

    def img(self, key, alt, cls="", eager=False):
        a = e(self.t("alt_" + key) if alt is None else alt)
        c = f' class="{cls}"' if cls else ""
        if self.mode == "preview":
            return f'<img{c} src="{PX}" data-img="{key}" alt="{a}" width="960" height="960">'
        load = "" if eager else ' loading="lazy"'
        return f'<img{c} src="/assets/img/{key}.jpg" alt="{a}" width="960" height="960"{load} decoding="async">'

    def yen(self, n):
        s = f"{n:,}"
        return {"ja": f"{s}<small>円（税込）</small>", "en": f"¥{s}<small>tax incl.</small>",
                "zh-cn": f"{s}<small>日元（含税）</small>", "zh-tw": f"{s}<small>日圓（含稅）</small>",
                "ko": f"{s}<small>엔(세금 포함)</small>"}[self.lang]

    def yen_plain(self, s):
        return {"ja": f"{s}円", "en": f"¥{s}", "zh-cn": f"{s}日元", "zh-tw": f"{s}日圓", "ko": f"{s}엔"}[self.lang]

    # ------------------------------------------------------------ 共通パーツ
    def header(self):
        t = self.t
        cur = lambda p: ' aria-current="page"' if p == self.page else ""
        langs = "".join(
            f'<li><a {self.href(lang=l)} hreflang="{HTML_LANG[l]}" lang="{HTML_LANG[l]}"'
            f'{" aria-current=\"true\"" if l == self.lang else ""}>{LANG_LABEL[l]}</a></li>' for l in LANGS)
        return f'''<a class="skip" href="#main">{t("skip")}</a>
<header class="hd"><div class="wrap">
<a class="brand" {self.href("top")}><b>{e(self.x(STORE["name"]))}</b><span>{e(self.x(STORE["tag"]))}</span></a>
<nav class="nav" aria-label="main">
<a {self.href("top")}{cur("top")}>{t("nav_top")}</a>
<a {self.href("course")}{cur("course")}>{t("nav_course")}</a>
<a {self.href("anniv")}{cur("anniv")}>{t("nav_anniv")}</a>
<a {self.href("top", "access")}>{t("nav_access")}</a>
<a {self.href("top", "reserve")}>{t("nav_reserve")}</a>
</nav>
<details class="langsel"><summary aria-label="{t("lang")}">{LANG_LABEL[self.lang]}</summary><ul>{langs}</ul></details>
<button class="burger" type="button" aria-label="menu" aria-expanded="false"><i></i><i></i><i></i></button>
</div></header>
<div class="drawer">
<a {self.href("top")}><small>Home</small>{t("nav_top")}</a>
<a {self.href("course")}><small>Courses &amp; menu</small>{t("nav_course")}</a>
<a {self.href("anniv")}><small>Celebrations</small>{t("nav_anniv")}</a>
<a {self.href("top", "access")}><small>Access</small>{t("nav_access")}</a>
<a {self.href("top", "reserve")}><small>Reservation</small>{t("nav_reserve")}</a>
<a class="tel" href="tel:{TEL_INTL}">{TEL}</a>
</div>'''

    def footer(self):
        t = self.t
        return f'''<footer class="ft"><div class="wrap">
<p class="name">{e(self.x(STORE["name"]))}</p>
<p>{e(self.x(STORE["addr"]))}<br><span class="num">{TEL}</span>（+81-99-248-7400）</p>
<div class="links"><a {self.href("top")}>{t("nav_top")}</a><a {self.href("course")}>{t("nav_course")}</a><a {self.href("anniv")}>{t("nav_anniv")}</a><a {self.href("top", "access")}>{t("nav_access")}</a><a {self.href("top", "reserve")}>{t("nav_reserve")}</a></div>
<p style="margin-top:24px">{t("foot_note")}<br>{t("foot_op")}</p>
</div></footer>
<nav class="bar" aria-label="quick">
<a {self.href("course")}>{t("nav_course")}</a>
<a class="main" {self.href("top", "reserve")}>{t("nav_reserve")}</a>
<a href="tel:{TEL_INTL}">{t("cta_call")}</a>
</nav>'''

    def course_cards(self):
        t, out = self.t, []
        for c in COURSES:
            badge = f'<span class="badge">{t("popular")}</span>' if c["popular"] else ""
            out.append(f'''<article class="card">{badge}
<p class="en">{c["en"]}</p>{"" if self.lang == "en" else "<h3>" + e(self.x(c["name"])) + "</h3>"}
<p class="price">{self.yen(c["price"])}</p>
<p class="lead">{e(self.x(c["lead"]))}</p>
<p class="meta">{t("r_count")} {c["count"]}</p></article>''')
        return '<div class="cards">' + "".join(out) + "</div>"

    def faq(self):
        items = "".join(f'<details><summary>{e(self.x(q))}</summary><p>{e(self.x(a))}</p></details>' for q, a in FAQ)
        return f'<div class="faq">{items}</div>'

    def form(self):
        t = self.t
        times = [f"{h}:{m}" for h in (11, 12, 13) for m in ("00", "30")] + [f"{h}:{m}" for h in range(17, 22) for m in ("00", "30")]
        times = [x for x in times if x != "13:30" or True]
        topt = "".join(f"<option>{x}</option>" for x in times)
        popt = "".join(f"<option>{n}{t('people_unit')}</option>" for n in range(1, 21))
        copt = "".join(f'<option>{e(self.x(c["name"]))} {self.yen_plain(f"{c['price']:,}")}</option>' for c in COURSES)
        copt += "".join(f"<option>{e(t(k))}</option>" for k in ("l1_n", "l2_n", "l3_n", "c_seat", "c_undecided"))
        purp = "".join(f"<option>{e(t(k))}</option>" for k in ("p_birthday", "p_anniv", "p_biz", "p_family", "p_trip", "p_other"))
        sel = f'<option value="">{t("sel")}</option>'
        return f'''<form class="form" name="reservation" method="POST" action="{API_URL}/reserve" data-rsv novalidate>
<input type="hidden" name="form-name" value="reservation"><input type="hidden" name="language" value="{self.lang}">
<p class="hp"><label>Company<input name="company" tabindex="-1" autocomplete="off"></label></p>
<div class="grid three">
<div><label for="f-date-{self.lang}">{t("f_date")}</label><input id="f-date-{self.lang}" type="date" name="date" required></div>
<div><label for="f-time-{self.lang}">{t("f_time")}</label><select id="f-time-{self.lang}" name="time" required>{sel}{topt}</select></div>
<div><label for="f-people-{self.lang}">{t("f_people")}</label><select id="f-people-{self.lang}" name="people" required>{sel}{popt}</select></div>
</div>
<div class="grid" style="margin-top:16px"><div><label for="f-course-{self.lang}">{t("f_course")}</label><select id="f-course-{self.lang}" name="course" required>{sel}{copt}</select></div></div>
<div class="grid two" style="margin-top:16px">
<div><label for="f-name-{self.lang}">{t("f_name")}</label><input id="f-name-{self.lang}" name="name" autocomplete="name" required></div>
<div><label for="f-email-{self.lang}">{t("f_email")}</label><input id="f-email-{self.lang}" type="email" name="email" autocomplete="email" inputmode="email" required></div>
<div><label for="f-tel-{self.lang}">{t("f_tel")}</label><input id="f-tel-{self.lang}" type="tel" name="tel" autocomplete="tel"></div>
<div><label for="f-purpose-{self.lang}">{t("f_purpose")}</label><select id="f-purpose-{self.lang}" name="purpose">{sel}{purp}</select></div>
</div>
<div class="grid" style="margin-top:16px"><div><label for="f-note-{self.lang}">{t("f_note")}</label><textarea id="f-note-{self.lang}" name="note" placeholder="{e(t("f_note_ph"))}"></textarea></div></div>
<p class="policy">{t("f_cancel")}<br>{t("f_privacy")}</p>
<label class="agree" for="f-agree-{self.lang}"><input id="f-agree-{self.lang}" type="checkbox" name="agree" value="yes" required><span>{t("f_agree")}</span></label>
<button class="btn solid" type="submit" data-label="{e(t("f_send"))}" data-sending="{e(t("f_sending"))}">{t("f_send")}</button>
<p class="msg" role="alert" data-err="{e(t("f_err"))}" data-req="{e(t("f_req"))}"></p>
</form>
<div class="done" hidden tabindex="-1"><h3>{t("done_h")}</h3><p>{t("done_p")}</p><ul></ul>
<p style="margin-top:16px"><span class="num" style="font-size:24px;color:var(--ink)">{TEL}</span></p>
{f'<p class="pv">{t("done_preview")}</p>' if self.mode == "preview" else ""}</div>'''

    def reserve(self):
        t = self.t
        return f'''<section class="sec deep" id="reserve"><span class="bigword" aria-hidden="true">Reserve</span><div class="wrap rsv">
<div><span class="kicker">Reservation</span><h2>{t("rsv_h")}</h2><span class="rule"></span>
<p class="intro">{t("rsv_p")}</p>
<a class="tel" href="tel:{TEL_INTL}">{TEL}</a><p class="sub">+81-99-248-7400</p></div>
<div><div class="rsv-off" hidden><p>{t("walkin")}</p><a class="num" href="tel:{TEL_INTL}">{TEL}</a><p>+81-99-248-7400</p></div>{self.form()}</div>
</div></section>'''

    # ------------------------------------------------------------ トップ
    def top(self):
        t = self.t
        h = t("hero_h")
        if self.lang == "ja":
            a, b = h.split("、")
            h1 = f"<span>{a}、</span><span>{b}</span>"
        else:
            h1 = e(h)
        sig = "".join(f'<figure>{self.img(k, None)}<figcaption><b>{e(t(n))}</b><span>{e(t(d))}</span></figcaption></figure>'
                      for k, n, d in (("sushi", "s1_n", "s1_d"), ("aburi", "s2_n", "s2_d"), ("rossini", "s3_n", "s3_d"), ("steak", "s4_n", "s4_d")))
        info = "".join(f"<div><dt>{t(k)}</dt><dd>{v}</dd></div>" for k, v in (
            ("i_name", e(self.x(STORE["name"])) + ("" if self.lang == "ja" else f'<br><span lang="ja">{STORE["full"][0]}</span>')),
            ("i_addr", e(self.x(STORE["addr"])) + ("" if self.lang == "ja" else f'<br><span lang="ja">{STORE["addr_ja"]}</span>')),
            ("i_tel", f'<a class="num" href="tel:{TEL_INTL}">{TEL}</a>（+81-99-248-7400）'),
            ("i_hours", t("i_hours_v")), ("i_closed", t("i_closed_v")), ("i_seats", t("i_seats_v")),
            ("i_access", t("i_access_v")), ("i_pay", t("i_pay_v")), ("i_lang", t("i_lang_v"))))
        mapq = "https://www.google.com/maps/search/?api=1&query=" + "%E3%81%8D%E3%82%8A%E3%81%97%E3%81%BE%E7%89%A7%E5%A0%B4+%E5%A4%A9%E6%96%87%E9%A4%A8%E5%BA%97+%E9%B9%BF%E5%85%90%E5%B3%B6%E5%B8%82%E5%8D%83%E6%97%A5%E7%94%BA3-5"
        dishes = "".join(
            f'<article class="dish-row rv"><figure>{self.img(k, None)}</figure><div><span class="no">{n:02d}</span><h3>{e(t(nm))}</h3><p>{e(t(d))}</p></div></article>'
            for n, (k, nm, d) in enumerate((("sushi", "s1_n", "s1_d"), ("aburi", "s2_n", "s2_d"), ("rossini", "s3_n", "s3_d"), ("steak", "s4_n", "s4_d")), 1))
        tabs = "".join(
            f'<button type="button" role="tab" data-tab="{c["id"]}" aria-selected="{"true" if c["popular"] else "false"}">'
            f'{"<span class=dot></span>" if c["popular"] else ""}<span class="en">{c["en"]}</span><span class="num">{self.yen_plain(f"{c["price"]:,}")}</span></button>' for c in COURSES)
        panels = ""
        for c in COURSES:
            dl = "".join(f"<dt>{e(self.x(cat))}</dt>" + "".join(f"<dd>{e(self.x(it))}</dd>" for it in items) for cat, items in c["menu"])
            swap = f'<p class="swap">{t("swap")}</p>' if c.get("swap") else ""
            pop = f'<span class="badge" style="position:static;display:inline-block;margin-bottom:10px">{t("popular")}</span>' if c["popular"] else ""
            panels += f'''<div class="panel" role="tabpanel" data-panel="{c["id"]}"{"" if c["popular"] else " hidden"}>
<div>{pop}<p class="big">{e(self.x(c["lead"]))}</p><p class="price">{self.yen(c["price"])}</p>
<dl class="kv"><div><dt>{t("r_sushi")}</dt><dd>{e(self.x(c["sushi"]))}</dd></div><div><dt>{t("r_steak")}</dt><dd>{e(self.x(c["steak"]))}</dd></div><div><dt>{t("r_extra")}</dt><dd>{e(self.x(c["extra"]))}</dd></div><div><dt>{t("r_count")}</dt><dd class="num">{c["count"]}</dd></div></dl></div>
<article class="menu-card"><p class="en">{c["en"]} course</p>{"" if self.lang == "en" else "<h3>" + e(self.x(c["name"])) + "</h3>"}<dl>{dl}</dl>{swap}</article></div>'''
        return f'''<section class="hero2">
<figure class="hero2-media">{self.img("steak", None, eager=True)}</figure>
<div class="wrap hero2-in">
<div class="hero2-head"><span class="kicker rv">Kagoshima Wagyu · Steak &amp; Nikuzushi</span><h1 class="rv d1">{h1}</h1></div>
<figure class="hero2-sub rv d3">{self.img("aburi", None)}</figure>
<div class="hero2-side rv d2">
<p class="lead">{t("hero_p")}</p>
<div class="btns"><a class="btn solid" {self.href("top", "reserve")}>{t("cta_reserve")}</a><a class="btn" {self.href("course")}>{t("cta_course")}</a></div>
<p class="status" data-open="{e(t("open_now"))}" data-closed="{e(t("closed_now"))}"><i></i><span>{t("i_hours")} 11:00–14:00 / 17:00–22:00</span></p>
</div></div>
<div class="wrap"><dl class="facts rv">
<div><dt>{t("fact_course")}</dt><dd>{t("fact_course_v")}</dd></div>
<div><dt>{t("fact_lunch")}</dt><dd>{t("fact_lunch_v")}</dd></div>
<div><dt>{t("fact_solo")}</dt><dd>{t("fact_solo_v")}</dd></div>
<div><dt>{t("fact_pay")}</dt><dd>{t("fact_pay_v")}</dd></div>
</dl></div></section>

<section class="sec paper" id="about"><span class="bigword" aria-hidden="true">Wagyu</span><div class="wrap">
<span class="kicker">Our way</span><h2 class="rv">{t("about_h")}</h2><span class="rule"></span>
<div class="pillars">
<article class="rv"><h3>{t("a1_h")}</h3><p>{t("a1_p")}</p></article>
<article class="rv d1"><h3>{t("a2_h")}</h3><p>{t("a2_p")}</p></article>
<article class="rv d2"><h3>{t("a3_h")}</h3><p>{t("a3_p")}</p></article>
</div></div></section>

<section class="sec" id="signature"><span class="bigword" aria-hidden="true">Nikuzushi</span><div class="wrap">
<span class="kicker">Signature</span><h2 class="rv">{t("sig_h")}</h2><span class="rule"></span>
<div class="dish">{dishes}</div>
</div></section>

<section class="sec paper" id="courses"><span class="bigword" aria-hidden="true">Course</span><div class="wrap">
<span class="kicker">Dinner course</span><h2 class="rv">{t("course_h")}</h2><span class="rule"></span>
<div data-tabs><div class="tablist" role="tablist">{tabs}</div>{panels}</div>
<p class="note">{t("course_note")}</p>
<p class="more"><a class="btn" {self.href("course")}>{t("course_more")}</a></p>
</div></section>

<div class="band">{self.img("sushi", None)}{self.img("rossini", None)}{self.img("spread", None)}</div>

<section class="sec" id="lunch"><span class="bigword" aria-hidden="true">Lunch</span><div class="wrap duo frame">
<figure>{self.img("table", None)}</figure>
<div><span class="kicker">Lunch</span><h2>{t("lunch_h")}</h2><span class="rule"></span>
<p class="intro">{t("lunch_time")}</p>
<div class="rows">
<div class="row"><h3>{t("l1_n")}</h3><p class="p">{self.yen_plain("1,800")}{t("from") if self.lang != "en" else ""}</p></div>
<div class="row"><h3>{t("l2_n")}</h3><p class="p">{self.yen_plain("3,800")}{t("from") if self.lang != "en" else ""}</p></div>
<div class="row"><h3>{t("l3_n")}</h3><p class="p">{self.yen_plain("6,800")}</p></div>
</div>
<p class="more"><a class="btn" {self.href("course", "lunch")}>{t("nav_course")}</a></p></div>
</div></section>

<section class="sec deep" id="celebrate"><div class="wrap duo flip">
<figure>{self.img("dessert", None)}</figure>
<div><span class="kicker">Celebrations</span><h2>{t("anniv_h")}</h2><span class="rule"></span>
<p class="intro">{t("anniv_p")}</p>
<p class="more"><a class="btn" {self.href("anniv")}>{t("nav_anniv")}</a></p></div>
</div></section>

<section class="sec" id="room"><div class="wrap duo frame">
<figure>{self.img("room", None)}</figure>
<div><span class="kicker">The room</span><h2>{t("seat_h")}</h2><span class="rule"></span>
<p class="intro">{t("seat_p")}</p></div>
</div></section>

<section class="sec paper" id="access"><span class="bigword" aria-hidden="true">Access</span><div class="wrap">
<span class="kicker">Hours &amp; access</span><h2>{t("info_h")}</h2><span class="rule"></span>
<div class="info"><dl>{info}</dl>
<div class="mapbox"><p class="addr" lang="ja" data-addr>{STORE["addr_ja"]}</p>
<p class="hint">{t("map_hint")}</p>
<div class="btns"><a class="btn" href="{mapq}" target="_blank" rel="noopener">{t("map_open")}</a>
<button class="btn" type="button" data-copy data-done="{e(t("map_copied"))}">{t("map_copy")}</button></div>
<p class="walk">{t("walkin")}<a class="tel" href="tel:{TEL_INTL}">{TEL}</a></p></div>
</div></div></section>

<section class="sec" id="faq"><div class="wrap">
<span class="kicker">Questions</span><h2>{t("faq_h")}</h2><span class="rule"></span>
{self.faq()}
</div></section>
{self.reserve()}'''

    # ------------------------------------------------------------ コース・メニュー
    def course(self):
        t = self.t
        cards = []
        for c in COURSES:
            dl = "".join(f"<dt>{e(self.x(cat))}</dt>" + "".join(f"<dd>{e(self.x(it))}</dd>" for it in items) for cat, items in c["menu"])
            swap = f'<p class="swap">{t("swap")}</p>' if c.get("swap") else ""
            pop = f'<p class="badge" style="position:static;display:inline-block;margin-bottom:8px">{t("popular")}</p>' if c["popular"] else ""
            cards.append(f'''<article class="menu-card" id="{c["id"]}">{pop}<p class="en">{c["en"]} course</p>{"" if self.lang == "en" else "<h3>" + e(self.x(c["name"])) + "</h3>"}
<p class="price">{self.yen(c["price"])}</p><dl>{dl}</dl>{swap}</article>''')
        head = "".join(f'<th scope="col"><span class="num">{self.yen_plain(f"{c['price']:,}")}</span>{e(self.x(c["name"]))}</th>' for c in COURSES)
        def row(lbl, key):
            return f'<tr><th scope="row">{t(lbl)}</th>' + "".join(f"<td>{e(self.x(c[key]))}</td>" for c in COURSES) + "</tr>"
        cnt = f'<tr><th scope="row">{t("r_count")}</th>' + "".join(f'<td class="num">{c["count"]}</td>' for c in COURSES) + "</tr>"
        def alc(key, items):
            li = "".join(f'<li><span>{e(self.x(n))}</span>' + (f'<span class="num">{self.yen_plain(p)}</span>' if p else "") + "</li>" for n, p in items)
            return f'<div><h3>{t(key)}</h3><ul>{li}</ul></div>'
        return f'''<section class="ph"><div class="wrap">
<p class="crumb"><a {self.href("top")}>{t("nav_top")}</a> ／ {t("nav_course")}</p>
<span class="kicker">Courses &amp; menu</span><h1>{t("course_h")}</h1>
<p>{t("course_note")}</p>
<p class="anchors"><a {self.href("course", "dinner")}>{t("course_k")}</a><a {self.href("course", "lunch")}>{t("lunch_k")}</a><a {self.href("course", "seasonal")}>{t("season_k")}</a><a {self.href("course", "alacarte")}>{t("alc_k")}</a></p>
</div></section>

<section class="sec paper" id="dinner" style="margin-top:56px"><div class="wrap">
<span class="kicker">Dinner course</span><h2>{t("cmp_h")}</h2><span class="rule"></span>
<div class="tbl-scroll"><table class="cmp"><thead><tr><th></th>{head}</tr></thead>
<tbody>{row("r_sushi", "sushi")}{row("r_steak", "steak")}{row("r_extra", "extra")}{cnt}</tbody></table></div>
<p class="note">{t("cmp_note")}</p>
<div class="menu-list">{"".join(cards)}</div>
<p class="note"><b>{t("opt_h")}</b>　{t("opt_p")}</p>
<p class="more"><a class="btn solid" {self.href("top", "reserve")}>{t("cta_reserve")}</a></p>
</div></section>

<section class="sec" id="lunch"><div class="wrap">
<span class="kicker">Lunch</span><h2>{t("lunch_h")}</h2><span class="rule"></span>
<p class="intro">{t("lunch_time")}</p>
<div class="rows">
<div class="row"><h3>{t("l1_n")}</h3><p class="p">{self.yen_plain("1,800")}{t("from") if self.lang != "en" else ""}<small>{t("tax")}</small></p><p class="d">{t("l1_d")}</p></div>
<div class="row"><h3>{t("l2_n")}</h3><p class="p" style="font-size:18px">{t("l2_p")}<small>{t("tax")}</small></p><p class="d">{t("l2_d")}</p></div>
<div class="row"><h3>{t("l3_n")}</h3><p class="p">{self.yen_plain("6,800")}<small>{t("tax")}</small></p><p class="d">{t("l3_d")}</p></div>
</div></div></section>

<section class="sec deep" id="seasonal"><div class="wrap">
<span class="kicker">Seasonal</span><h2>{t("season_k")}</h2><span class="rule"></span>
<div class="rows">
<div class="row"><h3>{t("x_n")}</h3><p class="p">{self.yen_plain("8,000")} / {self.yen_plain("10,000")}<small>{t("tax")}</small></p><p class="d">{t("x_d")}</p></div>
<div class="row"><h3>{t("n29_n")}</h3><p class="p">{self.yen_plain("8,290")}<small>{t("tax")}</small></p><p class="d">{t("n29_d")}</p></div>
</div></div></section>

<section class="sec" id="alacarte"><div class="wrap">
<span class="kicker">A la carte</span><h2>{t("alc_h")}</h2><span class="rule"></span>
<div class="alc">{alc("alc_steak", ALC["steak"])}{alc("alc_sushi", ALC["sushi"])}{alc("alc_special", ALC["special"])}</div>
<p class="note">{t("alc_note")}</p>
</div></section>
{self.reserve()}'''

    # ------------------------------------------------------------ 記念日
    def anniv(self):
        t = self.t
        feat = "".join(f"<article><h3>{t(h)}</h3><p>{t(p)}</p></article>" for h, p in (("an1_h", "an1_p"), ("an2_h", "an2_p"), ("an3_h", "an3_p"), ("an4_h", "an4_p")))
        return f'''<section class="ph"><div class="wrap">
<p class="crumb"><a {self.href("top")}>{t("nav_top")}</a> ／ {t("nav_anniv")}</p>
<span class="kicker">Celebrations &amp; private dining</span><h1>{t("anniv_h")}</h1>
<p>{t("anniv_p")}</p>
</div></section>

<section class="sec"><div class="wrap duo frame">
<figure>{self.img("table", None, eager=True)}</figure>
<figure>{self.img("dessert", None)}</figure>
</div></section>

<section class="sec paper"><div class="wrap">
<span class="kicker">What we prepare</span><h2>{t("anniv_k")}</h2><span class="rule"></span>
<div class="feat">{feat}</div>
<p class="more"><a class="btn" {self.href("course")}>{t("cta_course")}</a></p>
</div></section>

<section class="sec"><div class="wrap duo flip">
<figure>{self.img("room", None)}</figure>
<div><span class="kicker">Surprise</span><h2>{t("flow_h")}</h2><span class="rule"></span>
<ol class="flow"><li>{t("flow1")}</li><li>{t("flow2")}</li><li>{t("flow3")}</li></ol></div>
</div></section>
{self.reserve()}'''

    def body(self):
        return f'{self.header()}\n<main id="main">\n{getattr(self, self.page)()}\n</main>\n{self.footer()}'

    # ------------------------------------------------------------ head
    def canonical(self, lang=None, page=None):
        return SITE_URL + self.base(lang) + PATH[page or self.page]

    def jsonld(self):
        if self.page == "anniv":
            return ""
        i = self.i
        rest = {
            "@context": "https://schema.org", "@type": "Restaurant", "@id": SITE_URL + "/#restaurant",
            "name": STORE["name"][i], "alternateName": [STORE["full"][0], STORE["name"][1]],
            "url": self.canonical(page="top"), "telephone": TEL_INTL,
            "image": [SITE_URL + f"/assets/img/{k}.jpg" for k in ("steak", "sushi", "room")],
            "address": {"@type": "PostalAddress", "postalCode": "892-0843", "addressCountry": "JP", "addressRegion": "鹿児島県",
                        "addressLocality": "鹿児島市", "streetAddress": "千日町3-5 くらかわビル1階"},
            "servesCuisine": ["和牛ステーキ", "肉寿司", "Wagyu steak", "Wagyu sushi"],
            "priceRange": "¥1,800〜¥15,000", "acceptsReservations": True,
            "currenciesAccepted": "JPY",
            "paymentAccepted": "Cash, Visa, Mastercard, JCB, American Express, Diners Club, Discover, UnionPay, Alipay, WeChat Pay, PayPay",
            "openingHoursSpecification": [
                {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": o, "closes": c}
                for o, c in (("11:00", "14:00"), ("17:00", "22:00"))],
            "specialOpeningHoursSpecification": [
                {"@type": "OpeningHoursSpecification", "validFrom": "2026-12-31", "validThrough": "2027-01-01", "opens": "00:00", "closes": "00:00"}],
            "hasMenu": self.canonical(page="course"),
            "sameAs": ["https://www.hotpepper.jp/strJ003737356/", "https://tabelog.com/kagoshima/A4601/A460101/46014710/", "https://r.gnavi.co.jp/fbxs200/", "https://restaurant.ikyu.com/121127/"],
            "availableLanguage": ["ja", "en", "zh"],
        }
        out = [rest]
        if self.page == "course":
            out.append({"@context": "https://schema.org", "@type": "Menu", "name": self.t("nav_course"), "url": self.canonical(), "inLanguage": HTML_LANG[self.lang],
                        "hasMenuSection": [{"@type": "MenuSection", "name": self.t("course_k"), "hasMenuItem": [
                            {"@type": "MenuItem", "name": self.x(c["name"]), "description": self.x(c["lead"]),
                             "offers": {"@type": "Offer", "price": c["price"], "priceCurrency": "JPY"}} for c in COURSES]}]})
        if self.page == "top":
            out.append({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": HTML_LANG[self.lang],
                        "mainEntity": [{"@type": "Question", "name": self.x(q), "acceptedAnswer": {"@type": "Answer", "text": self.x(a)}} for q, a in FAQ]})
        return "\n".join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>" for o in out)

    def document(self):
        key = {"top": "top", "course": "course", "anniv": "anniv"}[self.page]
        alts = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{self.canonical(lang=l)}">' for l in LANGS)
        alts += f'<link rel="alternate" hreflang="x-default" href="{self.canonical(lang="en")}">'
        return f'''<!DOCTYPE html>
<html lang="{HTML_LANG[self.lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(self.t("t_" + key))}</title>
<meta name="description" content="{e(self.t("d_" + key))}">
<link rel="canonical" href="{self.canonical()}">
{alts}
<meta property="og:type" content="restaurant">
<meta property="og:title" content="{e(self.t("t_" + key))}">
<meta property="og:description" content="{e(self.t("d_" + key))}">
<meta property="og:url" content="{self.canonical()}">
<meta property="og:image" content="{SITE_URL}/assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#15110f">
<meta name="format-detection" content="telephone=no">
{'' if self.lang.startswith('zh') else '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Shippori+Mincho:wght@400;500;600&display=swap" rel="stylesheet">'}
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
<script>document.documentElement.classList.add("js");window.KB_API="{API_URL}";</script>
{self.jsonld()}
</head>
<body>
{self.body()}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def build_site():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "assets", "img"))
    for k in IMGS:
        shutil.copy(os.path.join(ROOT, "img2x", f"{k}.jpg"), os.path.join(OUT, "assets", "img", f"{k}.jpg"))
    shutil.copy(os.path.join(ROOT, "img2x", "og.jpg"), os.path.join(OUT, "assets", "img", "og.jpg"))
    for f in ("site.css", "site.js", "favicon.svg"):
        shutil.copy(os.path.join(ROOT, f), os.path.join(OUT, "assets", f))
    urls = []
    for lang in LANGS:
        for page in PAGES:
            r = R(lang, page, "site")
            d = os.path.join(OUT, r.base().strip("/"), PATH[page])
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
                f.write(r.document())
            urls.append(r.canonical())
        # 送信完了ページ（JSが動かない環境の受け皿）
        r = R(lang, "top", "site")
        d = os.path.join(OUT, r.base().strip("/"), "thanks")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(f'''<!DOCTYPE html><html lang="{HTML_LANG[lang]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>{e(r.t("done_h"))}</title><link rel="stylesheet" href="/assets/site.css"></head><body>{r.header()}<main id="main"><section class="sec"><div class="wrap"><div class="done"><h3>{r.t("done_h")}</h3><p>{r.t("done_p")}</p><p style="margin-top:16px"><span class="num" style="font-size:24px;color:var(--ink)">{TEL}</span></p></div></div></section></main>{r.footer()}</body></html>''')
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    for extra in ("netlify.toml", "README.md"):
        p = os.path.join(ROOT, "deploy", extra)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, "..", "site-package", extra)) if False else None
    return urls


def build_preview():
    views = []
    for lang in LANGS:
        for page in PAGES:
            r = R(lang, page, "preview")
            views.append(f'<div class="view" data-view="{lang}-{page}" lang="{HTML_LANG[lang]}" hidden>\n{r.body()}\n</div>')
    imgs = {}
    for k in IMGS:
        with open(os.path.join(ROOT, "img2x", f"{k}.jpg"), "rb") as f:
            imgs[k] = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    css = read("site.css")
    js = read("site.js")
    doc = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>きりしま牧場 天文館店 サイト案</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Shippori+Mincho:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
{"".join(views)}
<script>document.documentElement.classList.add("js");window.KB_PREVIEW=true;window.KB_IMG={json.dumps(imgs)};</script>
<script>
{js}
</script>
</body>
</html>
'''
    with open(os.path.join(ROOT, "..", "preview.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    return len(doc)


if __name__ == "__main__":
    urls = build_site()
    n = build_preview()
    print(len(urls), "pages; preview bytes:", n)
