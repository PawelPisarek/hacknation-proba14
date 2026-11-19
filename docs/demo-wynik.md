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

## Wariant `test/d019_B`, bez pary, „sprzęt i AGD” — pełna lista w kolejności z ekranu (dla P39)

Prawda generatora (`opis.json`, ramki w px obrazu 1200×420): (a) duży obiekt w ładunku [693,94–836,209]; (b) mały obiekt
przy ścianie od kabiny [86,245–93,252]; (c) średni obiekt w podwójnej podłodze, przeróbka [562,294–708,297].
Dopasowanie: ramka miejsca nachodzi na ramkę prawdy.

**Na liście (5)** — nagłówek „Miejsca od najpewniejszego”, linia „5 miejsc do sprawdzenia · zostało 5”:

| # | Miejsce | Strefa | Pewność | Prawda generatora |
|---|---|---|---|---|
| 1 | Ściana przednia — dół | konstrukcja | 69% | (b) mały obiekt przy ścianie od kabiny — **trafienie** |
| 2 | Podłoga — środek | konstrukcja | 54% | (c) fragment obiektu w podwójnej podłodze — trafienie |
| 3 | Podłoga — środek | konstrukcja | 52% | (c) ten sam obiekt, inny fragment |
| 4 | Podłoga — środek | konstrukcja | 52% | (c) ten sam obiekt, inny fragment |
| 5 | Podłoga — środek | konstrukcja | 51% | (c) ten sam obiekt, inny fragment |

**Pominięte (5)** — „pominięto 5 różnic … Pokaż pominięte” (kategoria „inny ładunek niż we wzorcu”):

| # | Miejsce | Strefa | Pewność | Prawda generatora |
|---|---|---|---|---|
| 1 | Ładownia — tył | ładownia | 94% | **zawiera (a) duży obiekt w ładunku** — prawdziwy dodatek ukryty pod „pominięte” |
| 2 | Ładownia — środek | ładownia | 91% | brak dodatku — inny ładunek niż we wzorcu |
| 3 | Ładownia — przód | ładownia | 89% | brak dodatku — inny ładunek niż we wzorcu |
| 4 | Ładownia — tył | ładownia | 86% | brak dodatku — inny ładunek niż we wzorcu |
| 5 | Ładownia — środek | ładownia | 83% | brak dodatku — inny ładunek niż we wzorcu |

Wnioski dla P39:
- Pierwsze miejsce na liście **jest w konstrukcji** (ściana przy kabinie, 69%) — pokaz zaczyna się od skrytki (P4).
- Na liście **nie ma pozycji do „odrzuć”** — wszystkie 5 to prawdziwe dodatki; pozycje 2–5 to jeden obiekt w podłodze podzielony na 4 ramki o niskiej pewności (51–54%).
- Do „odrzuć” nadają się pominięte 2–5 (inny ładunek, powód „ładunek zgodny z deklaracją”) — po „Pokaż pominięte”.
- **Ryzyko:** prawdziwy dodatek w ładunku (a) trafia do pominiętych (ramka „inny ładunek” 94% go obejmuje); widać go tylko po „Pokaż pominięte” (kłóci się z A15b: dodatek w ładunku ma być wykryty mimo rodzaju towaru).
- Z parą (`test/d019_B`, para) ten sam obraz daje 3 miejsca bez pominiętych: Ładownia — środek 95% (a), Ściana przednia — dół 90% (b), Podłoga — środek 85% (c) — tam pierwsze jest w ładowni, nie w konstrukcji.

## Pokaz (P39)

Wariant (Artur, 12:53): `test/d019_B`, **bez pary** (wzorzec dobrany z katalogu: typ B, pewność doboru 48%), towar
**„sprzęt i AGD”**. Metoda `C_model_typu`, karta GTX 1050, **czas przebiegu na karcie 1,06 s** (od kliknięcia do wyniku
na ksefbot.pl ok. 1,3–1,6 s). Zapis: `aplikacja/zapisane/analiza-4.json`. Ekran na starcie ma ten wariant już wybrany;
w trybie „wynik zapisany” pokazuje ten sam wynik.

Linia na ekranie: „5 miejsc do sprawdzenia · zostało 5”; nad listą „pominięto 5 różnic … Pokaż pominięte”.

**Lista (kolejność z ekranu):**

| # | Strefa | Położenie | Pewność | Konstrukcja / ładunek | Prawda generatora |
|---|---|---|---|---|---|
| 1 | Ściana przednia | dół | 69% | konstrukcja | mały obiekt przy ścianie od kabiny |
| 2 | Podłoga | środek | 54% | konstrukcja | obiekt w podwójnej podłodze (fragment) |
| 3 | Podłoga | środek | 52% | konstrukcja | ten sam obiekt (inny fragment) |
| 4 | Podłoga | środek | 52% | konstrukcja | ten sam obiekt (inny fragment) |
| 5 | Podłoga | środek | 51% | konstrukcja | ten sam obiekt (inny fragment) |

(Ściana przednia ma położenie wg wysokości: góra/środek/dół; pozostałe strefy przód/środek/tył.)

**Pominięte (5, po „Pokaż pominięte”):**

| # | Strefa | Położenie | Pewność | Rodzaj | Prawda generatora |
|---|---|---|---|---|---|
| 1 | Ładownia | tył | 94% | inny ładunek niż we wzorcu | **zawiera duży obiekt ukryty w ładunku** |
| 2 | Ładownia | środek | 91% | inny ładunek niż we wzorcu | brak dodatku |
| 3 | Ładownia | przód | 89% | inny ładunek niż we wzorcu | brak dodatku |
| 4 | Ładownia | tył | 86% | inny ładunek niż we wzorcu | brak dodatku |
| 5 | Ładownia | środek | 83% | inny ładunek niż we wzorcu | brak dodatku |

- **Pierwsze miejsce jest w konstrukcji** (Ściana przednia — dół, 69%, skrytka przy kabinie) — pokaz zaczyna się od niej (P4). Kolejności nie zmieniano.
- **„Odrzuć” (P3, P20):** na liście nie ma fałszywego alarmu — wszystkie 5 miejsc to prawdziwe dodatki. Najmniej szkodliwy kandydat: **#5 Podłoga — środek, 51%**,
  najniższa pewność, to czwarta ramka na tym samym obiekcie co #2 (zlecone do kontroli). Powód z listy: **„inne”** (to samo miejsce co #2).
  Odrzucenie #5 nie gubi skrytki, bo #2–#4 wskazują ten sam obiekt. Powód „znany element konstrukcji” byłby nieprawdziwy (tam jest przeróbka podłogi).
- Ryzyko do pokazu: prawdziwy dodatek w ładunku jest w **pominiętych #1** (ramka „inny ładunek” 94% go obejmuje) — widać go dopiero po „Pokaż pominięte” (A15b).
