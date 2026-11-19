"""Wynik bazowy: metody A, A0, B, C w jednym przebiegu na karcie.

1. próg k każdej metody dobrany na zbiorze kalib (same czyste): najmniejsze k bez alarmu
   (C: tylko obrazy bez ładunku — model czystego typu nie zna ładunku zgłoszonego);
2. ocena na zbiorze test (+ tabela dla całej siatki k, do wglądu);
3. zbiór pełnowymiarowy (~50 MB .bmp): ocena + czas na obraz od odczytu pliku do ramek, pamięć karty.

python skrypty/bazowy.py --dane ~/dane/proba14/gen-v2 --wyniki wyniki/bazowy
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anomalie import detektor as D  # noqa: E402
from anomalie import ocena as O     # noqa: E402
from anomalie import raport as RAP  # noqa: E402

PROG_PEWNOSCI = 0.2  # założenie: poniżej — flaga „wzorzec niepewny” (P16)
SIATKA_K = [3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40]
METODY = ["A_piksele_para", "A0_piksele_para_r0", "B_cechy_para", "C_model_typu"]


def synchronizuj():
    torch.cuda.synchronize()
    return time.perf_counter()


def mapy_zbioru(katalog, model, metody=METODY):
    """Dla każdej pary: {metoda: (z, par, f, rozmiar, czas_s)}; czas = od odczytu plików do mapy."""
    opis = json.load(open(os.path.join(katalog, "opis.json")))["obrazy"]
    wyn = {}
    for nazwa in sorted(opis):
        wyn[nazwa] = {}
        for m in metody:
            t0 = synchronizuj()
            if m == "C_model_typu":
                P, _, f, rozm = D.wczytaj(os.path.join(katalog, "badane", nazwa + ".bmp"))
                z, par, typ = model.mapa(P)
                wyn[nazwa]["typ_rozpoznany"] = typ
                wyn[nazwa]["pewnosc_wzorca"] = model.ostatnia_pewnosc
            else:
                R, Rj, f, _ = D.wczytaj(os.path.join(katalog, "wzorce", nazwa + ".bmp"))
                P, _, f, rozm = D.wczytaj(os.path.join(katalog, "badane", nazwa + ".bmp"))
                par, _ = D.rejestruj(R, P)
                Pw, wazne = D.wyrownaj(R, P, par)
                if m == "A_piksele_para":
                    z = D.mapa_piksele(R, Rj, Pw, wazne, r=2)
                elif m == "A0_piksele_para_r0":
                    z = D.mapa_piksele(R, Rj, Pw, wazne, r=0)
                else:
                    z = D.mapa_cechy(R, Pw, wazne)
            t1 = synchronizuj()
            wyn[nazwa][m] = (z, par, f, rozm, t1 - t0)
    return opis, wyn


def predykcje(mapy, m, k, dodaj_czas_ramek=True):
    obrazy = {}
    for nazwa, d in mapy.items():
        z, par, f, rozm, czas = d[m]
        t0 = time.perf_counter()
        r, oc, op = D.ramki(z, k, par, f, rozm, z_opisem=True)
        obrazy[nazwa] = dict(ramki=r, oceny=oc, opisy=op, czas_s=round(czas + (time.perf_counter() - t0), 3))
        if "pewnosc_wzorca" in d and m == "C_model_typu":
            obrazy[nazwa]["pewnosc_wzorca"] = d["pewnosc_wzorca"]
            obrazy[nazwa]["wzorzec_niepewny"] = d["pewnosc_wzorca"] < PROG_PEWNOSCI
    return dict(metoda=m, k=k, obrazy=obrazy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dane", required=True)
    ap.add_argument("--wyniki", default="wyniki/bazowy")
    a = ap.parse_args()
    os.makedirs(a.wyniki, exist_ok=True)
    D.dev()
    print(f"KARTA: {torch.cuda.get_device_name(0)} | torch {torch.__version__} CUDA {torch.version.cuda}", flush=True)
    t = time.time()
    model = D.ModelTypu(os.path.join(a.dane, "nauka"))
    print(f"model czystego obrazu: typy {sorted(model.typy)} ({time.time() - t:.1f} s)", flush=True)
    D._siec()  # wagi ResNet18 (raz, do ~/.cache)

    # --- kalibracja progu na czystych
    opis_k, mapy_k = mapy_zbioru(os.path.join(a.dane, "kalib"), model)
    progi = {}
    for m in METODY:
        nazwy = [n for n in mapy_k if m != "C_model_typu" or not opis_k[n]["ladunek"]]
        sub = {n: mapy_k[n] for n in nazwy}
        k_wyb = SIATKA_K[-1]
        for k in SIATKA_K:
            if sum(len(v["ramki"]) for v in predykcje(sub, m, k)["obrazy"].values()) == 0:
                k_wyb = k
                break
        progi[m] = k_wyb
    print("progi z kalibracji (czyste, kalib):", progi, flush=True)

    # --- test
    kat = os.path.join(a.dane, "test")
    opis_t, mapy_t = mapy_zbioru(kat, model)
    prawda = O.wczytaj_prawde(os.path.join(kat, "badane"), os.path.join(kat, "maski"), os.path.join(kat, "opis.json"))
    tabela = []
    print("\n== TEST (mały, 1200×420) — próg z kalibracji ==")
    for m in METODY:
        pr = predykcje(mapy_t, m, progi[m])
        json.dump(pr, open(os.path.join(a.wyniki, f"predykcje_test_{m}.json"), "w"))
        w = O.ocen(prawda, pr)
        print(O.linia(f"{m} k={progi[m]}", w))
        if m == "C_model_typu":
            for lad in (False, True):
                pd = {n: v for n, v in prawda.items() if opis_t[n]["ladunek"] == lad}
                print("   " + O.linia(f"{m} ładunek={'tak' if lad else 'nie'}", O.ocen(pd, pr)))
        tabela.append((m, progi[m], w))
    trafne = sum(opis_t[n].get("typ_naczepy") == mapy_t[n].get("typ_rozpoznany") for n in opis_t)
    print(f"C: typ naczepy rozpoznany {trafne}/{len(opis_t)}")
    print("C: dobór wzorca bez pary (typ z biblioteki 3 typów) — trafny {}/{}".format(trafne, len(opis_t)))
    pw = sorted(mapy_t[n]["pewnosc_wzorca"] for n in mapy_t)
    print(f"C: pewność doboru wzorca min {pw[0]} mediana {pw[len(pw) // 2]} | niepewnych (< {PROG_PEWNOSCI}): {sum(p < PROG_PEWNOSCI for p in pw)}/{len(pw)}")
    for m in ("A_piksele_para", "C_model_typu"):
        pr = json.load(open(os.path.join(a.wyniki, f"predykcje_test_{m}.json")))
        for n in [x for x in sorted(opis_t) if not opis_t[x]["czysty"]][:3]:
            o = pr["obrazy"][n]
            print(f"raport {m} {n}: " + RAP.raport(os.path.join(kat, "badane", n + ".bmp"), o["ramki"], o["oceny"],
                  o["opisy"], os.path.join(a.wyniki, "raporty", m)))
    print("\n== siatka k (test, do wglądu; wybór progu tylko z kalib) ==")
    for m in METODY:
        wiersz = []
        for k in SIATKA_K:
            w = O.ocen(prawda, predykcje(mapy_t, m, k))
            wiersz.append(f"k={k}: FP {w['czyste_z_alarmem']}/{w['czyste']} FN {w['przeoczone']}/{w['dodatki']}")
        print(m + " | " + " | ".join(wiersz))

    # --- pełnowymiarowe
    kat = os.path.join(a.dane, "pelny")
    torch.cuda.reset_peak_memory_stats()
    opis_p, mapy_p = mapy_zbioru(kat, model)
    prawda_p = O.wczytaj_prawde(os.path.join(kat, "badane"), os.path.join(kat, "maski"), os.path.join(kat, "opis.json"))
    roz = os.path.getsize(os.path.join(kat, "badane", sorted(opis_p)[0] + ".bmp")) / 1e6
    print(f"\n== PEŁNOWYMIAROWE ({len(opis_p)} par, plik {roz:.1f} MB) — czas od odczytu .bmp do ramek ==")
    wyniki_p = {}
    for m in METODY:
        pr = predykcje(mapy_p, m, progi[m])
        json.dump(pr, open(os.path.join(a.wyniki, f"predykcje_pelny_{m}.json"), "w"))
        w = O.ocen(prawda_p, pr)
        wyniki_p[m] = w
        print(O.linia(f"{m} k={progi[m]}", w))
    trafne = sum(opis_p[n]["typ_naczepy"] == mapy_p[n].get("typ_rozpoznany") for n in opis_p)
    print(f"C pełne: dobór wzorca trafny {trafne}/{len(opis_p)}")
    pr = json.load(open(os.path.join(a.wyniki, "predykcje_pelny_C_model_typu.json")))
    n = [x for x in sorted(opis_p) if not opis_p[x]["czysty"]][0]
    o = pr["obrazy"][n]
    print(f"raport C pełny {n}: " + RAP.raport(os.path.join(kat, "badane", n + ".bmp"), o["ramki"], o["oceny"], o["opisy"],
          os.path.join(a.wyniki, "raporty", "pelny")))
    print(f"pamięć karty (szczyt): {torch.cuda.max_memory_allocated() / 2**20:.0f} MiB")

    # --- tabela zbiorcza
    with open(os.path.join(a.wyniki, "tabela.md"), "w") as f:
        f.write("| metoda | k | FP test (czyste z alarmem) | obszary na czystych | FN test (dodatki) | FN test konstrukcja | "
                "zbędne obszary | miejsc na auto | FN pełny | FP pełny | czas/obraz pełny [s] |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
        for m, k, w in tabela:
            wp = wyniki_p[m]
            cz = max(wp["czasy"]) if wp["czasy"] else float("nan")
            nk = sum(n for t, n in w["n_typ"].items() if t.endswith("_konstrukcja"))
            fk = sum(n for t, n in w["fn_typ"].items() if t.endswith("_konstrukcja"))
            na = sum(w["ramki_na_auto"]) / max(1, len(w["ramki_na_auto"]))
            f.write(f"| {m} | {k} | {w['czyste_z_alarmem']}/{w['czyste']} | {w['obszary_na_czystych']} | "
                    f"{w['przeoczone']}/{w['dodatki']} | {fk}/{nk} | {w['zbedne_obszary']} | {na:.1f} | {wp['przeoczone']}/{wp['dodatki']} | "
                    f"{wp['czyste_z_alarmem']}/{wp['czyste']} | {sum(wp['czasy']) / len(wp['czasy']):.2f} (maks {cz:.2f}) |\n")
    print("\n" + open(os.path.join(a.wyniki, "tabela.md")).read())


if __name__ == "__main__":
    main()
