// Makieta: udawane dane, bez backendu. Sztuczny obraz RTG naczepy z boku (SVG, skala szarości).
const DANE={
  auto:"Ciągnik + naczepa plandeka, nr rej. XX 0000 (dane udawane)",
  wzorzec:"wzorzec dobrany: typ naczepa plandeka 3-osiowa, 13,6 m (podobieństwo 0,93)",
  miejsca:[
    {id:1,nazwa:"Podwójna podłoga — środek naczepy",pew:0.91,box:{x:395,y:246,w:230,h:42},
     roznica:"Pod podłogą dodatkowa warstwa ok. 12 cm na długości ok. 2,3 m; we wzorcu podłoga pojedyncza.",
     przedmiot:"podłoga naczepy między 1. a 2. paletą"},
    {id:2,nazwa:"Ściana przy kabinie",pew:0.78,box:{x:180,y:96,w:48,h:138},
     roznica:"Przednia ściana grubsza (ok. 18 cm zamiast 6 cm), wewnątrz jednolity gęsty kształt.",
     przedmiot:"przednia ściana skrzyni ładunkowej"},
    {id:3,nazwa:"W ładunku — paleta 5",pew:0.54,box:{x:683,y:176,w:74,h:70},
     roznica:"Gęstszy prostokątny obiekt w środku palety; we wzorcu brak (ładunek inny, ostrożnie).",
     przedmiot:"paleta nr 5 (licząc od kabiny)"}
  ],
  powody:["znany element konstrukcji","ładunek zgodny z deklaracją","artefakt obrazu (szum, krawędź)","inny typ naczepy niż wzorzec","inne"]
};
DANE.miejsca.sort((a,b)=>b.pew-a.pew);
const STAN={}; let AKT=DANE.miejsca[0].id;

function rysuj(anomalie){ // zwraca zawartość SVG (bez ramek)
  let s=`<defs><filter id="szum"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .18 0"/><feComposite in2="SourceGraphic" operator="in"/></filter></defs>
  <rect width="1000" height="360" fill="#ececec"/>
  <g fill="#9a9a9a" stroke="#555" stroke-width="2">
   <path d="M20 260 L20 120 Q22 80 60 75 L150 70 L170 90 L170 260 Z" fill="#8a8a8a"/>
   <rect x="35" y="95" width="60" height="55" fill="#d8d8d8"/>
   <rect x="190" y="60" width="790" height="200" fill="#dcdcdc"/>
   <rect x="190" y="60" width="8" height="200" fill="#8f8f8f"/>
   <rect x="972" y="60" width="8" height="200" fill="#8f8f8f"/>
   <rect x="190" y="258" width="790" height="10" fill="#7a7a7a"/>
   <rect x="200" y="272" width="770" height="14" fill="#6a6a6a"/>
   <rect x="20" y="262" width="150" height="14" fill="#6a6a6a"/>`;
  for(let x=230;x<970;x+=45) s+=`<rect x="${x}" y="268" width="6" height="18" fill="#5a5a5a" stroke="none"/>`; // żebra ramy
  for(let x=220;x<960;x+=60) s+=`<rect x="${x}" y="62" width="4" height="196" fill="#c4c4c4" stroke="none"/>`; // słupki plandeki
  const pal=[[250,"#b5b5b5"],[365,"#aaaaaa"],[480,"#b0b0b0"],[595,"#a8a8a8"],[690,"#b3b3b3"],[805,"#adadad"]];
  pal.forEach(([x,c])=>{s+=`<rect x="${x}" y="150" width="${x==690?85:100}" height="106" fill="${c}"/><rect x="${x}" y="246" width="${x==690?85:100}" height="10" fill="#777"/>`});
  [70,140,780,840,900].forEach(x=>s+=`<circle cx="${x}" cy="305" r="28" fill="#4a4a4a"/><circle cx="${x}" cy="305" r="10" fill="#999"/>`);
  s+=`</g>`;
  if(anomalie){
    s+=`<rect x="410" y="268" width="200" height="10" fill="#555" opacity=".9"/><rect x="420" y="270" width="180" height="6" fill="#3a3a3a" opacity=".7"/>`;
    s+=`<rect x="198" y="110" width="20" height="112" fill="#6b6b6b"/><rect x="202" y="125" width="12" height="80" fill="#404040" opacity=".8"/>`;
    s+=`<rect x="702" y="192" width="38" height="40" fill="#555" opacity=".85"/>`;
  }
  s+=`<rect width="1000" height="360" filter="url(#szum)"/>`;
  return s;
}
function svg(anomalie,ramki,viewBox){
  let r="";
  if(ramki) DANE.miejsca.forEach(m=>{const b=m.box,st=STAN[m.id];
    r+=`<rect class="ramka ${m.id==AKT?'akt':''} ${st?st.typ:''}" data-id="${m.id}" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="4"/><text class="etyk" x="${b.x+4}" y="${b.y-6}">${m.id}</text>`});
  return `<svg class="rtg" viewBox="${viewBox||'0 0 1000 360'}" role="img" aria-label="Sztuczny obraz RTG naczepy z boku">${rysuj(anomalie)}${r}</svg>`;
}
function vbMiejsca(m,pad=40){const b=m.box;return `${b.x-pad} ${b.y-pad} ${b.w+2*pad} ${b.h+2*pad}`}
function pozostalo(){return DANE.miejsca.filter(m=>!STAN[m.id]).length}
function liczLinia(){const n=DANE.miejsca.length,p=pozostalo();return `${n} miejsca do sprawdzenia`+(p<n?` · zostało ${p}`:"")}
function kartaMiejsca(m){const st=STAN[m.id];
  return `<div class="miejsce ${m.id==AKT?'akt':''}" data-id="${m.id}">
  <h3>${m.id}. ${m.nazwa}</h3><p>${m.roznica}</p><p>Pewność: <span class="pew">${Math.round(m.pew*100)}%</span></p>
  ${st?`<div class="stan ${st.typ}">${st.typ=='zlec'?'✔ Zlecono kontrolę: '+m.przedmiot:'✖ Odrzucono: '+st.powod}</div>`:
  `<div class="btns"><button class="kontrola" data-k="${m.id}">Do kontroli</button>
   <select data-p="${m.id}" aria-label="Powód odrzucenia"><option value="">Powód odrzucenia…</option>${DANE.powody.map(p=>`<option>${p}</option>`).join("")}</select>
   <button class="odrzuc" data-o="${m.id}">Odrzuć</button><button data-z="${m.id}">Powiększ</button></div>`}</div>`}
