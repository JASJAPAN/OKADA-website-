// 営業中かどうかを日本時間で表示する（日〜木 16:00-24:00、金土 16:00-翌2:00。祝前日の延長は判定に入れていない）
(function () {
  var el = document.querySelector("[data-status]");
  if (!el) return;
  var p = new Intl.DateTimeFormat("en-US", { timeZone: "Asia/Tokyo", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(new Date());
  var g = function (t) { return p.filter(function (x) { return x.type === t; })[0].value; };
  var day = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(g("weekday"));
  var min = (parseInt(g("hour"), 10) % 24) * 60 + parseInt(g("minute"), 10);
  var late = day === 5 || day === 6;            // 当日が金・土
  var prevLate = day === 6 || day === 0;        // 前日が金・土（深夜2時まで）
  var open = min >= 960 || (prevLate && min < 120);
  el.classList.toggle("on", open);
  el.querySelector("span").textContent = open
    ? "ただいま営業中（" + (min < 120 || late ? "翌2:00" : "24:00") + "まで）"
    : "本日は16:00から営業します";
})();

// スマホのメニュー開閉
(function () {
  var b = document.querySelector(".burger"), d = document.getElementById("drawer");
  if (!b || !d) return;
  b.addEventListener("click", function () {
    var open = d.hasAttribute("hidden");
    if (open) d.removeAttribute("hidden"); else d.setAttribute("hidden", "");
    b.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
