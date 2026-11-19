"""Metody wykrywania dodatków — wszystko na karcie (torch, CUDA). Na procesorze tylko
odczyt pliku .bmp i etykietowanie małej maski binarnej (spójne składowe).

Metody:
  A   piksele_para     — wyrównanie pary (skala X/Y + przesunięcie, korelacja fazowa), różnica
                         w dziedzinie tłumienia względem filtru maksimum wzorca (tolerancja ±r px)
  A0  piksele_para_r0  — ablacja: to samo bez filtru maksimum (r = 0)
  B   cechy_para       — różnica w przestrzeni cech ResNet18 (layer2, wagi ImageNet), dopasowanie 3×3
  C   model_typu       — tryb bez pary: model czystego obrazu typu naczepy (mediana + MAD z obrazów
                         wzorcowych), typ rozpoznany automatycznie (najlepsza korelacja)
"""
from __future__ import annotations

import glob
import math
import os

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from scipy import ndimage

SZER_ROBOCZA = 1200
Image.MAX_IMAGE_PIXELS = None


def urzadzenie():
    if not torch.cuda.is_available():
        raise SystemExit("BŁĄD: brak karty CUDA — liczenie na procesorze zabronione")
    return torch.device("cuda")


DEV = None


def dev():
    global DEV
    if DEV is None:
        DEV = urzadzenie()
    return DEV


# ---------------------------------------------------------------- wczytanie
def wczytaj(sciezka):
    """Plik .bmp → (tłumienie robocze [h, w] na karcie, jasność robocza, współczynnik zmniejszenia, rozmiar)."""
    img = np.asarray(Image.open(sciezka).convert("L"))
    H, W = img.shape
    t = torch.from_numpy(img).to(dev(), non_blocking=True).float()[None, None]
    f = max(1, math.ceil(W / SZER_ROBOCZA))
    if f > 1:
        t = F.avg_pool2d(t, f, ceil_mode=True)
    jas = t[0, 0]
    att = -torch.log((jas + 1.0) / 256.0)
    return att, jas, f, (W, H)


