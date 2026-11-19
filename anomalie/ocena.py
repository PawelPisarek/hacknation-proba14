"""Skrypt oceny wg „Sposobu testowania” zadania (p. 6) i ustaleń docs/decyzje.md (11:26).

Wejście: dowolny katalog obrazów .bmp (badane), opcjonalnie katalog masek PNG o tej samej nazwie
(<nazwa>.png; 0 = tło, wartość k > 0 = dodatek k; maska binarna 0/255 dzielona na spójne
składowe), oraz plik predykcji JSON:
  {"metoda": "...", "obrazy": {"<nazwa bez .bmp>": {"ramki": [[x0, y0, x1, y1], ...], "czas_s": 0.4}}}
Obraz bez maski (albo z pustą maską) = obraz czysty.

Liczenie (FP i FN osobno, bez łączenia):
  FP  — obrazy czyste z jakimkolwiek alarmem (każdy zaznaczony obszar = alarm) + liczba obszarów na czystych;
  FN  — dodatki niewskazane; dodatek wskazany, gdy jakaś ramka ma IoU ≥ 0,1 z maską dodatku
        albo środek dodatku leży w ramce;
  zbędne obszary — ramki na obrazach z dodatkami, które nie wskazują żadnego dodatku (osobno).

Użycie:
  python -m anomalie.ocena --badane DIR [--maski DIR] [--opis opis.json] --predykcje P.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

PROG_IOU = 0.1


def wczytaj_prawde(badane, maski=None, opis=None):
    """Zwraca {nazwa: [ {maska_ramka, piksele (ys, xs), srodek, typ}, ... ]} — pusta lista = czysty."""
    typy = {}
    if opis and os.path.exists(opis):
        for nazwa, o in json.load(open(opis))["obrazy"].items():
            typy[nazwa] = {d["etykieta"]: (d["typ"], d.get("miejsce", "?")) for d in o.get("dodatki", []) if "etykieta" in d}
    prawda = {}
    for p in sorted(glob.glob(os.path.join(badane, "*.bmp"))):
        nazwa = os.path.splitext(os.path.basename(p))[0]
        dodatki = []
        mp = os.path.join(maski, nazwa + ".png") if maski else None
        if mp and os.path.exists(mp):
            m = np.asarray(Image.open(mp).convert("L"))
            wartosci = [v for v in np.unique(m) if v]
            if wartosci == [255]:  # maska binarna → spójne składowe
                m, _ = ndimage.label(m > 0)
                wartosci = list(range(1, m.max() + 1))
            obiekty = ndimage.find_objects(m.astype(np.int32))
            for v in wartosci:
                sl = obiekty[v - 1]
                if sl is None:
                    continue
                lok = m[sl] == v
                ys, xs = np.nonzero(lok)
                ys, xs = ys + sl[0].start, xs + sl[1].start
                y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                dodatki.append(dict(ramka=(int(x0), int(y0), int(x1), int(y1)), ys=ys, xs=xs,
                                    srodek=((x0 + x1) / 2, (y0 + y1) / 2),
                                    typ=typy.get(nazwa, {}).get(int(v), ("?", "?"))[0],
                                    miejsce=typy.get(nazwa, {}).get(int(v), ("?", "?"))[1]))
        prawda[nazwa] = dodatki
    return prawda


def wskazuje(ramka, d):
    x0, y0, x1, y1 = ramka
    cx, cy = d["srodek"]
    if x0 <= cx < x1 and y0 <= cy < y1:
        return True
    w = ((d["xs"] >= x0) & (d["xs"] < x1) & (d["ys"] >= y0) & (d["ys"] < y1)).sum()
    pole_r = max(0, x1 - x0) * max(0, y1 - y0)
    iou = w / (pole_r + len(d["xs"]) - w + 1e-9)
    return iou >= PROG_IOU


def ocen(prawda, predykcje):
    obrazy = predykcje["obrazy"]
    w = dict(czyste=0, czyste_z_alarmem=0, obszary_na_czystych=0, z_dodatkami=0, dodatki=0,
             przeoczone=0, obrazy_z_przeoczeniem=0, zbedne_obszary=0, fn_typ={}, n_typ={}, fn_miejsce={}, n_miejsce={}, czasy=[], ramki_na_auto=[])
    for nazwa, dodatki in prawda.items():
        p = obrazy.get(nazwa)
        ramki = p["ramki"] if p else []
        w["ramki_na_auto"].append(len(ramki))
        if p and "czas_s" in p:
            w["czasy"].append(p["czas_s"])
        if not dodatki:
            w["czyste"] += 1
            w["obszary_na_czystych"] += len(ramki)
            w["czyste_z_alarmem"] += bool(ramki)
            continue
        w["z_dodatkami"] += 1
        uzyte = set()
        przeocz = 0
        for d in dodatki:
            w["dodatki"] += 1
            w["n_typ"][d["typ"]] = w["n_typ"].get(d["typ"], 0) + 1
            w["n_miejsce"][d["miejsce"]] = w["n_miejsce"].get(d["miejsce"], 0) + 1
            traf = [i for i, r in enumerate(ramki) if wskazuje(r, d)]
            uzyte.update(traf)
            if not traf:
                przeocz += 1
                w["fn_typ"][d["typ"]] = w["fn_typ"].get(d["typ"], 0) + 1
                w["fn_miejsce"][d["miejsce"]] = w["fn_miejsce"].get(d["miejsce"], 0) + 1
        w["przeoczone"] += przeocz
        w["obrazy_z_przeoczeniem"] += przeocz > 0
        w["zbedne_obszary"] += len(ramki) - len(uzyte)
    return w


def linia(metoda, w):
    cz = w["czasy"]
    czas = f"{np.mean(cz):.2f} s (maks {np.max(cz):.2f} s)" if cz else "—"
    typy = ", ".join(f"{t} {w['fn_typ'].get(t, 0)}/{n}" for t, n in sorted(w["n_typ"].items()))
    n_k = sum(n for t, n in w["n_typ"].items() if t.endswith("_konstrukcja"))
    fn_k = sum(n for t, n in w["fn_typ"].items() if t.endswith("_konstrukcja"))
    miejsca = ", ".join(f"{m} {w['fn_miejsce'].get(m, 0)}/{n}" for m, n in sorted(w["n_miejsce"].items()) if m != "ladunek")
    ra = w["ramki_na_auto"]
    na_auto = f"{np.mean(ra):.1f} (maks {max(ra)})" if ra else "—"
    return (f"WYNIK {metoda}: FP = {w['czyste_z_alarmem']}/{w['czyste']} czystych z alarmem "
            f"({w['obszary_na_czystych']} obszarów) | FN konstrukcja = {fn_k}/{n_k} [{miejsca}] | "
            f"FN wszystkie = {w['przeoczone']}/{w['dodatki']} [{typy}] | zbędne obszary: {w['zbedne_obszary']} | "
            f"miejsc do sprawdzenia na auto {na_auto} | czas/obraz {czas}")


def linia_dluga(metoda, w):
    cz = w["czasy"]
    czas = f"{np.mean(cz):.2f} s (maks {np.max(cz):.2f} s)" if cz else "—"
    typy = ", ".join(f"{t} {w['fn_typ'].get(t, 0)}/{n}" for t, n in sorted(w["n_typ"].items()))
    return (f"WYNIK {metoda}: FP = {w['czyste_z_alarmem']}/{w['czyste']} czystych z alarmem "
            f"({w['obszary_na_czystych']} obszarów) | FN = {w['przeoczone']}/{w['dodatki']} dodatków "
            f"przeoczonych ({w['obrazy_z_przeoczeniem']}/{w['z_dodatkami']} obrazów) [{typy}] | "
            f"zbędne obszary na obrazach z dodatkami: {w['zbedne_obszary']} | czas/obraz {czas}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--badane", required=True)
    ap.add_argument("--maski")
    ap.add_argument("--opis")
    ap.add_argument("--predykcje", required=True, nargs="+")
    a = ap.parse_args()
    prawda = wczytaj_prawde(a.badane, a.maski, a.opis)
    for p in a.predykcje:
        pr = json.load(open(p))
        print(linia(pr.get("metoda", os.path.basename(p)), ocen(prawda, pr)))


if __name__ == "__main__":
    main()
