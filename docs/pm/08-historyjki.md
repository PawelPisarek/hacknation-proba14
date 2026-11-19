# Krok 4: historyjki (operator) — Różnica RTG

Źródła: `docs/spec.md` (§1, §4–§7, testy A1–A18), `docs/decyzje.md` (P1–P26). Kolejność = ścieżka pokazu do 2 minut (P4, P11, A10). Dane i ekrany sztuczne; ekran po polsku. Dla Programisty (makieta R2): historyjki H1–H10 to ekran główny wariantu 3 + lista miejsc z boku (P12); H11 to zapis (ostatni krok demo), H12 to ścieżka techniczna poza makietą.
Format: „Gdy [sytuacja], chcę [czynność], żeby [skutek]” (skill job-stories, przyjęty zamiast `user-stories` decyzją Szefa) + kryteria akceptacji (K) z numerem testu A ze spec §7. Pozycja bez testu A w spec jest oznaczona „(makieta)”.

## Role
- **Operator RTG** — przy stanowisku, w trakcie kontroli, kilka minut na auto (P1, P5). Główny użytkownik.
- Jedna rola: operator (P1). Roli „kierownik stanowiska” nie ma w specu ani u Artura — usunięta decyzją Szefa (wpis w docs/decyzje.md).

## Ścieżka pokazu (≤ 2 min)

### H1. Wczytanie obrazu i rodzaju towaru — operator
Gdy auto wjechało na stanowisko, chcę wczytać obraz `.bmp` i wybrać z listy rodzaj zgłoszonego towaru (lub „nie wiem”), żeby narzędzie wiedziało, co jest zgodne ze zgłoszeniem.
- K1. Lista: sprzęt i AGD · odzież i tekstylia · żywność i napoje · materiały budowlane · inne · pusta naczepa · „nie wiem” (domyślnie) (P17; spec §2, §6). Test: makieta R3 (pole rodzaju towaru przed analizą); skutki — K2–K5.
- K2. Przy „nie wiem” narzędzie zaznacza wszystko, co różni się od wzorca (P15, P2). Test: A16.
- K3. Przy „pusta naczepa” każdy przedmiot w ładowni dostaje ramkę. Test: A17.
- K4. Przy rodzaju towaru zgodnym z ładunkiem inny ładunek niż we wzorcu nie dostaje ramki, ale dodatek ukryty w ładunku nadal jest wykryty. Testy: A15 (brak alarmu na ładunku), A15b (dodatek w ładunku wykryty).
- K5. Dodatek w konstrukcji (podłoga, ściana przy kabinie, rama, dach) jest alarmem zawsze, także przy podanym rodzaju towaru i przy „nie wiem” (spec §4a). Testy: A15, A16.

### H2. Wzorzec dobrany sam — operator
Gdy nie mam czystego obrazu tego samego typu naczepy (zwykle nie mam, P8), chcę, żeby narzędzie samo dobrało wzorzec i pokazało podpis „dobrany: typ …, podobieństwo …”, żeby nie szukać wzorca ręcznie.
- K1. Podpis dobranego wzorca widoczny przy obrazach (spec §6: „typ naczepa plandeka 3-osiowa, 13,6 m (podobieństwo 0,93)”). Test: A4.
- K2. Wynik w kilka sekund (pokaz), obraz pełnowymiarowy < 60 s, pamięć karty < 4 GB. Test: A6.
- K3. Detektor działa lokalnie bez sieci (CLI i usługa na tej samej maszynie, karta OMENa). Test: A11. Pokaz pod linkiem idzie przez sieć (decyzja Szefa 11:55; spec §4d) i jest mierzony osobno: A10.

### H3. Dwa obrazy obok siebie — operator
Gdy analiza się skończyła, chcę widzieć wzorzec i badane auto obok siebie, a na badanym ramki, żeby od razu zobaczyć „jest / nie ma” w tym samym miejscu (P12).
- K1. Wzorzec i badane auto obok siebie, na badanym ramki numerowane wg listy (spec §1, §5). Układ lewy/prawy (wzorzec z zaznaczonym odpowiednikiem miejsca po lewej) to układ makiety wariantu 3, nie wymóg speca. Test: makieta.
- K2. Na aucie kilka ramek, nie kilkadziesiąt (P2); raportowana średnia i maksimum ramek na obraz. Test: A3.
- K3. Przeoczenie dodatku liczone osobno i traktowane jako gorsze niż zbędny alarm. Testy: A1 (zbędne alarmy na czystych), A2 (przeoczenia).