def _rozmyj(x, k):
    return F.avg_pool2d(x[None, None], k, 1, k // 2, count_include_pad=False)[0, 0]


def _maks(x, r):
    if r <= 0:
        return x
    return F.max_pool2d(x[None, None], 2 * r + 1, 1, r)[0, 0]


# ---------------------------------------------------------------- wyrównanie
def przeksztalc(P, sx, sy, dx, dy):
    """P_wyr(x, y) = P(sx·(x − dx), sy·(y − dy)); zwraca też maskę ważności. sx, sy, dx, dy: tensory [B]."""
    h, w = P.shape
    B = sx.shape[0]
    ys = torch.arange(h, device=P.device, dtype=torch.float32)
    xs = torch.arange(w, device=P.device, dtype=torch.float32)
    xsrc = sx[:, None] * (xs[None, :] - dx[:, None])            # [B, w]
    ysrc = sy[:, None] * (ys[None, :] - dy[:, None])            # [B, h]
    gx = (2 * xsrc / (w - 1) - 1)[:, None, :].expand(B, h, w)
    gy = (2 * ysrc / (h - 1) - 1)[:, :, None].expand(B, h, w)
    siatka = torch.stack([gx, gy], -1)
    wyn = F.grid_sample(P[None, None].expand(B, 1, h, w), siatka, mode="bilinear",
                        padding_mode="border", align_corners=True)[:, 0]
    wazne = (gx.abs() <= 1) & (gy.abs() <= 1)
    return wyn, wazne


def _przygotuj(a):
    hp = a - _rozmyj(a, 9) if a.dim() == 2 else a - F.avg_pool2d(a[:, None], 9, 1, 4, count_include_pad=False)[:, 0]
    h, w = hp.shape[-2:]
    okno = torch.hann_window(h, device=a.device)[:, None] * torch.hann_window(w, device=a.device)[None, :]
    hp = hp - hp.mean(dim=(-2, -1), keepdim=True)
    return hp * okno


def rejestruj(R, P, skale_x=None, skale_y=None):
    """Szuka (sx, sy, dx, dy) maksymalizujących korelację fazową; zwraca też wartość szczytu."""
    if skale_x is None:
        skale_x = torch.linspace(0.975, 1.025, 21)
    if skale_y is None:
        skale_y = torch.linspace(0.994, 1.006, 5)
    h, w = R.shape
    FR = torch.fft.rfft2(_przygotuj(R))
    najl = (-1.0, None)
    siatka = torch.cartesian_prod(skale_x, skale_y).to(R.device)
    for part in siatka.split(21):
        zero = torch.zeros(part.shape[0], device=R.device)
        Ps, _ = przeksztalc(P, part[:, 0], part[:, 1], zero, zero)
        FP = torch.fft.rfft2(_przygotuj(Ps))
        cp = FR[None] * FP.conj()
        cp = cp / (cp.abs() + 1e-9)
        r = torch.fft.irfft2(cp, s=(h, w))
        m, idx = r.flatten(1).max(1)
        b = int(m.argmax())
        if float(m[b]) > najl[0]:
            iy, ix = divmod(int(idx[b]), w)
            dy = iy - h if iy > h // 2 else iy
            dx = ix - w if ix > w // 2 else ix
            najl = (float(m[b]), (float(part[b, 0]), float(part[b, 1]), float(dx), float(dy)))
    return najl[1], najl[0]


def wyrownaj(R, P, par):
    sx, sy, dx, dy = par
    t = lambda v: torch.tensor([v], device=P.device, dtype=torch.float32)
    Pw, wazne = przeksztalc(P, t(sx), t(sy), t(dx), t(dy))
    wazne = (-_maks((~wazne[0]).float(), 3) + 1) > 0   # odsuń od krawędzi
    return Pw[0], wazne


# ---------------------------------------------------------------- mapy wyników (z-score)
def _mad(x):
    med = x.median()
    return med, 1.4826 * (x - med).abs().median() + 1e-6


def mapa_piksele(R, Rjas, Pw, wazne, r=2):
    """Dodatek = wzrost tłumienia. z = (P − max_r(R) − przesunięcie jasności) / szum lokalny."""
    surowa = Pw - R
    med = surowa[wazne].median()                        # różnica jasności (w log = przesunięcie)
    # szum w dziedzinie tłumienia ~ σ_I / I
    sig_I = 1.4826 * ((surowa - med) * Rjas)[wazne].abs().median() + 1e-6
    roznica = _rozmyj(Pw, 3) - _maks(_rozmyj(R, 3), r) - med
    z = roznica * Rjas.clamp(min=4.0) / (sig_I / 3.0)   # /3: rozmycie 3×3 zmniejsza szum ~3×
    return torch.where(wazne, z, torch.zeros_like(z))


_SIEC = None


def _siec():
    global _SIEC
    if _SIEC is None:
        import torchvision
        m = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.DEFAULT)
        _SIEC = torch.nn.Sequential(m.conv1, m.bn1, m.relu, m.maxpool, m.layer1, m.layer2).eval().to(dev())
    return _SIEC


def _cechy(a, med):
    x = ((a - med) / 2.5).clamp(0, 1)[None, None]
    x = F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)
    sr = torch.tensor([0.485, 0.456, 0.406], device=a.device)[None, :, None, None]
    od = torch.tensor([0.229, 0.224, 0.225], device=a.device)[None, :, None, None]
    with torch.no_grad():
        f = _siec()((x.expand(1, 3, -1, -1) - sr) / od)[0]
    return F.normalize(f, dim=0)


