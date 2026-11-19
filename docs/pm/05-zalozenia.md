# Założenia, sondy i atak na spec (krok 3)

Źródła: `docs/spec.md` (po /write-prd), `docs/pm/02-discover.md`, `docs/zadanie.md`, `docs/decyzje.md` (P1–P17). Liczb bez źródła nie wpisuję: progi liczbowe ustala Szef po pierwszym przebiegu (spec §7); tu są tylko progi z zadania (czas < 60 s, pamięć < 4 GB, cel FP 0 z H1) i kryteria względne.
Ocena: **Wpływ** (co się stanie z produktem, gdy fałsz) i **Ryzyko** = (1 − pewność) × koszt sprawdzenia, W/Ś/N. Kolejność Artura (P11): Z1 → Z2 → Z3 — zachowana w tabeli jako pierwsza trójka.

## (a) Założenia według ryzyka (prioritize-assumptions)

| # | Założenie | Test w spec | Wpływ | Ryzyko | Decyzja matrycy | Sonda |
|---|---|---|---|---|---|---|
| Z1 | Bez pary system sam dobiera wzorzec właściwego typu naczepy; gdy niepewny, ostrzega (P16) | A4 | W | W | eksperyment, pierwszy (P11) | S1 |
| Z2 | Skrytka w podwójnej podłodze / ścianie przy kabinie dostaje ramkę, kilka ramek na auto, także przy błędnym wzorcu | A5, A3 | W | W | eksperyment, razem z Z1 (P11) | S1 |
| Z3 | Operator ocenia ramki w kilka minut i ufa kolejności od najpewniejszej | A14 | Ś–W | Ś | eksperyment z człowiekiem (E3), po S3 | E3 |
| Z5 | Reguła „towar zgodny ze zgłoszeniem nie dostaje ramki” gasi alarm na ładunku, a **nie** gasi dodatku ukrytego w ładunku ani w konstrukcji | A15, A16 (bez dodatku w ładunku!) | W | W | eksperyment | S3 |
| Z8 | Wyniki ze sztucznego zbioru mówią coś o danych KAS | spec §8 p. 2 | W | W | tylko zastępnik (nie da się sprawdzić bez danych KAS) | S4 |
| Z4 | FP = 0 na czystych (H1) | A1 | W | Ś | eksperyment | S1, S4 |
| Z6 | Zmniejszenie do szer. 1200 px nie gubi małych dodatków w konstrukcji | A12 | W | Ś | eksperyment | S2 |
| Z11 | Nazwa miejsca i opis różnicy da się wygenerować z danych obrazu (P7, P9), a nie tylko z makiety | A5, §6 | Ś | W | eksperyment | S1 |
| Z10 | Pewność porządkuje listę: skrytka w konstrukcji przed ładunkiem, prawdziwe przed zbędnymi | A7 | Ś | Ś | eksperyment | S3 |
| Z9 | Próg z 12 czystych par kalibracji przenosi się na test i na inny rozkład | A1 | Ś | Ś | eksperyment | S4 |
| Z7 | Czas < 60 s i pamięć < 4 GB na obrazie ~50 MB; partia bez obietnic | A6, A13 | Ś | N | wdrożyć i zmierzyć | S2 |
| Z12 | Pokaz działa przez sieć lokalną na usługę OMENa | A11 | Ś | N | odłożyć; plan B: nagrany wynik (spec §8 p. 5) | — |

## Sondy do zlecenia Programiście (OMEN, `--klasa gpu-tlo`, jedno ciężkie liczenie naraz)

Każda sonda sprawdza ≥ 2 założenia jednym przebiegiem. Liczby FP i FN osobno (spec A1/A2), wyniki do `docs/` z liczbami, wszystko na sztucznym zbiorze (mówimy to wprost).

**S0 — przebieg bazowy Programisty (H1–H5, `decyzje.md` 11:33).** Bez zmian; S1–S4 używają jego metod (A, A0, B, C) i zbiorów. S1–S3 mogą być jednym skryptem z kilkoma trybami, o ile każdy tryb raportuje osobno.

