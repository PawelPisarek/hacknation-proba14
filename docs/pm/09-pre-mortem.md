# Pre-mortem: rano nie ma działającej wersji

Podstawa: `docs/spec.md`, `docs/pm/05`, `07`, `docs/decyzje.md`, `docs/zadania/01-mvp-z-makiety.md`, `wyniki/bazowy/`. Stan 12:35: ksefbot.pl → 530; makieta R3 (GitHub Pages) → 200; wynik bazowy A: FP 2/30, FN 0/60, 0,49 s/obraz 50 MB (Programista, 12:09). Prawdopodobieństwo i skutek: W/Ś/N — moja ocena, nie pomiar.
Założenie: wyobrażam sobie oddanie rano; co poszło źle.

## Ryzyka (Tigers = wymagają działania; 10 pozycji)
| # | Ryzyko | Typ | P | Skutek | Sygnał wczesny | Działanie zapobiegawcze | Właściciel | Termin |
|---|---|---|---|---|---|---|---|---|
| R1 | ksefbot.pl dalej daje 530/5xx — brak aplikacji pod linkiem | Tiger, blokujące | W (dziś 530) | W: brak dema „na żywo” | `curl -L` ≠ 200 po 16:00 | Wdrożenie Coolify najpierw z makietą statyczną (200), potem podpięcie usługi; kod HTTP w meldunku | Programista | 17:00 |
| R2 | Usługa na karcie OMENa nie odpowiada z ksefbot.pl (sieć lokalna 192.168.1.112 niewidoczna z serwera zewnętrznego) | Tiger, blokujące | W | W: aplikacja bez wyniku | zapytanie z ksefbot.pl do usługi → timeout; nikt tego jeszcze nie sprawdził | Test osiągalności już teraz; jeśli nie — tunel/proxy albo pokaz z lokalnego komputera; fallback „wersja z nagranym wynikiem” (niżej) | Programista (pytanie o sieć: Szef) | 15:00 |
| R3 | Karta/OMEN zajęta przez przebiegi S1–S4/B4–B16, restart OMENa albo `kod 75` w momencie pokazu | Tiger, blokujące | W | Ś–W | brak odpowiedzi usługi; kolejka orkiestratora | Zamrozić przebiegi na ≥ 2 h przed oddaniem; usługa jako osobne długie zlecenie `gpu-tlo`; wynik z ostatniego dobrego przebiegu zapisany w repo | Szef (zegar) + Programista | 19:00 |
| R4 | MVP nie dowiezie wszystkich P1–P37 (wiersze „—” w `01-mvp-z-makiety.md`) | Tiger, fast-follow | W | Ś: rozjazd z makietą/slajdami | wiersze bez „działa” + zrzutu po 18:00 | Cięcie po P: najpierw ścieżka pokazu (4 pozycje, zapis), reszta oznaczona w README „w planie” | Programista | 18:00 |
| R5 | Teksty obiecują więcej niż jest (partia CLI, offline, uczenie na czystych, „sam dobiera wzorzec”) | Tiger, blokujące | W | W: kryteria oceny, wiarygodność | recenzja R3 wykrywa zdanie bez źródła w kodzie/WYNIK | Każde zdanie o możliwości = źródło (linia WYNIK, test) albo „w planie”; recenzja materiałów po ostatnim przebiegu | Prezenter (recenzja: Analityk) | 20:00 |
| R6 | Liczby w README/slajdach/HackTribe rozjeżdżają się po nowych przebiegach (FP 2/30 → inne po kalibracji ≥60 par) | Tiger, blokujące | W | Ś–W | nowy wpis WYNIK w decyzje.md | Jedno źródło: `wyniki/bazowy/tabela.md`; po każdym werdykcie Programisty Prezenter aktualizuje liczby i datę w trzech plikach | Prezenter | po każdym przebiegu |
| R7 | Wynik na sztucznym zbiorze nie przenosi się na dane KAS (ocena w próbie wewnętrznej wygląda lepiej niż na pendrive) | Elephant | W | Ś (ocena skuteczności) | brak jakiegokolwiek obrazu KAS; zbiór własny generowany tym samym kodem | W materiałach jawne zastrzeżenie (jest); dane KAS tylko po pytaniu do Pawła; nie podawać liczb jako „skuteczności” | Prezenter + Szef | 20:00 |
| R8 | Pełny obraz ~50 MB przez HTTP (upload ksefbot.pl → OMEN) przekracza limit/czas proxy; czas całkowity > 1 min | Tiger, fast-follow | Ś | Ś: zadanie p. 7 (< 1 min) | upload 50 MB > kilkadziesiąt s; błąd 413/504 | Test jednego prawdziwego pliku 50 MB end-to-end; limity Coolify/proxy podnieść; pokaz na obrazie zmniejszonym z podpisem | Programista | 17:00 |
| R9 | Brak zrzutów/nagrania pokazu, gdy coś padnie rano (slajdy „Co pokazać” puste) | Tiger, blokujące | Ś | W | brak `docs/zrzuty/mvp-*.png`, brak nagrania do 19:00 | Zrobić zrzuty i nagranie ścieżki pokazu z działającej wersji + wynik JSON/PNG z prawdziwego przebiegu, commit do repo | Programista (zrzuty), Prezenter (wstawienie) | 19:00 |
| R10 | Praca nocna/zmęczenie: nikt nie sprawdza ksefbot.pl i OMENa po 20:00; usługa pada o 3:00 | Paper Tiger → Track | Ś | Ś | `curl` co ~godzinę zwraca ≠ 200 | Szef robi kontrolę kodu HTTP przy każdym zdarzeniu zegara; plik `docs/stan.md` z ostatnim kodem i godziną | Szef | całą noc |

