# Slajdy: Różnica RTG

Prezentacja (9 slajdów, jeden nagłówek `##` = jeden slajd; docelowo PDF). Źródła: `docs/spec.md`, `docs/hacktribe.md`, `README.md`. Dane są sztuczne; liczby skuteczności pochodzą z wyniku bazowego (`wyniki/bazowy/`) i nie przesądzają o jakości na prawdziwych obrazach. Działająca wersja: https://hacknation.ksefbot.pl/ . Makieta (R3): https://pawelpisarek.github.io/hacknation-proba14/makieta/

## 1. Różnica RTG

**Pokazuje na obrazie RTG naczepy to, czego nie ma we wzorcu — zaczynając od najpewniejszego miejsca.**

Narzędzie dla operatora RTG Służby Celno-Skarbowej. Zespół: Hackathon.

*Co pokazać:* ekran główny makiety R3: obraz badany obok wzorcowego, z boku lista miejsc.

## 2. Problem operatora

- Operator RTG ma kilka minut na jedno auto.
- Towar bywa ukryty w drobnych przeróbkach konstrukcji naczepy: w podwójnej podłodze, w ścianie przy kabinie.
- Obecne narzędzie do wykrywania papierosów słabo radzi sobie z małymi ilościami.
- Szukanie różnic „na oko” między obrazami zabiera czas, którego operator nie ma.

*Co pokazać:* zrzut surowego obrazu RTG naczepy (sztucznego, z generatora) bez żadnych zaznaczeń.

## 3. Jak działa: wzorzec obok badanego

- Operator wczytuje obraz badanej naczepy (`.bmp`).
- Na ekranie dwa obrazy obok siebie: wzorzec i badane auto z ramkami.
- Z boku lista miejsc od najpewniejszego (w pokazie: obraz bez pary, towar „sprzęt i AGD”, lista od ściany przedniej; miejsca i pewności: [z prawdziwego wyniku]), każde z opisem różnicy bez miar.
- Klik w miejsce przybliża je na obu obrazach; „Następne miejsce” prowadzi do kolejnego bez zamykania okna.
- Decyzja zostaje po operatorze: „do kontroli” albo „odrzuć” (z powodem z listy).
- Zapis kontroli: miejsce, przedmiot kontroli, „do kontroli” / odrzucone (powód) i pominięte różnice; zawiera obraz naczepy z ramkami (podgląd, pobranie JSON + PNG) — dowód dla kontroli fizycznej. Zapis kończy demo.

*Co pokazać:* lista miejsc ([z prawdziwego wyniku]); klik w pierwsze i powiększenie na obu obrazach, „Następne miejsce”; jedną pozycję „do kontroli”, jedną „odrzuć”; na końcu zapis kontroli z obrazem z ramkami.

## 4. Tryb bez pary i niepewny wzorzec

- Operator zwykle nie ma czystego obrazu tego samego typu naczepy.
- Program sam dobiera wzorzec z katalogu (podpis „dobrany: typ …, podobieństwo …”).
- Gdy dobór jest niepewny, nie ukrywa różnic: pokazuje ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec”.
- Operator wskazuje wzorzec z listy typów (obraz wzorca zmienia się z typem, podpis „obraz poglądowy”) albo wgrywa plik; znacznik „wskazany ręcznie” zostaje, a ramki i pewność się przeliczają.

*Co pokazać:* podpis dobranego wzorca; auto z ostrzeżeniem „wzorzec niepewny” i niższą pewnością przy ramkach; wskazanie wzorca.

## 5. Rodzaj towaru

- Przed analizą operator wybiera rodzaj zgłoszonego towaru: sprzęt i AGD, odzież i tekstylia, żywność i napoje, materiały budowlane, inne, „pusta naczepa” albo „nie wiem”.
- Towar zgodny ze zgłoszeniem nie dostaje ramki; dodatek ukryty w ładunku ma nadal dawać ramkę (rozpoznanie „zgodny” dopiero mierzymy).
- Dodatek poza ładownią (podłoga, ściana przy kabinie, rama, dach) jest zawsze alarmem.
- „Pusta naczepa”: alarmem jest każdy przedmiot w ładowni — pozycja z flagą „alarm z reguły: pusta naczepa” na górze listy. „Nie wiem”: zaznaczamy każdą różnicę.
- Pominięta różnica (towar zgodny ze zgłoszeniem) nie ginie: „Pokaż pominięte” (z odmianą „1 różnicę / 2 różnice / 5 różnic”), można ją zlecić do kontroli; w zapisie „pominięte: N”.

