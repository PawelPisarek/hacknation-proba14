// Wariant pokazu P39 z ustawień startowych: „Analizuj” bez zmian → 5 miejsc + 5 pominiętych; zrzut.
// node skrypty/mvp/sprawdz_pokaz.mjs <URL> <zrzut.png>
import { spawn } from "child_process"; import fs from "fs";
const [, , U, Z] = process.argv; const sleep = (m) => new Promise((r) => setTimeout(r, m));
const ch = spawn("/data/.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell", ["--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--remote-debugging-port=9342", "--window-size=1400,950", "about:blank"], { stdio: "ignore" });
let ws, id = 0; const c = {};
const cmd = (method, params = {}) => new Promise((ok) => { const i = ++id; c[i] = ok; ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (e) => (await cmd("Runtime.evaluate", { expression: e, awaitPromise: true, returnByValue: true })).result.value;
let u; for (let i = 0; i < 50 && !u; i++) { try { u = (await (await fetch("http://127.0.0.1:9342/json/list")).json()).find((t) => t.type == "page")?.webSocketDebuggerUrl; } catch { } await sleep(200); }
ws = new WebSocket(u); await new Promise((r) => (ws.onopen = r)); ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && c[d.id]) { c[d.id](d.result); delete c[d.id]; } };
await cmd("Emulation.setDeviceMetricsOverride", { width: 1400, height: 950, deviceScaleFactor: 1, mobile: false });
await cmd("Page.navigate", { url: U }); for (let i = 0; i < 80 && !(await ev('document.querySelectorAll("#zrodlo option").length>1')); i++) await sleep(250);
const start = await ev('[document.getElementById("zrodlo").value,document.getElementById("towar").value,document.getElementById("para").checked].join(" | ")');
await ev('document.querySelector("[data-a=analizuj]").click()'); for (let i = 0; i < 200 && !(await ev("!!S.R&&!document.querySelector('.ladow')")); i++) await sleep(250); await sleep(400);
const R = await ev("S.R"), lis = R.miejsca.filter((m) => !m.pominieta), pom = R.miejsca.filter((m) => m.pominieta);
fs.writeFileSync(Z, Buffer.from((await cmd("Page.captureScreenshot", { format: "png" })).data, "base64"));
const ok = lis.length == 5 && pom.length == 5 && (await ev('document.querySelector(".licz").innerText')).startsWith("5 miejsc");
console.log(`start: ${start}\n${R.zapisany ? "wynik zapisany (" + R.zapisano + ")" : "wynik na żywo z karty, " + R.czas_analizy_s + " s"}\nlinia: ${await ev('document.querySelector(".licz").innerText')}\nlista: ${lis.map((m) => m.nazwa + " " + Math.round(m.pew * 100) + "%").join("; ")}\npominięte: ${pom.map((m) => m.nazwa + " " + Math.round(m.pew * 100) + "%").join("; ")}\n${ok ? "OK" : "BŁĄD"} 5 miejsc + 5 pominiętych`);
ch.kill(); process.exit(ok ? 0 : 1);
