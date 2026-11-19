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

WERSJA = "gen-v2"
ROZMIAR_MALY = (1200, 420)      # szer., wys.
ROZMIAR_PELNY = (12000, 4200)   # 8-bit → ~50,4 MB .bmp
TYPY_NACZEP = ["A", "B", "C"]
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
    rng = np.random.default_rng(1000 + TYPY_NACZEP.index(typ))
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


def rysuj_dodatek(A, etykiety, rng, typ, obszary_k, obszar_l, nr):
    """Rysuje dodatek; zwraca opis (typ, miejsce, mu)."""
    H, W = A.shape
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
    g = torch.Generator(device=DEV).manual_seed(77 + TYPY_NACZEP.index(typ))
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


def zapisz_bmp(sciezka, img):
    Image.fromarray(img.cpu().numpy()).save(sciezka, format="BMP")


def _gen(rng):
    return torch.Generator(device=DEV).manual_seed(int(rng.integers(0, 2**62)))


# ---------------------------------------------------------------- zbiory
def generuj_pare(katalog, ident, rng, W, H, typ, ladunek, typy_dodatkow, opis):
    g = geometria_typu(typ)
    gen = _gen(rng)
    scena = torch.zeros((H, W), device=DEV)
    obszary_k, obszar_l = rysuj_konstrukcje(scena, g)
    if ladunek:
        rysuj_ladunek(scena, rng, obszar_l)
    wz = do_obrazu(scena, gen, rng.uniform(0.95, 1.05), rng.uniform(-3, 3), typ)
    for k in ("wzorce", "badane", "maski"):
        os.makedirs(os.path.join(katalog, k), exist_ok=True)
    zapisz_bmp(os.path.join(katalog, "wzorce", ident + ".bmp"), wz)
    del wz
    etykiety = torch.zeros((H, W), dtype=torch.uint8, device=DEV)
    dodatki = []
    for typ_d in typy_dodatkow:
        d = rysuj_dodatek(scena, etykiety, rng, typ_d, obszary_k, obszar_l, len(dodatki) + 1)
        if d:
            dodatki.append(d)
    sx, sy = rng.uniform(0.985, 1.015), rng.uniform(0.997, 1.003)
    tx, ty = rng.uniform(-0.01, 0.01) * W, rng.uniform(-0.01, 0.01) * H
    badana = przeksztalc(scena, sx, sy, tx, ty)
    del scena
    bad = do_obrazu(badana, gen, rng.uniform(0.85, 1.15), rng.uniform(-6, 6), typ)
    del badana
    zapisz_bmp(os.path.join(katalog, "badane", ident + ".bmp"), bad)
    del bad
    if dodatki:
        et = przeksztalc(etykiety, sx, sy, tx, ty, najblizszy=True)
        Image.fromarray(et.cpu().numpy()).save(os.path.join(katalog, "maski", ident + ".png"))
        for k, d in enumerate(dodatki, 1):
            m = et == k
            rows, cols = m.any(1).nonzero().flatten(), m.any(0).nonzero().flatten()
            d["ramka"] = ([int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1]
                          if len(rows) else None)
            d["etykieta"] = k
    opis[ident] = dict(typ_naczepy=typ, ladunek=bool(ladunek), czysty=not dodatki, dodatki=dodatki,
                       przeksztalcenie=dict(sx=round(sx, 5), sy=round(sy, 5), tx=round(tx, 2), ty=round(ty, 2)))


def generuj_nauke(katalog, rng, W, H, n_na_typ):
    """Czyste obrazy wzorcowe (pusta naczepa) każdego typu — biblioteka wzorców dla trybu bez pary."""
    for typ in TYPY_NACZEP:
        d = os.path.join(katalog, typ)
        os.makedirs(d, exist_ok=True)
        g = geometria_typu(typ)
        for i in range(n_na_typ):
            gen = _gen(rng)
            scena = torch.zeros((H, W), device=DEV)
            rysuj_konstrukcje(scena, g)
            sx, sy = rng.uniform(0.985, 1.015), rng.uniform(0.997, 1.003)
            scena = przeksztalc(scena, sx, sy, rng.uniform(-0.01, 0.01) * W, rng.uniform(-0.01, 0.01) * H)
            zapisz_bmp(os.path.join(d, f"{typ}_{i:02d}.bmp"),
                       do_obrazu(scena, gen, rng.uniform(0.85, 1.15), rng.uniform(-6, 6), typ))


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
    global DEV
    ap = argparse.ArgumentParser()
    ap.add_argument("--wyjscie", required=True)
    ap.add_argument("--ziarno", type=int, default=14)
    ap.add_argument("--maly", action="store_true", help="zbiory małe: nauka, kalib, test")
    ap.add_argument("--pelny", action="store_true", help="zbiór pełnowymiarowy (~50 MB .bmp)")
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
        print(f"zbiory małe gotowe ({time.time() - t:.1f} s, {DEV})", flush=True)
    if a.pelny:
        W, H = ROZMIAR_PELNY
        generuj_zbior(os.path.join(a.wyjscie, "pelny"), a.ziarno + 4, W, H, 3, 3)
        print(f"zbiór pełnowymiarowy gotowy ({time.time() - t:.1f} s, {DEV})", flush=True)


if __name__ == "__main__":
    main()
