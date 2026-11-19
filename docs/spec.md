# Specyfikacja: Różnica RTG (wersja robocza do recenzji przejścia)

Źródła: `docs/pm/04-write-prd.md`, `docs/pm/02-discover.md`, `docs/pm/03-warianty-ekranu.md`, `docs/zadanie.md`, `docs/decyzje.md` (P1–P12). Dane i ekrany są **sztuczne** (zdjęć KAS nie mamy). Liczenie wyłącznie na karcie (GTX 1050, 4 GB), nigdy na procesorze. Ekran po polsku.

## 1. Co zobaczy i zrobi użytkownik (według Artura)
Użytkownik: operator RTG przy stanowisku, kilka minut na auto (P1).
Ekran główny = **wariant 3 + lista z wariantu 2** (P12). Makieta: https://pawelpisarek.github.io/hacknation-proba14/warianty/3/
1. Operator wczytuje obraz badanego auta (`.bmp`); wzorzec dobiera się sam (podpis „dobrany: typ …, podobieństwo …”) albo operator wskazuje wzorzec (tryb z parą).
2. Widzi **dwa obrazy obok siebie**: wzorzec (z zaznaczonym odpowiednikiem miejsca) i badane auto (z ramkami).
3. Z boku **lista miejsc od najpewniejszego** (P7). Każda pozycja: nazwa miejsca, krótko czym różni się od wzorca (P9), pewność.
4. Klik w miejsce (na liście albo w ramce) — **oba obrazy przybliżają to samo miejsce** (powiększenie, P10/idea 5).
5. Decyzja: **„do kontroli”** (zleca kontrolę fizyczną miejsca) albo **„odrzuć”** jednym kliknięciem z **powodem z listy** (P3). Przyciski przy każdej pozycji listy z boku (P13, odpowiedź A).
6. Linia „N miejsc do sprawdzenia · zostało M” (P10).
7. Zapis kontroli: lista „miejsce — do kontroli: przedmiot / odrzucone (powód)” (zadanie, p. 9).
Poza zakresem: podsumowanie partii poza linią „ile miejsc”, uszkodzenia naczepy (P6), ciche pomijanie różnic (P8).

**Demo ≤ 2 min (P4, P11):** wczytanie → wzorzec dobrany → ramka na podwójnej podłodze (najpewniejsza, pierwsza) → klik → powiększenie na obu obrazach → „do kontroli” → ściana przy kabinie → „do kontroli” → trzecie (ładunek) → „odrzuć” z powodem → zapis i linia „zostało 0”.

## 2. Wejście i wyjście
**Wejście:** plik `.bmp` badanego auta (8 bit, skala szarości; docelowo ~50 MB, zadanie p. 3/7); opcjonalnie drugi `.bmp` jako wzorzec (tryb z parą); katalog czystych wzorców (do nauki i doboru).
**Wyjście na plik wynikowy:**
- obraz z ramkami (PNG, układ obrazu badanego w pełnej rozdzielczości);
- JSON: lista miejsc `{id, nazwa, ramka {x,y,w,h}, pewność, opis różnicy, przedmiot kontroli, decyzja, powód}` + wzorzec użyty + czas analizy;
- linia „N miejsc do sprawdzenia”.
Wynik zapisuje **miejsce i przedmiot kontroli** (zadanie p. 9); integracja z repozytorium obrazów Nuctech/Multicontrol — poza pierwszą wersją, jako ścieżka wdrożenia.

