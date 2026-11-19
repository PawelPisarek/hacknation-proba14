# Wynik pokazu — prawdziwy wynik z karty (R10)

Obraz pokazu: **`test/d019_B`** (naczepa typu B z ładunkiem), tryb **z parą** (czysty obraz tej samej naczepy), rodzaj
towaru „nie wiem”. Wynik z usługi na karcie OMENa (GTX 1050), metoda `A_piksele_para`, próg k=5. Pobrany przez
ksefbot.pl 19.11 (zapis: `aplikacja/zapisane/analiza-1.json`). Czas analizy na karcie: 1,16 s (tylko w JSON zapisu, nie na ekranie — P26).

| # | Miejsce (strefa — położenie) | Pewność | Przedmiot kontroli | Co tam jest naprawdę (prawda generatora) |
|---|---|---|---|---|
| 1 | Ładownia — środek | 95% | ładunek w środkowej części ładowni | duży obiekt w ładunku |
| 2 | Ściana przednia — dół | 90% | przednia ściana skrzyni ładunkowej (przy kabinie) | mały obiekt przy ścianie od kabiny |
| 3 | Podłoga — środek | 85% | podłoga naczepy, środek | średni obiekt w podwójnej podłodze |

Wszystkie trzy ukryte dodatki znalezione, brak fałszywych alarmów. Linia na ekranie: „3 miejsca do sprawdzenia · zostało 3”.
Teksty pokazu (README, slajdy) piszemy według tej tabeli, nie według udawanych 91/78/66/57% z makiety.

## Pozostałe zapisane przebiegi (tryb „wynik zapisany”, gdy karta lub sieć nie odpowiada)

| Wariant | Wynik z karty |
|---|---|
| `test/d028_B`, para, „nie wiem” | 3 miejsca: Ściana przednia — środek 90%, Ładownia — środek 86%, Podłoga — przód 79% |
| pusta naczepa: `test/c001_B`, bez pary, „pusta naczepa” | 6 miejsc w ładowni, każde z flagą „⚑ alarm z reguły: pusta naczepa”, 84–93% (P27, P34) |
| towar: `test/d019_B`, bez pary, „sprzęt i AGD” | 10 miejsc, 5 pominiętych (ładunek zgodny ze zgłoszeniem) → na liście 5, „Pokaż pominięte” (P23, P29, P30) |
| `test/d019_B`, bez pary, „nie wiem” | 10 miejsc (5 w ładowni 83–94%, ściana 69%, 4 słabe w podłodze 51–54%) |
| wzorzec z pliku: `test/d019_B` + plik `wzorzec-d028_B.bmp` | 7 miejsc; zapis „wzorzec: plik wzorzec-d028_B.bmp (wskazany ręcznie)” (P36) — celowo zły wzorzec |
| własne pliki: `badany-d028_B.bmp` + `wzorzec-d028_B.bmp` | 3 miejsca, jak `test/d028_B` z parą |
| wzorzec niepewny: `lustro-d028_B.bmp` (odbity w poziomie, bez pary) | dobrany typ C, pewność doboru 0,12 → „⚠ Wzorzec niepewny — wskaż wzorzec”, 22 miejsca z pewnością ×0,8 (P16, P24) |
| ten sam plik, wskazany typ A z katalogu | 6 miejsc, „wzorzec wskazany ręcznie” (P28) |

Wśród 66 przykładów zbioru żaden nie ma pewności doboru < 0,2 (najniższa 0,47, typ zawsze trafiony) — „wzorzec niepewny”
pokazujemy na odbitym obrazie, którego układ nie pasuje do żadnego wzorca.
