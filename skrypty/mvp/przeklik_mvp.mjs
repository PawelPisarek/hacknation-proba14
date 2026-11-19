// Przeklik MVP na adresie produkcyjnym (chrome-headless-shell, CDP, bez bibliotek).
// node skrypty/mvp/przeklik_mvp.mjs <URL> <katalog zrzutów> <katalog pobrań> <badany.bmp> <wzorzec.bmp>
// Zmienne: DEMO (przykład pokazu, domyślnie test/d028_B, para), PUSTA (przykład pustej naczepy, tryb bez pary),
// TOWAR_POM (przykład do „Pokaż pominięte”, tryb bez pary), NIEPEWNY (plik .bmp bez pary, dla którego dobór wzorca jest niepewny; puste = pomiń).
import { spawn } from "child_process"; import fs from "fs";
const [, , URL_, ZRZ, POB, BMP_B, BMP_W] = process.argv;
const DEMO = process.env.DEMO || "test/d028_B", PUSTA = process.env.PUSTA || "test/c001_B", TOWAR_POM = process.env.TOWAR_POM || "test/c001_B", NIEPEWNY = process.env.NIEPEWNY || "";
const H = "/data/.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell";
fs.rmSync(POB, { recursive: true, force: true }); fs.mkdirSync(POB, { recursive: true }); fs.mkdirSync(ZRZ, { recursive: true });
const ch = spawn(H, ["--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--remote-debugging-port=9341", "--window-size=1400,950", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms)); let ws, id = 0; const cze = {}; let wyb = false;
async function polacz() { for (let i = 0; i < 50; i++) { try { const l = await (await fetch("http://127.0.0.1:9341/json/list")).json(); const p = l.find((t) => t.type == "page"); if (p) return p.webSocketDebuggerUrl; } catch { } await sleep(200); } throw "brak przeglądarki"; }
const cmd = (method, params = {}) => new Promise((ok, zle) => { const i = ++id; cze[i] = { ok, zle }; ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (js) => { const r = await cmd("Runtime.evaluate", { expression: js, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 400)); return r.result.value; };
const klik = async (sel, opis) => { const ok = await ev(`(()=>{const e=document.querySelector(${JSON.stringify(sel)});if(!e)return false;e.dispatchEvent(new MouseEvent("click",{bubbles:true}));return true})()`); if (!ok) throw new Error("brak elementu: " + sel + " (" + opis + ")"); await sleep(200); };
const wybierz = async (sel, v) => { const ok = await ev(`(()=>{const e=document.querySelector(${JSON.stringify(sel)});if(!e)return false;e.value=${JSON.stringify(v)};e.dispatchEvent(new Event("change",{bubbles:true}));return e.value==${JSON.stringify(v)}})()`); if (!ok) throw new Error("nie wybrano " + v + " w " + sel); };
const tekst = (sel) => ev(`(document.querySelector(${JSON.stringify(sel)})||{}).innerText||""`);
const czekaj = async (js, ms = 120000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (await ev(js)) return Date.now() - t0; await sleep(250); } throw new Error("nie doczekano: " + js); };
const wynik = () => czekaj('!document.querySelector(".ladow")').then(() => sleep(300));
const wyn = []; const spr = (war, opis) => { wyn.push((war ? "OK   " : "BŁĄD ") + opis); if (!war) process.exitCode = 1; };
const zrzut = async (n, w = 1400, h = 950, mob = false) => { await cmd("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: mob }); await sleep(600);
  const r = await cmd("Page.captureScreenshot", { format: "png" }); fs.writeFileSync(`${ZRZ}/${n}.png`, Buffer.from(r.data, "base64")); wyn.push("zrzut " + n + ".png"); };
const desk = () => cmd("Emulation.setDeviceMetricsOverride", { width: 1400, height: 950, deviceScaleFactor: 1, mobile: false });
const odm = (n) => { const d = n % 10, s = n % 100; return n == 1 ? "miejsce" : (d >= 2 && d <= 4 && (s < 12 || s > 14)) ? "miejsca" : "miejsc"; };
async function analizuj(przyklad, towar, para) {
  await wybierz("#zrodlo", "przyklad:" + przyklad); await wybierz("#towar", towar);
  await ev(`document.getElementById("para").checked=${para}`); await klik('[data-a="analizuj"]', "Analizuj"); const t0 = Date.now(); await wynik();
  const b = await ev('S.blad'); if (b) throw new Error(b); return Date.now() - t0;
}
const nowe = () => klik('[data-a="nowe"]', "Nowe auto");
try {
  ws = new WebSocket(await polacz()); await new Promise((r) => (ws.onopen = r));
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.method == "Page.fileChooserOpened") wyb = true; if (d.id && cze[d.id]) { d.error ? cze[d.id].zle(new Error(d.error.message)) : cze[d.id].ok(d.result); delete cze[d.id]; } };
  await cmd("Page.enable"); await cmd("Runtime.enable"); await cmd("DOM.enable");
  await cmd("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: POB }); await desk();
  await cmd("Page.navigate", { url: URL_ }); await czekaj('document.querySelectorAll("#zrodlo option").length>1', 20000);
  const zap = await ev("!!K.zapisany"); wyn.push(zap ? "UWAGA: usługa na karcie nie odpowiada — tryb „wynik zapisany”" : "usługa na karcie odpowiada (wynik na żywo)");
  // ---------- Ścieżka 1: pokaz (P3, P7, P10, P12–P14, P18, P19, P21, P22, P25, P26, P31, P32, P35)
  const ms = await analizuj(DEMO, "nie wiem", true);
  const R = await ev("S.R"); const n = R.miejsca.length;
  wyn.push(`pokaz: ${DEMO}, para, „nie wiem” → ${n} ${odm(n)}, ${R.metoda}, karta ${R.karta}, czas karty ${R.czas_analizy_s} s, od kliknięcia ${ms} ms${R.zapisany ? " (wynik zapisany)" : ""}`);
  spr(n >= 3, `pokaz: co najmniej 3 miejsca (jest ${n}): ` + R.miejsca.map((m) => `${m.nazwa} ${Math.round(m.pew * 100)}%`).join("; "));
  let l = await tekst(".licz"); spr(l == `${n} ${odm(n)} do sprawdzenia · zostało ${n}`, "linia: " + l + " (P25)");
  const pew = await ev('[...document.querySelectorAll(".lista .pew")].map(e=>parseInt(e.innerText))'); spr(pew.every((v, i) => i == 0 || pew[i - 1] >= v), "lista od najpewniejszego: " + pew.join(", ") + " (P7)");
  const nazwy = await ev('[...document.querySelectorAll(".lista .miejsce h3")].map(e=>e.innerText)'); spr(nazwy.every((t) => / — /.test(t)), "nazwy = strefa — położenie: " + nazwy.join(" | ") + " (P18)");
  spr(!/\b(cm|mm|px)\b/.test(await tekst(".lista")), "opisy bez miar (P19)");
  spr(!/\d+[,.]\d+\s*s\b|czas analizy/i.test(await tekst("#app")), "bez czasu analizy na ekranie (P26)");
  spr(await ev('document.querySelectorAll(".obok svg").length==2&&document.querySelectorAll(".obok svg image").length==2'), "badany obok wzorca, oba obrazy z karty (P12)");
  const img = await ev('Promise.all([...document.querySelectorAll(".obok svg image")].map(i=>fetch(i.getAttribute("href")).then(r=>r.status+" "+r.headers.get("content-type"))))'); spr(img.every((s) => s.startsWith("200 image/png")), "obrazy: " + img.join(", "));
  const fs16 = await ev('(()=>{const t=document.querySelector(".obok > div:nth-child(2) text.etyk");const r=t.getBoundingClientRect();return Math.round(r.height)})()'); spr(fs16 >= 16, `numer ramki ${fs16} px wysokości (≥ 16, P25)`);
  await klik('.obok > div:nth-child(2) rect.ramka[data-id="1"]', "ramka 1 na badanym");
  spr(await ev('document.getElementById("zoom").classList.contains("on")'), "klik w ramkę otwiera powiększenie (P10)");
  spr(await ev('document.querySelectorAll("#zoom svg").length==2&&!!document.querySelector("#zoom svg:not(.x) rect.ramka.odp")'), "powiększenie: wzorzec i badany, odpowiednik na wzorcu (P10, P12)");
  spr(await ev('!!document.querySelector("#zoom [data-nast]")&&!!document.querySelector("#zoom [data-o]")&&!!document.querySelector("#zoom [data-k]")'), "w powiększeniu: Do kontroli, Odrzuć z powodem, Następne miejsce (P22, P31)");
  await zrzut("mvp-powiekszenie");
  const b1 = await tekst("#zoom .okno b"); await klik("#zoom [data-nast]", "Następne miejsce"); const b2 = await tekst("#zoom .okno b");
  spr(b2 && b2 != b1 && b2.startsWith(R.miejsca[1].nazwa), `Następne miejsce: ${b1.split(" — pew")[0]} → ${b2} (P31)`);
  await klik("#zoom [data-k]", "Do kontroli w powiększeniu");
  spr(!(await ev('document.getElementById("zoom").classList.contains("on")')), "po decyzji w powiększeniu okno się zamyka");
  l = await tekst(".licz"); spr(l.endsWith(`zostało ${n - 1}`), "po 1 decyzji: " + l + " (A9)");
  // P35: przejście po nierozstrzygniętych; po ostatnim zamyka okno
  await klik(`.lista [data-z="${R.miejsca[n - 1].id}"]`, "Powiększ ostatnie");
  await klik("#zoom [data-nast]", "Następne z ostatniego"); const b3 = await tekst("#zoom .okno b");
  spr(b3.startsWith(R.miejsca[0].nazwa) && !b3.startsWith(R.miejsca[1].nazwa), `z ostatniego „Następne miejsce” → pierwsze nierozstrzygnięte (${b3.split(" — pew")[0]}), pomija rozstrzygnięte (P35)`);
  await klik("[data-zamknij]", "Zamknij");
  for (const m of R.miejsca.slice(0, n - 1)) if (!(await ev(`!!S.stan[${m.id}]`))) await klik(`.lista [data-k="${m.id}"]`, "Do kontroli " + m.nazwa);
  const ost = R.miejsca[n - 1];
  await klik(`.lista [data-o="${ost.id}"]`, "Odrzuć bez powodu"); spr(await ev(`!!document.querySelector('.lista [data-o="${ost.id}"]')`), "odrzucenie bez powodu zablokowane (P3)");
  const powody = await ev(`[...document.querySelector('.lista select[data-p="${ost.id}"]').options].map(o=>o.text)`); spr(powody.includes("ładunek zgodny z dokumentami (sprawdzony ręcznie)"), "przy „nie wiem” powód „…z dokumentami (sprawdzony ręcznie)” (P21)");
  await wybierz(`.lista select[data-p="${ost.id}"]`, "znany element konstrukcji"); await klik(`.lista [data-o="${ost.id}"]`, "Odrzuć z powodem");
  l = await tekst(".licz"); spr(l == `${n} ${odm(n)} do sprawdzenia · zostało 0`, "linia: " + l);
  await klik('[data-a="zapisz"]', "Zapisz kontrolę"); await czekaj('(document.getElementById("zapisPng")||{}).naturalWidth>0', 15000);
  const z = await tekst(".zapis"); spr(z.includes(`${R.miejsca[0].nazwa} — do kontroli: ${R.miejsca[0].przedmiot}`) && z.includes("odrzucone (znany element konstrukcji)"), "zapis kontroli: miejsce i przedmiot, odrzucone z powodem (A8)");
  spr(await ev('document.getElementById("zapisPng").src.startsWith("data:image/png")&&document.getElementById("zapisPng").naturalWidth>=2000'), "obraz z ramkami PNG w zapisie (P32)");
  await zrzut("mvp-pokaz-koniec");
  await ev('document.querySelector(".zapis").scrollIntoView()'); await zrzut("mvp-telefon", 390, 1600, true); await ev("scrollTo(0,0)"); await zrzut("mvp-telefon-gora", 390, 1000, true); await desk();
  await klik('[data-a="pobierz"]', "Pobierz zapis"); await sleep(3000);
  const pl = fs.readdirSync(POB); spr(pl.includes("zapis-kontroli.json") && pl.includes("zapis-kontroli.png"), "pobrane: " + pl.join(", ") + " (P32)");
  if (pl.includes("zapis-kontroli.json")) { const j = JSON.parse(fs.readFileSync(POB + "/zapis-kontroli.json")); spr(j.miejsca.length == n && j.obraz_z_ramkami == "zapis-kontroli.png" && j.miejsca.every((m) => m.przedmiot_kontroli && m.decyzja) && j.czas_analizy_s != null, `JSON: ${j.miejsca.length} miejsc z przedmiotem i decyzją, obraz_z_ramkami, czas_analizy_s=${j.czas_analizy_s} tylko w JSON`); }
  if (pl.includes("zapis-kontroli.png")) fs.copyFileSync(POB + "/zapis-kontroli.png", ZRZ + "/mvp-zapis-obraz.png");
  // ---------- Ścieżka 2: pusta naczepa (P27, P34)
  await nowe(); await analizuj(PUSTA, "pusta naczepa", false);
  const RP = await ev("S.R"), lad = RP.miejsca.filter((m) => m.strefa == "Ładownia");
  spr(lad.length > 0 && lad.every((m) => m.regula), `pusta naczepa: każde z ${lad.length} miejsc w ładowni z flagą reguły (P34)`);
  spr((await tekst(".lista h2")).startsWith("Najpierw alarmy z reguły"), "nagłówek listy: " + (await tekst(".lista h2")) + " (P34)");
  const pierw = await tekst(".lista .miejsce"); spr(pierw.includes("alarm z reguły: pusta naczepa"), "pusta naczepa: alarm z reguły na górze listy (P27)");
  spr(new Set(lad.map((m) => m.pew)).size > 1 || lad.length == 1, "pewność z wyniku (różne wartości): " + lad.map((m) => Math.round(m.pew * 100) + "%").join(", ") + " (P27)");
  await zrzut("mvp-pusta");
  for (const m of RP.miejsca.filter((m) => !m.pominieta)) await klik(`.lista [data-k="${m.id}"]`, "Do kontroli");
  await klik('[data-a="zapisz"]', "Zapisz"); await sleep(500); const zp = await tekst(".zapis");
  spr(zp.includes(`${lad[0].nazwa} (⚑ alarm z reguły: pusta naczepa) — do kontroli`) && !/pusta wg zgłoszenia/.test(zp), "zapis: ten sam tekst flagi „alarm z reguły: pusta naczepa” (P27)");
  // ---------- Ścieżka 3: rodzaj towaru, pominięte (P15, P17, P23, P29, P30)
  await nowe(); spr((await ev('[...document.querySelectorAll("#towar option")].map(o=>o.text)')).join("|") == "nie wiem|sprzęt i AGD|odzież i tekstylia|żywność i napoje|materiały budowlane|inne|pusta naczepa", "lista rodzajów towaru (P17)");
  await analizuj(TOWAR_POM, "sprzęt i AGD", false);
  const RT = await ev("S.R"), np = RT.miejsca.filter((m) => m.pominieta).length;
  const info = await tekst(".info"); spr(np > 0 && info.includes(`pominięto ${np} `) && info.includes("Pokaż pominięte"), `pominięte: ${np} — „${info.split(". ")[1] || info}” (P23, P30)`);
  const nVis = RT.miejsca.length - np; l = await tekst(".licz"); spr(l.startsWith(`${nVis} ${odm(nVis)}`), "linia bez pominiętych: " + l);
  await klik('[data-a="pom"]', "Pokaż pominięte"); spr((await ev('document.querySelectorAll(".lista .pomb").length')) == np, "Pokaż pominięte: na liście z oznaczeniem");
  await zrzut("mvp-pominiete");
  const p1 = RT.miejsca.find((m) => m.pominieta); await klik(`.lista [data-k="${p1.id}"]`, "Do kontroli pominiętej");
  l = await tekst(".licz"); spr(l.startsWith(`${nVis + 1} ${odm(nVis + 1)}`), "zlecona pominięta liczy się: " + l + " (P23)");
  for (const m of RT.miejsca.filter((m) => !m.pominieta)) await klik(`.lista [data-k="${m.id}"]`, "Do kontroli");
  await klik('[data-a="zapisz"]', "Zapisz"); await sleep(500);
  spr((await tekst(".zapis")).includes(`pominięte (towar zgodny ze zgłoszeniem): ${np - 1}`), `zapis: „pominięte (towar zgodny ze zgłoszeniem): ${np - 1}” (P29)`);
  // ---------- Ścieżka 4: własny plik badanego + plik wzorca (P28, P36)
  await nowe(); await wybierz("#zrodlo", "plik"); await wybierz("#towar", "nie wiem");
  const doc = await cmd("DOM.getDocument");
  for (const [sel, f] of [["#plikB", BMP_B], ["#plikW", BMP_W]]) { const nd = await cmd("DOM.querySelector", { nodeId: doc.root.nodeId, selector: sel }); await cmd("DOM.setFileInputFiles", { nodeId: nd.nodeId, files: [f] }); }
  await klik('[data-a="analizuj"]', "Analizuj pliki"); await wynik(); await czekaj("!!S.R&&S.ekran=='glowny'||!!S.blad", 60000);
  const RF = await ev("S.R"); spr(RF && RF.tryb == "plik wzorca", `wgrane pliki: tryb ${RF && RF.tryb}, ${RF && RF.miejsca.length} miejsc${RF && RF.zapisany ? " (wynik zapisany)" : ""}`);
  spr((await tekst("header .wz")).includes("(wskazany ręcznie)"), "podpis: " + (await tekst("header .wz")) + " (P28)");
  for (const m of RF.miejsca) await klik(`.lista [data-k="${m.id}"]`, "Do kontroli");
  await klik('[data-a="zapisz"]', "Zapisz"); await sleep(500);
  spr((await tekst(".zapis")).includes(`wzorzec: plik ${RF.plik_wzorca} (wskazany ręcznie)`), `zapis: „wzorzec: plik ${RF.plik_wzorca} (wskazany ręcznie)” (P36)`);
  await zrzut("mvp-wzorzec-plik");
  // ---------- Ścieżka 5: wzorzec niepewny → wskazanie z katalogu, „Wgraj plik wzorca” (P8, P9, P16, P24, P28)
  if (NIEPEWNY) {
    await nowe(); await wybierz("#zrodlo", "plik"); await wybierz("#towar", "nie wiem"); const d2 = await cmd("DOM.getDocument");
    const nb = await cmd("DOM.querySelector", { nodeId: d2.root.nodeId, selector: "#plikB" }); await cmd("DOM.setFileInputFiles", { nodeId: nb.nodeId, files: [NIEPEWNY] });
    await klik('[data-a="analizuj"]', "Analizuj plik bez wzorca"); await wynik(); const RN = await ev("S.R");
    spr(RN.niepewny && (await tekst(".ostrz")).includes("Wzorzec niepewny — wskaż wzorzec"), `bez pary: dobrany ${RN.typ}, pewność doboru ${RN.pewnosc_doboru} → flaga „wzorzec niepewny” (P9, P16)`);
    spr(RN.miejsca.every((m) => Math.abs(m.pew - Math.max(0.5, Math.round(m.pew_wynik * 0.8 * 100) / 100)) < 0.011), "pewność ×0,8, min. 50% (P24)");
    await zrzut("mvp-niepewny");
    await cmd("Page.setInterceptFileChooserDialog", { enabled: true }); wyb = false; await klik('[data-a="plik"]', "Wgraj plik wzorca"); await sleep(500);
    spr(wyb, "„Wgraj plik wzorca” otwiera wybór pliku (P28)"); await cmd("Page.setInterceptFileChooserDialog", { enabled: false });
    const inny = (await ev("K.katalog.map(k=>k.typ)")).find((t) => t != RN.typ); await wybierz("#wskaz", inny); await klik('[data-a="wskaz"]', "Przelicz z tym wzorcem"); await wynik();
    const RW = await ev("S.R"); spr(RW.wskazany_recznie && RW.typ == inny && (await tekst("header .wz")).includes("wskazany ręcznie"), `wskazany ręcznie typ ${inny}: przeliczone, ${RW.miejsca.length} miejsc (P24, P28)`);
    await zrzut("mvp-wskazany");
  } else wyn.push("pominięto ścieżkę „wzorzec niepewny” (brak przykładu z niską pewnością doboru)");
} catch (e) { spr(false, "PRZERWANE: " + (e.message || e)); }
finally { console.log(wyn.join("\n")); const ok = wyn.filter((w) => w.startsWith("OK")).length, bl = wyn.filter((w) => w.startsWith("BŁĄD")).length; console.log(`\nWYNIK: ${ok} OK, ${bl} błędów`); ch.kill(); process.exit(); }
