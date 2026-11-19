# hacknation-proba14

## Uruchomienie (roboczo, Programista)

Wykrywanie dodatków w obrazach RTG naczepy (para wzorzec–badany albo model czystego obrazu typu).

- `anomalie/generator.py` — sztuczny zbiór .bmp (naczepa z boku, dodatki 4 typów, maski PNG + `opis.json`):
  `python -m anomalie.generator --wyjscie dane/gen-v2 --maly [--pelny]`
- `anomalie/ocena.py` — skrypt oceny (dowolny katalog .bmp + opcjonalne maski): FP (czyste z alarmem, liczba obszarów),
  FN (dodatek wskazany: IoU ≥ 0,1 albo środek w ramce), zbędne obszary, czas/obraz:
  `python -m anomalie.ocena --badane DIR/badane --maski DIR/maski --predykcje P.json`
- `anomalie/detektor.py` — metody (tylko karta CUDA): A piksele_para, A0 ablacja, B cechy_para (ResNet18), C model_typu.
- `skrypty/przebieg_bazowy.sh` — całość na OMENie (środowisko, dane, wynik bazowy → `wyniki/bazowy/tabela.md`).
- `testy/test_dymny.py` — test generatora i oceny bez modeli.

Duże obrazy nie trafiają do repo (`dane/`, `*.bmp` w `.gitignore`).
