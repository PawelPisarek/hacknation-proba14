# Zgłoszenie HackTribe — DRAFT 

> Zgodne ze specyfikacją docs/spec.md (zamkniętą 11:51). Limity liczone `wc -m`. Bez liczb skuteczności do czasu pomiaru.

## Nazwa projektu (≤ 50 znaków)

**Różnica RTG** [11/50] — wybór Szefa (docs/decyzje.md, 11:49): krótka, mówi wprost, że chodzi o różnicę między obrazami RTG. Rozważane: Drugie Oko RTG, Wzorzec RTG, Znajdź Skrytkę, RTG Obok (docs/pm/06-nazwa-haslo.md).

## Hasło (jedno zdanie, ≤ 120 znaków) [102/120]

Pokazuje na obrazie RTG naczepy to, czego nie ma we wzorcu — zaczynając od najpewniejszego miejsca.

## Nazwa zespołu

Hackathon (do potwierdzenia przez ludzi)

## Link do repo

https://github.com/PawelPisarek/hacknation-proba14

## Opis krótki (≤ 300 znaków) [297/300]

Operator RTG widzi obraz naczepy obok wzorcowego i listę miejsc od najpewniejszego; wybiera rodzaj towaru (też „pusta naczepa”) i „do kontroli” albo „odrzuć”. Bez pary sam dobiera wzorzec, a gdy niepewny, ostrzega „wzorzec niepewny”. Szuka skrytek w konstrukcji. Dane sztuczne.

## Opis średni (≤ 1000 znaków) [899/1000]

Przemytnicy ukrywają towar w skrytkach w konstrukcji naczepy (podwójna podłoga, ściana przy kabinie), a operator RTG ma kilka minut na auto. Operator wczytuje obraz, wybiera rodzaj zgłoszonego towaru (sprzęt i AGD, odzież, żywność, materiały budowlane, inne, „pusta naczepa” lub „nie wiem”) i widzi obraz badany obok wzorcowego oraz listę miejsc od najpewniejszego, z opisem różnicy i powiększeniem. Decyzja: „do kontroli” albo „odrzuć” z powodem.

Wzorzec nie jest konieczny: bez pary program sam dobiera czysty obraz tego typu naczepy, a gdy jest niepewny, pokazuje ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec”. Towar zgodny ze zgłoszeniem nie dostaje ramki; przy „nie wiem” zaznaczamy wszystko.

Sprawdzamy na własnym, sztucznym zbiorze naczep (prawdziwych obrazów nie mamy). Wyniki: [TODO: zbędne alarmy / przeoczenia / czas na obraz].

## Opis pełny (≤ 2000 znaków) [1909/2000]

Problem. Operatorzy RTG Służby Celno-Skarbowej oceniają obrazy naczep i decydują o kontroli fizycznej. Towar bywa ukryty w drobnych przeróbkach konstrukcji, np. w podwójnej podłodze albo ścianie przy kabinie, a istniejące narzędzie do wykrywania papierosów słabo radzi sobie z małymi ilościami. Operator przy stanowisku ma kilka minut na auto.

Rozwiązanie. Operator wczytuje obraz badanej naczepy i wybiera z listy rodzaj zgłoszonego towaru: sprzęt i AGD, odzież i tekstylia, żywność i napoje, materiały budowlane, inne, „pusta naczepa” albo „nie wiem”. Na ekranie widzi obraz badany obok wzorcowego i z boku listę miejsc od najpewniejszego, każde z krótkim opisem różnicy. Kliknięcie miejsca przybliża je na obu obrazach. Przy każdej pozycji są przyciski „do kontroli” i „odrzuć” (z powodem z listy); zapis zawiera miejsce i przedmiot kontroli. Decyzja zostaje po stronie operatora.

Tryb bez pary. Operator zwykle nie ma czystego obrazu tego samego typu, więc program sam dobiera wzorzec z katalogu. Gdy dobór jest niepewny, nie ukrywa różnic: pokazuje ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec”.

Skrytki w konstrukcji. Dodatek poza ładownią (podłoga, ściana przy kabinie, rama, dach) zawsze jest alarmem. Towar w ładowni zgodny z wybranym rodzajem nie jest zaznaczany; dla „pustej naczepy” alarmem jest każdy przedmiot w ładowni; przy „nie wiem” zaznaczamy każdą różnicę.

Wyróżnik (cele, jeszcze niezmierzone). Celujemy w model uczony tylko na obrazach czystych, bez przykładów przemytu, działający bez internetu na małej karcie graficznej.

Pomiar. Zdjęć KAS nie mamy, więc sprawdzamy na własnym, sztucznym zbiorze naczep; wyniki na nim nie przesądzają o jakości na prawdziwych obrazach. Zbędne alarmy i przeoczenia liczymy osobno. Wyniki: [TODO: zbędne alarmy / przeoczenia / czas na obraz].

## Narzędzia przygotowane wcześniej

- **OpenMausBot** — zespół botów (github.com/milind-soni/OpenMausBot, Apache-2.0), który pracował nad projektem.
- **Modele Claude** (Anthropic) — pisanie kodu i tekstów.
- **pm-skills** (github.com/phuryn/pm-skills, MIT) — skille produktowe (m.in. nazwa produktu, value proposition).

<!-- skill: product-name -->
<!-- skill: value-prop-statements -->
