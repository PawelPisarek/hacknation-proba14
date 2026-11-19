# Materiały zadania (KAS — wyszukiwarka anomalii na obrazach RTG)

Źródło: `docs/zadanie.md` (nr sekcji w nawiasach), `docs/decyzje.md`. Liczb spoza zadania nie wpisuję.

## 1. Wymagania wprost
| Wymaganie | Źródło |
|---|---|
| Autonomiczne porównanie par/grup obrazów RTG środków przewozowych, bez człowieka | 2, 3 |
| Wykrycie odstępstwa od „reguły” (np. wzorzec pusty vs z dodatkowymi elementami) | 3 |
| Techniki dowolne: detekcja anomalii, segmentacja, porównanie pikselowe | 3 |
| Raport z wykrytymi anomaliami (np. zaznaczone obszary na obrazie) | 3 |
| Wejście: `*.bmp`, ~50 MB/plik; kompresja i przetwarzanie partiami | 3 |
| Skalowalność na większe zbiory w przyszłości | 3 |
| Uczenie na obrazach wzorcowych (prawidłowy środek transportu, bez anomalii) | 5 |
| < 1 min na obraz | 7 |
| Docelowo bez internetu/chmury AI (na hackathonie narzędzia AI do pisania kodu wolno) | 9 |
| Oddanie: tytuł + szczegółowy opis, repozytorium, PDF ≤ 10 slajdów (opcjonalnie zrzuty, linki do dema) | 4 |
| Dane KAS: chronione — nie udostępniać, nie kopiować, tylko na potrzeby hackathonu | 7 |

## 2. Sprawdzanie (6)
- Zbiór „czystych”: model nie ma zaznaczać niczego; każdy alarm = **false positive** (liczony poziom FP).
- Zbiór z „dodatkami” (elementy niekonstrukcyjne): model ma je wskazać graficznie; brak wskazania = **false negative**.
- Kryteria: skuteczność (FP i FN), innowacyjność, skalowalność. Pełna lista kryteriów (sekcja 8) — „zna Szef”, w zadaniu jej nie ma.
- Zadanie nie podaje: progu FP/FN, definicji trafienia (IoU? środek w ramce?), wagi kryteriów.

## 3. Dane
- KAS: ~200 obrazów RTG, pary/grupy („przed”/„po” załadunku), ~50 MB każdy, ~10 GB razem, anonimizowane symulacyjne; Nuctech i Multicontrol (1). Wydanie: pendrive na stoisku KAS (7).
- **Nie mamy ich** → decyzja (11:24, Szef, od ludzi): własny sztuczny zbiór naczep `.bmp` (czyste / z dodatkami). Wniosek: wyniki FP/FN na sztucznym zbiorze nie przenoszą się na dane KAS; w prezentacji pisać to uczciwie.
- Brak: etykiet/masek dodatków, informacji o parowaniu plików, głębi bitowej i wymiarów BMP, podziału train/test.

## 4. Ryzyka techniczne
1. **GTX 1050, 4 GB, nigdy CPU** (decyzje): obraz ~50 MB nie mieści się w całości w sieci → kafelki/skalowanie obowiązkowe; model mały.
2. **Rozmiar BMP:** wczytanie i dekodowanie ~50 MB × pary; pamięć RAM ThinkPada 7,6 GB — ciężkie tylko na OMENie.
3. **Wyrównanie par:** wzorzec i badany zwykle różnią się pozycją/skalą/pojazdem (nie ten sam kadr) → różnica pikselowa da lawinę FP; potrzebna rejestracja albo model „reguły” zamiast diffu.
4. **< 1 min/obraz** na GTX 1050 przy ~50 MB — do zmierzenia (jeden przebieg ≥ 2 hipotezy).
5. **Sztuczny zbiór ≠ prawdziwy RTG:** ryzyko przeuczenia na artefaktach generatora.
6. **Pokaz:** aplikacja pod linkiem zależy od usługi na OMENie w sieci lokalnej (single point of failure; konieczny plan B — nagrany wynik).
7. **Skalowalność:** tylko deklaracja bez pomiaru nie punktuje — potrzebna liczba obrazów/min z przebiegu partiami.

## 5. Pytania otwarte (z rekomendacją)
| # | Pytanie | Zadanie rozstrzyga? | Rekomendacja |
|---|---|---|---|
| Q1 | Kryteria oceny (sekcja 8) i wagi? | Nie („zna Szef”) | Szef poda treść; do tego czasu optymalizować FP i FN równo. |
| Q2 | Co jest ważniejsze: FP czy FN (koszt operatora)? | Nie | Artur: priorytet mało FP na czystych (zadanie: „nie zaznaczała jakichkolwiek”), FN na drugim miejscu. |
| Q3 | Kiedy alarm uznajemy za trafiony (nakładanie ramki)? | Nie | Trafienie = ramka z IoU ≥ 0,1 z maską dodatku (luźno; do uzgodnienia w Q-lista Projektanta). |
| Q4 | Jak liczyć FP: na obraz (jakikolwiek alarm) czy na region? | Częściowo (6: „nie zaznaczała jakichkolwiek” → na obraz) | Na obraz; dodatkowo raportować liczbę regionów. |
| Q5 | Co generator sztucznego zbioru ma odwzorować (naczepa z boku, skala szarości, typy dodatków)? | Nie (nie mamy próbek KAS) | Artur: 1 typ pojazdu, szarość, 3–4 typy dodatków (mały, w konstrukcji, w ładunku), z maskami. |
| Q6 | Czy wzorzec to ten sam pojazd, czy „czysty obraz tego typu”? | Nie (pary „przed/po”, ale też „grupy”) | Obsłużyć oba: tryb pary (rejestracja + diff) i tryb bez pary (model reguły). |
| Q7 | Kompresja: bezstratna (PNG/zstd) czy skalowanie w dół do analizy? | Nie | Przechowywanie bezstratne, analiza na kafelkach/obrazie zmniejszonym; zmierzyć wpływ na FN. |
| Q8 | Format raportu: nakładka PNG + lista współrzędnych JSON/HTML? | Nie („np. zaznaczone obszary”) | PNG z ramkami + JSON (współrzędne, wynik) + podsumowanie partii. |
| Q9 | Czy w dniu oceny jury podaje własne obrazy (dane KAS z pendrive’a)? | Nie | Założyć tak: skrypt `ocena` ma przyjąć katalog `.bmp` i wypisać FP/FN; przetestować na obrazie 50 MB. |