## 3. Dane
- Zbiór sztuczny (generator gen-v1, Programista, `docs/decyzje.md` 11:33): 3 typy naczep; para = ta sama konstrukcja i ładunek; badany: szum, przesunięcie ±1%, skala X ±1,5% / Y ±0,3%, jasność ±15%; dodatki 4 typów z maskami PNG.
- Zbiory: nauka 3×6 pustych; kalibracja 12 czystych par; test 30 czystych + 30 z dodatkami (1200×420); pełny 3+3 pary 12000×4200 (~50 MB).
- Analiza na zmniejszeniu do szerokości 1200 px; ramki przeliczane na układ pełnej rozdzielczości. Próg z osobnego zbioru kalibracji (same czyste), bez podglądania testu.
- Dane KAS (jeśli będą z pendrive'a): chronione, nie kopiować poza hackathon (zadanie p. 7).

## 4. Tryby
| Tryb | Kiedy | Zachowanie |
|---|---|---|
| **Z parą** | operator ma czysty obraz tego samego typu | wyrównanie badanego do wzorca, różnica tłumienia, ramki |
| **Bez pary (dobór wzorca)** | domyślny — operator zwykle pary nie ma (P8) | system wybiera z katalogu czystych najbliższy typ naczepy, potem jak wyżej; podpis „dobrany: …” |
Jeśli dobór wzorca zawodzi (podobieństwo poniżej progu z kalibracji) — ekran prosi o wskazanie wzorca (tryb z parą) i nie pokazuje ramek (decyzja Szefa: tryb pary pierwszy w razie porażki E1, `docs/pm/02`).
Inny ładunek zgodny ze zgłoszeniem (P15, Artur): **nie zaznaczamy go, ale tylko gdy narzędzie zna zgłoszenie** — operator wybiera rodzaj towaru z listy (pole na ekranie przed analizą). Bez wybranego rodzaju towaru zaznaczamy wszystko, co różni się od wzorca (P2: zbędny alarm lepszy niż przeoczenie).

## 5. Raport
- Obraz z ramkami + JSON (pkt 2) — układ jak w makiecie: ramki numerowane wg kolejności listy.
- Pozycja miejsca: nazwa, opis różnicy (np. „pod podłogą dodatkowa warstwa; we wzorcu podłoga pojedyncza” — dane udawane z makiety), pewność, przedmiot kontroli.
- Powiększenie: wycinek wokół ramki z marginesem, na wzorcu i badanym.
- Linia „ile miejsc do sprawdzenia”; podsumowanie partii poza tą linią — poza zakresem.
- Wynik dla partii: ta sama struktura, jeden JSON na obraz (skalowanie — cel, nie obietnica, do czasu pomiaru).

## 6. Udawane dane ekranu (dla Programisty)
Auto: „Ciągnik + naczepa plandeka, nr rej. XX 0000 (dane udawane)”. Wzorzec: „typ naczepa plandeka 3-osiowa, 13,6 m (podobieństwo 0,93)”.
1. Podwójna podłoga — środek naczepy, pewność 91%, „pod podłogą dodatkowa warstwa ok. 12 cm na długości ok. 2,3 m; we wzorcu podłoga pojedyncza”, przedmiot: podłoga naczepy między 1. a 2. paletą.
2. Ściana przy kabinie, 78%, „przednia ściana grubsza, wewnątrz jednolity gęsty kształt”, przedmiot: przednia ściana skrzyni.
3. W ładunku — paleta 5, 54%, „gęstszy prostokątny obiekt w środku palety; we wzorcu brak”, przedmiot: paleta nr 5.
Powody odrzucenia: znany element konstrukcji · ładunek zgodny z deklaracją · artefakt obrazu · inny typ naczepy niż wzorzec · inne.
(Źródło: `docs/makieta/warianty/wspolne.js`; liczby w opisach to dane udawane makiety, nie wyniki modelu.)

## 7. Kryteria akceptacji (testy)
Liczby progowe ustala Szef po pierwszym przebiegu (E1+E2); do tego czasu kryteria jakościowe i pomiary.
| # | Test | Spełnione, gdy |
|---|---|---|
| A1 | Czyste obrazy testowe (30) | liczba obrazów z jakimkolwiek alarmem (FP) zmierzona i podana; cel: 0 (hipoteza H1 Programisty) |
| A2 | Obrazy z dodatkami (30) | liczba dodatków bez ramki (FN) zmierzona osobno od FP; przeoczenie traktowane jako gorsze (P2) |
| A3 | Ramki na auto | kilka (nie kilkadziesiąt) na obraz (P2) |
| A4 | Dobór wzorca bez pary | wybrany wzorzec = właściwy typ naczepy; odsetek trafień zmierzony (E1, H4) |
| A5 | Skrytka w konstrukcji | podwójna podłoga / ściana przy kabinie wskazana ramką z powiększeniem (E2, P4, P11) |
| A6 | Czas | czas na obraz pełnowymiarowy < 60 s, pamięć karty < 4 GB (H5; zadanie p. 7); pokaz: wynik w kilka sekund (P5) |
| A7 | Kolejność | lista od najpewniejszej pewności (P7) |
| A8 | Decyzja | „do kontroli” i „odrzuć” (z powodem) zapisują się w zapisie kontroli z miejscem i przedmiotem |
| A9 | Linia | „N miejsc do sprawdzenia” zgadza się z liczbą ramek i maleje po decyzji |
| A10 | Demo | główna ścieżka z pkt 1 wykonalna w ≤ 2 min |
| A11 | Praca bez internetu | działa bez sieci (zadanie p. 9); wynik z karty OMENa |

## 8. Ryzyka (z /discover i zadania)
1. Dobór wzorca bez pary zawodzi → tryb pary jako ratunek (P11, E1).
2. Sztuczny zbiór ≠ prawdziwy RTG: wyniki FP/FN nie przenoszą się na dane KAS — mówimy to wprost.
3. Operator nie zdąży lub nie zaufa kolejności (P11, E3) — sprawdzenie na makiecie z Arturem.
4. Przeoczenie dodatku (FN) — gorsze od zbędnego alarmu (P2); wyniki raportowane osobno.
5. Pokaz zależy od usługi na OMENie (sieć lokalna): plan B — nagrany wynik.
6. Liczba aut dziennie nieznana (założenie, P5).

## 9. Otwarte
- P13, P14, P15 rozstrzygnięte przez Artura (przyciski przy pozycji listy; układ wariantu 3 + powiększenie, linia „ile miejsc”, powód przy „odrzuć”; zgłoszony towar niezaznaczany tylko gdy operator wybrał rodzaj towaru).

<!-- skill: przeplywy-pm -->
<!-- skill: create-prd -->
