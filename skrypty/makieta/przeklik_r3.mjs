// Przeklikanie makiety R3 w chrome-headless-shell przez protokół CDP (bez bibliotek).
import {spawn} from "child_process";import fs from "fs";
const [,,URL_,ZRZ,POB]=process.argv;const H="/data/.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell";
fs.rmSync(POB,{recursive:true,force:true});fs.mkdirSync(POB,{recursive:true});
const ch=spawn(H,["--no-sandbox","--disable-gpu","--hide-scrollbars","--remote-debugging-port=9339","--window-size=1400,950","about:blank"],{stdio:"ignore"});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws,id=0;const cze={};
async function polacz(){for(let i=0;i<50;i++){try{const l=await (await fetch("http://127.0.0.1:9339/json/list")).json();const p=l.find(t=>t.type=="page");if(p)return p.webSocketDebuggerUrl}catch{}await sleep(200)}throw "brak przeglądarki"}
const cmd=(method,params={})=>new Promise((ok,zle)=>{const i=++id;cze[i]={ok,zle};ws.send(JSON.stringify({id:i,method,params}))});
const ev=async js=>{const r=await cmd("Runtime.evaluate",{expression:js,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails).slice(0,400));return r.result.value};
const klik=async(sel,opis)=>{const ok=await ev(`(()=>{const e=document.querySelector(${JSON.stringify(sel)});if(!e)return false;e.dispatchEvent(new MouseEvent("click",{bubbles:true}));return true})()`);if(!ok)throw new Error("brak elementu: "+sel+" ("+opis+")");await sleep(150)};
const wybierz=async(sel,v)=>{const ok=await ev(`(()=>{const e=document.querySelector(${JSON.stringify(sel)});if(!e)return false;e.value=${JSON.stringify(v)};return e.value==${JSON.stringify(v)}})()`);if(!ok)throw new Error("nie wybrano "+v+" w "+sel)};
const tekst=sel=>ev(`(document.querySelector(${JSON.stringify(sel)})||{}).innerText||""`);
let wyn=[];const spr=(war,opis)=>{wyn.push((war?"OK   ":"BŁĄD ")+opis);if(!war)process.exitCode=1};
const zrzut=async(n,w=1400,h=950,mob=false)=>{await cmd("Emulation.setDeviceMetricsOverride",{width:w,height:h,deviceScaleFactor:1,mobile:mob});await sleep(400);
 const r=await cmd("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(`${ZRZ}/${n}.png`,Buffer.from(r.data,"base64"));wyn.push("zrzut "+n+".png")};
try{
 ws=new WebSocket(await polacz());await new Promise(r=>ws.onopen=r);
 ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&cze[d.id]){d.error?cze[d.id].zle(new Error(d.error.message)):cze[d.id].ok(d.result);delete cze[d.id]}};
 await cmd("Page.enable");await cmd("Runtime.enable");await cmd("DOM.enable");
 await cmd("Browser.setDownloadBehavior",{behavior:"allow",downloadPath:POB});
 await cmd("Emulation.setDeviceMetricsOverride",{width:1400,height:950,deviceScaleFactor:1,mobile:false});
 await cmd("Page.navigate",{url:URL_});await sleep(1200);
 spr((await ev("document.title")).includes("makieta R3"),"tytuł zawiera „makieta R3”");
 // Ścieżka 1: auto A, „nie wiem” — pokaz
 await wybierz("#auto","A");await wybierz("#towar","nie wiem");await klik('[data-a="analizuj"]',"Analizuj");await sleep(1300);
 let l=await tekst(".licz");spr(l=="4 miejsca do sprawdzenia · zostało 4","linia: "+l);
 spr((await tekst(".lista .miejsce h3")).startsWith("1. Podłoga — środek"),"pierwsza pozycja: Podłoga — środek");
 spr(!/\bcm\b/.test(await tekst(".lista")),"opisy bez cm (P19)");
 await klik('.obok > div:nth-child(2) rect.ramka[data-id="1"]',"ramka 1 na badanym");
 spr(await ev('document.getElementById("zoom").classList.contains("on")'),"klik w ramkę otwiera powiększenie");
 spr((await tekst("#zoom .okno b")).startsWith("Podłoga — środek"),"powiększenie: Podłoga — środek");
 spr(await ev('!!document.querySelector("#zoom [data-nast]")&&!!document.querySelector("#zoom [data-o]")&&!!document.querySelector("#zoom [data-k]")'),"w powiększeniu: Do kontroli, Odrzuć, Następne miejsce (P22, P31)");
 await zrzut("makieta-r3-powiekszenie");
 await klik("#zoom [data-nast]","Następne miejsce");spr((await tekst("#zoom .okno b")).startsWith("Ściana przednia — przód"),"Następne miejsce → Ściana przednia — przód (P31)");
 await klik("#zoom [data-k]","Do kontroli w powiększeniu (ściana)");
 spr(!(await ev('document.getElementById("zoom").classList.contains("on")')),"po decyzji okno się zamyka");
 l=await tekst(".licz");spr(l.endsWith("zostało 3"),"po 1 decyzji: "+l);
 await klik('.lista [data-k="1"]',"Do kontroli podłoga");await klik('.lista [data-k="3"]',"Do kontroli ładownia tył");
 await klik('.lista [data-o="4"]',"Odrzuć bez powodu");spr(await ev('!!document.querySelector(\'.lista [data-o="4"]\')'),"odrzucenie bez powodu zablokowane");
 const powody=await ev('[...document.querySelector(\'.lista select[data-p="4"]\').options].map(o=>o.text)');spr(powody.includes("ładunek zgodny z dokumentami (sprawdzony ręcznie)"),"przy „nie wiem” powód „…z dokumentami (sprawdzony ręcznie)” (P21)");
 await wybierz('.lista select[data-p="4"]',"ładunek zgodny z dokumentami (sprawdzony ręcznie)");await klik('.lista [data-o="4"]',"Odrzuć z powodem");
 l=await tekst(".licz");spr(l=="4 miejsca do sprawdzenia · zostało 0","linia: "+l);
 await klik('[data-a="zapisz"]',"Zapisz kontrolę");await sleep(800);
 const z=await tekst(".zapis");spr(z.includes("Podłoga — środek — do kontroli")&&z.includes("odrzucone (ładunek zgodny z dokumentami (sprawdzony ręcznie))"),"zapis kontroli: linie miejsc");
 spr(await ev('(document.getElementById("zapisPng").src||"").startsWith("data:image/png")&&document.getElementById("zapisPng").naturalWidth==2000'),"obraz z ramkami PNG w zapisie, 2000 px (P32)");
 await zrzut("makieta-r3");
 await ev('document.querySelector(".zapis").scrollIntoView()');await zrzut("makieta-r3-telefon",390,1600,true);await ev("scrollTo(0,0)");await zrzut("makieta-r3-telefon-gora",390,1000,true);
 await cmd("Emulation.setDeviceMetricsOverride",{width:1400,height:950,deviceScaleFactor:1,mobile:false});
 await klik('[data-a="pobierz"]',"Pobierz zapis");await sleep(2500);
 const pl=fs.readdirSync(POB);spr(pl.includes("zapis-kontroli.json")&&pl.includes("zapis-kontroli.png"),"pobrane: "+pl.join(", "));
 if(pl.includes("zapis-kontroli.json")){const j=JSON.parse(fs.readFileSync(POB+"/zapis-kontroli.json"));spr(j.miejsca.length==4&&j.obraz_z_ramkami=="zapis-kontroli.png"&&j.pominiete_towar_zgodny==0,"JSON: 4 miejsca, obraz_z_ramkami, pominięte 0")}
 if(pl.includes("zapis-kontroli.png"))fs.copyFileSync(POB+"/zapis-kontroli.png",ZRZ+"/makieta-r3-zapis-obraz.png");
 // Ścieżka 2: pusta naczepa (P27)
 await klik('[data-a="nowe"]',"Nowe auto");await wybierz("#auto","A");await wybierz("#towar","pusta naczepa");await klik('[data-a="analizuj"]',"Analizuj");await sleep(1300);
 const p1=await tekst(".lista .miejsce");spr(p1.startsWith("1. Ładownia — przód")&&p1.includes("alarm z reguły: pusta naczepa")&&p1.includes("57%"),"pusta naczepa: na górze, flaga reguły, pewność 57% z wyniku (P27)");
 spr((await tekst(".obok")).includes("obraz poglądowy"),"pusta naczepa: podpis „obraz poglądowy” przy badanym (P27)");
 await zrzut("makieta-r3-pusta");
 // Ścieżka 3: auto B, sprzęt i AGD — pominięte, wzorzec niepewny, wskazanie, plik (P28–P30)
 await klik('[data-a="nowe"]',"Nowe auto");await wybierz("#auto","B");await wybierz("#towar","sprzęt i AGD");await klik('[data-a="analizuj"]',"Analizuj");await sleep(1300);
 spr((await tekst(".ostrz")).includes("Wzorzec niepewny — wskaż wzorzec"),"ostrzeżenie o niepewnym wzorcu");
 spr((await tekst(".info")).includes("pominięto 1 różnicę"),"komunikat: „pominięto 1 różnicę” (P30)");
 spr(await ev('[odmR(1),odmR(2),odmR(4),odmR(5),odmR(12),odmR(22)].join(",")')=="różnicę,różnice,różnice,różnic,różnic,różnice","odmiana różnic 1/2/4/5/12/22 (P30)");
 l=await tekst(".licz");const n0=l;
 await klik('[data-a="pom"]',"Pokaż pominięte");await klik('.lista .miejsce [data-k="4"]',"Do kontroli na pominiętej");
 l=await tekst(".licz");spr(n0=="3 miejsca do sprawdzenia · zostało 3"&&l=="4 miejsca do sprawdzenia · zostało 3","zlecona pominięta liczy się do miejsc: "+n0+" → "+l+" (P29)");
 await wybierz("#wskaz","naczepa skrzyniowa 2-osiowa, 12 m");await klik('[data-a="wskaz"]',"Przelicz z tym wzorcem");
 const hd=await tekst("header"),ob=await tekst(".obok");spr(hd.includes("wskazany ręcznie")&&ob.includes("wskazany ręcznie")&&ob.includes("obraz poglądowy"),"po wskazaniu: „wskazany ręcznie” i „obraz poglądowy” (P28)");
 spr(await ev('document.querySelector(".obok svg").innerHTML.includes(\'cx="660"\')'),"obraz wzorca zmienił się z typem (skrzyniowa, 2 osie) (P28)");
 spr((await tekst(".licz"))=="4 miejsca do sprawdzenia · zostało 4"&&(await tekst(".info")).includes("pominięto 1 różnicę")&&(await tekst(".lista")).includes("Rama — tył"),"przeliczenie po wskazaniu: nowa ramka Rama — tył, "+await tekst(".licz")+" + 1 pominięta (P24)");spr(await ev("[1,2,5,12,22].map(n=>n+\" \"+odm(n)).join(\", \")")=="1 miejsce, 2 miejsca, 5 miejsc, 12 miejsc, 22 miejsca","odmiana miejsc (P25)");
 await zrzut("makieta-r3-wskazany");
 // plik wzorca: klik otwiera wybór pliku; plik podajemy przez CDP
 await cmd("Page.setInterceptFileChooserDialog",{enabled:true});let wyb=false;const st=ws.onmessage;ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.method=="Page.fileChooserOpened")wyb=true;st(m)};
 await ev('(()=>{S.niepewny=true;S.wskazany=null;S.wz=AUTA.B.wzorzec;odswiez()})()'); // wracamy do stanu „niepewny”, żeby był przycisk
 await cmd("Runtime.evaluate",{expression:'document.querySelector(\'[data-a="plik"]\').click()',userGesture:true});await sleep(500);
 spr(wyb,"„Wgraj plik wzorca” otwiera wybór pliku (P28)");
 const doc=await cmd("DOM.getDocument");const nd=await cmd("DOM.querySelector",{nodeId:doc.root.nodeId,selector:"#plikWz"});
 fs.writeFileSync("/tmp/r3/wzorzec-plandeka.bmp","BM");await cmd("DOM.setFileInputFiles",{nodeId:nd.nodeId,files:["/tmp/r3/wzorzec-plandeka.bmp"]});await sleep(400);
 spr((await tekst("header")).includes("plik wzorzec-plandeka.bmp (wskazany ręcznie)"),"po wyborze pliku: podpis „plik … (wskazany ręcznie)”");
 // Ścieżka 4: pominięta niezlecona w zapisie (P29)
 await klik('[data-a="nowe"]',"Nowe auto");await wybierz("#auto","A");await wybierz("#towar","sprzęt i AGD");await klik('[data-a="analizuj"]',"Analizuj");await sleep(1300);
 for(const k of [1,2,3])await klik(`.lista [data-k="${k}"]`,"Do kontroli "+k);
 await klik('[data-a="zapisz"]',"Zapisz");await sleep(500);spr((await tekst(".zapis")).includes("pominięte (towar zgodny ze zgłoszeniem): 1"),"zapis: „pominięte (towar zgodny ze zgłoszeniem): 1” (P29)");
 fs.rmSync(POB+"/zapis-kontroli.json",{force:true});await klik('[data-a="pobierz"]',"Pobierz");await sleep(2000);
 if(fs.existsSync(POB+"/zapis-kontroli.json")){const j=JSON.parse(fs.readFileSync(POB+"/zapis-kontroli.json"));spr(j.pominiete_towar_zgodny==1&&j.pominiete.length==1,"JSON: pominiete_towar_zgodny = 1 (P29)")}else spr(false,"JSON ścieżki 4 nie pobrany");
}catch(e){wyn.push("BŁĄD SKRYPTU "+e.message);process.exitCode=1}
console.log(wyn.join("\n"));ch.kill();process.exit();
