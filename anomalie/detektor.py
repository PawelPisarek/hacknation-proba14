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
# Pole wejścia „rodzaj towaru” (P15, P17): opcjonalne; „nie wiem” → zaznaczamy wszystko,
# „pusta naczepa” → każdy przedmiot w ładowni to alarm; rodzaj z listy → reguła towaru (RegulaTowaru).
RODZAJE_TOWARU = ["sprzęt i AGD", "odzież i tekstylia", "żywność i napoje", "materiały budowlane", "inne",
                  "nie wiem", "pusta naczepa"]
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
# ---------------------------------------------------------------- wczytanie
def wczytaj(sciezka, szer=SZER_ROBOCZA):
    """Plik .bmp → (tłumienie robocze [h, w] na karcie, jasność robocza, współczynnik zmniejszenia, rozmiar).
    szer: szerokość robocza (1200 domyślnie; None albo ≥ W = pełna rozdzielczość, B11)."""
    img = np.asarray(Image.open(sciezka).convert("L"))
    H, W = img.shape
    t = torch.from_numpy(img).to(dev(), non_blocking=True).float()[None, None]
    del img
    f = max(1, math.ceil(W / szer)) if szer else 1
    if f > 1:
        t = F.avg_pool2d(t, f, ceil_mode=True)
    jas = t[0, 0]
    att = -torch.log((jas + 1.0) / 256.0)
    return att, jas, f, (W, H)


STREFY = ["poza naczepą", "ładownia", "podłoga", "ściana przednia", "rama/osie", "dach"]
LADOWNIA = 1


def wczytaj_strefy(sciezka_bmp, f, ksztalt):
    """Mapa stref wzorca (<nazwa>.strefy.png obok .bmp; katalog wzorców, spec §4a) w układzie roboczym; brak → None."""
    p = os.path.splitext(sciezka_bmp)[0] + ".strefy.png"
    if not os.path.exists(p):
        return None
    m = np.asarray(Image.open(p))[::f, ::f]
    h, w = ksztalt
    out = np.zeros((h, w), np.uint8)
    out[:min(h, m.shape[0]), :min(w, m.shape[1])] = m[:h, :w]
    return out


