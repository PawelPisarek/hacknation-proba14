"""Generator sztucznego zbioru obrazów RTG naczepy (widok z boku, skala szarości, .bmp 8-bit).

Model obrazu: tłumienie A(x, y) = suma mu*t elementów; jasność I = I0 * exp(-A) + szum
(jasne = powietrze, ciemne = gęste elementy). Para wzorzec–badany ma tę samą konstrukcję
i ten sam ładunek zgłoszony; badany różni się zmianami nieistotnymi (szum, przesunięcie,
skala skanu w osi X — prędkość przejazdu, jasność) i — w obrazach z dodatkami — przedmiotami
dodanymi w konstrukcji lub ładunku. Prawda: maska (PNG, wartość k = dodatek k) + opis.json.

Typy dodatków (z ustaleń docs/decyzje.md, 11:26 Q5):
  maly_konstrukcja, sredni_konstrukcja, w_ladunku, duzy_w_ladunku.

Użycie:
  python -m anomalie.generator --wyjscie DIR [--maly] [--pelny] [--ziarno 14]
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
from PIL import Image
from scipy import ndimage

WERSJA = "gen-v1"
ROZMIAR_MALY = (1200, 420)      # szer., wys.
ROZMIAR_PELNY = (12000, 4200)   # 8-bit → ~50,4 MB .bmp
TYPY_NACZEP = ["A", "B", "C"]
TYPY_DODATKOW = ["maly_konstrukcja", "sredni_konstrukcja", "w_ladunku", "duzy_w_ladunku"]


# ---------------------------------------------------------------- rysowanie
def _r(v):
    return int(round(v))


def dodaj_prostokat(A, x0, y0, x1, y1, wartosc, etykiety=None, etykieta=0):
    H, W = A.shape
    x0, x1 = max(0, _r(x0)), min(W, _r(x1))
    y0, y1 = max(0, _r(y0)), min(H, _r(y1))
    if x1 <= x0 or y1 <= y0:
        return None
    A[y0:y1, x0:x1] += wartosc
    if etykiety is not None:
        etykiety[y0:y1, x0:x1] = etykieta
    return (x0, y0, x1, y1)


def tekstura(rng, h, w, komorki, amplituda):
    """Gładka losowa tekstura h×w (mała siatka losowa powiększona liniowo)."""
    ch, cw = max(2, komorki), max(2, int(komorki * w / max(h, 1)))
    male = rng.standard_normal((ch, cw)).astype(np.float32)
    duze = ndimage.zoom(male, (h / ch, w / cw), order=1)[:h, :w]
    if duze.shape != (h, w):
        duze = np.pad(duze, ((0, h - duze.shape[0]), (0, w - duze.shape[1])), mode="edge")
    return amplituda * duze


def dodaj_prostokat_tekstura(A, rng, x0, y0, x1, y1, baza, amplituda, komorki=6):
    H, W = A.shape
    x0, x1 = max(0, _r(x0)), min(W, _r(x1))
    y0, y1 = max(0, _r(y0)), min(H, _r(y1))
    if x1 <= x0 or y1 <= y0:
        return
    A[y0:y1, x0:x1] += np.maximum(0, baza + tekstura(rng, y1 - y0, x1 - x0, komorki, amplituda))


def dodaj_kolo(A, cx, cy, r, wartosc, r_wew=0.0):
    H, W = A.shape
    x0, x1 = max(0, _r(cx - r)), min(W, _r(cx + r) + 1)
    y0, y1 = max(0, _r(cy - r)), min(H, _r(cy + r) + 1)
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.ogrid[y0:y1, x0:x1]
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    m = (d2 <= r * r) & (d2 >= r_wew * r_wew)
    A[y0:y1, x0:x1][m] += wartosc


# ---------------------------------------------------------------- konstrukcja
def geometria_typu(typ: str):
    """Stała geometria typu naczepy (wartości względne: x w jednostkach W, y w jednostkach H)."""
    rng = np.random.default_rng(1000 + TYPY_NACZEP.index(typ))
    g = dict(
        x0=rng.uniform(0.04, 0.07), x1=rng.uniform(0.92, 0.96),
        gora=rng.uniform(0.09, 0.14), podloga=rng.uniform(0.68, 0.72),
        zebro_co=rng.uniform(0.028, 0.05), zebro_sz=rng.uniform(0.0025, 0.004),
        zebro_mu=rng.uniform(0.25, 0.4), sciana_mu=rng.uniform(0.05, 0.1),
        podloga_h=rng.uniform(0.022, 0.03), belka_h=rng.uniform(0.035, 0.045),
        belka_mu=rng.uniform(0.85, 1.1), osie=int(rng.integers(2, 4)),
        os_x=rng.uniform(0.70, 0.76), os_co=rng.uniform(0.055, 0.065),
        kolo_r=rng.uniform(0.10, 0.12), podpora_x=rng.uniform(0.22, 0.3),
        skrzynka_x=rng.uniform(0.42, 0.55), skrzynka_w=rng.uniform(0.05, 0.08),
    )
    return g


def rysuj_konstrukcje(A, g):
    """Rysuje konstrukcję; zwraca obszary konstrukcji (piksele), w których można ukryć dodatek."""
    H, W = A.shape
    X0, X1 = g["x0"] * W, g["x1"] * W
    Yg, Yp = g["gora"] * H, g["podloga"] * H
    sc = 0.006 * W
    # ściana boczna (blacha), dach, przód, tył
    dodaj_prostokat(A, X0, Yg, X1, Yp, g["sciana_mu"])
    dodaj_prostokat(A, X0, Yg, X1, Yg + 0.012 * H, 0.45)
    dodaj_prostokat(A, X0, Yg, X0 + sc, Yp, 0.6)
    dodaj_prostokat(A, X1 - sc, Yg, X1, Yp, 0.6)
    # żebra
    x = X0 + g["zebro_co"] * W
    while x < X1 - g["zebro_co"] * W * 0.5:
        dodaj_prostokat(A, x, Yg, x + g["zebro_sz"] * W, Yp, g["zebro_mu"])
        x += g["zebro_co"] * W
    # podłoga i rama (belka główna) + poprzeczki
    Yb0 = Yp + g["podloga_h"] * H
    Yb1 = Yb0 + g["belka_h"] * H
    dodaj_prostokat(A, X0, Yp, X1, Yb0, 0.55)
    dodaj_prostokat(A, X0 + 0.02 * W, Yb0, X1 - 0.01 * W, Yb1, g["belka_mu"])
    x = X0 + 0.04 * W
    while x < X1 - 0.03 * W:
        dodaj_prostokat(A, x, Yb0, x + 0.004 * W, Yb1 + 0.01 * H, 0.4)
        x += 0.06 * W
    # podpora (nogi postojowe) i skrzynka narzędziowa
    px = g["podpora_x"] * W
    dodaj_prostokat(A, px, Yb1, px + 0.008 * W, 0.93 * H, 1.1)
    dodaj_prostokat(A, px - 0.01 * W, 0.92 * H, px + 0.018 * W, 0.94 * H, 1.2)
    sx0 = g["skrzynka_x"] * W
    skrz = (sx0, Yb1, sx0 + g["skrzynka_w"] * W, Yb1 + 0.09 * H)
    dodaj_prostokat(A, *skrz, 0.25)
    dodaj_prostokat(A, skrz[0], skrz[1], skrz[2], skrz[1] + 0.006 * H, 0.4)
    # osie i koła
    r = g["kolo_r"] * H
    cy = Yb1 + 0.6 * r
    for i in range(g["osie"]):
        cx = (g["os_x"] + i * g["os_co"]) * W
        dodaj_kolo(A, cx, cy, r, 0.9, 0.62 * r)
        dodaj_kolo(A, cx, cy, 0.62 * r, 1.6, 0.3 * r)
        dodaj_kolo(A, cx, cy, 0.3 * r, 2.2)
        dodaj_prostokat(A, cx - 0.004 * W, Yb1, cx + 0.004 * W, cy, 0.8)  # zawieszenie
    obszary_konstrukcji = {
        "belka": (X0 + 0.03 * W, Yb0 + 0.1 * (Yb1 - Yb0), g["os_x"] * W - r, Yb1 - 0.1 * (Yb1 - Yb0)),
        "podloga": (X0 + 0.02 * W, Yp + 0.1 * (Yb0 - Yp), X1 - 0.02 * W, Yb0 - 0.1 * (Yb0 - Yp)),
        "skrzynka": (skrz[0] + 0.003 * W, skrz[1] + 0.012 * H, skrz[2] - 0.003 * W, skrz[3] - 0.01 * H),
        "sciana_przod": (X0 + sc, Yg + 0.02 * H, X0 + g["zebro_co"] * W - 0.002 * W, Yp - 0.02 * H),
    }
    obszar_ladunku = (X0 + sc, Yg + 0.015 * H, X1 - sc, Yp)
    return obszary_konstrukcji, obszar_ladunku


def rysuj_ladunek(A, rng, obszar):
    """Ładunek zgłoszony: palety z kartonami (wspólny dla wzorca i badanego w parze)."""
    H, W = A.shape
    x0, y0, x1, y1 = obszar
    x = x0 + rng.uniform(0.005, 0.02) * W
    while x < x1 - 0.06 * W:
        pw = rng.uniform(0.05, 0.12) * W
        ph = rng.uniform(0.25, 0.85) * (y1 - y0)
        if rng.random() < 0.85:
            dodaj_prostokat(A, x, y1 - 0.02 * H, x + pw, y1, 0.35)           # paleta
            dodaj_prostokat_tekstura(A, rng, x, y1 - 0.02 * H - ph, x + pw, y1 - 0.02 * H,
                                     rng.uniform(0.15, 0.7), 0.06, komorki=int(rng.integers(3, 10)))
            # linie kartonów
            n = int(rng.integers(2, 6))
            for k in range(1, n):
                yy = y1 - 0.02 * H - ph * k / n
                dodaj_prostokat(A, x, yy, x + pw, yy + 0.003 * H, 0.08)
        x += pw + rng.uniform(0.003, 0.03) * W


def rysuj_dodatek(A, etykiety, rng, typ, obszary_k, obszar_l, nr):
    """Rysuje dodatek wybranego typu; zwraca opis (ramka w układzie sceny)."""
    H, W = A.shape
    if typ in ("maly_konstrukcja", "sredni_konstrukcja"):
        nazwa = str(rng.choice(list(obszary_k)))
        ox0, oy0, ox1, oy1 = obszary_k[nazwa]
        oh = oy1 - oy0
        if typ == "maly_konstrukcja":
            w = rng.uniform(0.006, 0.012) * W
            h = min(oh, rng.uniform(0.006, 0.012) * W)
            mu = rng.uniform(0.15, 0.3)
        else:
            w = rng.uniform(0.015, 0.04) * W
            h = min(oh, rng.uniform(0.012, 0.03) * W)
            mu = rng.uniform(0.2, 0.4)
        w = min(w, ox1 - ox0)
        x = rng.uniform(ox0, ox1 - w)
        y = rng.uniform(oy0, oy1 - h)
        miejsce = nazwa
    else:
        ox0, oy0, ox1, oy1 = obszar_l
        if typ == "w_ladunku":
            w, h, mu = rng.uniform(0.015, 0.04) * W, rng.uniform(0.04, 0.12) * H, rng.uniform(0.2, 0.4)
        else:
            w, h, mu = rng.uniform(0.06, 0.15) * W, rng.uniform(0.15, 0.35) * H, rng.uniform(0.25, 0.5)
        x = rng.uniform(ox0, ox1 - w)
        y = rng.uniform(oy0 + 0.3 * (oy1 - oy0 - h), oy1 - h)  # raczej nisko, jak towar
        miejsce = "ladunek"
    rx0, ry0 = max(0, _r(x)), max(0, _r(y))
    rx1, ry1 = min(W, _r(x + w)), min(H, _r(y + h))
    if rx1 - rx0 < 2 or ry1 - ry0 < 2:
        return None
    ksztalt = np.ones((ry1 - ry0, rx1 - rx0), bool)
    if rng.random() < 0.3:  # owalny pakunek
        yy, xx = np.mgrid[0:ry1 - ry0, 0:rx1 - rx0]
        ksztalt = ((xx - (rx1 - rx0) / 2) / ((rx1 - rx0) / 2 + 1e-6)) ** 2 + \
                  ((yy - (ry1 - ry0) / 2) / ((ry1 - ry0) / 2 + 1e-6)) ** 2 <= 1
    tex = np.maximum(0, mu + tekstura(rng, ry1 - ry0, rx1 - rx0, 4, 0.03 * mu / 0.3))
    A[ry0:ry1, rx0:rx1] += tex * ksztalt
    etykiety[ry0:ry1, rx0:rx1][ksztalt] = nr
    return dict(typ=typ, miejsce=miejsce, mu=round(float(mu), 3))


# ---------------------------------------------------------------- obraz z tłumienia
def wzmocnienia_wierszy(H, typ):
    """Stała nierówność czułości detektorów (wiersze) — wspólna dla skanera."""
    rng = np.random.default_rng(77 + TYPY_NACZEP.index(typ))
    g = 1 + 0.01 * ndimage.gaussian_filter1d(rng.standard_normal(H), max(1, H / 400))
    return g.astype(np.float32)[:, None]


def do_obrazu(A, rng, jasnosc, przesuniecie, typ):
    H, W = A.shape
    I = (240.0 * jasnosc) * np.exp(-A) * wzmocnienia_wierszy(H, typ)
    I = ndimage.gaussian_filter(I, 0.0006 * W)          # rozmycie ogniska / detektora
    I += przesuniecie
    I += rng.standard_normal(A.shape, dtype=np.float32) * (1.5 + 0.18 * np.sqrt(np.maximum(I, 0)))
    return np.clip(I, 0, 255).astype(np.uint8)


def przeksztalc(arr, sx, sy, tx, ty, order):
    """Badany(o) = scena(M o + off): skala wokół środka, przesunięcie (tx, ty) w pikselach."""
    H, W = arr.shape
    c = np.array([H / 2, W / 2])
    M = np.array([1 / sy, 1 / sx])
    off = c - c * M - np.array([ty, tx]) * M
    return ndimage.affine_transform(arr, M, offset=off, order=order, mode="nearest")


def zapisz_bmp(sciezka, img):
    Image.fromarray(img).save(sciezka, format="BMP")


# ---------------------------------------------------------------- zbiory
def generuj_pare(katalog, ident, rng, W, H, typ, ladunek, typy_dodatkow, opis):
    g = geometria_typu(typ)
    scena = np.zeros((H, W), np.float32)
    obszary_k, obszar_l = rysuj_konstrukcje(scena, g)
    if ladunek:
        rysuj_ladunek(scena, rng, obszar_l)
    wz = do_obrazu(scena, rng, rng.uniform(0.95, 1.05), rng.uniform(-3, 3), typ)
    badana = scena.copy()
    etykiety = np.zeros((H, W), np.uint8)
    dodatki = []
    for typ_d in typy_dodatkow:
        d = rysuj_dodatek(badana, etykiety, rng, typ_d, obszary_k, obszar_l, len(dodatki) + 1)
        if d:
            dodatki.append(d)
    sx, sy = rng.uniform(0.985, 1.015), rng.uniform(0.997, 1.003)
    tx, ty = rng.uniform(-0.01, 0.01) * W, rng.uniform(-0.01, 0.01) * H
    badana = przeksztalc(badana, sx, sy, tx, ty, order=1)
    bad = do_obrazu(badana, rng, rng.uniform(0.85, 1.15), rng.uniform(-6, 6), typ)
    for k in ("wzorce", "badane", "maski"):
        os.makedirs(os.path.join(katalog, k), exist_ok=True)
    zapisz_bmp(os.path.join(katalog, "wzorce", ident + ".bmp"), wz)
    zapisz_bmp(os.path.join(katalog, "badane", ident + ".bmp"), bad)
    if dodatki:
        et = przeksztalc(etykiety, sx, sy, tx, ty, order=0)
        Image.fromarray(et).save(os.path.join(katalog, "maski", ident + ".png"))
        for k, d in enumerate(dodatki, 1):
            ys, xs = np.nonzero(et == k)
            d["ramka"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None
            d["etykieta"] = k
    opis[ident] = dict(typ_naczepy=typ, ladunek=bool(ladunek), czysty=not dodatki, dodatki=dodatki,
                       przeksztalcenie=dict(sx=round(sx, 5), sy=round(sy, 5), tx=round(tx, 2), ty=round(ty, 2)))


def generuj_nauke(katalog, rng, W, H, n_na_typ):
    """Czyste obrazy wzorcowe (pusta naczepa) każdego typu — do trybu „model czystego obrazu”."""
    for typ in TYPY_NACZEP:
        d = os.path.join(katalog, typ)
        os.makedirs(d, exist_ok=True)
        g = geometria_typu(typ)
        for i in range(n_na_typ):
            scena = np.zeros((H, W), np.float32)
            rysuj_konstrukcje(scena, g)
            sx, sy = rng.uniform(0.985, 1.015), rng.uniform(0.997, 1.003)
            scena = przeksztalc(scena, sx, sy, rng.uniform(-0.01, 0.01) * W, rng.uniform(-0.01, 0.01) * H, 1)
            zapisz_bmp(os.path.join(d, f"{typ}_{i:02d}.bmp"),
                       do_obrazu(scena, rng, rng.uniform(0.85, 1.15), rng.uniform(-6, 6), typ))


def generuj_zbior(katalog, ziarno, W, H, n_czystych, n_z_dodatkami, opis_nazwa="opis.json"):
    rng = np.random.default_rng(ziarno)
    opis = {}
    i = 0
    for n, czyste in ((n_czystych, True), (n_z_dodatkami, False)):
        for j in range(n):
            typ = TYPY_NACZEP[i % len(TYPY_NACZEP)]
            ladunek = (j // len(TYPY_NACZEP)) % 2 == 0
            if czyste:
                dod = []
            else:
                k = int(rng.integers(1, 4))
                dod = [TYPY_DODATKOW[(j + m) % 4] for m in range(k)]
            ident = f"{'c' if czyste else 'd'}{j:03d}_{typ}"
            generuj_pare(katalog, ident, rng, W, H, typ, ladunek, dod, opis)
            i += 1
    with open(os.path.join(katalog, opis_nazwa), "w") as f:
        json.dump(dict(wersja=WERSJA, ziarno=ziarno, rozmiar=[W, H], obrazy=opis), f, indent=1, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wyjscie", required=True)
    ap.add_argument("--ziarno", type=int, default=14)
    ap.add_argument("--maly", action="store_true", help="zbiory małe: nauka, kalib, test")
    ap.add_argument("--pelny", action="store_true", help="zbiór pełnowymiarowy (~50 MB .bmp)")
    a = ap.parse_args()
    t = time.time()
    if a.maly:
        W, H = ROZMIAR_MALY
        generuj_nauke(os.path.join(a.wyjscie, "nauka"), np.random.default_rng(a.ziarno + 1), W, H, 6)
        generuj_zbior(os.path.join(a.wyjscie, "kalib"), a.ziarno + 2, W, H, 12, 0)
        generuj_zbior(os.path.join(a.wyjscie, "test"), a.ziarno + 3, W, H, 30, 30)
        print(f"zbiory małe gotowe ({time.time() - t:.1f} s)", flush=True)
    if a.pelny:
        W, H = ROZMIAR_PELNY
        generuj_zbior(os.path.join(a.wyjscie, "pelny"), a.ziarno + 4, W, H, 3, 3)
        print(f"zbiór pełnowymiarowy gotowy ({time.time() - t:.1f} s)", flush=True)


if __name__ == "__main__":
    main()
