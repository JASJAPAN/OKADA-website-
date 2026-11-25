// きりしま牧場 予約リクエストの受け口。
// サイトのフォームから届いた内容を、トークノートの「きりしま牧場」ノートへ投稿する。
// 外部ライブラリは使わない（Node 18 以上）。
//
// 環境変数
//   TALKNOTE_TOKEN     トークノート外部公開APIのアクセストークン
//   TALKNOTE_GROUP_ID  投稿先ノートのID
//   ALLOW_ORIGIN       サイトのURL（カンマ区切りで複数可）
const http = require("http");

const PORT = process.env.PORT || 10000;
const ORIGINS = (process.env.ALLOW_ORIGIN || "").split(",").map((s) => s.trim()).filter(Boolean);
const LANG = { ja: "日本語", en: "英語", "zh-cn": "中国語（簡体字）", "zh-tw": "中国語（繁体字）", ko: "韓国語" };
const configured = () => Boolean(process.env.TALKNOTE_TOKEN && process.env.TALKNOTE_GROUP_ID);

// 同じ送信元からの連投を抑える（10分で5件まで）
const hits = new Map();
function limited(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < 600000);
  list.push(now);
  hits.set(ip, list);
  if (hits.size > 5000) hits.clear();
  return list.length > 5;
}

function cors(req, res) {
  const o = req.headers.origin;
  if (o && (ORIGINS.length === 0 || ORIGINS.includes(o))) {
    res.setHeader("Access-Control-Allow-Origin", o);
    res.setHeader("Vary", "Origin");
  }
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function send(res, code, obj) {
  res.writeHead(code, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(JSON.stringify(obj));
}

function buildMessage(d) {
  const v = (k, n = 300) => String(d[k] || "").replace(/\r/g, "").trim().slice(0, n);
  return [
    "【予約リクエスト】きりしま牧場 ホームページより",
    "※まだ確定していません。お席を確認して、お客様へメールで返信してください。",
    "",
    `希望日時：${v("date", 20)} ${v("time", 10)}`,
    `人数：${v("people", 10)}`,
    `コース：${v("course", 80)}`,
    `お名前：${v("name", 80)}`,
    `メール：${v("email", 120)}`,
    `電話：${v("tel", 40) || "（記入なし）"}`,
    `目的：${v("purpose", 40) || "（記入なし）"}`,
    `ご要望：${v("note", 1000) || "（記入なし）"}`,
    `入力言語：${LANG[v("language", 10)] || v("language", 10)}`,
  ].join("\n");
}

async function handleReserve(req, res) {
  if (!configured()) return send(res, 503, { ok: false, error: "not_configured" });
  const ip = (req.headers["x-forwarded-for"] || req.socket.remoteAddress || "").split(",")[0].trim();
  if (limited(ip)) return send(res, 429, { ok: false, error: "too_many" });

  let body = "";
  for await (const chunk of req) {
    body += chunk;
    if (body.length > 20000) return send(res, 413, { ok: false, error: "too_large" });
  }
  let d = {};
  try {
    d = (req.headers["content-type"] || "").includes("json") ? JSON.parse(body) : Object.fromEntries(new URLSearchParams(body));
  } catch (e) {
    return send(res, 400, { ok: false, error: "bad_request" });
  }
  if (d.company) return send(res, 200, { ok: true }); // 自動投稿よけ（人には見えない欄）
  const need = ["date", "time", "people", "course", "name", "email"];
  if (need.some((k) => !String(d[k] || "").trim()) || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(d.email))) {
    return send(res, 400, { ok: false, error: "missing" });
  }

  const r = await fetch(`https://eapi.talknote.com/api/v1/group/post/${encodeURIComponent(process.env.TALKNOTE_GROUP_ID)}`, {
    method: "POST",
    headers: { "X-TALKNOTE-OAUTH-TOKEN": process.env.TALKNOTE_TOKEN, "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ message: buildMessage(d) }).toString(),
  });
  if (!r.ok) {
    console.error("Talknote への投稿に失敗", r.status, (await r.text()).slice(0, 300));
    return send(res, 502, { ok: false, error: "talknote" });
  }
  console.log("予約リクエストをトークノートへ投稿しました", d.date, d.time);
  send(res, 200, { ok: true });
}

http
  .createServer((req, res) => {
    cors(req, res);
    const path = req.url.split("?")[0];
    if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }
    if (req.method === "GET" && (path === "/" || path === "/health")) return send(res, 200, { ok: true });
    if (req.method === "GET" && path === "/status") return send(res, 200, { configured: configured() });
    if (req.method === "POST" && path === "/reserve") {
      return handleReserve(req, res).catch((e) => { console.error(e); send(res, 500, { ok: false, error: "server" }); });
    }
    send(res, 404, { ok: false });
  })
  .listen(PORT, () => console.log("kirishima-reserve listening on", PORT, "configured:", configured()));

module.exports = { buildMessage };