function zapis(){const z=DANE.miejsca.filter(m=>STAN[m.id]);if(!z.length)return"";
  return `<div class="zapis"><b>Zapis kontroli</b><ul>${z.map(m=>`<li>${m.nazwa} — ${STAN[m.id].typ=='zlec'?'do kontroli: '+m.przedmiot:'odrzucone ('+STAN[m.id].powod+')'}</li>`).join("")}</ul></div>`}
function naglowek(tytul){return `<header><h1>${tytul}</h1><span class="licz" id="licz">${liczLinia()}</span><span class="wzorzec">${DANE.wzorzec}</span><span class="meta">${DANE.auto}</span></header>`}
function powieksz(id,zWzorcem){const m=DANE.miejsca.find(x=>x.id==id);AKT=id;
  let z=document.getElementById("zoom");if(!z){z=document.createElement("div");z.id="zoom";document.body.appendChild(z);z.onclick=e=>{if(e.target==z||e.target.dataset.zamknij!==undefined)z.classList.remove("on")}}
  z.innerHTML=`<div class="okno"><b>${m.id}. ${m.nazwa}</b> — pewność ${Math.round(m.pew*100)}%<div class="obrazy">
   ${zWzorcem?`<div><b>Wzorzec (dobrany)</b>${svg(false,false,vbMiejsca(m))}</div>`:""}<div><b>Badane auto</b>${svg(true,false,vbMiejsca(m))}</div></div>
   <p>${m.roznica}</p><button data-zamknij>Zamknij</button></div>`;z.classList.add("on");if(window.odswiez)odswiez()}
// delegacja zdarzeń wspólna dla wariantów
document.addEventListener("click",e=>{const t=e.target,d=t.dataset;
  if(d.k){STAN[d.k]={typ:"zlec"};nastepny();return odswiez()}
  if(d.o){const s=document.querySelector(`select[data-p="${d.o}"]`);if(!s.value){s.focus();s.style.borderColor="#d11";return}
    STAN[d.o]={typ:"odrz",powod:s.value};nastepny();return odswiez()}
  if(d.z)return powieksz(+d.z,window.ZOOM_WZORZEC);
  if(t.tagName=="SELECT"||t.tagName=="BUTTON")return;
  const r=t.closest("[data-id]");if(r&&!t.closest("#zoom")){AKT=+r.dataset.id;if(window.KLIK_POWIEKSZA&&t.classList.contains("ramka"))powieksz(AKT,window.ZOOM_WZORZEC);else odswiez()}
});
function nastepny(){const n=DANE.miejsca.find(m=>!STAN[m.id]);if(n)AKT=n.id}
