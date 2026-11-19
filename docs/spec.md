# Specyfikacja: Różnica RTG (po recenzji przejścia, runda 1)

Źródła: `docs/pm/04-write-prd.md`, `docs/pm/02-discover.md`, `docs/pm/03-warianty-ekranu.md`, `docs/zadanie.md`, `docs/decyzje.md` (P1–P33). Dane i ekrany są **sztuczne** (zdjęć KAS nie mamy). Liczenie wyłącznie na karcie (GTX 1050, 4 GB), nigdy na procesorze. Ekran po polsku.

## 1. Co zobaczy i zrobi użytkownik (według Artura)
Użytkownik: operator RTG przy stanowisku, kilka minut na auto (P1).
Ekran główny = **wariant 3 + lista z wariantu 2** (P12). Makieta: https://pawelpisarek.github.io/hacknation-proba14/warianty/3/
1. Operator wczytuje obraz badanego auta (`.bmp`) i wybiera z listy **rodzaj zgłoszonego towaru** albo „nie wiem” (P15, P17); wzorzec dobiera się sam (podpis „dobrany: typ …, podobieństwo …”) albo operator wskazuje wzorzec (tryb z parą).
2. Widzi **dwa obrazy obok siebie**: wzorzec (z zaznaczonym odpowiednikiem miejsca) i badane auto (z ramkami).
3. Z boku **lista miejsc od najpewniejszego** (P7). Każda pozycja: nazwa miejsca, krótko czym różni się od wzorca (P9), pewność.
4. Klik w miejsce (na liście albo w ramce) — **oba obrazy przybliżają to samo miejsce** (powiększenie, P10/idea 5).
5. Decyzja: **„do kontroli”** (zleca kontrolę fizyczną miejsca) albo **„odrzuć”** jednym kliknięciem z **powodem z listy** (P3). Przyciski przy każdej pozycji listy z boku (P13, odpowiedź A).
6. Linia „N miejsc do sprawdzenia · zostało M” (P10).
7. Zapis kontroli: lista „miejsce — do kontroli: przedmiot / odrzucone (powód)” (zadanie, p. 9).
Poza zakresem: podsumowanie partii poza linią „ile miejsc” (z 7 Artur wziął tylko ją, P10; zastępuje „podsumowanie partii” z Q8), uszkodzenia naczepy (P6), ciche pomijanie różnic (P8).

**Demo ≤ 2 min (P4, P11):** wczytanie → wzorzec dobrany → ramka „Podłoga — środek” (najpewniejsza, pierwsza) → klik → powiększenie na obu obrazach → „do kontroli” → „Ściana przednia — przód” → „do kontroli” → „Ładownia — tył” → „do kontroli” → „Ładownia — przód” → „odrzuć” z powodem → zapis i linia „zostało 0”.

## 2. Wejście i wyjście
**Wejście:** rodzaj zgłoszonego towaru z listy (domyślnie „nie wiem”; lista wstępna — założenie = rekomendacja P17: sprzęt i AGD · odzież i tekstylia · żywność i napoje · materiały budowlane · inne · pusta naczepa); plik `.bmp` badanego auta (8 bit, skala szarości; docelowo ~50 MB, zadanie p. 3/7); opcjonalnie drugi `.bmp` jako wzorzec (tryb z parą); katalog czystych wzorców (do nauki i doboru).
**Wyjście na plik wynikowy:**
- obraz z ramkami (PNG, układ obrazu badanego w pełnej rozdzielczości);
- JSON: lista miejsc `{id, nazwa, ramka {x,y,w,h}, pewność, opis różnicy, przedmiot kontroli, decyzja, powód}` + wzorzec użyty (czas analizy tylko w danych, nie na ekranie — P25/P26);
- linia „N miejsc do sprawdzenia”.
Wynik zapisuje **miejsce i przedmiot kontroli** (zadanie p. 9); integracja z repozytorium obrazów Nuctech/Multicontrol — poza pierwszą wersją, jako ścieżka wdrożenia.