**S1 — dobór wzorca × skrytka × nazwa miejsca → Z1, Z2, Z4, Z11.**
- Zbiór: test 30 czystych + 30 z dodatkami, katalog wzorców 3×6. Trzy warunki na każdym badanym: (i) wzorzec prawidłowego typu z doboru, (ii) wzorzec **wymuszony błędny typ**, (iii) **katalog bez typu badanego** (typ wyjęty).
- Mierzy: odsetek trafnych doborów (A4); rozkład „podobieństwa” dla (i) vs (ii)/(iii) — czy próg podobieństwa je rozdziela (ostrzeżenie P16 działa); FN dodatków „mały / średni w konstrukcji” przy (i) i (ii); FP na czystych; średnia i maksimum ramek na obraz (A3); trafność nazwy strefy (podłoga / ściana przy kabinie / ładunek) przypisanej z geometrii wzorca względem strefy z metadanych generatora.
- Obala: Z1 — dobór nie odróżnia warunku (i) od (iii) progiem podobieństwa (ostrzeżenie P16 niewykonalne) albo myli typ częściej niż losowo; Z2 — dodatek w konstrukcji przy dobrym wzorcu przeoczony częściej niż przy A0 albo ramek na auto „kilkadziesiąt”; Z11 — strefa przypisana błędnie w większości ramek; Z4 — jakiekolwiek FP przy progu z kalibracji (cel z H1: 0).

**S2 — rozdzielczość × czas × pamięć → Z6, Z7.**
- Zbiór: test 1200×420 oraz pełny 3+3 pary 12000×4200; ten sam dodatek „mały w konstrukcji” generowany z **parametryczną grubością** (kilka wartości) — wynik podany jako krzywa FN od grubości, osobno dla szer. 1200, pośredniej i pełnej.
- Mierzy: FN na zmniejszeniu vs pełnym obrazie (A12); najmniejsza wykrywana grubość; czas na obraz, szczytowa pamięć karty, obrazy/min dla partii (A6, A13).
- Obala: Z6 — FN dla szer. 1200 wyraźnie większe niż na pełnym lub pośrednim obrazie dla grubości zbliżonych do podwójnej podłogi z makiety; Z7 — czas ≥ 60 s lub pamięć ≥ 4 GB (zadanie p. 7, GTX 1050 4 GB).

**S3 — ładunek zgodny ze zgłoszeniem × dodatek w ładunku × kolejność → Z5, Z10 (i Z2 pośrednio).**
- Zbiór: zbiór kontrolny 6 par (A15/A16) **rozszerzony o 6 par: inny ładunek zgodny ze zgłoszeniem + dodatek ukryty w ładunku** (typy „w ładunku” średni i duży) oraz warunek „pusta naczepa” (P17).
- Mierzy: z rodzajem towaru: brak alarmu na ładunku zgodnym (A15), **FN dodatku w ładunku** (nowy test — dziś go nie ma), dodatek w konstrukcji wykryty; bez rodzaju towaru (A16): alarm na ładunku jest. Dla wszystkich: miejsce na liście dodatku w konstrukcji vs ładunku zgodnego (precision@k po pewności, A7); średnia liczba ramek.
- Obala: Z5 — reguła wygasza także dodatki w ładunku (FN w ładunku przy rodzaju towaru ≫ bez rodzaju), albo ładunek zgodny dostaje ramkę mimo rodzaju towaru; Z10 — ładunek zgodny lub czysty szum stoi na liście wyżej niż prawdziwy dodatek w konstrukcji w większości aut.

**S4 — zmiana rozkładu danych → Z8 (zastępnik), Z9, Z4.**
- Zbiór: generator **gen-v2** napisany inaczej niż gen-v1 (inny kształt dodatków, nieliniowe rozciągnięcie osi X jak przy zmiennej prędkości skanu, szum innego rodzaju, tło i inny rozkład ładunku, więcej typów naczep), próg i parametry **zamrożone** z kalibracji gen-v1; test 30+30.
- Mierzy: FP i FN na gen-v2 przy progu z gen-v1; ile trzeba przekalibrować (liczba par kalibracyjnych do FP 0); zmianę trafności doboru wzorca.
- Obala: Z9 — próg z gen-v1 daje FP na gen-v2; Z8 (część osiągalna) — wyniki spadają przy zmianie generatora w większym stopniu niż przy zmianie parametrów w gen-v1; wtedy w README piszemy „na sztucznych danych, bez przenoszenia na KAS”. Dane KAS z pendrive'a, jeśli będą: chronione (zadanie p. 7) — czy wolno je wgrać na OMENa, rozstrzyga Szef; do tego czasu nie.

