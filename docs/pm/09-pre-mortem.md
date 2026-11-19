# Pre-mortem: rano nie ma działającej wersji (po recenzji R1)

Podstawa: `docs/spec.md`, `docs/pm/05`, `07`, `docs/decyzje.md`, `docs/zadania/01-mvp-z-makiety.md`, `wyniki/bazowy/`. Stan 12:37: ksefbot.pl → 530; makieta R3 (GitHub Pages) → 200; wynik bazowy A: FP 2/30, FN 0/60, 0,49 s/obraz 50 MB (Programista, 12:09). Prawdopodobieństwo i skutek: W/Ś/N — moja ocena, nie pomiar.
Założenie: wyobrażam sobie oddanie rano; co poszło źle.

## Ryzyka (10; Tigers = wymagają działania)
| # | Ryzyko | Typ | P | Skutek | Sygnał wczesny | Działanie zapobiegawcze | Właściciel | Termin |
|---|---|---|---|---|---|---|---|---|
| R1 | ksefbot.pl dalej daje 530/5xx — brak aplikacji pod linkiem | Tiger, blokujące | W (dziś 530) | W: brak dema „na żywo” | `curl -L` ≠ 200 po 16:00 | Wdrożenie Coolify najpierw z makietą statyczną (200), potem podpięcie usługi; kod HTTP w meldunku | Programista | 17:00 |
| R2 | Usługa na karcie OMENa nie odpowiada z ksefbot.pl (sieć lokalna może być niewidoczna z serwera zewnętrznego) | Tiger, blokujące | W | W: aplikacja bez wyniku | zapytanie z ksefbot.pl do usługi → timeout; nikt tego jeszcze nie sprawdził | Test osiągalności teraz; jeśli nie — tunel/proxy albo pokaz z lokalnego komputera; fallback „wynik zapisany” (niżej) | Programista (pytanie o sieć: Szef) | 15:00 |
| R3 | Karta/OMEN zajęta przez przebiegi S1–S4/B4–B16, restart OMENa albo `kod 75` w momencie pokazu | Tiger, blokujące | W | Ś–W | brak odpowiedzi usługi; kolejka orkiestratora | Zamrozić przebiegi na ≥ 2 h przed oddaniem; usługa jako osobne długie zlecenie `gpu-tlo`; ostatni dobry wynik zapisany w repo | Szef (zegar) + Programista | 19:00 |
| R4 | MVP nie dowiezie wszystkich P1–P37 (wiersze „—” w `01-mvp-z-makiety.md`) | Tiger, fast-follow | W | Ś: rozjazd z makietą/slajdami | wiersze bez „działa” + zrzutu po 18:00 | Zakresu nie tnie Analityk ani Programista: kolejność cięcia rozstrzyga człowiek od kształtu produktu (Artur, przez Projektanta). Rekomendacja: zostawiamy wszystko, tniemy od końca listy MVP. Do czasu decyzji niezrobione wiersze oznaczone w README „w planie” | Szef (pytanie do Artura), Programista (stan wierszy) | 18:00 |
| R5 | Teksty obiecują więcej niż jest (partia CLI, offline, uczenie na czystych, „sam dobiera wzorzec”) | Tiger, blokujące | W | W: kryteria oceny, wiarygodność | recenzja wykrywa zdanie bez źródła w kodzie/WYNIK | Każde zdanie o możliwości = źródło (linia WYNIK, test) albo „w planie”; recenzja materiałów po ostatnim przebiegu | Prezenter (recenzja: Analityk) | 20:00 |
| R6 | Liczby w README/slajdach/HackTribe rozjeżdżają się po nowych przebiegach (FP 2/30 → inne po kalibracji ≥ 60 par) | Tiger, blokujące | W | Ś–W | nowy wpis WYNIK w decyzje.md | Jedno źródło: `wyniki/bazowy/tabela.md`; po każdym werdykcie Programisty Prezenter aktualizuje liczby i datę w trzech plikach | Prezenter | po każdym przebiegu |
| R7 | Wynik na sztucznym zbiorze nie przenosi się na dane KAS | Elephant | W | Ś (ocena skuteczności) | brak jakiegokolwiek obrazu KAS; zbiór własny z jednego generatora | Jawne zastrzeżenie (jest); dane KAS tylko po pytaniu do Pawła; liczb nie podawać jako „skuteczności” | Prezenter + Szef | 20:00 |
| R8 | Pełny obraz ~50 MB przez HTTP (ksefbot.pl → usługa) przekracza limit/czas proxy; czas całkowity > 1 min | Tiger, fast-follow | Ś | Ś: zadanie p. 7 (< 1 min) | upload 50 MB trwa dziesiątki sekund; błąd 413/504 | Test jednego prawdziwego pliku 50 MB end-to-end; podnieść limity Coolify/proxy; w razie czego pokaz na obrazie zmniejszonym z podpisem | Programista | 17:00 |
| R9 | Brak zrzutów/nagrania pokazu, gdy coś padnie rano | Tiger, blokujące | Ś | W | brak `docs/zrzuty/mvp-*.png` do 19:00 | Zrzuty obowiązkowe (lista w warstwie 4) i nagranie ścieżki z działającej wersji, commit do repo | Programista (zrzuty), Prezenter (wstawienie) | 19:00 |
| R10 | Prawdziwy wynik na obrazie demo nie da 4 miejsc 91/78/66/57% z makiety (tam dane udawane): inna liczba miejsc, pewności, nazwy stref; slajdy, scenariusz i zrzuty przestają pasować | Tiger, blokujące | W | W: rozjazd tekstów z tym, co widać | pierwszy prawdziwy wynik na obrazie demo ≠ spec §6 | Programista wybiera obraz demo, spisuje jego prawdziwy wynik (miejsca, pewności, strefy) w `docs/decyzje.md`; Prezenter i scenariusz pokazu (spec §6, slajdy 3, 5) idą za prawdziwym wynikiem; makieta pozostaje z udawanymi danymi i takim podpisem | Programista (wybór i wynik), Prezenter (teksty) | 18:00 |