## 3. Dane
- Zbiór sztuczny (generator gen-v1, Programista, `docs/decyzje.md` 11:33): 3 typy naczep; para = ta sama konstrukcja i ładunek (plus zbiór kontrolny „inny ładunek zgodny ze zgłoszeniem”: 6 par, w metadanych rodzaj towaru zgodny z ładunkiem, w 3 parach dodatkowo mały dodatek w konstrukcji — decyzja Szefa, `docs/decyzje.md`) oraz drugi zbiór kontrolny „dodatek ukryty w ładunku przy podanym rodzaju towaru”: 6 par (ładunek zgodny ze zgłoszeniem + dodatek typu „w ładunku”, średni lub duży; Szef 11:51); badany: szum, przesunięcie ±1%, skala X ±1,5% / Y ±0,3%, jasność ±15%; dodatki 4 typów z maskami PNG.
- Zbiory: nauka 3×6 pustych; kalibracja 12 czystych par; test 30 czystych + 30 z dodatkami (1200×420); pełny 3+3 pary 12000×4200 (~50 MB).
- Analiza na zmniejszeniu do szerokości 1200 px; ramki przeliczane na układ pełnej rozdzielczości. Próg z osobnego zbioru kalibracji (same czyste), bez podglądania testu.
- Dane KAS (jeśli będą z pendrive'a): chronione, nie kopiować poza hackathon (zadanie p. 7).

## 4. Tryby
| Tryb | Kiedy | Zachowanie |
|---|---|---|
| **Z parą** | operator ma czysty obraz tego samego typu | wyrównanie badanego do wzorca, różnica tłumienia, ramki |
| **Bez pary (dobór wzorca)** | domyślny — operator zwykle pary nie ma (P8) | system wybiera z katalogu czystych najbliższy typ naczepy, potem jak wyżej; podpis „dobrany: …” |
Jeśli dobór wzorca zawodzi (podobieństwo poniżej progu z kalibracji) — ekran pokazuje ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec” i prosi o wskazanie wzorca (tryb z parą; tryb pary pierwszy w razie porażki E1, `docs/pm/02`). P16 (A): Artur odpowiedział 11:46; ramek nie ukrywamy (P2, P8).
Inny ładunek zgodny ze zgłoszeniem (P15, Artur): **nie zaznaczamy go, ale tylko gdy narzędzie zna zgłoszenie** — operator wybiera rodzaj towaru z listy (pole na ekranie przed analizą). Bez wybranego rodzaju towaru zaznaczamy wszystko, co różni się od wzorca (P2: zbędny alarm lepszy niż przeoczenie).
Lista rodzajów towaru na ekranie (P17, Artur): sprzęt i AGD; odzież i tekstylia; żywność i napoje; materiały budowlane; inne; „nie wiem” (zaznaczamy wszystko); **„pusta naczepa”** (najczęstszy przypadek — każdy przedmiot w ładowni jest alarmem).
Reguła (nie gasi dodatku ukrytego w ładunku — test A15b): przy wybranym rodzaju towaru różnica w ładunku, którą da się wyjaśnić tym rodzajem (inny ładunek niż we wzorcu), nie dostaje ramki; przy „nie wiem” zaznaczamy wszystko, co różni się od wzorca (P2). Rozpoznanie „zgodny ze zgłoszeniem” — zadanie dla Programisty, do zmierzenia w A15/A16; generator: zbiór kontrolny 6 par (decyzja Szefa).

### 4a. Strefy naczepy (rozstrzygnięcie Szefa 11:49, p. 1)
Generator i katalog wzorców mają dla każdego typu naczepy **mapę stref**: ładownia · podłoga · ściana przednia (przy kabinie) · rama/osie · dach. Ramka dostaje strefę z największego pokrycia; **nazwa strefy = „miejsce kontroli”** w raporcie i w JSON. Podział: **konstrukcja = wszystko poza ładownią**, **ładunek = ładownia**. Dodatek w konstrukcji zawsze jest alarmem; różnica w ładowni — według reguły rodzaju towaru (wyżej).

### 4b. Wygląd ładunku i „pusta naczepa” (p. 2)
Generator ma stałe przypisanie wyglądu ładunku do każdego rodzaju z P17 (np. sprzęt i AGD — gęste prostokątne bryły; odzież i tekstylia — jednolita średnia gęstość; żywność i napoje — wiele małych równych kształtów; materiały budowlane — długie, gęste elementy; inne — mieszanka). Dla „pusta naczepa” ładownia jest pusta, więc **każdy przedmiot w ładowni = alarm** (test A17).

### 4c. Typ naczepy spoza katalogu (p. 3)
Gdy badany typ nie ma wzorca w katalogu (podobieństwo poniżej progu z kalibracji): flaga **„wzorzec niepewny”**, ramki **są** pokazane (nie ukrywamy różnic, P2/P8), a operator **wskazuje wzorzec z listy typów w katalogu albo wgrywa plik wzorca** (tryb z parą). Test A18.

Przedmiot kontroli = strefa + położenie wzdłuż naczepy (przód, środek, tył), liczone z ramki (ustalenie Programisty, R2).

### 4d. Przepływ i zapis kontroli (p. 4)
- Pojedynczy obraz: przeglądarka → aplikacja na ksefbot.pl → usługa HTTP na karcie (OMEN; obraz `.bmp` w żądaniu) → JSON (ramki, strefy, pewność, opis, flaga wzorca) + PNG podglądu.
- Zapis kontroli (miejsce + przedmiot kontroli + decyzja i powód): plik JSON na serwerze aplikacji, z możliwością pobrania.
- Partia z wiersza poleceń: folder `.bmp` → JSON i PNG na obraz + zbiorczy CSV (test A13).

## 5. Raport
- Obraz z ramkami + JSON (pkt 2) — układ jak w makiecie: ramki numerowane wg kolejności listy.
- Pewność: 50–99%, liczona względem progu z kalibracji (wynik metody ÷ próg, ograniczony do skali); opis różnicy z szablonu: strefa + „gęściej/rzadziej niż wzorzec” + wielkość (Szef 11:49, p. 5).
- Pozycja miejsca: nazwa, opis różnicy (np. „pod podłogą dodatkowa warstwa; we wzorcu podłoga pojedyncza” — dane udawane z makiety), pewność, przedmiot kontroli.
- Powiększenie: wycinek wokół ramki z marginesem, na wzorcu i badanym.
- Linia „ile miejsc do sprawdzenia” (P10); pełne podsumowanie partii — poza zakresem (decyzja Artura P10).
- Wynik dla partii: ta sama struktura, jeden JSON na obraz; skalowalność mierzona testem A13 (nie obietnica).

## 6. Udawane dane ekranu (dla Programisty)
Źródło: `docs/makieta/index.html` (R3, zamknięta), zgodne z P1–P33. Nazwa miejsca = strefa + położenie (P18); opis różnicy bez miar (P19); w pokazie 4 pozycje (P20).
Auto: „Ciągnik + naczepa plandeka, nr rej. XX 0000 (dane udawane)”. Wzorzec: „typ naczepa plandeka 3-osiowa, 13,6 m (podobieństwo 0,93)”.
1. Podłoga — środek, 91% (konstrukcja), „Gęściej niż wzorzec, ok. 1/4 długości naczepy.”, przedmiot: podłoga naczepy, środek.
2. Ściana przednia — przód, 78% (konstrukcja), „Gęściej niż wzorzec, ściana grubsza na większości wysokości.”, przedmiot: przednia ściana skrzyni ładunkowej (przy kabinie).
3. Ładownia — tył, 66% (mały dodatek w ładunku), „Gęstszy mały obiekt wewnątrz ładunku, we wzorcu brak.”, przedmiot: ładunek w tylnej części ładowni — w pokazie „do kontroli”.
4. Ładownia — przód, 57% (inny ładunek niż we wzorcu), „Rzadziej niż wzorzec — inny ładunek, ok. 1/4 długości naczepy.”, przedmiot: ładunek w przedniej części ładowni — w pokazie „odrzuć” z powodem; ramka tylko przy „nie wiem” i „pusta naczepa”; przy wybranym rodzaju towaru jest pominięta (P15).
Powody odrzucenia: znany element konstrukcji · ładunek zgodny z deklaracją · artefakt obrazu · inny typ naczepy niż wzorzec · inne. Przy „nie wiem” powód „ładunek zgodny z deklaracją” zastępuje „ładunek zgodny z dokumentami (sprawdzony ręcznie)” (P21).
Ekran: pole „Rodzaj zgłoszonego towaru” (lista rozwijana nad obrazami, domyślnie „nie wiem”) jest w makiecie. W powiększeniu miejsca są oba przyciski, „do kontroli” i „odrzuć” z powodem (P22). Pominięta różnica (towar zgodny ze zgłoszeniem): komunikat „pominięto N różnic” i przycisk „Pokaż pominięte” (P23). Przy niepewnym wzorcu pewność jest niższa, a po wskazaniu wzorca ramki i pewność się przeliczają (P24). Numery ramek większe, z białą obwódką; linia „N miejsc” z poprawną odmianą (3 miejsca, 5 miejsc); **czasu analizy na ekranie nie ma** (P25, P26) — zostaje tylko w JSON (§2).
Układ „pusta naczepa” (A17): każde miejsce w ładowni dostaje ramkę z flagą „ładownia pusta wg zgłoszenia”, a nagłówek listy brzmi „najpierw alarmy z reguły” (kolejność: miejsca w konstrukcji od najpewniejszego, potem ładownia). Założenie = rekomendacja A z P34, do potwierdzenia przez Artura; makieta R3 ma flagę tylko przy „Ładownia — przód”, reszta w aplikacji.
„Następne miejsce”: przechodzi do następnego jeszcze nierozstrzygniętego miejsca, po ostatnim zamyka okno (założenie = rekomendacja A z P35; makieta chodzi w kółko).
Wzorzec z pliku: w zapisie osobna linia „wzorzec: plik <nazwa> (wskazany ręcznie)” (założenie = rekomendacja A z P36; makieta R3 ma „wzorzec: para”).
(Liczby i opisy to dane udawane makiety, nie wyniki modelu.)

## 7. Kryteria akceptacji (testy)
Liczby progowe ustala Szef po pierwszym przebiegu (E1+E2); do tego czasu kryteria jakościowe i pomiary.
| # | Test | Spełnione, gdy |
|---|---|---|
| A1 | Czyste obrazy testowe (30) | liczba obrazów z jakimkolwiek alarmem (FP) zmierzona i podana; cel: 0 (hipoteza H1 Programisty) |
| A2 | Obrazy z dodatkami (30) | liczba dodatków bez ramki (FN) zmierzona osobno od FP; przeoczenie traktowane jako gorsze (P2) |
| A3 | Ramki na auto | kilka (nie kilkadziesiąt) na obraz (P2); liczbę graniczną ustala Szef po pierwszym przebiegu E1+E2, do tego czasu raportujemy średnią i maksimum ramek na obraz |
| A4 | Dobór wzorca bez pary | wybrany wzorzec = właściwy typ naczepy; odsetek trafień zmierzony (E1, H4) |
| A5 | Skrytka w konstrukcji | podwójna podłoga / ściana przy kabinie wskazana ramką z powiększeniem (E2, P4, P11) |
| A6 | Czas | czas na obraz pełnowymiarowy < 60 s, pamięć karty < 4 GB (H5; zadanie p. 7); pokaz: wynik w kilka sekund (P5) |
| A7 | Kolejność | lista od najpewniejszej pewności (P7) |
| A8 | Decyzja | „do kontroli” i „odrzuć” (z powodem) zapisują się w zapisie kontroli z miejscem i przedmiotem |
| A9 | Linia | „N miejsc do sprawdzenia” zgadza się z liczbą ramek i maleje po decyzji |
| A10 | Demo | główna ścieżka z pkt 1 wykonalna w ≤ 2 min |
| A11 | Praca bez internetu | działa bez sieci (zadanie p. 9); wynik z karty OMENa |
| A12 | Zmniejszenie obrazu | mały dodatek w konstrukcji (typ „mały w konstrukcji”, Q5) wykrywany po zmniejszeniu do 1200 px; porównanie FN na zmniejszeniu i na pełnym obrazie (decyzja Q7) |
| A13 | Partia i duże pliki | przebieg partii pełnowymiarowych obrazów (3+3 pary 12000×4200, ~50 MB): czas na obraz, szczytowa pamięć karty, obrazy/min; wynik zapisany, wynik bez obietnic (zadanie p. 3, 6) |
| A14 | Ocena przez operatora (E3) | próba ręczna z Arturem na makiecie: czy z ramek, opisu różnicy i powiększenia da się podjąć „do kontroli / odrzuć” dla każdej ramki w kilka minut; wynik: tak/nie + uwagi |
| A15 | Zbiór kontrolny z podanym rodzajem towaru | 6 par (inny ładunek niż we wzorcu, rodzaj towaru zgodny z ładunkiem; w 3 parach dodatkowo mały dodatek w konstrukcji): brak alarmu na ładunku, a dodatek w konstrukcji wykryty; FP i FN osobno |
| A16 | Zbiór kontrolny bez rodzaju towaru („nie wiem”) | te same 6 par: alarm na ładunku jest (zaznaczone wszystko, co różni się od wzorca; P15, P2); dodatek w konstrukcji nadal wykryty; FP i FN osobno |
| A15b | Dodatek ukryty w ładunku przy podanym rodzaju towaru | 6 par z dodatkiem w ładunku, wybrany rodzaj towaru zgodny z ładunkiem: dodatek w ładunku **wykryty** mimo wygaszania towaru zgodnego (P4 + P15: gasimy tylko towar zgodny ze zgłoszeniem); FN osobno i porównane z FN tych samych par przy „nie wiem” — większe FN przy rodzaju towaru = reguła do wycofania („zwiń”, nie „ukryj”); FP i FN osobno |
| A17 | Pusta naczepa | wybrany rodzaj „pusta naczepa”: każdy przedmiot w ładowni daje ramkę (strefa: ładownia); FP i FN osobno |
| A18 | Typ spoza katalogu | zbiór kontrolny + 2 pary typu spoza katalogu: flaga „wzorzec niepewny” i ramki są; operator może wskazać wzorzec z listy lub z pliku |

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

## Ustalenia po przeglądzie makiety (P18–P26, Artur)
- Nazwa miejsca wg strefy i położenia („Podłoga — środek”); opis różnicy bez miar (P18, P19).
- Pokaz: 4 pozycje, „paleta 5” do kontroli, czwarta „odrzuć” (P20).
- Przy „nie wiem” powód „ładunek zgodny z dokumentami (sprawdzony ręcznie)” (P21).
- W powiększeniu „do kontroli” i „odrzuć” z powodem (P22); przycisk „Pokaż pominięte” (P23).
- Niepewny wzorzec: niższa pewność przy ramkach, po wskazaniu wzorca przeliczenie (P24).
- Czytelność: większe numery ramek z białą obwódką, „3 miejsca / 5 miejsc”, zrzut powiększenia; **czasu analizy na ekranie nie pokazujemy** (P25, P26).

## Ustalenia po przeglądzie makiety R2 (P27–P33, Artur)
- „Pusta naczepa”: pewność z wyniku, pozycja z flagą „alarm z reguły: pusta naczepa” na górze, obraz auta bez ładunku lub podpis „obraz poglądowy” (P27).
- Po ręcznym wskazaniu wzorca: obraz wzorca zmienia się z typem, znacznik „wskazany ręcznie” zostaje, „Wgraj plik wzorca” pozwala wybrać plik (P28).
- Pominięte różnice (towar zgodny ze zgłoszeniem) trafiają do zapisu jako „pominięte (towar zgodny ze zgłoszeniem): N”; po „Pokaż pominięte” można je zlecić do kontroli i liczą się do „zostało” (P29). Odmiana „1 różnicę / 2 różnice / 5 różnic” (P30).
- W powiększeniu przycisk „Następne miejsce” (P31).
- **Obraz naczepy z ramkami w zapisie kontroli jest już w makiecie** (P32 = B, dowód dla kontroli fizycznej). Nic do wyrzucenia z ekranu (P33).