**E3 — nie obliczeniowa, na makiecie z Arturem → Z3, Z10 (po stronie człowieka).** Wymaga, by makieta pokazywała **prawdziwy wynik modelu z S1/S3**, nie dane udawane z `wspolne.js`. Obala: Artur nie decyduje o ramce w kilka minut albo kolejność mu nie pasuje (A14).

## (b) Najmocniejsze ataki na spec (strategy-red-team)

### Ranking: S1/S2 (najtańsze, w pierwszym przebiegu) → atak 1, 2; S3 (tani, decyduje o P15) → atak 3; S4 (tani, ale wynik tylko ostrzega) → atak 4; E3 → atak 5.

**Atak 1 — filtr maksimum i wyrównanie mogą zamaskować dokładnie główne demo.**
- Teza spec: różnica tłumienia względem filtru maksimum wzorca daje małe FP przy małym FN (H1, A5).
- Steelman: tolerancja na przesunięcie ±1% i skalę X ±1,5% jest potrzebna, bez niej FP są wszędzie.
- Fails if: tolerancja (rozmiar filtru) jest szersza niż pas zmiany, np. cienka dodatkowa warstwa pod podłogą, więc podwójna podłoga znika razem z szumem.
- Kontrposunięcie: grubość dodatku jako parametr generatora (S2) i krzywa FN od grubości; jeśli FN rośnie, filtr maksimum zastąpić dopasowaniem lokalnym (wyrównanie na strefach) albo dwustopniową analizą: strefy konstrukcji z mniejszą tolerancją niż ładunek. Kryterium zabicia: nie ma tolerancji dającej FP 0 i podwójną podłogę z makiety jednocześnie → demo od skrytki (P4, P11) niewykonalne na tej metodzie, przejść na metodę B lub C.

**Atak 2 — „bez pary” działa na trzech sztucznych typach; wzorce są puste, badane załadowane.**
- Teza: system dobiera wzorzec z katalogu czystych (spec §4, A4).
- Steelman: typów naczep jest mało i różnią się kształtem skrzyni.
- Fails if: ładunek i typ naczepy mieszają się w podobieństwie (załadowana naczepa A wygląda bliżej pustej B niż pustej A), więc dobór myli typ właśnie na załadowanych autach, a po złym doborze ramki zalewają ładunek.
- Kontrposunięcie: S1 warunek (ii)/(iii) + dobór po cechach konstrukcji (rama, osie, kabina), nie po całym obrazie; ostrzeżenie P16 jako zabezpieczenie, nie ukrywanie ramek (P2). Kryterium: podobieństwo nie rozdziela dobrego doboru od złego → tryb pary jako domyślny i „bez pary” w README jako cel.

**Atak 3 — reguła P15/P17 przeczy P4: ładunek zgodny nie jest zaznaczany, ale towar w ładunku ma być wykryty, a spec nie testuje dodatku w ładunku przy wybranym rodzaju towaru.**
- Teza: z podanym rodzajem towaru „inny ładunek” nie dostaje ramki (spec §4, A15), dodatek w konstrukcji wykryty.
- Steelman: pięć kategorii + „pusta naczepa” pokrywa większość kontroli (P17), a w konstrukcji dodatki są niezależne od ładunku.
- Fails if: rodzaj towaru z listy nie niesie informacji obrazowej (model nie wie, jak wygląda „żywność” bez danych per kategoria), więc reguła w praktyce wycisza cały obszar ładunku — przemyt w ładunku (P4, „oba”) przepada, a A15/A16 mierzą tylko dodatek w konstrukcji, więc FN tego nie pokażą.
- Kontrposunięcie: dopisać do spec test A15b (dodatek w ładunku przy wybranym rodzaju towaru, FN osobno); zamiast wygaszania — niższa pewność i zwinięcie pozycji „ładunek zgodny” na dole listy (nadal widoczna, P2). Kryterium: FN w ładunku przy rodzaju towaru większe niż przy „nie wiem” → reguła wycofana do trybu „zwiń”, nie „ukryj”.

