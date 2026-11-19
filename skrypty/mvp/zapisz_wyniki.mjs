// Zapisuje odpowiedzi usługi na karcie (OMEN) do aplikacja/zapisane/ — tryb „wynik zapisany” na ksefbot.pl,
// gdy karta albo sieć nie odpowiada. Użycie: node skrypty/mvp/zapisz_wyniki.mjs http://<omen>:8770 <wzorzec.bmp do wgrania>
import fs from "node:fs";
import path from "node:path";
const [USL, PLIK_WZ] = process.argv.slice(2);
const KAT = path.join(path.dirname(new URL(import.meta.url).pathname), "../../aplikacja/zapisane");
fs.mkdirSync(KAT, { recursive: true });
const WARIANTY = JSON.parse(process.env.WARIANTY || "[]"); // [[badany, wzorzec, towar], …]; wzorzec "plik" = wgranie PLIK_WZ
const j = async (u, o) => { const r = await fetch(USL + u, o); const t = await r.json(); if (!r.ok) throw new Error(u + ": " + t.blad); return t; };
const png = async (t) => { const p = path.join(KAT, t + ".png"); if (!fs.existsSync(p)) fs.writeFileSync(p, Buffer.from(await (await fetch(`${USL}/obraz/${t}.png`)).arrayBuffer())); };
const przyklady = await j("/przyklady");
for (const k of przyklady.katalog) await png(k.obraz);
const analizy = {};
for (const [b, w, t] of WARIANTY) {
  let wz = w;
  if (w === "plik") {
    const r = await fetch(USL + "/wgraj", { method: "POST", headers: { "content-type": "application/octet-stream", "x-nazwa": path.basename(PLIK_WZ) }, body: fs.readFileSync(PLIK_WZ) });
    wz = (await r.json()).id;
  }
  const a = await j("/analiza", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ badany: b, wzorzec: wz, towar: t }) });
  await png(a.obraz_badany); await png(a.obraz_wzorca);
  const nazwa = `analiza-${Object.keys(analizy).length + 1}.json`;
  fs.writeFileSync(path.join(KAT, nazwa), JSON.stringify(a, null, 1));
  analizy[`${b}|${w === "plik" ? "plik:zapisany" : w}|${t}`] = nazwa;
  console.log(`${b} | ${w} | ${t} → ${a.tryb}, ${a.miejsca.length} miejsc: ${a.miejsca.map((m) => `${m.nazwa} ${Math.round(m.pew * 100)}%${m.pominieta ? " (pominięta)" : ""}${m.regula ? " (reguła)" : ""}`).join("; ")}`);
}
fs.writeFileSync(path.join(KAT, "indeks.json"), JSON.stringify({ zapisano: new Date().toISOString(), przyklady, analizy }, null, 1));
console.log("zapisano", Object.keys(analizy).length, "wariantów do", KAT);