### H4. Lista miejsc od najpewniejszego — operator
Gdy mam kilka minut na auto, chcę listy miejsc z boku od najpewniejszego, z nazwą miejsca, krótkim opisem różnicy i pewnością, żeby zacząć od najważniejszego (P7, P9, P12).
- K1. Kolejność malejąco wg pewności. Test: A7.
- K2. Pozycja: nazwa miejsca (strefa), opis różnicy (szablon: strefa + gęściej/rzadziej niż wzorzec + wielkość), pewność 50–99% (spec §5, 4a). Test: A7, makieta.
- K3. Dane udawane makiety (spec §6, P18–P20): 1. Podłoga — środek, 91% · 2. Ściana przednia — przód, 78% · 3. Ładownia — tył, 66% (do kontroli) · 4. Ładownia — przód, 57% (odrzuć; przy „nie wiem” powód „ładunek zgodny z dokumentami (sprawdzony ręcznie)”, P21). Nazwy = strefa + położenie, opisy bez miar.

### H5. Klik w miejsce → powiększenie na obu obrazach — operator
Gdy klikam miejsce na liście albo w ramce, chcę, żeby oba obrazy przybliżyły to samo miejsce, żeby zobaczyć, czym różni się od wzorca (P10, P12).
- K1. Klik na liście i klik w ramkę dają ten sam efekt: wycinek z marginesem na wzorcu i badanym. Test: A5 (Podłoga — środek, Ściana przednia — przód — z powiększeniem), makieta.
- K2. Mały dodatek w konstrukcji nadal wykryty po zmniejszeniu obrazu do 1200 px; porównanie FN na zmniejszeniu i na pełnym obrazie. Test: A12.

### H6. „Do kontroli” jednym kliknięciem — operator
Gdy miejsce wygląda groźnie, chcę jednym kliknięciem przy pozycji listy zlecić kontrolę fizyczną, żeby nie szukać przycisku (P3, P13: przyciski przy każdej pozycji).
- K1. Przycisk „do kontroli” przy każdej pozycji listy; decyzja zapisuje się z miejscem i przedmiotem kontroli (strefa + przód/środek/tył; spec §4c). Test: A8.
- K2. Po decyzji licznik z H8 maleje. Test: A9. (Wygląd pozycji po decyzji — makieta, bez testu A.)

### H7. „Odrzuć” z powodem z listy — operator
Gdy alarm jest zbędny, chcę odrzucić go jednym kliknięciem z powodem z listy, żeby w zapisie było wiadomo, czemu alarm był zbędny (P3).
- K1. Powody: znany element konstrukcji · ładunek zgodny z deklaracją · artefakt obrazu · inny typ naczepy niż wzorzec · inne; przy „nie wiem” zamiast „ładunek zgodny z deklaracją”: „ładunek zgodny z dokumentami (sprawdzony ręcznie)” (P21) (spec §6). Test: A8.
- K2. Odrzucenie bez powodu niemożliwe; powód trafia do zapisu. Test: A8.

### H8. Linia „ile miejsc zostało” — operator
Gdy przechodzę po liście, chcę linii „N miejsc do sprawdzenia · zostało M” przy aucie, żeby wiedzieć, ile jeszcze mam (P10).
- K1. N zgadza się z liczbą ramek, M maleje po każdej decyzji (H6, H7), w demo kończy na 0. Test: A9.
- K2. Nic poza tą linią z „podsumowania partii” (poza zakresem, P10).