**Atak 4 — sztuczny zbiór sprawdza własne założenia autorów metody.**
- Teza: FP/FN na gen-v1 (+ kalibracja) mówią o jakości (A1, A2).
- Steelman: nie mamy danych KAS (decyzja zespołu), a metoda uczy się tylko na czystych, więc nie zależy od kształtu dodatków.
- Fails if: generator i detektor dzielą założenia (dodatek = gęsty prostokąt, szum, przesunięcie), więc wynik FP 0 / FN 0 to tautologia i na prawdziwych skanach próg kalibracji nie przenosi się.
- Kontrposunięcie: S4 (gen-v2 pisany inaczej, próg zamrożony); w README i pokazie zdanie „zmierzone na sztucznych danych, bez przenoszenia na KAS” (spec §8 p. 2 już to mówi). Kryterium: spadek na gen-v2 większy niż zmiana parametrów w gen-v1 → nie podajemy pojedynczej liczby FP jako „skuteczności”, tylko przedział z S4.

**Atak 5 — makieta obiecuje opisy i kolejność, których detektor ramek nie wytwarza.**
- Teza: lista miejsc od najpewniejszego, z nazwą miejsca i krótkim opisem różnicy (P7, P9; spec §1 p. 3, §6).
- Steelman: nazwa strefy wynika z geometrii wzorca, a opis można szablonować z cech ramki.
- Fails if: metoda daje tylko ramkę i pewność; opisy w makiecie („dodatkowa warstwa ok. 12 cm na długości ok. 2,3 m”) to dane udawane; kolejność po pewności nie jest skalibrowana, więc na żywym wyniku pierwszy jest szum, nie podwójna podłoga, a próba z Arturem (A14) ocenia coś, czego narzędzie nie robi.
- Kontrposunięcie: opis szablonowy z mierzalnych cech (strefa, powierzchnia ramki, średni kontrast względem wzorca) — bez wymyślonych cm; trafność strefy z S1, kolejność z S3; E3 na wyniku modelu, nie na wspolne.js. Kryterium: strefa błędna w większości ramek (S1) albo skrytka nie jest pierwsza w większości aut (S3) → w demo i spec „opis różnicy” zostaje tylko strefą i kontrastem.

### Co jest dobrze uzasadnione
- Kolejność ryzyk Artura (dobór wzorca przed skrytką, P11) — bez wzorca skrytka nie ma punktu odniesienia, i tak ją sprawdza jedna sonda.
- Zasada „zbędny alarm lepszy niż przeoczenie” (P2, P8, P16) spójnie przeprowadzona przez spec: ostrzeżenie zamiast ukrywania ramek.
- Próg z osobnego zbioru kalibracji, bez podglądania testu (spec §3), oraz FP i FN raportowane osobno.

### Czego nie umiem ocenić
- Czy rzeczywiste skany KAS mają nieliniowe zniekształcenia, wzorce pustych naczep i podobny rozkład typów (nie mamy danych; zadanie p. 7 mówi tylko o ~200 obrazach w parach/grupach).
- Czy wolno wgrać dane KAS na OMENa (zadanie p. 7: dane chronione).
- Ile aut dziennie i ile typów naczep (P5: założenie, Artur nie zna).

## Co zrobić teraz (kolejność)
1. Programista zleca S1 i S2 (te same zbiory, ten sam przebieg co S0), potem S3 i S4; do S3 potrzebny rozszerzony zbiór kontrolny (6 par z dodatkiem w ładunku) — decyzja Szefa, bo zmienia zakres generatora.
2. Do `docs/spec.md` (Projektant): test A15b (atak 3) i zapis, że makieta pokazuje wynik modelu, nie dane udawane (atak 5).
3. E3 z Arturem dopiero po S1 i S3.

<!-- skill: prioritize-assumptions -->
<!-- skill: strategy-red-team -->
