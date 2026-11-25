/* きりしま牧場 天文館店 */
(function () {
  var PREVIEW = !!window.KB_PREVIEW;
  var root = document;

  /* ---- プレビュー専用: 1ファイルの中で言語とページを切り替える */
  function currentView() { return document.querySelector('.view:not([hidden])') || document; }
  function show(lang, page, anchor) {
    var id = lang + '-' + page;
    var target = document.querySelector('.view[data-view="' + id + '"]');
    if (!target) return;
    document.querySelectorAll('.view').forEach(function (v) { v.hidden = v !== target; });
    document.documentElement.lang = target.getAttribute('lang');
    fillImages(target);
    setStatus(target);
    if (window.KB_reveal) window.KB_reveal(target);
    var el = anchor ? target.querySelector('#' + anchor) : null;
    if (el) el.scrollIntoView(); else window.scrollTo(0, 0);
    try { history.replaceState(null, '', '#' + id); } catch (e) { location.hash = id; }
  }
  function fillImages(scope) {
    scope.querySelectorAll('img[data-img]').forEach(function (im) {
      var k = im.getAttribute('data-img');
      if (window.KB_IMG && window.KB_IMG[k]) { im.src = window.KB_IMG[k]; im.removeAttribute('data-img'); }
    });
  }
  if (PREVIEW) {
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest('a[data-go]');
      if (!a) return;
      ev.preventDefault();
      var p = a.getAttribute('data-go').split(':');
      var open = a.closest('details[open]'); if (open) open.open = false;
      show(p[0], p[1], p[2]);
    });
    window.addEventListener('hashchange', function () {
      var h = (location.hash || '').replace('#', '').match(/^(ja|en|zh-cn|zh-tw|ko)-(top|course|anniv)$/);
      if (h) show(h[1], h[2], '');
    });
  }

  /* ---- 営業中の表示（日本時間で判定。12/31と1/1は休み） */
  function setStatus(scope) {
    (scope || document).querySelectorAll('.status').forEach(function (el) {
      var now = new Date(Date.now() + 9 * 3600 * 1000);
      var mo = now.getUTCMonth() + 1, d = now.getUTCDate();
      var min = now.getUTCHours() * 60 + now.getUTCMinutes();
      var closedDay = (mo === 12 && d === 31) || (mo === 1 && d === 1);
      var open = !closedDay && ((min >= 660 && min < 840) || (min >= 1020 && min < 1320));
      var span = el.querySelector('span');
      if (!el.dataset.hours) el.dataset.hours = span.textContent;
      span.textContent = (open ? el.dataset.open : el.dataset.closed) + '｜' + el.dataset.hours.replace(/^[^0-9]*/, '');
      el.classList.toggle('on', open);
    });
  }
  if (!PREVIEW) setStatus(document);

  /* ---- 出現の動き（見えたら表示。2.5秒たてば必ず表示） */
  function reveal() {
    var h = window.innerHeight || 800;
    document.querySelectorAll('.rv:not(.in)').forEach(function (x) {
      if (!x.offsetParent) return;
      if (x.getBoundingClientRect().top < h * 0.94) x.classList.add('in');
    });
  }
  var rvTick = false;
  window.addEventListener('scroll', function () { if (rvTick) return; rvTick = true; requestAnimationFrame(function () { rvTick = false; reveal(); }); }, { passive: true });
  window.addEventListener('scroll', function () { var on = window.scrollY > (window.innerHeight || 700) * 0.9; document.querySelectorAll('.bar').forEach(function (b) { b.classList.toggle('show', on); }); }, { passive: true });
  window.addEventListener('resize', reveal);
  window.addEventListener('load', reveal);
  window.KB_reveal = reveal;
  if (!PREVIEW) reveal(document);

  /* ---- コースのタブ */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-tab]'); if (!b) return;
    var box = b.closest('[data-tabs]');
    box.querySelectorAll('[data-tab]').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
    box.querySelectorAll('[data-panel]').forEach(function (x) { x.hidden = x.getAttribute('data-panel') !== b.getAttribute('data-tab'); });
  });

  /* ---- スマホのメニュー */
  document.addEventListener('click', function (ev) {
    var bg = ev.target.closest('.burger');
    var open = document.querySelector('.drawer.open');
    if (bg) {
      var d = bg.closest('.hd').nextElementSibling, on = !d.classList.contains('open');
      d.classList.toggle('open', on); bg.setAttribute('aria-expanded', on ? 'true' : 'false');
      document.body.style.overflow = on ? 'hidden' : '';
    } else if (open && ev.target.closest('.drawer a')) {
      open.classList.remove('open'); document.body.style.overflow = '';
      var x = open.previousElementSibling.querySelector('.burger'); if (x) x.setAttribute('aria-expanded', 'false');
    }
  });

  /* ---- 予約の受け口が使えるか確かめる（使えないときは電話の案内に切り替える） */
  var API = window.KB_API || '';
  if (!PREVIEW) {
    var setForm = function (on) {
      document.querySelectorAll('form[data-rsv]').forEach(function (f) { f.hidden = !on; var o = f.parentNode.querySelector('.rsv-off'); if (o) o.hidden = on; });
      document.querySelectorAll('#reserve [data-off]').forEach(function (x) { x.textContent = on ? x.dataset.on : x.dataset.off; });
      document.querySelectorAll('a[href$="#reserve"]').forEach(function (x) { if (!on && x.closest('.nav,.drawer,.bar,.ft,.btns,.more')) { if (!x.dataset.t) x.dataset.t = x.textContent; x.textContent = document.querySelector('#reserve [data-off]') ? document.querySelector('.bar a[href^="tel:"]').textContent + ' ' + '099-248-7400' : x.textContent; x.setAttribute('href', 'tel:+81-99-248-7400'); } });
    };
    document.body.classList.add('rsv-phone');
    setForm(false);
    if (API) {
      fetch(API + '/status?store=' + encodeURIComponent(window.KB_STORE || '')).then(function (r) { return r.json(); }).then(function (j) { if (j.configured) { document.body.classList.remove('rsv-phone'); setForm(true); } }).catch(function () {});
    }
  }

  /* ---- 住所コピー */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-copy]');
    if (!b) return;
    var addr = b.closest('.mapbox').querySelector('[data-addr]').textContent;
    var label = b.textContent;
    var ok = function () { b.textContent = b.dataset.done; setTimeout(function () { b.textContent = label; }, 1800); };
    try { navigator.clipboard.writeText(addr).then(ok, function () {}); } catch (e) {}
  });

  /* ---- 予約リクエスト */
  document.querySelectorAll('form[data-rsv]').forEach(function (form) {
    var dateEl = form.querySelector('input[type="date"]');
    if (dateEl) {
      var j = new Date(Date.now() + 9 * 3600 * 1000);
      dateEl.min = j.toISOString().slice(0, 10);
    }
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var msg = form.querySelector('.msg'), btn = form.querySelector('button[type="submit"]');
      msg.textContent = '';
      if (!form.checkValidity()) {
        msg.textContent = msg.dataset.req;
        var bad = form.querySelector(':invalid'); if (bad) bad.focus();
        return;
      }
      var fd = new FormData(form);
      var finish = function () {
        var done = form.nextElementSibling, ul = done.querySelector('ul');
        ul.innerHTML = '';
        ['date', 'time', 'people', 'course', 'name', 'email'].forEach(function (k) {
          var li = document.createElement('li'); li.textContent = fd.get(k); ul.appendChild(li);
        });
        form.hidden = true; done.hidden = false; done.focus();
        done.scrollIntoView({ block: 'center' });
      };
      if (PREVIEW) { finish(); return; }
      btn.disabled = true; btn.textContent = btn.dataset.sending;
      fetch(API + '/reserve', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(fd).toString() })
        .then(function (r) { if (!r.ok) throw new Error(r.status); finish(); })
        .catch(function () { msg.textContent = msg.dataset.err; btn.disabled = false; btn.textContent = btn.dataset.label; });
    });
  });

  if (PREVIEW) {
    var m0 = (location.hash || '').replace('#', '').match(/^(ja|en|zh-cn|zh-tw|ko)-(top|course|anniv)$/);
    show(m0 ? m0[1] : 'ja', m0 ? m0[2] : 'top', '');
  }
})();
