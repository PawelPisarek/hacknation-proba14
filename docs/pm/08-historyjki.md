# Krok 4: historyjki (operator, kierownik stanowiska) — Różnica RTG

Źródła: `docs/spec.md` (§1, §4–§7, testy A1–A18), `docs/decyzje.md` (P1–P17). Kolejność = ścieżka pokazu do 2 minut (P4, P11, A10). Dane i ekrany sztuczne; ekran po polsku. Dla Programisty (makieta R1): historyjki H1–H10 to ekran główny wariantu 3 + lista miejsc z boku (P12); H11–H12 to zapis i kierownik.
Format: „Gdy [sytuacja], chcę [czynność], żeby [skutek]” (job-stories — w zestawie pm-skills nie ma skilla `user-stories`, to jest jego odpowiednik) + kryteria akceptacji (K) z numerem testu A ze spec §7. Pozycja bez testu A w spec jest oznaczona „(makieta)”.

## Role
- **Operator RTG** — przy stanowisku, w trakcie kontroli, kilka minut na auto (P1, P5). Główny użytkownik.
- **Kierownik stanowiska** — *założenie, nie ustalenie Artura* (P1 mówi tylko o operatorze): ogląda zapis kontroli po fakcie i powody odrzuceń (P3: „żeby było wiadomo, czemu alarm był zbędny”). Nie ma własnych funkcji ponad zapisem z H11 — zakres się nie zmienia.

## Ścieżka pokazu (≤ 2 min)

### H1. Wczytanie obrazu i rodzaju towaru — operator
Gdy auto wjechało na stanowisko, chcę wczytać obraz `.bmp` i wybrać z listy rodzaj zgłoszonego towaru (lub „nie wiem”), żeby narzędzie wiedziało, co jest zgodne ze zgłoszeniem.
- K1. Lista: sprzęt i AGD · odzież i tekstylia · żywność i napoje · materiały budowlane · inne · pusta naczepa · „nie wiem” (domyślnie) (P17; spec §2, §6). Test: A10 (ścieżka), makieta.
- K2. Przy „nie wiem” narzędzie zaznacza wszystko, co różni się od wzorca (P15, P2). Test: A16.
- K3. Przy „pusta naczepa” każdy przedmiot w ładowni dostaje ramkę. Test: A17.
- K4. Przy rodzaju towaru zgodnym z ładunkiem inny ładunek niż we wzorcu nie dostaje ramki, ale dodatek ukryty w ładunku nadal jest wykryty. Testy: A15, A15b.

### H2. Wzorzec dobrany sam — operator
Gdy nie mam czystego obrazu tego samego typu naczepy (zwykle nie mam, P8), chcę, żeby narzędzie samo dobrało wzorzec i pokazało podpis „dobrany: typ …, podobieństwo …”, żeby nie szukać wzorca ręcznie.
- K1. Podpis dobranego wzorca widoczny przy obrazach (spec §6: „typ naczepa plandeka 3-osiowa, 13,6 m (podobieństwo 0,93)”). Test: A4.
- K2. Wynik w kilka sekund (pokaz), obraz pełnowymiarowy < 60 s, pamięć karty < 4 GB. Test: A6.
- K3. Praca bez internetu (liczenie na karcie, lokalnie). Test: A11.

### H3. Dwa obrazy obok siebie — operator
Gdy analiza się skończyła, chcę widzieć wzorzec i badane auto obok siebie, a na badanym ramki, żeby od razu zobaczyć „jest / nie ma” w tym samym miejscu (P12).
- K1. Lewy obraz: wzorzec z zaznaczonym odpowiednikiem miejsca; prawy: badane auto z ramkami, numerowanymi wg listy (spec §1, §5). Test: A10, makieta.
- K2. Na aucie kilka ramek, nie kilkadziesiąt (P2); raportowana średnia i maksimum ramek na obraz. Test: A3.
- K3. Przeoczenie dodatku liczone osobno i traktowane jako gorsze niż zbędny alarm. Testy: A1 (zbędne alarmy na czystych), A2 (przeoczenia).

### H4. Lista miejsc od najpewniejszego — operator
Gdy mam kilka minut na auto, chcę listy miejsc z boku od najpewniejszego, z nazwą miejsca, krótkim opisem różnicy i pewnością, żeby zacząć od najważniejszego (P7, P9, P12).
- K1. Kolejność malejąco wg pewności. Test: A7.
- K2. Pozycja: nazwa miejsca (strefa), opis różnicy (szablon: strefa + gęściej/rzadziej niż wzorzec + wielkość), pewność 50–99% (spec §5, 4a). Test: A7, makieta.
- K3. Dane udawane makiety (spec §6): 1. podwójna podłoga 91% · 2. ściana przy kabinie 78% · 3. w ładunku — paleta 5, 54%.

### H5. Klik w miejsce → powiększenie na obu obrazach — operator
Gdy klikam miejsce na liście albo w ramce, chcę, żeby oba obrazy przybliżyły to samo miejsce, żeby zobaczyć, czym różni się od wzorca (P10, P12).
- K1. Klik na liście i klik w ramkę dają ten sam efekt: wycinek z marginesem na wzorcu i badanym. Test: A5 (podwójna podłoga, ściana przy kabinie — z powiększeniem), makieta.
- K2. Mały dodatek w konstrukcji widoczny po zmniejszeniu obrazu do 1200 px. Test: A12.

