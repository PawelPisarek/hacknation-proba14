// Aplikacja na ksefbot.pl (Coolify, port 3000): ekran + przekazanie /api/* do usługi na karcie OMENa.
// Tu nic nie liczymy (zakaz liczenia na procesorze). Gdy usługa nie odpowiada → tryb „wynik zapisany”:
// odpowiedzi karty zapisane wcześniej w aplikacja/zapisane/ (skrypty/mvp/zapisz_wyniki.mjs).
import http from "node:http";
import net from "node:net";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const KAT = path.dirname(fileURLToPath(import.meta.url));
const PORT = +(process.env.PORT || 3000);
const OMEN = new URL(process.env.OMEN_URL || "http://192.168.1.112:8770");
const ZAP = path.join(KAT, "zapisane");
const TYPY = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".png": "image/png", ".json": "application/json; charset=utf-8" };

const zapisane = (() => {
  try { return JSON.parse(fs.readFileSync(path.join(ZAP, "indeks.json"), "utf8")); } catch { return null; }
})();

function json(res, kod, obj) {
  const b = Buffer.from(JSON.stringify(obj));
  res.writeHead(kod, { "Content-Type": TYPY[".json"], "Content-Length": b.length, "Cache-Control": "no-store" });
  res.end(b);
}

// test łączności TCP (R2): czas połączenia z OMENem
function tcp(host, port, ms = 3000) {
  return new Promise((ok) => {
    const t0 = Date.now(), s = net.connect({ host, port });
    const kon = (wyn) => { s.destroy(); ok({ port, ...wyn, ms: Date.now() - t0 }); };
    s.setTimeout(ms, () => kon({ ok: false, blad: "przekroczony czas" }));
    s.on("connect", () => kon({ ok: true }));
    s.on("error", (e) => kon({ ok: false, blad: e.code || e.message }));
  });
}

function doOmena(req, res, sciezka, cialo, zapas) {
  const p = http.request({ host: OMEN.hostname, port: OMEN.port, path: sciezka, method: req.method, timeout: 180000,
    headers: { "content-type": req.headers["content-type"] || "application/octet-stream",
      ...(req.headers["content-length"] ? { "content-length": req.headers["content-length"] } : {}),
      ...(req.headers["x-nazwa"] ? { "x-nazwa": decodeURIComponent(req.headers["x-nazwa"]) .replace(/[^\w.\- ]/g, "_") } : {}) } },
  (o) => { res.writeHead(o.statusCode, { "content-type": o.headers["content-type"] || "application/json", "cache-control": o.headers["cache-control"] || "no-store" }); o.pipe(res); });
  const blad = (e) => { if (res.headersSent) return res.destroy(); zapas ? zapas(e) : json(res, 502, { blad: "usługa na karcie (OMEN) nie odpowiada: " + (e.code || e.message) }); };
  p.on("timeout", () => p.destroy(Object.assign(new Error("przekroczony czas"), { code: "ETIMEDOUT" })));
  p.on("error", blad);
  if (cialo !== undefined) p.end(cialo); else req.pipe(p);
}

const czytaj = (req) => new Promise((ok, zle) => { const c = []; let n = 0;
  req.on("data", (d) => { n += d.length; if (n > 1e6) { zle(new Error("za duże")); req.destroy(); } else c.push(d); });
  req.on("end", () => ok(Buffer.concat(c))); req.on("error", zle); });

// ------------------------------------------------ tryb „wynik zapisany”
function zapisanePrzyklady(res) {
  if (!zapisane) return json(res, 502, { blad: "usługa na karcie nie odpowiada, a zapisanych wyników brak" });
  json(res, 200, { ...zapisane.przyklady, zapisany: true, zapisano: zapisane.zapisano });
}
function zapisanaAnaliza(res, z) {
  if (!zapisane) return json(res, 502, { blad: "usługa na karcie nie odpowiada, a zapisanych wyników brak" });
  const k = `${z.badany}|${z.wzorzec}|${z.towar}`, plik = zapisane.analizy[k];
  if (!plik) return json(res, 502, { blad: `usługa na karcie nie odpowiada; zapisany wynik jest tylko dla przykładów pokazu (${Object.keys(zapisane.analizy).length} wariantów)`, zapisane: Object.keys(zapisane.analizy) });
  json(res, 200, { ...JSON.parse(fs.readFileSync(path.join(ZAP, plik), "utf8")), zapisany: true, zapisano: zapisane.zapisano });
}

const serwer = http.createServer(async (req, res) => {
  const u = new URL(req.url, "http://x");
  try {
    if (u.pathname === "/api/zdrowie") {
      const t0 = Date.now();
      const [ssh, usl] = await Promise.all([tcp(OMEN.hostname, 22), tcp(OMEN.hostname, +OMEN.port)]);
      let usluga = null;
      if (usl.ok) usluga = await new Promise((ok) => { const p = http.get({ host: OMEN.hostname, port: OMEN.port, path: "/zdrowie", timeout: 5000 }, (o) => { let s = ""; o.on("data", (d) => (s += d)).on("end", () => { try { ok(JSON.parse(s)); } catch { ok({ blad: s.slice(0, 200) }); } }); }); p.on("timeout", () => p.destroy()); p.on("error", (e) => ok({ blad: e.code || e.message })); });
      return json(res, 200, { aplikacja: "ok", omen: OMEN.host, tcp: [ssh, usl], usluga, zapisane: zapisane ? { zapisano: zapisane.zapisano, warianty: Object.keys(zapisane.analizy).length } : null, ms: Date.now() - t0, czas: new Date().toISOString() });
    }
    if (u.pathname === "/api/przyklady") return doOmena(req, res, "/przyklady", undefined, () => zapisanePrzyklady(res));
    if (u.pathname.startsWith("/api/obraz/") && /^\/api\/obraz\/[0-9a-f]{16}\.png$/.test(u.pathname)) {
      const lok = path.join(ZAP, path.basename(u.pathname));
      if (fs.existsSync(lok)) { res.writeHead(200, { "Content-Type": "image/png", "Cache-Control": "max-age=86400" }); return fs.createReadStream(lok).pipe(res); }
      return doOmena(req, res, u.pathname.slice(4));
    }
    if (u.pathname === "/api/wgraj" && req.method === "POST") return doOmena(req, res, "/wgraj");
    if (u.pathname === "/api/analiza" && req.method === "POST") {
      const b = await czytaj(req);
      let z = {}; try { z = JSON.parse(b); } catch { return json(res, 400, { blad: "zły JSON" }); }
      req.headers["content-length"] = String(b.length);
      return doOmena(req, res, "/analiza", b, () => zapisanaAnaliza(res, z));
    }
    if (u.pathname.startsWith("/api/")) return json(res, 404, { blad: "nie ma" });
    const p = path.join(KAT, "public", path.normalize(u.pathname === "/" ? "/index.html" : u.pathname).replace(/^(\.\.[/\\])+/, ""));
    if (!p.startsWith(path.join(KAT, "public")) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end("nie ma"); }
    res.writeHead(200, { "Content-Type": TYPY[path.extname(p)] || "application/octet-stream", "Cache-Control": "no-cache" });
    fs.createReadStream(p).pipe(res);
  } catch (e) { if (!res.headersSent) json(res, 500, { blad: e.message }); }
});
serwer.listen(PORT, () => console.log(`aplikacja na :${PORT}, usługa karty: ${OMEN.href}, zapisane: ${zapisane ? zapisane.zapisano : "brak"}`));