Paper Tigers (nie działamy): brak ceny/wejścia na rynek (n/d, decyzja 11:29); „za mało obrazów” (zbiór generujemy); nazwa zespołu (P38 zamknięte). Track: kontrola kodu HTTP w nocy — Szef przy każdym zdarzeniu zegara, ostatni kod i godzina w `docs/stan.md`.

## Wersja „działa na pewno”
Pokaz ma cztery warstwy; przełączenie = jedna zmiana linku „Demo” w README/slajdach/HackTribe (Prezenter), ok. minuty. Ścieżka pokazu (spec §6) ma kroki: **K1** 4 miejsca do „zostało 0”, **K2** pusta naczepa (P27/P34), **K3** „Następne miejsce” (P35), **K4** pominięte (P29), **K5** wzorzec z pliku (P36), **K6** zapis z PNG z ramkami (P32).

| Warstwa | Pokazujemy | Skąd | Które kroki daje | Przełączenie |
|---|---|---|---|---|
| 1. Wszystko działa | ksefbot.pl, analiza prawdziwego obrazu przez usługę na karcie OMENa | link w README | K1–K6 na żywo (po dowiezieniu MVP; wiersze bez „działa” = „w planie”) | — |
| 2. Padła karta OMENa albo sieć lokalna | ksefbot.pl w trybie „wynik zapisany” (podpis „wynik zapisany z przebiegu <data, godz.>”) | zapisane przebiegi w repo, aplikacja czyta pliki, nie usługę | K1–K6 **tylko jeśli** zapisano kilka przebiegów: (a) zwykły (K1, K3, K4, K6), (b) pusta naczepa (K2), (c) z plikiem wzorca (K5, linia „wzorzec: plik <nazwa> (wskazany ręcznie)”); każdy z polami P29 (pominięte), P32 (PNG z ramkami) i P36. Bez tych przebiegów warstwa pokazuje tylko K1 | Programista: tryb zapisu (do zbudowania w MVP); albo Szef: link na warstwę 3 |
| 3. Padł ksefbot.pl | Makieta R3 (statyczna, GitHub Pages, 200): ścieżka 4 pozycje, ~12 kliknięć. **Podpis: „makieta zamknięta, dane udawane; P34–P36 dopiero w MVP”** — makieta ma flagę „pusta naczepa” przy jednym miejscu (nie P34), „Następne miejsce” chodzi w kółko (nie P35), zapis bez linii „wzorzec: plik” (nie P36) | https://pawelpisarek.github.io/hacknation-proba14/makieta/ | K1, K4, K6 w wersji z makiety; K2, K3, K5 częściowo (zachowanie sprzed P34–P36) | podmiana linku „Demo” |
| 4. Nic z internetu | Zrzuty + nagranie ścieżki + slajdy PDF, lokalnie z repo | repo | K1–K6 jako obrazy (jeśli zrzuty zrobione z MVP) | otworzyć pliki lokalne |

**Obowiązkowe zrzuty dla warstwy 4** (z działającej wersji, nie z makiety): `docs/zrzuty/mvp-lista-4-miejsca.png` (K1), `mvp-zostalo-0.png` (K1), `mvp-pusta-naczepa.png` (K2: flaga przy każdym miejscu w ładowni, nagłówek „najpierw alarmy z reguły”), `mvp-nastepne-miejsce.png` (K3), `mvp-pokaz-pominiete.png` (K4), `mvp-wzorzec-plik.png` (K5), `mvp-zapis-png.png` (K6: zapis z obrazem z ramkami i linią „wzorzec: plik…”), `mvp-niepewny-wzorzec.png` (flaga P16). Nazwy to propozycja; liczy się lista kroków.

Warunki, by ta wersja istniała (do 20:00): (1) zrzuty i nagranie z MVP (R9); (2) jeden przebieg na prawdziwym ~50 MB .bmp z zapisanym JSON i PNG (R8); (3) kilka zapisanych przebiegów dla warstwy 2 (wyżej); (4) w README podpis przy każdej warstwie, co jest „na żywo”, a co „zapisane”/„makieta” (R5); (5) kod HTTP z `curl -L` w meldunku.

Kryterium „działa”: makieta 200 (jest), ksefbot.pl 200 + wynik z prawdziwego obrazu, albo jawnie oznaczony tryb zapisu.

<!-- skill: pre-mortem -->