Paper Tigers (nie działamy): brak ceny/wejścia na rynek (n/d, decyzja 11:29); „za mało obrazów” (zbiór generujemy; liczba parametryzowana); nazwa zespołu (P38 zamknięte).

## Wersja „działa na pewno”
Zasada: pokaz ma trzy warstwy, od najbardziej do najmniej zależnej od sieci. Przełączenie = jedna zmiana adresu w README/slajdzie/HackTribe (Prezenter) — 1 minuta.

| Co padło | Pokazujemy | Skąd | Przełączenie |
|---|---|---|---|
| Wszystko działa | ksefbot.pl, analiza prawdziwego obrazu przez usługę na OMENie | link w README | — |
| Karta OMENa albo sieć lokalna | ksefbot.pl w trybie „wynik zapisany”: ostatni dobry JSON + PNG z przebiegu (podpis: „wynik zapisany z przebiegu <data>, godz.”) | `wyniki/bazowy/raporty` w repo (aplikacja czyta plik, nie usługę) | Programista: zmienna `TRYB=zapis` (do zbudowania w MVP); albo Szef: przekierowanie linku w README na makietę |
| ksefbot.pl | Makieta R3 (statyczna, GitHub Pages, 200) — ścieżka pokazu 4 pozycje ~12 kliknięć | https://pawelpisarek.github.io/hacknation-proba14/makieta/ | podmiana linku „Demo” w README/slajdach/HackTribe |
| Nic z internetu | Zrzuty `docs/zrzuty/mvp-*.png` + nagranie ścieżki + slajdy PDF | repo (lokalna kopia) | otworzyć pliki lokalne |

Warunki, by ta wersja istniała (do zrobienia przed 20:00): (1) zrzuty i nagranie ścieżki z działającej wersji (R9); (2) jeden przebieg na prawdziwym ~50 MB .bmp z zapisanym JSON i PNG (R8); (3) w README podpis przy każdej warstwie, co jest „na żywo”, a co „zapisane” (R5); (4) każdy link z kodem HTTP z `curl -L` w meldunku.

Kryterium „działa”: makieta 200 (jest), ksefbot.pl 200 + wynik z prawdziwego obrazu, albo jawnie oznaczony tryb zapisu.

<!-- skill: pre-mortem -->
