"""Sondy na karcie OMENa (docs/pm/05-zalozenia.md, docs/pm/07-scenariusze-testow.md B1–B3).

  --przebieg p1 : kalibracja na 60 czystych parach (H-a), scalanie ramek (H-b), S1 (dobór wzorca × skrytka ×
                  strefa; Z1, Z2, Z4, Z11, Z14), S2 (grubość × szerokość robocza × czas × pamięć; Z6, Z7)
  --przebieg s3 : zbiory kontrolne KL, KW, KP, KS × rodzaj towaru podany / „nie wiem” × tryb para (A) i bez pary (C);
                  Z5, Z10, Z13 (A15, A15b, A16, A17, A18)

Progi zawsze z kalibracji (czyste pary kalib60), nigdy z testu. FP i FN osobno.
python skrypty/sondy.py --dane ~/dane/proba14/gen-v3 --przebieg p1 --wyniki wyniki/sondy
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anomalie import detektor as D  # noqa: E402
from anomalie import ocena as O     # noqa: E402

SIATKA_K = [3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 60, 80]
SCAL = 4          # px roboczych: żebro 3–5 px przy szer. 1200
TYPY = ["A", "B", "C"]


TEST_CPU = False   # tylko test kodu na ThinkPadzie (małe obrazy); liczby właściwe — karta OMENa


def sync():
    if not TEST_CPU:
        torch.cuda.synchronize()
    return time.perf_counter()


def opis(kat):
    return json.load(open(os.path.join(kat, "opis.json")))["obrazy"]


def prawda(kat):
    return O.wczytaj_prawde(os.path.join(kat, "badane"), os.path.join(kat, "maski"), os.path.join(kat, "opis.json"))


# ---------------------------------------------------------------- mapy
def _odloz(m):
    """Mapy zbioru trzymane w RAM (karta 4 GB), na kartę wracają w miejsca()."""
    m["z"] = m["z"].cpu()
    m["D"] = m["D"].cpu() if m.get("D") is not None else None
    return m


def mapa_A(kat, n, szer=D.SZER_ROBOCZA, r=2, roznice=True, odloz=True):
    t0 = sync()
    m = D.para(os.path.join(kat, "wzorce", n + ".bmp"), os.path.join(kat, "badane", n + ".bmp"), szer, r, zwroc_roznice=roznice)
    m["czas"] = sync() - t0
    return _odloz(m) if odloz else m


def mapa_C(model, kat, n, typ=None, bez=()):
    t0 = sync()
    P, _, f, rozm = D.wczytaj(os.path.join(kat, "badane", n + ".bmp"))
    z, par, typ_u, Dm = model.mapa(P, typ=typ, bez=bez, zwroc_roznice=True)
    return _odloz(dict(z=z, D=Dm, par=par, f=f, rozmiar=rozm, skala=1.0, strefy=model.typy[typ_u]["strefy"], typ=typ_u,
                       szczyt=model.ostatni_szczyt, pewnosc=model.ostatnia_pewnosc, czas=sync() - t0))


def miejsca(m, k, scal=0, zostaw=None):
    t0 = time.perf_counter()
    w = D.wykryj(m["z"].to(D.dev()), k, m["par"], m["f"], m["rozmiar"], strefy=m["strefy"], scal=scal, skala=m["skala"], zostaw=zostaw)
    return w, time.perf_counter() - t0


def predykcje(mapy, k, scal=0, metoda="", zostaw=None):
    obrazy = {}
    for n, m in mapy.items():
        w, dt = miejsca(m, k, scal, zostaw(n, _na_karte(m)) if zostaw else None)
        obrazy[n] = dict(ramki=[x["ramka"] for x in w], strefy=[x["strefa"] for x in w], oceny=[x["ocena"] for x in w],
                         pewnosci=[x["pewnosc"] for x in w], nazwy=[x["nazwa"] for x in w], opisy=[x["opis"] for x in w],
                         przedmioty=[x["przedmiot"] for x in w], czas_s=round(m["czas"] + dt, 3))
        for kl in ("typ", "szczyt", "pewnosc"):
            if kl in m:
                obrazy[n]["wzorzec_" + kl] = m[kl]
    return dict(metoda=metoda, k=k, scal=scal, obrazy=obrazy)


def _na_karte(m):
    return dict(m, D=m["D"].to(D.dev()) if m.get("D") is not None else None)


def k_obrazu(m, scal=0):
    """Najmniejsze k z siatki, przy którym czysta para nie ma żadnej ramki."""
    for k in SIATKA_K:
        if not miejsca(m, k, scal)[0]:
            return k
    return SIATKA_K[-1]


def kalibruj(mapy, scal=0):
    """Próg = największe k_obrazu na czystych parach kalibracji (zero ramek na każdej)."""
    return max(k_obrazu(m, scal) for m in mapy.values())


def wynik(etykieta, pr_obrazy, prawda_zb, plik=None):
    w = O.ocen(prawda_zb, pr_obrazy)
    print(O.linia(etykieta, w), flush=True)
    if plik:
        json.dump(pr_obrazy, open(plik, "w"), ensure_ascii=False)
    return w


def _fn_k(w):
    return (sum(v for t, v in w["fn_typ"].items() if t.endswith("_konstrukcja")),
            sum(v for t, v in w["n_typ"].items() if t.endswith("_konstrukcja")))


# ---------------------------------------------------------------- przebieg 1
def przebieg_p1(a, model, tab):
    dane = a.dane
    # --- kalibracja: 12 vs 60 czystych par; scalanie ramek
    print("\n== KALIBRACJA (H-a) i SCALANIE RAMEK (H-b) ==", flush=True)
    k12 = {n: mapa_A(os.path.join(dane, "kalib"), n) for n in opis(os.path.join(dane, "kalib"))}
    ok60 = opis(os.path.join(dane, "kalib60"))
    k60 = {n: mapa_A(os.path.join(dane, "kalib60"), n) for n in ok60}
    k60_r0 = {n: mapa_A(os.path.join(dane, "kalib60"), n, r=0) for n in ok60}
    k60_C = {n: mapa_C(model, os.path.join(dane, "kalib60"), n) for n in ok60 if not ok60[n]["ladunek"]}
    progi = {"A_k12": kalibruj(k12), "A_k60": kalibruj(k60), "A_k60_scal": kalibruj(k60, SCAL),
             "A0_k60": kalibruj(k60_r0), "C_k60": kalibruj(k60_C), "C_k60_scal": kalibruj(k60_C, SCAL)}
    print("progi:", progi, f"(C: {len(k60_C)} pustych par kalib60)", flush=True)
    kt = os.path.join(dane, "test")
    ot, pt = opis(kt), prawda(kt)
    mt = {n: mapa_A(kt, n) for n in ot}
    mt_r0 = {n: mapa_A(kt, n, r=0) for n in ot}
    W = {}
    W["A_k12"] = wynik(f"A para, próg z 12 par k={progi['A_k12']}", predykcje(mt, progi["A_k12"]), pt)
    W["A_k60"] = wynik(f"A para, próg z 60 par k={progi['A_k60']}", predykcje(mt, progi["A_k60"]), pt,
                       os.path.join(a.wyniki, "pred_test_A_k60.json"))
    W["A_k60_scal"] = wynik(f"A para, 60 par + scalanie {SCAL} px k={progi['A_k60_scal']}",
                            predykcje(mt, progi["A_k60_scal"], SCAL), pt, os.path.join(a.wyniki, "pred_test_A_k60_scal.json"))
    W["A0_k60"] = wynik(f"A0 para r=0, 60 par k={progi['A0_k60']}", predykcje(mt_r0, progi["A0_k60"]), pt)
    for key in ("A_k12", "A_k60", "A_k60_scal", "A0_k60"):
        tab.append(("test", key, progi[key], W[key]))

    # --- S1: dobór wzorca × skrytka × strefa
    print("\n== S1: dobór wzorca (i) właściwy / (ii) wymuszony błędny / (iii) katalog bez typu; KS typ D ==", flush=True)
    # próg podobieństwa (P16) z kalibracji: szczyt właściwego typu vs najlepszy szczyt po wyjęciu typu (kalib60)
    sz_ok, sz_brak = [], []
    for n in ok60:
        P, _, _, _ = D.wczytaj(os.path.join(dane, "kalib60", "badane", n + ".bmp"))
        typ = ok60[n]["typ_naczepy"]
        sz_ok.append(float(D.rejestruj(model.typy[typ]["wzor"], P)[1]))
        sz_brak.append(max(float(D.rejestruj(model.typy[t]["wzor"], P)[1]) for t in model.typy if t != typ))
    rozdz = min(sz_ok) > max(sz_brak)
    prog_sz = (min(sz_ok) + max(sz_brak)) / 2 if rozdz else float(np.median(sz_ok + sz_brak))
    print(f"kalib60 szczyt: właściwy min {min(sz_ok):.3f} med {np.median(sz_ok):.3f} | bez typu maks {max(sz_brak):.3f} "
          f"med {np.median(sz_brak):.3f} | rozdzielne: {'tak' if rozdz else 'NIE'} → próg podobieństwa {prog_sz:.3f}", flush=True)
    kC = progi["C_k60"]
    war = {}
    war["i"] = {n: mapa_C(model, kt, n) for n in ot}
    war["ii"] = {n: mapa_C(model, kt, n, typ=TYPY[(TYPY.index(ot[n]["typ_naczepy"]) + 1) % 3]) for n in ot}
    war["iii"] = {n: mapa_C(model, kt, n, bez=(ot[n]["typ_naczepy"],)) for n in ot}
    ks = os.path.join(dane, "KS")
    oks, pks = opis(ks), prawda(ks)
    mks_C = {n: mapa_C(model, ks, n) for n in oks}
    mks_A = {n: mapa_A(ks, n) for n in oks}
    s1 = {}
    for wk, mp in war.items():
        szc = [m["szczyt"] for m in mp.values()]
        flag = sum(s < prog_sz for s in szc)
        traf = sum(mp[n]["typ"] == ot[n]["typ_naczepy"] for n in mp)
        pr = predykcje(mp, kC, metoda=f"C_{wk}")
        w = wynik(f"S1 C ({wk}) k={kC}: wzorzec {traf}/{len(mp)} właściwy, flaga niepewny {flag}/{len(mp)}, "
                  f"szczyt med {np.median(szc):.3f} [{min(szc):.3f}–{max(szc):.3f}]", pr, pt,
                  os.path.join(a.wyniki, f"pred_test_C_{wk}.json"))
        for lad in (False, True):
            sub = {n: v for n, v in pt.items() if ot[n]["ladunek"] == lad}
            print("   " + O.linia(f"C ({wk}) ładunek={'tak' if lad else 'nie'}", O.ocen(sub, pr)), flush=True)
        s1[wk] = dict(flagi=flag, traf=traf, w=w, szczyt_med=float(np.median(szc)))
        tab.append(("test", f"C_{wk}", kC, w))
    pew = sorted(m["pewnosc"] for m in war["i"].values())
    print(f"pewność doboru (1 − drugi/najlepszy) w (i): min {pew[0]} med {pew[len(pew) // 2]}; (iii): "
          f"med {np.median([m['pewnosc'] for m in war['iii'].values()]):.3f}", flush=True)
    szk = [m["szczyt"] for m in mks_C.values()]
    wks_C = wynik(f"S1 KS typ D bez pary (C) k={kC}: dobrany {[m['typ'] for m in mks_C.values()]}, "
                  f"flaga niepewny {sum(s < prog_sz for s in szk)}/{len(szk)} (szczyt {['%.3f' % s for s in szk]})",
                  predykcje(mks_C, kC), pks)
    wks_A = wynik(f"S1 KS typ D, wzorzec wskazany z pliku (A) k={progi['A_k60']}", predykcje(mks_A, progi["A_k60"]), pks)
    tab.append(("KS", "C_auto", kC, wks_C))
    tab.append(("KS", "A_z_pliku", progi["A_k60"], wks_A))
    wa = W["A_k60"]
    print(f"S1 strefa trafna: A {wa['strefa_ok']}/{wa['strefa_n']}, C(i) {s1['i']['w']['strefa_ok']}/{s1['i']['w']['strefa_n']}", flush=True)

    # --- S2: grubość × szerokość robocza
    print("\n== S2: grubość małego dodatku w podwójnej podłodze × szerokość robocza (1200 / 3000 / pełna 12000) ==", flush=True)
    km, kp, kpel = os.path.join(dane, "km"), os.path.join(dane, "kalib_pelny"), os.path.join(dane, "pelny")
    okm, pkm, okp, opel, ppel = opis(km), prawda(km), opis(kp), opis(kpel), prawda(kpel)
    s2 = {}
    for szer in (1200, 3000, 12000):
        try:
            if not TEST_CPU:
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
            # po jednym obrazie naraz: mapa 12000 × 4200 nie mieści się w zbiorze na karcie
            k = max(k_obrazu(mapa_A(kp, n, szer, roznice=False, odloz=False)) for n in okp)
            fn_g, n_g, cz = {}, {}, []
            for n in okm:
                m = mapa_A(km, n, szer, roznice=False, odloz=False)
                w_, dt = miejsca(m, k)
                cz.append(m["czas"] + dt)
                dod = pkm[n][0]
                g = okm[n]["dodatki"][0].get("grubosc_px")
                n_g[g] = n_g.get(g, 0) + 1
                fn_g[g] = fn_g.get(g, 0) + (not any(O.wskazuje(x["ramka"], dod) for x in w_))
                del m
            fp = sum(bool(miejsca(mapa_A(kpel, n, szer, roznice=False, odloz=False), k)[0]) for n in opel if not ppel[n])
            pam = 0 if TEST_CPU else torch.cuda.max_memory_allocated() / 2**20
            krzywa = " ".join(f"{g}px:{fn_g[g]}/{n_g[g]}" for g in sorted(n_g, key=lambda x: (x is None, x)))
            print(f"WYNIK S2 szer={szer} k={k} (kalib_pelny 6 czystych): FN od grubości (px pełnej rozdz.) {krzywa} "
                  f"= {sum(fn_g.values())}/{sum(n_g.values())} | FP pelny {fp}/{sum(not v for v in ppel.values())} czystych | "
                  f"czas/obraz {np.mean(cz):.2f} s (maks {max(cz):.2f}) | {60 / np.mean(cz):.1f} obrazów/min | "
                  f"pamięć karty szczyt {pam:.0f} MiB", flush=True)
            s2[szer] = dict(k=k, fn={str(g): v for g, v in fn_g.items()}, n={str(g): v for g, v in n_g.items()}, fp=fp,
                            czas=float(np.mean(cz)), maks=max(cz), pam=pam)
        except torch.cuda.OutOfMemoryError as e:
            print(f"WYNIK S2 szer={szer}: BRAK PAMIĘCI KARTY ({str(e)[:120]})", flush=True)
            s2[szer] = dict(oom=True)
            torch.cuda.empty_cache()
    json.dump(dict(progi=progi, prog_podobienstwa=prog_sz, s2={str(k): v for k, v in s2.items()},
                   s1={k: dict(flagi=v["flagi"], traf=v["traf"], szczyt_med=v["szczyt_med"]) for k, v in s1.items()}),
              open(os.path.join(a.wyniki, "p1.json"), "w"), indent=1, default=str)


# ---------------------------------------------------------------- przebieg S3
def przebieg_s3(a, model, tab):
    dane = a.dane
    ok60 = opis(os.path.join(dane, "kalib60"))
    k60 = {n: mapa_A(os.path.join(dane, "kalib60"), n) for n in ok60}
    k60_C = {n: mapa_C(model, os.path.join(dane, "kalib60"), n) for n in ok60 if not ok60[n]["ladunek"]}
    kA, kC = kalibruj(k60, a.scal), kalibruj(k60_C, a.scal)
    del k60, k60_C
    # reguła towaru: progi z katalogu wyglądu towaru (czyste pary pusta → załadowana), osobno dla A i C
    kt = os.path.join(dane, "towar")
    otw = opis(kt)
    regA, regC = D.RegulaTowaru(), D.RegulaTowaru()
    for n, o in otw.items():
        m = mapa_A(kt, n)
        regA.dodaj(o["rodzaj_towaru"], _na_karte(m)["D"], m["strefy"])
        m = mapa_C(model, kt, n)
        regC.dodaj(o["rodzaj_towaru"], _na_karte(m)["D"], m["strefy"])
    pA, pC = regA.zamknij(), regC.zamknij()
    print(f"progi: A k={kA}, C k={kC} (kalib60, scalanie {a.scal} px) | reguła towaru (t1 top-hat, t2 gęstość) "
          f"A: { {r: tuple(round(x, 3) for x in v) for r, v in pA.items()} } | "
          f"C: { {r: tuple(round(x, 3) for x in v) for r, v in pC.items()} }", flush=True)
    # kontrola: katalog towaru z regułą — czy towar zgodny zostaje wygaszony na danych, z których są progi
    print("\n== S3: zbiory kontrolne × rodzaj towaru (podany / „nie wiem”) × tryb (A para / C bez pary) ==", flush=True)
    s3 = {}
    zbiory = ["KL", "KW", "KP", "KS", "test"]
    for zb in zbiory:
        kat = os.path.join(dane, zb)
        oz, pz = opis(kat), prawda(kat)
        mA = {n: mapa_A(kat, n) for n in oz}
        mC = {n: mapa_C(model, kat, n) for n in oz}
        for tryb, mp, k, reg in (("A", mA, kA, regA), ("C", mC, kC, regC)):
            for rz in ("podany", "nie wiem"):
                if zb == "test" and rz == "nie wiem":
                    continue
                zost = None
                if rz == "podany":
                    zost = lambda n, m, reg=reg, oz=oz: reg.maska_zostaw(oz[n]["rodzaj_towaru"], m["D"], m["strefy"])
                pr = predykcje(mp, k, a.scal, f"{tryb}_{zb}_{rz}", zost)
                rodz = sorted({oz[n]["rodzaj_towaru"] for n in oz})
                w = wynik(f"S3 {zb} {tryb} rodzaj={rz} {rodz if rz == 'podany' else ''} k={k}", pr, pz,
                          os.path.join(a.wyniki, f"pred_s3_{zb}_{tryb}_{rz.replace(' ', '_')}.json"))
                if zb == "KS" and tryb == "C":
                    print(f"   KS C: szczyt doboru {[m['szczyt'] for m in mC.values()]}, typ {[m['typ'] for m in mC.values()]}")
                if zb == "test":
                    for lad in (False, True):
                        sub = {n: v for n, v in pz.items() if oz[n]["ladunek"] == lad}
                        print("   " + O.linia(f"test {tryb} rodzaj podany, ładunek={'tak' if lad else 'nie'}", O.ocen(sub, pr)))
                s3[(zb, tryb, rz)] = w
                tab.append((zb, f"{tryb} rodzaj {rz}", k, w))
        del mA, mC
    json.dump({"|".join(k): {x: v[x] for x in ("czyste_z_alarmem", "czyste", "przeoczone", "dodatki", "alarmy_ladownia",
                                               "obrazy_z_alarmem_ladowni", "obrazy", "kolejnosc_ok", "kolejnosc_n", "p1_ok")}
               for k, v in s3.items()}, open(os.path.join(a.wyniki, "s3.json"), "w"), indent=1)


def tabela(tab, plik):
    with open(plik, "w") as f:
        f.write("| zbiór | wariant | k | FP (czyste z alarmem) | obszary na czystych | FN (dodatki) | FN konstrukcja | "
                "alarm na ładunku (aut / ramek) | strefa trafna | miejsc na auto (śr / maks) | czas/obraz [s] |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n")
        for zb, war, k, w in tab:
            fk, nk = _fn_k(w)
            ra = w["ramki_na_auto"]
            cz = np.mean(w["czasy"]) if w["czasy"] else float("nan")
            f.write(f"| {zb} | {war} | {k} | {w['czyste_z_alarmem']}/{w['czyste']} | {w['obszary_na_czystych']} | "
                    f"{w['przeoczone']}/{w['dodatki']} | {fk}/{nk} | {w['obrazy_z_alarmem_ladowni']}/{w['obrazy']} / "
                    f"{w['alarmy_ladownia']} | {w['strefa_ok']}/{w['strefa_n']} | {np.mean(ra):.1f} / {max(ra)} | {cz:.2f} |\n")
    print("\n" + open(plik).read(), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dane", required=True)
    ap.add_argument("--przebieg", choices=["p1", "s3"], required=True)
    ap.add_argument("--wyniki", default="wyniki/sondy")
    ap.add_argument("--scal", type=int, default=SCAL)
    ap.add_argument("--test-cpu", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()
    os.makedirs(a.wyniki, exist_ok=True)
    global TEST_CPU
    if a.test_cpu:
        TEST_CPU, D.DEV = True, torch.device("cpu")
        _rej = D.rejestruj   # mała siatka skal: tylko żeby kod przeszedł w rozsądnym czasie
        D.rejestruj = lambda R, P, skale_x=None, skale_y=None: _rej(R, P, torch.linspace(0.985, 1.015, 3), torch.ones(1))
    else:
        D.dev()
        print(f"KARTA: {torch.cuda.get_device_name(0)} | torch {torch.__version__} CUDA {torch.version.cuda}", flush=True)
    model = D.ModelTypu(os.path.join(a.dane, "nauka"))
    tab = []
    t = time.time()
    (przebieg_p1 if a.przebieg == "p1" else przebieg_s3)(a, model, tab)
    tabela(tab, os.path.join(a.wyniki, f"tabela_{a.przebieg}.md"))
    print(f"czas przebiegu {time.time() - t:.0f} s", flush=True)


if __name__ == "__main__":
    main()
