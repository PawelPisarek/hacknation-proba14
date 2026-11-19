"""Generator sztucznego zbioru obrazów RTG naczepy (widok z boku, skala szarości, .bmp 8-bit).
Liczy na karcie (torch, CUDA) — na OMENie nic nie liczymy na procesorze (docs/decyzje.md 11:33).

Model obrazu: tłumienie A(x, y) = suma mu*t elementów; jasność I = I0 * exp(-A) + szum
(jasne = powietrze, ciemne = gęste elementy). Para wzorzec–badany ma tę samą konstrukcję
i ten sam ładunek zgłoszony; badany różni się zmianami nieistotnymi (szum, przesunięcie,
skala skanu w osi X — prędkość przejazdu, jasność) i — w obrazach z dodatkami — przedmiotami
dodanymi w konstrukcji lub ładunku. Prawda: maska (PNG, wartość k = dodatek k) + opis.json.

Typy dodatków (docs/decyzje.md 11:26 Q5; P4, P6 Artura):
  maly_konstrukcja, sredni_konstrukcja (także przeróbka: płyta/druga ścianka), w_ladunku, duzy_w_ladunku.
Miejsca w konstrukcji: podwojna_podloga i sciana_przy_kabinie (najczęstsze, P4), belka, skrzynka.

Użycie:
  python -m anomalie.generator --wyjscie DIR [--maly] [--pelny] [--ziarno 14] [--urzadzenie cuda]
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

WERSJA = "gen-v3"
ROZMIAR_MALY = (1200, 420)      # szer., wys.
ROZMIAR_PELNY = (12000, 4200)   # 8-bit → ~50,4 MB .bmp
TYPY_NACZEP = ["A", "B", "C"]          # w katalogu wzorców (nauka)
TYPY_SPOZA = ["D"]                     # typ spoza katalogu (A18) — tylko w zbiorze kontrolnym KS
TYPY_WSZYSTKIE = TYPY_NACZEP + TYPY_SPOZA
TYPY_DODATKOW = ["maly_konstrukcja", "sredni_konstrukcja", "w_ladunku", "duzy_w_ladunku"]
MIEJSCA_KONSTR = ["podwojna_podloga", "sciana_przy_kabinie", "belka", "skrzynka"]
WAGI_MIEJSC = [0.4, 0.4, 0.1, 0.1]
DEV = torch.device("cuda")


# ---------------------------------------------------------------- rysowanie
def _r(v):
    return int(round(v))


def _przytnij(A, x0, y0, x1, y1):
    H, W = A.shape
    return max(0, _r(x0)), max(0, _r(y0)), min(W, _r(x1)), min(H, _r(y1))


def dodaj_prostokat(A, x0, y0, x1, y1, wartosc):
    x0, y0, x1, y1 = _przytnij(A, x0, y0, x1, y1)
    if x1 > x0 and y1 > y0:
        A[y0:y1, x0:x1] += wartosc


def tekstura(rng, h, w, komorki, amplituda):
    """Gładka losowa tekstura h×w (mała siatka losowa powiększona dwuliniowo) — na karcie."""
    ch, cw = max(2, komorki), max(2, int(komorki * w / max(h, 1)))
    male = torch.from_numpy(rng.standard_normal((ch, cw)).astype(np.float32)).to(DEV)
    return amplituda * F.interpolate(male[None, None], size=(h, w), mode="bilinear", align_corners=True)[0, 0]


def dodaj_prostokat_tekstura(A, rng, x0, y0, x1, y1, baza, amplituda, komorki=6):
    x0, y0, x1, y1 = _przytnij(A, x0, y0, x1, y1)
    if x1 > x0 and y1 > y0:
        A[y0:y1, x0:x1] += (baza + tekstura(rng, y1 - y0, x1 - x0, komorki, amplituda)).clamp(min=0)


def dodaj_kolo(A, cx, cy, r, wartosc, r_wew=0.0):
    x0, y0, x1, y1 = _przytnij(A, cx - r, cy - r, cx + r + 1, cy + r + 1)
    if x1 <= x0 or y1 <= y0:
        return
    yy = torch.arange(y0, y1, device=DEV, dtype=torch.float32)[:, None]
    xx = torch.arange(x0, x1, device=DEV, dtype=torch.float32)[None, :]
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    A[y0:y1, x0:x1] += wartosc * ((d2 <= r * r) & (d2 >= r_wew * r_wew)).float()


# ---------------------------------------------------------------- konstrukcja
def geometria_typu(typ: str):
    """Stała geometria typu naczepy (wartości względne: x w jednostkach W, y w jednostkach H)."""
    rng = np.random.default_rng(1000 + TYPY_WSZYSTKIE.index(typ))
    return dict(
        x0=rng.uniform(0.04, 0.07), x1=rng.uniform(0.92, 0.96),
        gora=rng.uniform(0.09, 0.14), podloga=rng.uniform(0.66, 0.70),
        zebro_co=rng.uniform(0.028, 0.05), zebro_sz=rng.uniform(0.0025, 0.004),
        zebro_mu=rng.uniform(0.25, 0.4), sciana_mu=rng.uniform(0.05, 0.1),
        podloga_h=rng.uniform(0.035, 0.045), belka_h=rng.uniform(0.035, 0.045),
        belka_mu=rng.uniform(0.85, 1.1), osie=int(rng.integers(2, 4)),
        os_x=rng.uniform(0.70, 0.76), os_co=rng.uniform(0.055, 0.065),
        kolo_r=rng.uniform(0.10, 0.12), podpora_x=rng.uniform(0.22, 0.3),
        skrzynka_x=rng.uniform(0.42, 0.55), skrzynka_w=rng.uniform(0.05, 0.08),
        przod_sz=rng.uniform(0.015, 0.025),
    )


def rysuj_konstrukcje(A, g):
    """Rysuje konstrukcję; zwraca obszary konstrukcji, w których można ukryć dodatek, i obszar ładunku."""
    H, W = A.shape
    X0, X1 = g["x0"] * W, g["x1"] * W
    Yg, Yp = g["gora"] * H, g["podloga"] * H
    sc = 0.006 * W
    P = g["przod_sz"] * W                       # ściana przednia (przy kabinie) — podwójna blacha z pustką
    dodaj_prostokat(A, X0, Yg, X1, Yp, g["sciana_mu"])
    dodaj_prostokat(A, X0, Yg, X1, Yg + 0.012 * H, 0.45)
    dodaj_prostokat(A, X0, Yg, X0 + sc, Yp, 0.6)
    dodaj_prostokat(A, X0 + P - 0.3 * sc, Yg, X0 + P, Yp, 0.35)
    dodaj_prostokat(A, X1 - sc, Yg, X1, Yp, 0.6)
    x = X0 + P + g["zebro_co"] * W
    while x < X1 - g["zebro_co"] * W * 0.5:
        dodaj_prostokat(A, x, Yg, x + g["zebro_sz"] * W, Yp, g["zebro_mu"])
        x += g["zebro_co"] * W
    # podłoga: dwie warstwy (górna i dolna płyta) z przestrzenią między nimi
    Yb0 = Yp + g["podloga_h"] * H
    Yb1 = Yb0 + g["belka_h"] * H
    dodaj_prostokat(A, X0, Yp, X1, Yp + 0.009 * H, 0.5)
    dodaj_prostokat(A, X0, Yb0 - 0.007 * H, X1, Yb0, 0.45)
    dodaj_prostokat(A, X0, Yp, X1, Yb0, 0.05)
    dodaj_prostokat(A, X0 + 0.02 * W, Yb0, X1 - 0.01 * W, Yb1, g["belka_mu"])
    x = X0 + 0.04 * W
    while x < X1 - 0.03 * W:
        dodaj_prostokat(A, x, Yp, x + 0.003 * W, Yb1 + 0.01 * H, 0.35)  # poprzeczki
        x += 0.06 * W
    px = g["podpora_x"] * W
    dodaj_prostokat(A, px, Yb1, px + 0.008 * W, 0.93 * H, 1.1)
    dodaj_prostokat(A, px - 0.01 * W, 0.92 * H, px + 0.018 * W, 0.94 * H, 1.2)
    sx0 = g["skrzynka_x"] * W
    skrz = (sx0, Yb1, sx0 + g["skrzynka_w"] * W, Yb1 + 0.09 * H)
    dodaj_prostokat(A, *skrz, 0.25)
    dodaj_prostokat(A, skrz[0], skrz[1], skrz[2], skrz[1] + 0.006 * H, 0.4)
    r = g["kolo_r"] * H
    cy = Yb1 + 0.6 * r
    for i in range(g["osie"]):
        cx = (g["os_x"] + i * g["os_co"]) * W
        dodaj_kolo(A, cx, cy, r, 0.9, 0.62 * r)
        dodaj_kolo(A, cx, cy, 0.62 * r, 1.6, 0.3 * r)
        dodaj_kolo(A, cx, cy, 0.3 * r, 2.2)
        dodaj_prostokat(A, cx - 0.004 * W, Yb1, cx + 0.004 * W, cy, 0.8)
    obszary = {
        "podwojna_podloga": (X0 + 0.02 * W, Yp + 0.011 * H, X1 - 0.02 * W, Yb0 - 0.009 * H),
        "sciana_przy_kabinie": (X0 + sc + 0.001 * W, Yg + 0.02 * H, X0 + P - 0.3 * sc - 0.001 * W, Yp - 0.01 * H),
        "belka": (X0 + 0.03 * W, Yb0 + 0.1 * (Yb1 - Yb0), g["os_x"] * W - r, Yb1 - 0.1 * (Yb1 - Yb0)),
        "skrzynka": (skrz[0] + 0.003 * W, skrz[1] + 0.012 * H, skrz[2] - 0.003 * W, skrz[3] - 0.01 * H),
    }
    obszar_ladunku = (X0 + P + 0.002 * W, Yg + 0.015 * H, X1 - sc, Yp)
    return obszary, obszar_ladunku


def rysuj_ladunek(A, rng, obszar):
    """Ładunek zgłoszony: palety z kartonami (wspólny dla wzorca i badanego w parze)."""
    H, W = A.shape
    x0, y0, x1, y1 = obszar
    x = x0 + rng.uniform(0.005, 0.02) * W
    while x < x1 - 0.06 * W:
        pw = rng.uniform(0.05, 0.12) * W
        ph = rng.uniform(0.25, 0.85) * (y1 - y0)
        if rng.random() < 0.85:
            dodaj_prostokat(A, x, y1 - 0.02 * H, x + pw, y1, 0.35)
            dodaj_prostokat_tekstura(A, rng, x, y1 - 0.02 * H - ph, x + pw, y1 - 0.02 * H,
                                     rng.uniform(0.15, 0.7), 0.06, komorki=int(rng.integers(3, 10)))
            n = int(rng.integers(2, 6))
            for k in range(1, n):
                yy = y1 - 0.02 * H - ph * k / n
                dodaj_prostokat(A, x, yy, x + pw, yy + 0.003 * H, 0.08)
        x += pw + rng.uniform(0.003, 0.03) * W


# ---------------------------------------------------------------- strefy naczepy (spec §4a)
STREFY = ["poza naczepą", "ładownia", "podłoga", "ściana przednia", "rama/osie", "dach"]
STREFA_MIEJSCA = {"podwojna_podloga": "podłoga", "sciana_przy_kabinie": "ściana przednia",
                  "belka": "rama/osie", "skrzynka": "rama/osie", "ladunek": "ładownia"}


def mapa_stref(g, W, H):
    """Mapa stref typu naczepy w układzie sceny (uint8, indeks w STREFY) — z tej samej geometrii co rysunek."""
    m = torch.zeros((H, W), dtype=torch.uint8, device=DEV)
    X0, X1 = _r(g["x0"] * W), _r(g["x1"] * W)
    Yg, Yp = _r(g["gora"] * H), _r(g["podloga"] * H)
    Yd = _r(g["gora"] * H + 0.012 * H)
    P = _r(g["x0"] * W + g["przod_sz"] * W)
    Yb0 = _r(g["podloga"] * H + g["podloga_h"] * H)
    m[Yd:Yp, P:X1] = 1
    m[Yp:Yb0, X0:X1] = 2
    m[Yd:Yp, X0:P] = 3
    m[Yb0:, X0:X1] = 4
    m[Yg:Yd, X0:X1] = 5
    return m


def zapisz_strefy(sciezka, m):
    Image.fromarray(m.cpu().numpy()).save(sciezka)


# ---------------------------------------------------------------- rodzaje towaru (P17, spec §4b)
RODZAJE_TOWARU = ["sprzęt i AGD", "odzież i tekstylia", "żywność i napoje", "materiały budowlane", "inne"]
PUSTA = "pusta naczepa"


def _wzor_okresowy(h, w, okres_x, okres_y, wyp_x, wyp_y):
    yy = torch.arange(h, device=DEV, dtype=torch.float32)[:, None]
    xx = torch.arange(w, device=DEV, dtype=torch.float32)[None, :]
    return (((xx % okres_x) < wyp_x * okres_x) & ((yy % okres_y) < wyp_y * okres_y)).float()


def _paleta(A, rng, x, y_dol, pw, ph, styl):
    H, W = A.shape
    y0 = y_dol - ph
    dodaj_prostokat(A, x, y_dol, x + pw, y_dol + 0.02 * H, 0.35)  # paleta (deska)
    x0, yy0, x1, yy1 = _przytnij(A, x, y0, x + pw, y_dol)
    if x1 - x0 < 2 or yy1 - yy0 < 2:
        return
    h, w = yy1 - yy0, x1 - x0
    if styl == "odzież i tekstylia":       # jednolita średnia gęstość, miękkie bele
        A[yy0:yy1, x0:x1] += (rng.uniform(0.12, 0.25) + tekstura(rng, h, w, 3, 0.015)).clamp(min=0)
    elif styl == "żywność i napoje":       # wiele małych równych kształtów (puszki, butelki)
        ok = max(3.0, rng.uniform(0.005, 0.008) * W)
        A[yy0:yy1, x0:x1] += rng.uniform(0.08, 0.15) * _wzor_okresowy(h, w, ok, ok * rng.uniform(0.9, 1.4), 0.75, 0.8)
    elif styl == "materiały budowlane":    # długie, gęste elementy (pręty, płyty) warstwami
        ok = max(3.0, rng.uniform(0.012, 0.024) * H)
        A[yy0:yy1, x0:x1] += rng.uniform(0.3, 0.6) * _wzor_okresowy(h, w, 10 * W, ok, 1.0, 0.55)
    else:                                  # sprzęt i AGD: gęste prostokątne bryły z teksturą
        A[yy0:yy1, x0:x1] += (rng.uniform(0.15, 0.7) + tekstura(rng, h, w, int(rng.integers(3, 10)), 0.06)).clamp(min=0)
        n = int(rng.integers(2, 6))
        for k in range(1, n):
            yk = y_dol - ph * k / n
            dodaj_prostokat(A, x, yk, x + pw, yk + 0.003 * H, 0.08)


def rysuj_towar(A, rng, obszar, rodzaj):
    """Ładunek danego rodzaju (stałe przypisanie wyglądu, spec §4b). „sprzęt i AGD” = palety gen-v2 (ten sam strumień losowy)."""
    if rodzaj == PUSTA or rodzaj is None:
        return
    if rodzaj == "sprzęt i AGD":
        rysuj_ladunek(A, rng, obszar)
        return
    H, W = A.shape
    x0, y0, x1, y1 = obszar
    dl = rodzaj == "materiały budowlane"
    x = x0 + rng.uniform(0.005, 0.02) * W
    while x < x1 - 0.06 * W:
        pw = min(rng.uniform(0.15, 0.35) if dl else rng.uniform(0.05, 0.12), (x1 - x) / W) * W
        ph = rng.uniform(0.25, 0.6 if dl else 0.85) * (y1 - y0)
        styl = str(rng.choice(RODZAJE_TOWARU[:4])) if rodzaj == "inne" else rodzaj
        if rng.random() < 0.85:
            _paleta(A, rng, x, y1 - 0.02 * H, pw, ph, styl)
        x += pw + rng.uniform(0.003, 0.03) * W


def rysuj_dodatek(A, etykiety, rng, typ, obszary_k, obszar_l, nr, grubosc=None, x_wzgl=0.5):
    """Rysuje dodatek; zwraca opis (typ, miejsce, mu). grubosc (ułamek H) — sonda S2: cienka warstwa
    „mały w konstrukcji” w podwójnej podłodze, szer. 0,01 W, mu 0,25, położenie x_wzgl wzdłuż podłogi."""
    H, W = A.shape
    if grubosc is not None:
        ox0, oy0, ox1, oy1 = obszary_k["podwojna_podloga"]
        w, h, mu = 0.01 * W, max(1.0, grubosc * H), 0.25
        x = ox0 + x_wzgl * (ox1 - ox0 - w)
        y = oy0 + 0.5 * (oy1 - oy0 - h)
        rx0, ry0, rx1, ry1 = _przytnij(A, x, y, x + w, y + h)
        A[ry0:ry1, rx0:rx1] += mu
        etykiety[ry0:ry1, rx0:rx1] = nr
        return dict(typ="maly_konstrukcja", miejsce="podwojna_podloga", mu=mu, grubosc=grubosc, grubosc_px=ry1 - ry0)
    ksztalt_owal = rng.random() < 0.3
    if typ in ("maly_konstrukcja", "sredni_konstrukcja"):
        miejsce = str(rng.choice(MIEJSCA_KONSTR, p=WAGI_MIEJSC))
        ox0, oy0, ox1, oy1 = obszary_k[miejsce]
        ow, oh = ox1 - ox0, oy1 - oy0
        if typ == "maly_konstrukcja":
            w = rng.uniform(0.006, 0.012) * W
            h = min(oh, rng.uniform(0.006, 0.012) * W)
            mu = rng.uniform(0.15, 0.3)
        else:
            w = rng.uniform(0.015, 0.04) * W
            h = min(oh, rng.uniform(0.012, 0.03) * W)
            mu = rng.uniform(0.2, 0.4)
            if miejsce == "sciana_przy_kabinie":     # skrytka wysoka i wąska
                w, h = min(ow, 0.8 * ow), min(oh, rng.uniform(0.1, 0.3) * H)
            if rng.random() < 0.3:                    # przeróbka: wstawiona płyta (długa, cienka)
                ksztalt_owal = False
                typ_przer = True
                if miejsce == "podwojna_podloga":
                    w, h, mu = rng.uniform(0.06, 0.15) * W, 0.5 * oh, rng.uniform(0.15, 0.3)
            else:
                typ_przer = False
        w = min(w, ow)
        h = min(h, oh)
        x = rng.uniform(ox0, ox1 - w)
        y = rng.uniform(oy0, oy1 - h)
    else:
        ox0, oy0, ox1, oy1 = obszar_l
        if typ == "w_ladunku":
            w, h, mu = rng.uniform(0.015, 0.04) * W, rng.uniform(0.04, 0.12) * H, rng.uniform(0.2, 0.4)
        else:
            w, h, mu = rng.uniform(0.06, 0.15) * W, rng.uniform(0.15, 0.35) * H, rng.uniform(0.25, 0.5)
        x = rng.uniform(ox0, ox1 - w)
        y = rng.uniform(oy0 + 0.3 * (oy1 - oy0 - h), oy1 - h)
        miejsce = "ladunek"
    rx0, ry0, rx1, ry1 = _przytnij(A, x, y, x + w, y + h)
    if rx1 - rx0 < 2 or ry1 - ry0 < 2:
        return None
    hh, ww = ry1 - ry0, rx1 - rx0
    ksztalt = torch.ones((hh, ww), dtype=torch.bool, device=DEV)
    if ksztalt_owal:
        yy = torch.arange(hh, device=DEV, dtype=torch.float32)[:, None]
        xx = torch.arange(ww, device=DEV, dtype=torch.float32)[None, :]
        ksztalt = ((xx - ww / 2) / (ww / 2 + 1e-6)) ** 2 + ((yy - hh / 2) / (hh / 2 + 1e-6)) ** 2 <= 1
    tex = (mu + tekstura(rng, hh, ww, 4, 0.03 * mu / 0.3)).clamp(min=0)
    A[ry0:ry1, rx0:rx1] += tex * ksztalt
    etykiety[ry0:ry1, rx0:rx1][ksztalt] = nr
    d = dict(typ=typ, miejsce=miejsce, mu=round(float(mu), 3))
    if typ == "sredni_konstrukcja" and typ_przer:
        d["przerobka"] = True
    return d


# ---------------------------------------------------------------- obraz z tłumienia
def _gauss1d(sigma):
    r = max(1, int(3 * sigma))
    x = torch.arange(-r, r + 1, device=DEV, dtype=torch.float32)
    k = torch.exp(-x ** 2 / (2 * sigma ** 2))
    return k / k.sum(), r


def rozmyj(I, sigma):
    if sigma < 0.3:
        return I
    k, r = _gauss1d(sigma)
    x = F.conv2d(F.pad(I[None, None], (r, r, 0, 0), mode="replicate"), k.view(1, 1, 1, -1))
    x = F.conv2d(F.pad(x, (0, 0, r, r), mode="replicate"), k.view(1, 1, -1, 1))
    return x[0, 0]


def wzmocnienia_wierszy(H, typ):
    """Stała nierówność czułości detektorów (wiersze) — wspólna dla skanera."""
    g = torch.Generator(device=DEV).manual_seed(77 + TYPY_WSZYSTKIE.index(typ))
    s = torch.randn(H, device=DEV, generator=g)
    s = rozmyj(s[None, :].expand(1, H).contiguous(), max(1.0, H / 400))[0] if H > 1 else s
    return (1 + 0.01 * s)[:, None]


def do_obrazu(A, gen, jasnosc, przesuniecie, typ):
    H, W = A.shape
    I = (240.0 * jasnosc) * torch.exp(-A) * wzmocnienia_wierszy(H, typ)
    I = rozmyj(I, 0.0006 * W)
    I = I + przesuniecie
    I = I + torch.randn(A.shape, device=DEV, generator=gen) * (1.5 + 0.18 * I.clamp(min=0).sqrt())
    return I.clamp(0, 255).round().to(torch.uint8)


def zapisz_bmp(sciezka, img):
    Image.fromarray(img.cpu().numpy()).save(sciezka, format="BMP")


def _gen(rng):
    return torch.Generator(device=DEV).manual_seed(int(rng.integers(0, 2**62)))


def przeksztalc(arr, sx, sy, tx, ty, najblizszy=False):
    """Badany(o) = scena(c + (o − c − t)/s): skala wokół środka, przesunięcie (tx, ty) w pikselach."""
    H, W = arr.shape
    xs = torch.arange(W, device=DEV, dtype=torch.float32)
    ys = torch.arange(H, device=DEV, dtype=torch.float32)
    xin = W / 2 + (xs - W / 2 - tx) / sx
    yin = H / 2 + (ys - H / 2 - ty) / sy
    gx = (2 * xin / (W - 1) - 1)[None, :].expand(H, W)
    gy = (2 * yin / (H - 1) - 1)[:, None].expand(H, W)
    siatka = torch.stack([gx, gy], -1)[None]
    wyn = F.grid_sample(arr.float()[None, None], siatka, mode="nearest" if najblizszy else "bilinear",
                        padding_mode="border", align_corners=True)[0, 0]
    del siatka
    return wyn.round().to(arr.dtype) if najblizszy else wyn

def _strefa_dodatku(strefy, etykiety, nr):
    v = strefy[etykiety == nr]
    return STREFY[int(torch.bincount(v.long(), minlength=len(STREFY)).argmax())] if v.numel() else "?"


def generuj_pare(katalog, ident, rng, W, H, typ, ladunek, typy_dodatkow, opis, rodzaj_wz=None, rodzaj_bad=None,
                 grubosci=None, x_wzgl=0.5):
    """Para wzorzec–badany. rodzaj_wz / rodzaj_bad: rodzaj towaru we wzorcu i w badanym (spec §4b);
    domyślnie (gen-v2) ten sam ładunek „sprzęt i AGD” albo pusta naczepa. grubosci: lista grubości
    dla sondy S2 — jeden wzorzec, po jednym badanym na grubość (<ident>_g<i>)."""
    if rodzaj_wz is None:
        rodzaj_wz = rodzaj_bad = "sprzęt i AGD" if ladunek else PUSTA
    g = geometria_typu(typ)
    gen = _gen(rng)
    scena = torch.zeros((H, W), device=DEV)
    obszary_k, obszar_l = rysuj_konstrukcje(scena, g)
    strefy = mapa_stref(g, W, H)
    if rodzaj_wz == rodzaj_bad:
        rysuj_towar(scena, rng, obszar_l, rodzaj_wz)
    else:
        baza = scena.clone()
        rysuj_towar(scena, rng, obszar_l, rodzaj_wz)
    wz = do_obrazu(scena, gen, rng.uniform(0.95, 1.05), rng.uniform(-3, 3), typ)
    for k in ("wzorce", "badane", "maski"):
        os.makedirs(os.path.join(katalog, k), exist_ok=True)
    zapisz_bmp(os.path.join(katalog, "wzorce", ident + ".bmp"), wz)
    zapisz_strefy(os.path.join(katalog, "wzorce", ident + ".strefy.png"), strefy)
    del wz
    if rodzaj_wz != rodzaj_bad:
        scena = baza
        rysuj_towar(scena, rng, obszar_l, rodzaj_bad)
    warianty = [(ident, None)] if grubosci is None else [(f"{ident}_g{i}", t) for i, t in enumerate(grubosci)]
    scena0 = scena if grubosci is None else scena.clone()
    for nazwa, grub in warianty:
        scena = scena0 if grubosci is None else scena0.clone()
        etykiety = torch.zeros((H, W), dtype=torch.uint8, device=DEV)
        dodatki = []
        for typ_d in ([] if grub is not None else typy_dodatkow):
            d = rysuj_dodatek(scena, etykiety, rng, typ_d, obszary_k, obszar_l, len(dodatki) + 1)
            if d:
                dodatki.append(d)
        if grub is not None:
            dodatki.append(rysuj_dodatek(scena, etykiety, rng, "maly_konstrukcja", obszary_k, obszar_l, 1, grub, x_wzgl))
            if nazwa != ident:
                for suf in (".bmp", ".strefy.png"):
                    cel = os.path.join(katalog, "wzorce", nazwa + suf)
                    if not os.path.exists(cel):
                        os.symlink(ident + suf, cel)
        for k, d in enumerate(dodatki, 1):
            d["strefa"] = _strefa_dodatku(strefy, etykiety, k)
        sx, sy = rng.uniform(0.985, 1.015), rng.uniform(0.997, 1.003)
        tx, ty = rng.uniform(-0.01, 0.01) * W, rng.uniform(-0.01, 0.01) * H
        badana = przeksztalc(scena, sx, sy, tx, ty)
        del scena
        bad = do_obrazu(badana, gen, rng.uniform(0.85, 1.15), rng.uniform(-6, 6), typ)
        del badana
        zapisz_bmp(os.path.join(katalog, "badane", nazwa + ".bmp"), bad)
        del bad
        if dodatki:
            et = przeksztalc(etykiety, sx, sy, tx, ty, najblizszy=True)
            Image.fromarray(et.cpu().numpy()).save(os.path.join(katalog, "maski", nazwa + ".png"))
            for k, d in enumerate(dodatki, 1):
                m = et == k
                rows, cols = m.any(1).nonzero().flatten(), m.any(0).nonzero().flatten()
                d["ramka"] = ([int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1]
                              if len(rows) else None)
                d["etykieta"] = k
            del et
        opis[nazwa] = dict(typ_naczepy=typ, w_katalogu=typ in TYPY_NACZEP, ladunek=rodzaj_bad != PUSTA,
                           rodzaj_towaru=rodzaj_bad, rodzaj_wzorca=rodzaj_wz,
                           ladunek_inny_niz_wzorzec=rodzaj_wz != rodzaj_bad, czysty=not dodatki, dodatki=dodatki,
                           przeksztalcenie=dict(sx=round(sx, 5), sy=round(sy, 5), tx=round(tx, 2), ty=round(ty, 2)))


def generuj_nauke(katalog, rng, W, H, n_na_typ):
    """Czyste obrazy wzorcowe (pusta naczepa) każdego typu — biblioteka wzorców dla trybu bez pary.
    Przy każdym obrazie mapa stref <nazwa>.strefy.png (w układzie tego obrazu)."""
    for typ in TYPY_NACZEP:
        d = os.path.join(katalog, typ)
        os.makedirs(d, exist_ok=True)
        g = geometria_typu(typ)
        for i in range(n_na_typ):
            gen = _gen(rng)
            scena = torch.zeros((H, W), device=DEV)
            rysuj_konstrukcje(scena, g)
            sx, sy = rng.uniform(0.985, 1.015), rng.uniform(0.997, 1.003)
            tx, ty = rng.uniform(-0.01, 0.01) * W, rng.uniform(-0.01, 0.01) * H
            scena = przeksztalc(scena, sx, sy, tx, ty)
            zapisz_strefy(os.path.join(d, f"{typ}_{i:02d}.strefy.png"),
                          przeksztalc(mapa_stref(g, W, H), sx, sy, tx, ty, najblizszy=True))
            zapisz_bmp(os.path.join(d, f"{typ}_{i:02d}.bmp"),
                       do_obrazu(scena, gen, rng.uniform(0.85, 1.15), rng.uniform(-6, 6), typ))


def _zapisz_opis(katalog, ziarno, W, H, opis, nazwa="opis.json"):
    with open(os.path.join(katalog, nazwa), "w") as f:
        json.dump(dict(wersja=WERSJA, ziarno=ziarno, rozmiar=[W, H], obrazy=opis), f, indent=1, ensure_ascii=False)


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
    _zapisz_opis(katalog, ziarno, W, H, opis, opis_nazwa)


def generuj_kontrolne(katalog, ziarno, W, H):
    """Zbiory kontrolne (spec §3, §7; docs/pm/07): KL, KW, KP, KS + katalog wyglądu towaru.
    Wzorzec w KL/KW: ta sama naczepa z pustą ładownią (jak katalog trybu bez pary) — założenie, decyzje.md."""
    rng = np.random.default_rng(ziarno)
    R = RODZAJE_TOWARU
    # KL: inny ładunek niż we wzorcu, rodzaj towaru zgodny z ładunkiem; w 3 parach mały dodatek w konstrukcji (A15/A16)
    opis = {}
    for j in range(6):
        typ = TYPY_NACZEP[j % 3]
        generuj_pare(os.path.join(katalog, "KL"), f"kl{j:02d}_{typ}", rng, W, H, typ, True,
                     ["maly_konstrukcja"] if j % 2 else [], opis, PUSTA, R[j % 5])
    _zapisz_opis(os.path.join(katalog, "KL"), ziarno, W, H, opis)
    # KW: ładunek zgodny ze zgłoszeniem + dodatek ukryty w ładunku (A15b)
    opis = {}
    for j in range(6):
        typ = TYPY_NACZEP[j % 3]
        generuj_pare(os.path.join(katalog, "KW"), f"kw{j:02d}_{typ}", rng, W, H, typ, True,
                     ["w_ladunku" if j % 2 == 0 else "duzy_w_ladunku"], opis, PUSTA, R[(j + 2) % 5])
    _zapisz_opis(os.path.join(katalog, "KW"), ziarno, W, H, opis)
    # KP: pusta naczepa we wzorcu i w badanym; 3 z jednym przedmiotem w ładowni, 3 bez (A17)
    opis = {}
    for j in range(6):
        typ = TYPY_NACZEP[j % 3]
        generuj_pare(os.path.join(katalog, "KP"), f"kp{j:02d}_{typ}", rng, W, H, typ, False,
                     (["w_ladunku"] if j % 4 == 0 else ["duzy_w_ladunku"]) if j < 3 else [], opis, PUSTA, PUSTA)
    _zapisz_opis(os.path.join(katalog, "KP"), ziarno, W, H, opis)
    # KS: 2 pary typu spoza katalogu (D), pusta ładownia, dodatek w konstrukcji (A18)
    opis = {}
    for j, dod in enumerate((["maly_konstrukcja"], ["sredni_konstrukcja"])):
        generuj_pare(os.path.join(katalog, "KS"), f"ks{j:02d}_D", rng, W, H, "D", False, dod, opis, PUSTA, PUSTA)
    _zapisz_opis(os.path.join(katalog, "KS"), ziarno, W, H, opis)
    # katalog wyglądu towaru: pusta naczepa (wzorzec) → załadowana rodzajem (badany), bez dodatków — do kalibracji reguły
    opis = {}
    for r_i, rodzaj in enumerate(R):
        for j in range(6):
            typ = TYPY_NACZEP[j % 3]
            generuj_pare(os.path.join(katalog, "towar"), f"t{r_i}{j:02d}_{typ}", rng, W, H, typ, True, [], opis, PUSTA, rodzaj)
    _zapisz_opis(os.path.join(katalog, "towar"), ziarno, W, H, opis)


GRUBOSCI = [0.001, 0.002, 0.004, 0.008, 0.012]   # ułamek H: przy 4200 px ≈ 4, 8, 17, 34, 50 px


def generuj_km(katalog, ziarno, W, H, n_scen=6):
    """Sonda S2 (A12): te same sceny, mały dodatek w podwójnej podłodze o grubości z GRUBOSCI."""
    rng = np.random.default_rng(ziarno)
    opis = {}
    for j in range(n_scen):
        typ = TYPY_NACZEP[j % 3]
        generuj_pare(katalog, f"s{j:02d}_{typ}", rng, W, H, typ, j % 2 == 0, [], opis,
                     grubosci=GRUBOSCI, x_wzgl=0.15 + 0.7 * j / max(1, n_scen - 1))
    _zapisz_opis(katalog, ziarno, W, H, opis)


def main():
    global DEV
    ap = argparse.ArgumentParser()
    ap.add_argument("--wyjscie", required=True)
    ap.add_argument("--ziarno", type=int, default=14)
    ap.add_argument("--maly", action="store_true", help="zbiory małe: nauka, kalib (12), kalib60, test")
    ap.add_argument("--pelny", action="store_true", help="zbiór pełnowymiarowy (~50 MB .bmp)")
    ap.add_argument("--kontrolne", action="store_true", help="zbiory kontrolne KL, KW, KP, KS + katalog towaru (małe)")
    ap.add_argument("--km", action="store_true", help="S2: KM (6 scen × 5 grubości, pełna rozdz.) + kalib_pelny (6 czystych)")
    ap.add_argument("--urzadzenie", default="cuda", help="cuda (OMEN); cpu tylko w teście dymnym kodu")
    a = ap.parse_args()
    DEV = torch.device(a.urzadzenie)
    if DEV.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("BŁĄD: brak karty CUDA — generator nie liczy na procesorze")
    t = time.time()
    if a.maly:
        W, H = ROZMIAR_MALY
        generuj_nauke(os.path.join(a.wyjscie, "nauka"), np.random.default_rng(a.ziarno + 1), W, H, 6)
        generuj_zbior(os.path.join(a.wyjscie, "kalib"), a.ziarno + 2, W, H, 12, 0)
        generuj_zbior(os.path.join(a.wyjscie, "test"), a.ziarno + 3, W, H, 30, 30)
        generuj_zbior(os.path.join(a.wyjscie, "kalib60"), a.ziarno + 5, W, H, 60, 0)
        print(f"zbiory małe gotowe ({time.time() - t:.1f} s, {DEV})", flush=True)
    if a.kontrolne:
        W, H = ROZMIAR_MALY
        generuj_kontrolne(a.wyjscie, a.ziarno + 6, W, H)
        print(f"zbiory kontrolne gotowe ({time.time() - t:.1f} s, {DEV})", flush=True)
    if a.pelny:
        W, H = ROZMIAR_PELNY
        generuj_zbior(os.path.join(a.wyjscie, "pelny"), a.ziarno + 4, W, H, 3, 3)
        print(f"zbiór pełnowymiarowy gotowy ({time.time() - t:.1f} s, {DEV})", flush=True)
    if a.km:
        W, H = ROZMIAR_PELNY
        generuj_km(os.path.join(a.wyjscie, "km"), a.ziarno + 7, W, H)
        generuj_zbior(os.path.join(a.wyjscie, "kalib_pelny"), a.ziarno + 8, W, H, 6, 0)
        print(f"KM i kalib_pelny gotowe ({time.time() - t:.1f} s, {DEV})", flush=True)


if __name__ == "__main__":
    main()
