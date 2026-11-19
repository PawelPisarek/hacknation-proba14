# Zgłoszenie HackTribe — DRAFT

> Zgodne z makietą R3 (zamkniętą) i docs/spec.md. Limity liczone w znakach (skrypt). Liczby skuteczności wyłącznie z wpisu Programisty 12:09 w docs/decyzje.md (wynik bazowy).

## Nazwa projektu (≤ 50 znaków)

**Różnica RTG** [11/50] — wybór Szefa (docs/decyzje.md, 11:49): krótka, mówi wprost, że chodzi o różnicę między obrazami RTG.

## Hasło (≤ 120 znaków) [102/120]

Pokazuje na obrazie RTG naczepy to, czego nie ma we wzorcu — zaczynając od najpewniejszego miejsca.

## Nazwa zespołu

Hackathon (do potwierdzenia przez ludzi)

## Link do repo

https://github.com/PawelPisarek/hacknation-proba14

## Link do makiety

https://pawelpisarek.github.io/hacknation-proba14/makieta/

## Opis krótki (≤ 300 znaków) [267/300]

Operator RTG widzi obraz naczepy obok wzorcowego i listę 4 miejsc od najpewniejszego; wybiera rodzaj towaru (też „pusta naczepa”) i „do kontroli” albo „odrzuć”. Bez pary sam dobiera wzorzec, a gdy niepewny, ostrzega. Zapis kontroli z obrazem z ramkami. Dane sztuczne.

## Opis średni (≤ 1000 znaków) [903/1000]

Przemytnicy ukrywają towar w skrytkach w konstrukcji naczepy (podwójna podłoga, ściana przy kabinie), a operator RTG ma kilka minut na auto. Operator wczytuje obraz, wybiera rodzaj zgłoszonego towaru (sprzęt i AGD, odzież, żywność, materiały budowlane, inne, „pusta naczepa” lub „nie wiem”) i widzi obraz badany obok wzorcowego oraz listę miejsc od najpewniejszego: np. „Podłoga — środek”, „Ściana przednia — przód”. Powiększenie ma przycisk „Następne miejsce”. Decyzja: „do kontroli” albo „odrzuć” z powodem; zapis zawiera obraz naczepy z ramkami.

Wzorzec nie jest konieczny: bez pary program sam go dobiera, a gdy jest niepewny, pokazuje ramki z ostrzeżeniem „wzorzec niepewny”. Towar zgodny ze zgłoszeniem nie dostaje ramki, ale można go obejrzeć w „Pokaż pominięte”.

Wynik bazowy na sztucznym zbiorze (prawdziwych obrazów nie mamy): 2 z 30 czystych obrazów z alarmem, 0 z 60 dodatków przeoczonych.

## Opis pełny (≤ 2000 znaków) [1780/2000]

Problem. Operatorzy RTG Służby Celno-Skarbowej oceniają obrazy naczep i decydują o kontroli fizycznej. Towar bywa ukryty w drobnych przeróbkach konstrukcji, np. w podwójnej podłodze albo ścianie przy kabinie, a istniejące narzędzie do wykrywania papierosów słabo radzi sobie z małymi ilościami. Operator przy stanowisku ma kilka minut na auto.

Rozwiązanie. Operator wczytuje obraz naczepy i wybiera rodzaj zgłoszonego towaru: sprzęt i AGD, odzież, żywność, materiały budowlane, inne, „pusta naczepa” albo „nie wiem”. Widzi obraz badany obok wzorcowego i listę miejsc od najpewniejszego (w makiecie 4: Podłoga — środek, Ściana przednia — przód, Ładownia — tył, Ładownia — przód), każde z opisem różnicy bez miar i pewnością. Dla „pustej naczepy” pozycja dostaje flagę „alarm z reguły”. Kliknięcie przybliża miejsce na obu obrazach, a „Następne miejsce” prowadzi do kolejnego bez zamykania okna. Operator zleca „do kontroli” albo odrzuca z powodem. Zapis kontroli (miejsce, przedmiot, pominięte różnice) zawiera obraz naczepy z ramkami — dowód dla kontroli fizycznej.

Bez pary. Program sam dobiera wzorzec z katalogu. Gdy jest niepewny, pokazuje ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec”; po wskazaniu ramki i pewność się przeliczają.

Skrytki. Dodatek poza ładownią zawsze jest alarmem. Towar zgodny ze zgłoszeniem nie jest zaznaczany, ale „Pokaż pominięte” pozwala go zlecić do kontroli.

Wynik bazowy (sztuczny zbiór, karta GTX 1050; nie przesądza o jakości na prawdziwych obrazach): na 30 czystych obrazach 2 z alarmem, z 60 dodatków 0 przeoczonych (0 z 33 w konstrukcji); pełny obraz 50,4 MB: 0,49 s. Cele jeszcze niezmierzone: uczenie tylko na czystych obrazach, praca bez internetu, partie.

Makieta: https://pawelpisarek.github.io/hacknation-proba14/makieta/

## Narzędzia przygotowane wcześniej

- **OpenMausBot** — zespół botów (github.com/milind-soni/OpenMausBot, Apache-2.0), który pracował nad projektem.
- **Modele Claude** (Anthropic) — pisanie kodu i tekstów.
- **pm-skills** (github.com/phuryn/pm-skills, MIT) — skille produktowe (m.in. nazwa produktu, value proposition).

<!-- skill: product-name -->
<!-- skill: value-prop-statements -->
