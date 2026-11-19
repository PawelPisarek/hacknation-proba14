"""Test dymny bez modeli: generator (mały) → ocena. Ramki = prawda → FN 0; brak ramek → FN wszystkie;
ramka na czystym → FP. python testy/test_dymny.py"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anomalie import generator as G, ocena as O

with tempfile.TemporaryDirectory() as d:
    G.generuj_zbior(d, 5, *G.ROZMIAR_MALY, 2, 4)
    opis = json.load(open(os.path.join(d, "opis.json")))["obrazy"]
    pr = O.wczytaj_prawde(os.path.join(d, "badane"), os.path.join(d, "maski"), os.path.join(d, "opis.json"))
    idealne = {"obrazy": {n: {"ramki": [x["ramka"] for x in o["dodatki"]], "czas_s": 0.1} for n, o in opis.items()}}
    w = O.ocen(pr, idealne); print(O.linia("idealne", w))
    assert w["przeoczone"] == 0 and w["czyste_z_alarmem"] == 0 and w["dodatki"] >= 4
    puste = {"obrazy": {n: {"ramki": []} for n in opis}}
    w = O.ocen(pr, puste); print(O.linia("puste", w)); assert w["przeoczone"] == w["dodatki"]
    n = sorted(opis)[0]; zle = {"obrazy": {n: {"ramki": [[0, 0, 10, 10]]}}}
    w = O.ocen(pr, zle); print(O.linia("alarm", w)); assert w["czyste_z_alarmem"] == 1
    print("typy dodatków:", sorted({x["typ"] for o in opis.values() for x in o["dodatki"]}))
    print("TESTY OK")