def _rozmyj(x, k):
    return F.avg_pool2d(x[None, None], k, 1, k // 2, count_include_pad=False)[0, 0]


def _maks(x, r):
    if r <= 0:
        return x
    return F.max_pool2d(x[None, None], 2 * r + 1, 1, r)[0, 0]


def _min(x, r):
    return -_maks(-x, r)


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


def mapa_piksele(R, Rjas, Pw, wazne, r=2, zwroc_roznice=False):
    """Dodatek = wzrost tłumienia. z = (P − max_r(R) − przesunięcie jasności) / szum lokalny.
    zwroc_roznice → także D = różnica tłumienia bez tolerancji (do reguły towaru)."""
    surowa = Pw - R
    med = surowa[wazne].median()                        # różnica jasności (w log = przesunięcie)
    # szum w dziedzinie tłumienia ~ σ_I / I
    sig_I = 1.4826 * ((surowa - med) * Rjas)[wazne].abs().median() + 1e-6
    del surowa
    Pr, Rr = _rozmyj(Pw, 3), _rozmyj(R, 3)
    roznica = Pr - _maks(Rr, r) - med
    z = roznica * Rjas.clamp(min=4.0) / (sig_I / 3.0)   # /3: rozmycie 3×3 zmniejsza szum ~3×
    z = torch.where(wazne, z, torch.zeros_like(z))
    if zwroc_roznice:
        return z, torch.where(wazne, Pr - Rr - med, torch.zeros_like(z))
    return z


def para(sciezka_R, sciezka_P, szer=SZER_ROBOCZA, r=2, zwroc_roznice=False):
    """Tryb z parą (metoda A) w dowolnej szerokości roboczej. Rejestracja zawsze na szer. 1200
    (siatka skal × FFT nie mieści się w 4 GB w pełnej rozdzielczości), parametry przeliczane.
    Zwraca dict(z, D, par, f, rozmiar, strefy)."""
    R, Rj, f, rozm = wczytaj(sciezka_R)
    P, _, _, _ = wczytaj(sciezka_P)
    par_lo, _ = rejestruj(R, P)
    if szer != SZER_ROBOCZA:
        del R, Rj, P
        R, Rj, f_hi, rozm = wczytaj(sciezka_R, szer)
        P, _, _, _ = wczytaj(sciezka_P, szer)
        c = f / f_hi
        par_hi = (par_lo[0], par_lo[1], par_lo[2] * c, par_lo[3] * c)
        r_hi = max(r, round(r * c)) if r else 0
        f = f_hi
    else:
        par_hi, r_hi, c = par_lo, r, 1.0
    Pw, wazne = wyrownaj(R, P, par_hi)
    del P
    wyn = mapa_piksele(R, Rj, Pw, wazne, r=r_hi, zwroc_roznice=zwroc_roznice)
    z, D = wyn if zwroc_roznice else (wyn, None)
    return dict(z=z, D=D, par=par_hi, f=f, rozmiar=rozm, skala=c, strefy=wczytaj_strefy(sciezka_R, f, z.shape))


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
            wzor, wzor_jas, f, _ = wczytaj(pliki[0])
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
            self.typy[os.path.basename(d)] = dict(wzor=wzor, med=med, mad=mad, jas=wzor_jas,
                                                  strefy=wczytaj_strefy(pliki[0], f, wzor.shape))

    def rozpoznaj(self, P, bez=()):
        """Dobór wzorca: typ z najwyższym szczytem korelacji; pewność = 1 − drugi/najlepszy szczyt.
        bez: typy wyjęte z katalogu (sonda S1, warunek iii)."""
        wyn = sorted(((rejestruj(m["wzor"], P), typ) for typ, m in self.typy.items() if typ not in bez),
                     key=lambda x: -x[0][1])
        (par, szczyt), typ = wyn[0]
        pewnosc = 1 - wyn[1][0][1] / szczyt if len(wyn) > 1 else 1.0
        self.ostatnia_pewnosc = round(float(pewnosc), 3)
        self.ostatni_szczyt = round(float(szczyt), 4)
        return typ, par, szczyt

    def mapa(self, P, r=2, rodzaj_towaru=None, typ=None, bez=(), zwroc_roznice=False):
        """typ: wymuszony typ wzorca (S1 ii); bez: typy wyjęte z katalogu (S1 iii).
        rodzaj_towaru działa w wykryj() (RegulaTowaru), tu bez wpływu."""
        if typ is None:
            typ, par, _ = self.rozpoznaj(P, bez)
        else:
            par, szczyt = rejestruj(self.typy[typ]["wzor"], P)
            self.ostatni_szczyt, self.ostatnia_pewnosc = round(float(szczyt), 4), None
        m = self.typy[typ]
        Pw, wazne = wyrownaj(m["med"], P, par)
        surowa = Pw - m["med"]
        med = surowa[wazne].median()
        sig_I = 1.4826 * ((surowa - med) * m["jas"])[wazne].abs().median() + 1e-6
        sig = torch.sqrt((1.4826 * _maks(m["mad"], 1)) ** 2 + (sig_I / m["jas"].clamp(min=4.0)) ** 2)
        Pr, Mr = _rozmyj(Pw, 3), _rozmyj(m["med"], 3)
        roznica = Pr - _maks(Mr, r) - med
        z = torch.where(wazne, roznica / (_rozmyj(sig, 3) / 2.0), torch.zeros_like(roznica))
        if zwroc_roznice:
            return z, par, typ, torch.where(wazne, Pr - Mr - med, torch.zeros_like(z))
        return z, par, typ


# ---------------------------------------------------------------- reguła rodzaju towaru (P15, P17, spec §4)
L_OTWARCIA = 61   # px roboczych (szer. 1200): dłuższe niż dodatek „w ładunku” (≤ 48 × 50 px)


def cechy_towaru(D):
    """Dwie cechy różnicy D w ładowni: (1) top-hat — gęstość ponad otwarcie liniami poziomą i pionową
    (zostają bryły i długie elementy towaru, znika mały zwarty przedmiot); (2) sama gęstość D.
    Obie po erozji 3×3 (wymagają podparcia ≥ 3×3 px)."""
    h = L_OTWARCIA // 2
    x = D[None, None]
    otw_poz = F.max_pool2d(-F.max_pool2d(-x, (1, L_OTWARCIA), 1, (0, h)), (1, L_OTWARCIA), 1, (0, h))
    otw_pion = F.max_pool2d(-F.max_pool2d(-x, (L_OTWARCIA, 1), 1, (h, 0)), (L_OTWARCIA, 1), 1, (h, 0))
    tophat = (x - torch.maximum(otw_poz, otw_pion))[0, 0]
    return _min(tophat, 1), _min(D, 1)


class RegulaTowaru:
    """„Towar zgodny ze zgłoszeniem nie dostaje ramki” (P15): różnica w ładowni, którą wyjaśnia wybrany rodzaj
    towaru, jest wygaszana; zostaje to, co wykracza poza wygląd tego rodzaju — małe zwarte zgęszczenie
    (top-hat > t1) albo gęstość większa niż ten towar daje (D > t2). Progi t1, t2 na rodzaj z katalogu wyglądu
    towaru (czyste pary: pusta naczepa → załadowana), max × zapas. „nie wiem” i „pusta naczepa” → bez wygaszania."""

    def __init__(self, zapas=1.1):
        self.progi = {}
        self.zapas = zapas
        self._zbior = {}

    def dodaj(self, rodzaj, D, strefy):
        if strefy is None:
            return
        t, d = cechy_towaru(D)
        lad = torch.from_numpy(strefy == LADOWNIA).to(D.device)
        a = self._zbior.setdefault(rodzaj, [0.0, 0.0])
        a[0] = max(a[0], float(t[lad].max()))
        a[1] = max(a[1], float(d[lad].max()))

    def zamknij(self):
        self.progi = {r: (v[0] * self.zapas, v[1] * self.zapas) for r, v in self._zbior.items()}
        return self.progi

    def maska_zostaw(self, rodzaj, D, strefy):
        """True = piksel może dać ramkę. None, gdy reguła nie działa (nie wiem / pusta naczepa / brak stref)."""
        if rodzaj not in self.progi or strefy is None or D is None:
            return None
        t1, t2 = self.progi[rodzaj]
        t, d = cechy_towaru(D)
        zost = _maks(((t > t1) | (d > t2)).float(), 2) > 0
        lad = torch.from_numpy(strefy == LADOWNIA).to(D.device)
        return zost | ~lad


# ---------------------------------------------------------------- mapa → miejsca
def _polozenie(strefy, cx):
    if strefy is None:
        return None
    kol = np.nonzero((strefy > 0).any(0))[0]
    if not len(kol):
        return None
    u = (cx - kol[0]) / max(1, kol[-1] - kol[0])
    return "przód" if u < 1 / 3 else ("środek" if u < 2 / 3 else "tył")


def wykryj(z, k, par, f, rozmiar, strefy=None, scal=0, min_pole=12, skala=1.0, zostaw=None):
    """Spójne składowe z > k → miejsca od najpewniejszego (P7). Każde: ramka w układzie badanego (pełna rozdz.),
    ocena (maks. z), pewność 50–99% = f(ocena ÷ próg) (spec §5), strefa (największe pokrycie, §4a),
    przedmiot kontroli = strefa + przód/środek/tył (§4a), opis bez miar (P19).
    scal: składowe bliżej niż `scal` px roboczych łączone w jedno miejsce (np. dodatek przecięty żebrem).
    skala: f_1200 / f — przelicza min_pole i scal przy innej szerokości roboczej. zostaw: maska reguły towaru."""
    maska = _maks((z > k).float(), 1) > 0
    if zostaw is not None:
        maska &= zostaw
    s_eff = round(scal * skala)
    grupy = _maks(maska.float(), s_eff) > 0 if s_eff > 0 else maska
    maska, grupy = maska.cpu().numpy(), grupy.cpu().numpy()
    et, n = ndimage.label(grupy)
    if n == 0:
        return []
    et = et * maska
    pola = np.bincount(et.ravel(), minlength=n + 1)
    mp = max(1, round(min_pole * skala * skala))
    zc = z.cpu().numpy()
    sx, sy, dx, dy = par
    W, H = rozmiar
    kol = np.nonzero((strefy > 0).any(0))[0] if strefy is not None else None
    dl_naczepy = (kol[-1] - kol[0]) if kol is not None and len(kol) else z.shape[1]
    wyn = []
    for i, sl in enumerate(ndimage.find_objects(et), 1):
        if sl is None or pola[i] < mp:
            continue
        lok = et[sl] == i
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        X0, X1 = sorted((sx * (x0 - dx) * f, sx * (x1 - dx) * f))
        Y0, Y1 = sorted((sy * (y0 - dy) * f, sy * (y1 - dy) * f))
        ocena = float(zc[sl][lok].max())
        strefa = None
        if strefy is not None:
            strefa = STREFY[int(np.bincount(strefy[sl][lok].ravel(), minlength=len(STREFY)).argmax())]
        pol = _polozenie(strefy, (x0 + x1) / 2)
        frac = (x1 - x0) / max(1, dl_naczepy)
        wielk = f"ok. 1/{max(2, round(1 / frac))} długości naczepy" if frac >= 0.08 else "mały obszar"
        nazwa = f"{(strefa or 'miejsce').capitalize()} — {pol}" if pol else (strefa or "miejsce").capitalize()
        wyn.append(dict(ramka=[max(0, int(X0)), max(0, int(Y0)), min(W, int(math.ceil(X1))), min(H, int(math.ceil(Y1)))],
                        ocena=round(ocena, 2), pewnosc=int(min(99, max(50, round(50 + 49 * (1 - k / max(ocena, k)))))),
                        strefa=strefa, polozenie=pol, nazwa=nazwa,
                        przedmiot=f"{strefa} ({pol})" if strefa and pol else strefa,
                        opis=f"{strefa or 'miejsce'}: gęściej niż wzorzec, {wielk}"))
    return sorted(wyn, key=lambda m: -m["ocena"])


def ramki(z, k, par, f, rozmiar, min_pole=12, z_opisem=False):
    """Zgodność z przebiegiem S0: (ramki, oceny[, opisy])."""
    m = wykryj(z, k, par, f, rozmiar, min_pole=min_pole)
    wyn, oc = [x["ramka"] for x in m], [x["ocena"] for x in m]
    if not z_opisem:
        return wyn, oc
    return wyn, oc, [f"gęstsze niż wzorzec ({o:.0f}× ponad szum), {r[2] - r[0]}×{r[3] - r[1]} px" for r, o in zip(wyn, oc)]