### H9. Wzorzec niepewny — operator
Gdy narzędzie nie jest pewne doboru wzorca (np. typ naczepy spoza katalogu), chcę widzieć ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec”, żeby nic nie zostało po cichu pominięte (P16 A, P2, P8).
- K1. Flaga i ramki pokazane jednocześnie (ramek nie ukrywamy). Test: A18 i makieta R3 (flaga „wzorzec niepewny” i ramki razem; spec §6).
- K2. Operator wskazuje wzorzec z listy typów w katalogu albo wgrywa plik wzorca (tryb z parą); po wskazaniu lista przelicza się. Test: A18.
- K3. Tryb z parą działa też, gdy operator od razu poda czysty obraz. (spec §4) Test: makieta R3; A4 mierzy tylko trafność doboru wzorca bez pary (H2).

### H10. Ocena ekranu przez operatora — operator (Artur)
Gdy mam kilka minut na auto, chcę z ramek, opisu różnicy i powiększenia podjąć decyzję dla każdej ramki, żeby nie potrzebować nic poza ekranem (P11, punkt 3).
- K1. Próba ręczna z Arturem na makiecie (dane udawane): tak/nie + uwagi. Test: A14.
- K2. Cała ścieżka H1→H8 i zapis w ≤ 2 min: wczytanie → wzorzec → „Podłoga — środek” → klik → powiększenie → „do kontroli” → „Ściana przednia — przód” → „do kontroli” → „Ładownia — tył” → „do kontroli” → „Ładownia — przód” → „odrzuć” z powodem → linia „zostało 0” → zapis z H11 (spec §1, demo). Test: A10.

## Koniec ścieżki pokazu i po kontroli

### H11. Zapis kontroli i jego odczyt — operator (ostatni krok demo)
Gdy skończyłem decyzje przy aucie, chcę zapisać kontrolę i pobrać plik „miejsce — do kontroli: przedmiot / odrzucone (powód)”, żeby dało się potem odczytać, co zlecono i dlaczego odrzucono (zadanie p. 9; P3).
- K1. Zapis: JSON na serwerze aplikacji z możliwością pobrania (zapis i pobranie JSON są w makiecie R2; spec §6); zawiera użyty wzorzec, rodzaj towaru, miejsce, przedmiot kontroli, decyzję i powód (spec §2, §4d). Test: A8.
- K2. Obraz naczepy z ramkami (PNG, układ pełnej rozdzielczości) jest częścią zapisu kontroli i **już w makiecie** — Artur: „dowód dla kontroli fizycznej” (P32 = B; spec §2, §4d, §6). W makiecie: podgląd obrazu z ramkami i przycisk „Pobierz obraz z ramkami (PNG)” obok JSON. Test: sprawdzenie ręczne w makiecie (A14).
- K3. Operator otwiera pobrany zapis i widzi dla każdej pozycji miejsce, decyzję i powód odrzucenia — bez nowych ekranów. Test: A8.

### H12. Partia obrazów i duże pliki — ścieżka techniczna, bez roli użytkownika (poza makietą)
Gdy trzeba przeliczyć wiele aut (wiersz poleceń, nie ekran), chcę uruchomić folder `.bmp` i dostać JSON i PNG na obraz plus zbiorczy CSV, żeby sprawdzić, czy narzędzie wytrzymuje duże pliki (wymaganie zadania p. 3, 6; nie funkcja operatora, P1).
- K1. Pełnowymiarowe obrazy (12000×4200, ~50 MB): czas na obraz, szczytowa pamięć karty, obrazy/min zapisane, bez obietnic. Test: A13.
- K2. Poza ścieżką pokazu i poza makietą R1 (spec §4d; podsumowanie partii na ekranie — poza zakresem, P10).

## Pokrycie testów A1–A18
A1, A2, A3 → H3 · A4, A6, A11 → H2 · A5 → H5 · A7 → H4 · A8 → H6, H7, H11 · A9 → H6, H8 · A10 → H10 · A12 → H5 (mierzone: FN po zmniejszeniu do 1200 px, nie widoczność) · A13 → H12 · A14 → H10 · A15, A15b, A16, A17 → H1 · A18 → H9. A4 tylko w H2, A10 tylko w H10.

## Założenia i otwarte
- Rola „kierownik stanowiska” usunięta (decyzja Szefa); jedyna rola to operator; H12 nie ma roli użytkownika.
- Wyniki A1–A18 na danych sztucznych nie przenoszą się na dane KAS (spec §8).

<!-- skill: przeplywy-pm -->
<!-- skill: job-stories -->
