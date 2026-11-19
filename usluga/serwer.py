"""Usługa analizy na karcie OMENa (sieć lokalna) — wynik dla aplikacji na ksefbot.pl.

Liczenie tylko na karcie (torch, CUDA): wczytanie, wyrównanie, mapa różnic. Na procesorze tylko odczyt
pliku, etykietowanie małej maski binarnej i zapis podglądu PNG (1200 px).

Metody (wyniki/bazowy/tabela.md): z parą — A_piksele_para (k = 5, FP 2/30, FN 0/60);
bez pary — C_model_typu (k = 7, model czystego obrazu typu z katalogu nauka/).

  python usluga/serwer.py --dane ~/dane/proba14/gen-v2 --port 8770 --bezczynnosc 1200

Usługa kończy się sama po --bezczynnosc s bez zapytań (zwalnia kartę dla innych przebiegów).
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys
import threading
import time
import uuid
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import numpy as np
import torch
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from anomalie import detektor as D            # noqa: E402
from anomalie.generator import geometria_typu, mapa_stref  # noqa: E402

K_PARA, K_TYPU = 5.0, 7.0          # progi z przebiegu bazowego (najmniejsze k bez alarmu na kalib)
PROG_PEWNOSCI_WZORCA = 0.2         # poniżej — „wzorzec niepewny — wskaż wzorzec” (P16)
TOWARY = ["nie wiem", "sprzęt i AGD", "odzież i tekstylia", "żywność i napoje", "materiały budowlane", "inne",
          "pusta naczepa"]
OPIS_TYPU = {"A": "typ A (katalog wzorców)", "B": "typ B (katalog wzorców)", "C": "typ C (katalog wzorców)"}
POLECANE = ["test/d028_B", "test/d016_B", "test/d019_B", "pelny/d000_A"]

BLOKADA = threading.Lock()         # jedno liczenie naraz na karcie
OSTATNIE = [time.time()]
OBRAZY: "OrderedDict[str, bytes]" = OrderedDict()
WGRANE = "/tmp/rtg-wgrane"


# ---------------------------------------------------------------- pomocnicze
def png(jas: torch.Tensor) -> str:
    """Jasność robocza (karta) → PNG w pamięci; zwraca żeton do GET /obraz/<żeton>.png."""
    a = jas.clamp(0, 255).to(torch.uint8).cpu().numpy()
    b = io.BytesIO()
    Image.fromarray(a, "L").save(b, "PNG", optimize=False)
    z = uuid.uuid4().hex[:16]
    OBRAZY[z] = b.getvalue()
    while len(OBRAZY) > 80:
        OBRAZY.popitem(last=False)
    return z


def odmiana_czesci(t):
    return "przedniej" if t < 1 / 3 else ("środkowej" if t < 2 / 3 else "tylnej")


def polozenie(t):
    return "przód" if t < 1 / 3 else ("środek" if t < 2 / 3 else "tył")


def strefa(g, cx, cy, h_rel):
    """Strefa naczepy (geometria typu z generatora, współrzędne względne); przód = strona kabiny (lewa)."""
    X0, X1, Yg, Yp = g["x0"], g["x1"], g["gora"], g["podloga"]
    Yb0 = Yp + g["podloga_h"]
    t = min(1, max(0, (cx - X0) / (X1 - X0)))
    if cx < X0 - 0.015 or cx > X1 + 0.015 or cy < Yg - 0.03:
        return "Poza naczepą", polozenie(t), t
    if cy < Yg + 0.02:
        return "Dach", polozenie(t), t
    if cy <= Yp + 0.004:
        if cx < X0 + g["przod_sz"] + 0.004:
            v = (cy - Yg) / (Yp - Yg)
            return "Ściana przednia", ("góra" if v < 1 / 3 else ("środek" if v < 2 / 3 else "dół")), t
        return "Ładownia", polozenie(t), t
    if cy <= Yb0 + 0.004:
        return "Podłoga", polozenie(t), t
    return "Rama i podwozie", polozenie(t), t


def przedmiot(s, p, t):
    return {"Podłoga": f"podłoga naczepy, {p}",
            "Ściana przednia": "przednia ściana skrzyni ładunkowej (przy kabinie)",
            "Ładownia": f"ładunek w {odmiana_czesci(t)} części ładowni",
            "Rama i podwozie": f"rama i podwozie, {p}",
            "Dach": f"dach naczepy, {p}",
            "Poza naczepą": "obszar poza obrysem naczepy"}[s]


def dlugosc(w_rel, g):
    q = round(4 * w_rel / (g["x1"] - g["x0"]))
    return {0: "", 1: ", ok. 1/4 długości naczepy", 2: ", ok. połowy długości naczepy",
            3: ", ok. 3/4 długości naczepy"}.get(q, ", na całej długości naczepy")


def pewnosc(z, k):
    """Pewność z wyniku: z = k → 50 %, z = 2k → 75 %, z ≫ k → 99 %."""
    return round(min(0.99, max(0.5, 1 - 0.5 * k / max(z, 1e-6))), 2)


def skladowe(z, k, min_pole, scal=2):
    maska = (D._maks((z > k).float(), scal) > 0).cpu().numpy()
    et, n = ndimage.label(maska)
    if n == 0:
        return []
    pola = np.bincount(et.ravel())
    zc = z.cpu().numpy()
    wyn = []
    for i, sl in enumerate(ndimage.find_objects(et), 1):
        if sl is None or pola[i] < min_pole:
            continue
        zm = float(zc[sl][et[sl] == i].max())
        if zm <= k:
            continue
        wyn.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop, zm, int(pola[i])))
    return wyn


# ---------------------------------------------------------------- reguła towaru (spec §4, P15, A15b)
def regula_towaru(dane_towaru):
    """Reguła towaru z detektora (D.RegulaTowaru, ta sama co w sondzie S3, tryb C): wygasza w ładowni tylko różnicę,
    którą wyjaśnia wybrany rodzaj towaru; dodatek ukryty w ładunku (zwarte zgęszczenie albo gęstość ponad ten towar)
    zostaje i dostaje ramkę. Progi z katalogu wyglądu towaru (<dane_towaru>/towar, czyste pary pusta → załadowana),
    liczone raz na karcie i trzymane w <dane_towaru>/progi_towaru_C.json. Brak katalogu → None (stara reguła)."""
    if not dane_towaru or not os.path.exists(os.path.join(dane_towaru, "towar", "opis.json")):
        print("reguła towaru: brak katalogu wyglądu towaru — pomijanie całych różnic w ładowni (stara reguła)", flush=True)
        return None
    reg = D.RegulaTowaru()
    plik = os.path.join(dane_towaru, "progi_towaru_C.json")
    if os.path.exists(plik):
        reg.progi = {r: tuple(v) for r, v in json.load(open(plik)).items()}
    else:
        model = D.ModelTypu(os.path.join(dane_towaru, "nauka"))
        kt = os.path.join(dane_towaru, "towar")
        for n, o in json.load(open(os.path.join(kt, "opis.json")))["obrazy"].items():
            P, _, _, _ = D.wczytaj(os.path.join(kt, "badane", n + ".bmp"))
            _, _, typ, Dm = model.mapa(P, zwroc_roznice=True)
            reg.dodaj(o["rodzaj_towaru"], Dm, model.typy[typ]["strefy"])
        reg.zamknij()
        json.dump(reg.progi, open(plik, "w"), ensure_ascii=False, indent=1)
        del model
    print("reguła towaru (t1 top-hat, t2 gęstość):", {r: tuple(round(x, 3) for x in v) for r, v in reg.progi.items()}, flush=True)
    return reg


# ---------------------------------------------------------------- model
class Usluga:
    def __init__(self, dane, dane_towaru=None):
        self.dane = dane
        t0 = time.time()
        self.model = D.ModelTypu(os.path.join(dane, "nauka"))
        self.reg = regula_towaru(dane_towaru)
        self.geom = {t: geometria_typu(t) for t in self.model.typy}
        self.katalog = {t: dict(obraz=png(m["jas"]), opis=OPIS_TYPU.get(t, f"typ {t}")) for t, m in self.model.typy.items()}
        self.przyklady = []
        for zb in ("test", "pelny"):
            op = os.path.join(dane, zb, "opis.json")
            if not os.path.exists(op):
                continue
            for n, o in sorted(json.load(open(op))["obrazy"].items()):
                self.przyklady.append(dict(id=f"{zb}/{n}", typ=o["typ_naczepy"], ladunek=o["ladunek"],
                                           dodatki=[f"{a.get('typ')} ({a.get('miejsce')})" for a in o["dodatki"]],
                                           pelny=zb == "pelny"))
        self.przyklady.sort(key=lambda p: (POLECANE.index(p["id"]) if p["id"] in POLECANE else 99, p["id"]))
        self.start_s = round(time.time() - t0, 1)

    def sciezka(self, ref, rola):
        if ref.startswith("przyklad:"):
            zb, n = ref[9:].split("/", 1)
            if zb not in ("test", "pelny") or "/" in n or ".." in n:
                raise ValueError("zły przykład")
            p = os.path.join(self.dane, zb, "badane" if rola == "badany" else "wzorce", n + ".bmp")
            nazwa = n + ".bmp"
        elif ref.startswith("plik:"):
            i = ref[5:]
            if not i.isalnum():
                raise ValueError("zły plik")
            p = os.path.join(WGRANE, i + ".bmp")
            nazwa = open(p + ".nazwa").read() if os.path.exists(p + ".nazwa") else i + ".bmp"
        else:
            raise ValueError("nieznane źródło obrazu")
        if not os.path.exists(p):
            raise FileNotFoundError(ref)
        return p, nazwa

    def analiza(self, z):
        t0 = time.time()
        towar = z.get("towar") or "nie wiem"
        if towar not in TOWARY:
            raise ValueError("nieznany rodzaj towaru")
        pB, nazwaB = self.sciezka(z["badany"], "badany")
        wz = z.get("wzorzec") or "auto"
        P, Pj, fP, rozm = D.wczytaj(pB)
        W, H = rozm
        typ_rozp, _, szczyt_rozp = self.model.rozpoznaj(P)
        pew_wz = self.model.ostatnia_pewnosc
        info = dict(plik_badany=nazwaB, rozmiar=[W, H], obraz_badany=png(Pj))
        if wz == "auto" or wz.startswith("typ:"):
            typ = wz[4:] if wz.startswith("typ:") else typ_rozp
            if typ not in self.model.typy:
                raise ValueError("nieznany typ wzorca")
            m = self.model.typy[typ]
            par, szczyt = D.rejestruj(m["wzor"], P)
            Pw, wazne = D.wyrownaj(m["med"], P, par)
            surowa = Pw - m["med"]
            med = surowa[wazne].median()
            sig_I = 1.4826 * ((surowa - med) * m["jas"])[wazne].abs().median() + 1e-6
            sig = torch.sqrt((1.4826 * D._maks(m["mad"], 1)) ** 2 + (sig_I / m["jas"].clamp(min=4.0)) ** 2)
            roz = D._rozmyj(Pw, 3) - D._maks(D._rozmyj(m["med"], 3), 2) - med
            zmap = torch.where(wazne, roz / (D._rozmyj(sig, 3) / 2.0), torch.zeros_like(roz))
            Dm = torch.where(wazne, D._rozmyj(Pw, 3) - D._rozmyj(m["med"], 3) - med, torch.zeros_like(roz))
            zneg = None
            k, fR, R_jas = K_TYPU, fP, m["jas"]
            wskazany = wz.startswith("typ:")
            info.update(tryb="wskazany typ" if wskazany else "dobrany", typ=typ, opis_typu=OPIS_TYPU.get(typ, typ),
                        podobienstwo=round(float(szczyt), 2), pewnosc_doboru=pew_wz,
                        niepewny=(not wskazany) and pew_wz < PROG_PEWNOSCI_WZORCA, wskazany_recznie=wskazany,
                        obraz_wzorca=self.katalog[typ]["obraz"], plik_wzorca=None)
        else:
            if wz == "para":
                if not z["badany"].startswith("przyklad:"):
                    raise ValueError("para tylko dla przykładu z danych")
                pR, nazwaR = self.sciezka(z["badany"], "wzorzec")
            else:
                pR, nazwaR = self.sciezka(wz, "wzorzec")
            R, Rj, fR, _ = D.wczytaj(pR)
            par, szczyt = D.rejestruj(R, P)
            Pw, wazne = D.wyrownaj(R, P, par)
            zmap = D.mapa_piksele(R, Rj, Pw, wazne, r=2)
            # rzadziej niż wzorzec (inny ładunek): role zamienione — wzorzec gęstszy od badanego
            Pwj = (256.0 * torch.exp(-Pw) - 1.0).clamp(min=0)
            zneg = D.mapa_piksele(Pw, Pwj, R, wazne, r=2)
            Dm = None
            k, R_jas = K_PARA, Rj
            plik = wz.startswith("plik:")
            typ = typ_rozp
            info.update(tryb="plik wzorca" if plik else "para", typ=typ, opis_typu=OPIS_TYPU.get(typ, typ),
                        podobienstwo=round(float(szczyt), 2), pewnosc_doboru=None, niepewny=False,
                        wskazany_recznie=plik, obraz_wzorca=png(Rj), plik_wzorca=nazwaR if plik else None,
                        para=nazwaR)
        g = self.geom.get(typ) or next(iter(self.geom.values()))
        hR, wR = zmap.shape
        sx, sy, dx, dy = par
        miejsca = []

        def dodaj(x0, y0, x1, y1, zm, pole, znak, wymus=None):
            cx, cy = (x0 + x1) / 2 / wR, (y0 + y1) / 2 / hR
            s, p, t = strefa(g, cx, cy, (y1 - y0) / hR)
            w_rel = (x1 - x0) / wR
            duzy = pole > 0.012 * wR * hR
            if s == "Ładownia" and wymus == "inny":
                kat, opis = "ładunek_inny", "Gęściej niż wzorzec — ładunek zgodny z rodzajem towaru" + dlugosc(w_rel, g) + "."
            elif s == "Ładownia" and wymus == "dodatek":
                kat, opis = "ładunek_dodatek", "Gęstszy obiekt wewnątrz ładunku — ponad to, co daje zgłoszony towar."
            elif s == "Ładownia":
                if znak < 0:
                    kat, opis = "ładunek_inny", "Rzadziej niż wzorzec — inny ładunek" + dlugosc(w_rel, g) + "."
                elif duzy and info["tryb"] in ("dobrany", "wskazany typ"):
                    kat, opis = "ładunek_inny", "Gęściej niż wzorzec — ładunek, którego we wzorcu nie ma" + dlugosc(w_rel, g) + "."
                else:
                    kat, opis = "ładunek_dodatek", "Gęstszy obiekt wewnątrz ładunku, we wzorcu brak."
            else:
                kat = "konstrukcja"
                if s == "Ściana przednia" and (y1 - y0) / hR > 0.5 * (g["podloga"] - g["gora"]):
                    opis = "Gęściej niż wzorzec, ściana grubsza na większości wysokości."
                elif duzy or w_rel > 0.12:
                    opis = "Gęściej niż wzorzec" + dlugosc(w_rel, g) + "."
                else:
                    opis = "Gęściej niż wzorzec, mały obiekt."
            X0, X1 = sorted((sx * (x0 - dx) * fP, sx * (x1 - dx) * fP))
            Y0, Y1 = sorted((sy * (y0 - dy) * fP, sy * (y1 - dy) * fP))
            miejsca.append(dict(
                strefa=s, polozenie=p, nazwa=f"{s} — {p}", kategoria=kat, opis=opis, przedmiot=przedmiot(s, p, t),
                z=round(zm, 1), pew_wynik=pewnosc(zm, k * (2 if znak < 0 else 1)),
                ramka=[max(0, int(X0)), max(0, int(Y0)), min(W, math.ceil(X1)), min(H, math.ceil(Y1))],
                ramka_wz=[x0 / wR, y0 / hR, x1 / wR, y1 / hR], _wygaszona=wymus == "inny" and s == "Ładownia"))

        min_pole = 12
        pusta = towar == "pusta naczepa"
        zost = None
        if self.reg is not None and Dm is not None and not pusta and towar != "nie wiem":
            strefy = mapa_stref(g, wR, hR).cpu().numpy()
            zost = self.reg.maska_zostaw(towar, Dm, strefy)
        if zost is None:
            for x0, y0, x1, y1, zm, pole in skladowe(zmap, k, min_pole):
                dodaj(x0, y0, x1, y1, zm, pole, +1)
        else:   # reguła towaru: ramka dla tego, co wykracza poza zgłoszony towar; reszta ładowni → pominięte
            for x0, y0, x1, y1, zm, pole in skladowe(torch.where(zost, zmap, torch.zeros_like(zmap)), k, min_pole):
                dodaj(x0, y0, x1, y1, zm, pole, +1, "dodatek")
            for x0, y0, x1, y1, zm, pole in skladowe(torch.where(zost, torch.zeros_like(zmap), zmap), k, min_pole):
                dodaj(x0, y0, x1, y1, zm, pole, +1, "inny")
        if zneg is not None:
            for x0, y0, x1, y1, zm, pole in skladowe(zneg, 2 * k, 0.004 * wR * hR, scal=3):
                cx, cy = (x0 + x1) / 2 / wR, (y0 + y1) / 2 / hR
                if strefa(g, cx, cy, 0)[0] == "Ładownia":
                    dodaj(x0, y0, x1, y1, zm, pole, -1)
        # reguły towaru (P15, P23, P27, P34)
        for mj in miejsca:
            wyg = mj.pop("_wygaszona")
            mj["regula"] = pusta and mj["strefa"] == "Ładownia"
            mj["pominieta"] = wyg if zost is not None else ((not pusta) and towar != "nie wiem" and mj["kategoria"] == "ładunek_inny")
            mj["pew"] = round(max(0.5, mj["pew_wynik"] * 0.8), 2) if info["niepewny"] else mj["pew_wynik"]
        miejsca.sort(key=lambda m: (not m["regula"], -m["pew"]))
        for i, mj in enumerate(miejsca, 1):
            mj["id"] = i
        info.update(towar=towar, miejsca=miejsca, czas_analizy_s=round(time.time() - t0, 2),
                    metoda="A_piksele_para" if info["tryb"] in ("para", "plik wzorca") else "C_model_typu",
                    karta=torch.cuda.get_device_name(0),
                    regula_towaru="katalog wyglądu towaru (D.RegulaTowaru)" if zost is not None else None)
        return info


# ---------------------------------------------------------------- HTTP
class Obsluga(BaseHTTPRequestHandler):
    U: Usluga = None

    def log_message(self, fmt, *a):
        sys.stderr.write("%s %s\n" % (time.strftime("%H:%M:%S"), fmt % a))

    def _json(self, kod, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        OSTATNIE[0] = time.time()
        u = urlparse(self.path).path
        if u == "/zdrowie":
            return self._json(200, dict(ok=True, karta=torch.cuda.get_device_name(0), typy=list(self.U.model.typy),
                                        przyklady=len(self.U.przyklady), start_s=self.U.start_s))
        if u == "/przyklady":
            return self._json(200, dict(przyklady=self.U.przyklady, towary=TOWARY,
                                        katalog=[dict(typ=t, **v) for t, v in self.U.katalog.items()]))
        if u.startswith("/obraz/") and u.endswith(".png"):
            b = OBRAZY.get(u[7:-4])
            if b is None:
                return self._json(404, dict(blad="brak obrazu"))
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "max-age=3600")
            self.end_headers()
            return self.wfile.write(b)
        self._json(404, dict(blad="nie ma"))

    def do_POST(self):
        OSTATNIE[0] = time.time()
        u = urlparse(self.path).path
        n = int(self.headers.get("Content-Length") or 0)
        try:
            if u == "/wgraj":
                if n < 54 or n > 150_000_000:
                    return self._json(400, dict(blad="plik .bmp: zły rozmiar"))
                os.makedirs(WGRANE, exist_ok=True)
                i = uuid.uuid4().hex[:12]
                p = os.path.join(WGRANE, i + ".bmp")
                with open(p, "wb") as f:
                    zostalo, pierwsze = n, True
                    while zostalo:
                        c = self.rfile.read(min(1 << 20, zostalo))
                        if not c:
                            break
                        if pierwsze and c[:2] != b"BM":
                            f.close()
                            os.remove(p)
                            return self._json(400, dict(blad="to nie jest plik .bmp"))
                        pierwsze = False
                        f.write(c)
                        zostalo -= len(c)
                nazwa = os.path.basename(self.headers.get("X-Nazwa") or "plik.bmp")[:120]
                open(p + ".nazwa", "w").write(nazwa)
                with Image.open(p) as im:
                    rozm = im.size
                return self._json(200, dict(id="plik:" + i, nazwa=nazwa, rozmiar=list(rozm)))
            if u == "/analiza":
                z = json.loads(self.rfile.read(n) or b"{}")
                with BLOKADA:
                    wyn = self.U.analiza(z)
                return self._json(200, wyn)
        except (ValueError, KeyError, FileNotFoundError) as e:
            return self._json(400, dict(blad=str(e)))
        except Exception as e:  # noqa: BLE001
            return self._json(500, dict(blad=f"{type(e).__name__}: {e}"))
        self._json(404, dict(blad="nie ma"))


def sprawdz(U):
    print("start (model typów + katalog):", U.start_s, "s")
    proby = [("przyklad:test/d028_B", "para", "nie wiem"), ("przyklad:test/d028_B", "para", "sprzęt i AGD"),
             ("przyklad:test/d028_B", "auto", "nie wiem"), ("przyklad:test/d028_B", "typ:B", "nie wiem"),
             ("przyklad:test/d016_B", "para", "pusta naczepa"), ("przyklad:test/c001_B", "para", "nie wiem"),
             ("przyklad:test/c001_B", "auto", "nie wiem"), ("przyklad:pelny/d000_A", "para", "nie wiem")]
    for b, w, t in proby:
        torch.cuda.reset_peak_memory_stats()
        r = U.analiza(dict(badany=b, wzorzec=w, towar=t))
        print(f"\n== {b} wz={w} towar={t}: tryb {r['tryb']} typ {r['typ']} (rozp.) podob. {r['podobienstwo']} "
              f"pew.doboru {r['pewnosc_doboru']} niepewny {r['niepewny']} czas {r['czas_analizy_s']} s "
              f"pamięć {torch.cuda.max_memory_allocated() / 2**30:.2f} GB, miejsc {len(r['miejsca'])}")
        for m in r["miejsca"][:12]:
            print(f"  {m['id']:2d} {m['nazwa']:28s} {m['pew']:.2f} {m['kategoria']:15s} pom={m['pominieta']} "
                  f"reg={m['regula']} z={m['z']} {m['ramka']} | {m['opis']}")
    pr = [p for p in U.przyklady if p["id"] in ("test/d028_B", "test/d016_B", "pelny/d000_A")]
    print("\nprawda:", json.dumps(pr, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dane", default=os.path.expanduser("~/dane/proba14/gen-v2"))
    ap.add_argument("--towar", default=os.path.expanduser("~/dane/proba14/gen-v3"),
                    help="dane z katalogiem wyglądu towaru (towar/, nauka/) — progi reguły towaru")
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--bezczynnosc", type=int, default=1200)
    ap.add_argument("--sprawdz", action="store_true", help="sonda: analiza polecanych przykładów i koniec")
    a = ap.parse_args()
    D.dev()
    Obsluga.U = Usluga(a.dane, a.towar)
    if a.sprawdz:
        return sprawdz(Obsluga.U)
    print(f"usługa gotowa: karta {torch.cuda.get_device_name(0)}, typy {list(Obsluga.U.model.typy)}, "
          f"przykłady {len(Obsluga.U.przyklady)}, start {Obsluga.U.start_s} s, port {a.port}", flush=True)

    def straz():
        while True:
            time.sleep(10)
            if time.time() - OSTATNIE[0] > a.bezczynnosc:
                print(f"koniec: {a.bezczynnosc} s bez zapytań", flush=True)
                os._exit(0)
    threading.Thread(target=straz, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", a.port), Obsluga).serve_forever()


if __name__ == "__main__":
    main()