### H6. „Do kontroli” jednym kliknięciem — operator
Gdy miejsce wygląda groźnie, chcę jednym kliknięciem przy pozycji listy zlecić kontrolę fizyczną, żeby nie szukać przycisku (P3, P13: przyciski przy każdej pozycji).
- K1. Przycisk „do kontroli” przy każdej pozycji listy; decyzja zapisuje się z miejscem i przedmiotem kontroli (strefa + przód/środek/tył; spec §4c). Test: A8.
- K2. Po decyzji pozycja zmienia stan, a licznik z H8 maleje. Test: A9.

### H7. „Odrzuć” z powodem z listy — operator
Gdy alarm jest zbędny, chcę odrzucić go jednym kliknięciem z powodem z listy, żeby kierownik wiedział, czemu alarm był zbędny (P3).
- K1. Powody: znany element konstrukcji · ładunek zgodny z deklaracją · artefakt obrazu · inny typ naczepy niż wzorzec · inne (spec §6). Test: A8.
- K2. Odrzucenie bez powodu niemożliwe; powód trafia do zapisu. Test: A8.

### H8. Linia „ile miejsc zostało” — operator
Gdy przechodzę po liście, chcę linii „N miejsc do sprawdzenia · zostało M” przy aucie, żeby wiedzieć, ile jeszcze mam (P10).
- K1. N zgadza się z liczbą ramek, M maleje po każdej decyzji (H6, H7), w demo kończy na 0. Test: A9.
- K2. Nic poza tą linią z „podsumowania partii” (poza zakresem, P10).

### H9. Wzorzec niepewny — operator
Gdy narzędzie nie jest pewne doboru wzorca (np. typ naczepy spoza katalogu), chcę widzieć ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec”, żeby nic nie zostało po cichu pominięte (P16 A, P2, P8).
- K1. Flaga i ramki pokazane jednocześnie (ramek nie ukrywamy). Test: A18.
- K2. Operator wskazuje wzorzec z listy typów w katalogu albo wgrywa plik wzorca (tryb z parą); po wskazaniu lista przelicza się. Test: A18.
- K3. Tryb z parą działa też, gdy operator od razu poda czysty obraz. Test: A4 (porównanie trybów), makieta.

### H10. Ocena ekranu przez operatora — operator (Artur)
Gdy mam kilka minut na auto, chcę z ramek, opisu różnicy i powiększenia podjąć decyzję dla każdej ramki, żeby nie potrzebować nic poza ekranem (P11, punkt 3).
- K1. Próba ręczna z Arturem na makiecie (dane udawane): tak/nie + uwagi. Test: A14.
- K2. Cała ścieżka H1→H8 w ≤ 2 min: wczytanie → wzorzec → podwójna podłoga → klik → powiększenie → „do kontroli” → ściana przy kabinie → „do kontroli” → ładunek → „odrzuć” z powodem → linia „zostało 0”. Test: A10.

## Po kontroli

### H11. Zapis kontroli — operator i kierownik stanowiska
Gdy skończyłem decyzje przy aucie, chcę zapisać kontrolę i pobrać plik „miejsce — do kontroli: przedmiot / odrzucone (powód)”, żeby kierownik mógł zobaczyć, co zlecono i dlaczego odrzucono (zadanie p. 9; P3).
- K1. Zapis: JSON na serwerze aplikacji z możliwością pobrania; zawiera użyty wzorzec, rodzaj towaru, miejsce, przedmiot kontroli, decyzję i powód (spec §2, §4d). Test: A8.
- K2. Obraz z ramkami (PNG, układ pełnej rozdzielczości) jako część wyniku. Test: A10, makieta.
- K3. **Kierownik** otwiera zapis i widzi dla każdej pozycji decyzję i powód odrzucenia — bez nowych ekranów (założenie roli).

### H12. Partia obrazów i duże pliki — kierownik stanowiska (poza makietą)
Gdy mam wiele aut do przeliczenia (CLI, nie ekran), chcę uruchomić folder `.bmp` i dostać JSON i PNG na obraz plus zbiorczy CSV, żeby sprawdzić, czy narzędzie wytrzymuje duże pliki.
- K1. Pełnowymiarowe obrazy (12000×4200, ~50 MB): czas na obraz, szczytowa pamięć karty, obrazy/min zapisane, bez obietnic. Test: A13.
- K2. Poza ścieżką pokazu i poza makietą R1 (spec §4d; podsumowanie partii na ekranie — poza zakresem, P10).

## Pokrycie testów A1–A18
A1, A2, A3 → H3 · A4, A6, A11 → H2 · A5, A12 → H5 · A7 → H4 · A8 → H6, H7, H11 · A9 → H8 · A10 → H10 · A13 → H12 · A14 → H10 · A15, A15b, A16, A17 → H1 · A18 → H9.

## Założenia i otwarte
- Rola „kierownik stanowiska” nie pochodzi od Artura (P1: użytkownik = operator); historyjki H11 K3 i H12 nie dodają funkcji. Pytanie do Artura tylko, jeśli Szef uzna rolę za zakres.
- Wyniki A1–A18 na danych sztucznych nie przenoszą się na dane KAS (spec §8).

<!-- skill: przeplywy-pm -->
<!-- skill: job-stories -->