*Co pokazać:* lista „Rodzaj zgłoszonego towaru” w makiecie; wybór „pusta naczepa” i „Pokaż pominięte”.

## 6. Wyniki

- Wynik bazowy (metoda A, para wzorzec–badany): zbędny alarm na 2 z 30 czystych obrazów; przeoczone 0 z 60 dodatków (0 z 33 w konstrukcji); 1,3 miejsca na auto.
- Pełny obraz 50,4 MB: 0,49 s na obraz; szczyt pamięci karty 991 MiB (źródło: `wyniki/bazowy/przebieg.log`).
- Inne metody: B (cechy) 0/30 zbędnych, ale 23/60 przeoczonych; C (model typu) 15/30 zbędnych, 3/60 przeoczonych.
- Źródło: wpis Programisty 12:09 w `docs/decyzje.md`, `wyniki/bazowy/tabela.md`. Kolejne pomiary dopiszemy, gdy będą.
- Zbędne alarmy i przeoczenia liczymy osobno; przeoczenie jest gorsze.
- Pomiar na własnym, sztucznym zbiorze: wynik nie przesądza o jakości na prawdziwych obrazach.

*Co pokazać:* tabela wyników z `wyniki/bazowy/tabela.md`.

## 7. Jak liczymy

- Zdjęć KAS nie mamy: własny sztuczny zbiór naczep (czyste i z dodatkami, 4 typy dodatków, maski).
- Cały model liczy na małej karcie graficznej (GTX 1050, 4 GB), nigdy na procesorze.
- Model uczony tylko na obrazach czystych, bez przykładów przemytu (cel, jeszcze niezmierzony).
- Skalowanie: pełny obraz (ok. 50 MB) przechodzi w 0,49 s; partia z wiersza poleceń (folder `.bmp` → JSON, PNG, CSV) — **w planie**, dopóki nie zadziała; pomiar na większych zbiorach jeszcze przed nami. Liczby 50,4 MB i 991 MiB: `wyniki/bazowy/przebieg.log`.
- Cel: praca bez internetu i chmury, jeszcze niezmierzony; pokaz pod linkiem idzie przez sieć (przeglądarka → ksefbot.pl → usługa na OMENie; działająca wersja: https://hacknation.ksefbot.pl/).

*Co pokazać:* zrzut z karty OMENa (przebieg na GPU) albo schemat: przeglądarka → ksefbot.pl → usługa na OMENie → JSON + PNG.

## 8. Narzędzia

- **OpenMausBot** (Apache-2.0): zespół 5 botów: Szef, Projektant, Analityk, Programista, Prezenter.
- **Modele Claude** (Anthropic): kod, specyfikacja, teksty.
- **pm-skills** (MIT): kroki produktowe, nazwa, value proposition, PRD.
- Skill `dummy-dataset` (plan sztucznego zbioru) i generator `anomalie/generator.py`; biblioteki `numpy`, `scipy`, `pillow`, `torch`, `torchvision`.
- GitHub Pages (makieta), Coolify na ksefbot.pl (https://hacknation.ksefbot.pl/), orkiestrator i karta graficzna OMENa.

*Co pokazać:* zrzut listy botów w OpenMausBot albo sekcja „Użyte narzędzia” z README.

## 9. Co dalej

- Kolejne pomiary na zbiorze testowym i wpisanie wyników (zbędne alarmy, przeoczenia, czas, skalowalność w partii).
- Próba ręczna na makiecie z Arturem: czy z ramek, opisu i powiększenia da się podjąć decyzję w kilka minut.
- Dane KAS: ich nie mamy; jeśli się pojawią, tylko w ramach zasad z zadania (chronione, bez kopiowania poza hackathon), po decyzji Pawła.
- Integracja z repozytorium obrazów skanera jako ścieżka wdrożenia.

*Co pokazać:* link do repo https://github.com/PawelPisarek/hacknation-proba14, do działającej wersji https://hacknation.ksefbot.pl/ i do makiety https://pawelpisarek.github.io/hacknation-proba14/makieta/ .

<!-- skill: value-prop-statements -->