def mapa_cechy(R, Pw, wazne):
    med = (Pw - R)[wazne].median()
    fR, fP = _cechy(R, 0.0), _cechy(Pw, med)
    C, h, w = fR.shape
    pad = F.pad(fR[None], (1, 1, 1, 1), mode="replicate")[0]
    najl = torch.full((h, w), -1.0, device=R.device)
    for dy in range(3):
        for dx in range(3):
            najl = torch.maximum(najl, (fP * pad[:, dy:dy + h, dx:dx + w]).sum(0))
    s = 1 - najl
    wz = F.interpolate(wazne[None, None].float(), size=(h, w), mode="nearest")[0, 0] > 0.5
    med_s, mad = _mad(s[wz])
    z = (s - med_s) / mad
    z = torch.where(wz, z, torch.zeros_like(z))
    return F.interpolate(z[None, None], size=R.shape, mode="bilinear", align_corners=False)[0, 0]


class ModelTypu:
    """Tryb bez pary: model czystego obrazu dla każdego typu naczepy z katalogu nauka/<typ>/*.bmp."""

    def __init__(self, katalog_nauki):
        self.typy = {}
        for d in sorted(glob.glob(os.path.join(katalog_nauki, "*"))):
            pliki = sorted(glob.glob(os.path.join(d, "*.bmp")))
            if not pliki:
                continue
            wzor, wzor_jas, _, _ = wczytaj(pliki[0])
            stos = [wzor]
            for p in pliki[1:]:
                a, _, _, _ = wczytaj(p)
                par, _ = rejestruj(wzor, a)
                aw, wz = wyrownaj(wzor, a, par)
                aw = aw - (aw - wzor)[wz].median()
                stos.append(aw)
            S = torch.stack(stos)
            med = S.median(0).values
            mad = (S - med).abs().median(0).values
            self.typy[os.path.basename(d)] = dict(wzor=wzor, med=med, mad=mad, jas=wzor_jas)

    def rozpoznaj(self, P):
        najl = None
        for typ, m in self.typy.items():
            par, szczyt = rejestruj(m["wzor"], P)
            if najl is None or szczyt > najl[2]:
                najl = (typ, par, szczyt)
        return najl

    def mapa(self, P, r=2):
        typ, par, _ = self.rozpoznaj(P)
        m = self.typy[typ]
        Pw, wazne = wyrownaj(m["med"], P, par)
        surowa = Pw - m["med"]
        med = surowa[wazne].median()
        sig_I = 1.4826 * ((surowa - med) * m["jas"])[wazne].abs().median() + 1e-6
        sig = torch.sqrt((1.4826 * _maks(m["mad"], 1)) ** 2 + (sig_I / m["jas"].clamp(min=4.0)) ** 2)
        roznica = _rozmyj(Pw, 3) - _maks(_rozmyj(m["med"], 3), r) - med
        z = roznica / (_rozmyj(sig, 3) / 2.0)
        return torch.where(wazne, z, torch.zeros_like(z)), par, typ


# ---------------------------------------------------------------- mapa → ramki
def ramki(z, k, par, f, rozmiar, min_pole=12):
    """Spójne składowe z > k (po dylatacji 1 px) → ramki w układzie obrazu badanego (pełna rozdzielczość)."""
    maska = (_maks((z > k).float(), 1) > 0).cpu().numpy()
    et, n = ndimage.label(maska)
    if n == 0:
        return [], []
    pola = np.bincount(et.ravel())
    zc = z.cpu().numpy()
    sx, sy, dx, dy = par
    W, H = rozmiar
    wyn, oceny = [], []
    for i, sl in enumerate(ndimage.find_objects(et), 1):
        if sl is None or pola[i] < min_pole:
            continue
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        X0, X1 = sorted((sx * (x0 - dx) * f, sx * (x1 - dx) * f))
        Y0, Y1 = sorted((sy * (y0 - dy) * f, sy * (y1 - dy) * f))
        wyn.append([max(0, int(X0)), max(0, int(Y0)), min(W, int(math.ceil(X1))), min(H, int(math.ceil(Y1)))])
        oceny.append(round(float(zc[sl][et[sl] == i].max()), 2))
    return wyn, oceny
