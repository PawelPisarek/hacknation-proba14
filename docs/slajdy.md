# Slajdy: Różnica RTG

Szkielet prezentacji (9 slajdów, jeden nagłówek `##` = jeden slajd; docelowo PDF). Źródła: `docs/spec.md`, `docs/hacktribe.md`, `README.md`. Dane są sztuczne; liczb skuteczności nie podajemy do czasu pomiaru. Makieta: https://pawelpisarek.github.io/hacknation-proba14/warianty/3/

## 1. Różnica RTG

**Pokazuje na obrazie RTG naczepy to, czego nie ma we wzorcu — zaczynając od najpewniejszego miejsca.**

Narzędzie dla operatora RTG Służby Celno-Skarbowej. Zespół: Hackathon.

*Co pokazać:* ekran główny makiety (wariant 3): obraz badany obok wzorcowego, z boku lista miejsc.

## 2. Problem operatora

- Operator RTG ma kilka minut na jedno auto.
- Towar bywa ukryty w drobnych przeróbkach konstrukcji naczepy: w podwójnej podłodze, w ścianie przy kabinie.
- Obecne narzędzie do wykrywania papierosów słabo radzi sobie z małymi ilościami.
- Szukanie różnic „na oko” między obrazami zabiera czas, którego operator nie ma.

*Co pokazać:* zrzut surowego obrazu RTG naczepy (sztucznego, z generatora) bez żadnych zaznaczeń.

## 3. Jak działa: wzorzec obok badanego

- Operator wczytuje obraz badanej naczepy (`.bmp`).
- Na ekranie dwa obrazy obok siebie: wzorzec i badane auto z ramkami.
- Z boku lista miejsc od najpewniejszego, każde z krótkim opisem różnicy i pewnością.
- Klik w miejsce przybliża je na obu obrazach.
- Decyzja zostaje po operatorze: „do kontroli” albo „odrzuć” (z powodem z listy).
- Zapis kontroli: lista „miejsce — do kontroli: przedmiot / odrzucone (powód)”; miejsce to strefa naczepy (np. podwójna podłoga), przedmiot kontroli to strefa i położenie wzdłuż naczepy (przód, środek, tył). Zapis kończy demo.

*Co pokazać:* ekran makiety z listą miejsc; klik w pierwsze miejsce (podwójna podłoga) i powiększenie na obu obrazach; na końcu zapis kontroli (w makiecie zapis jeszcze do dodania).

## 4. Tryb bez pary i niepewny wzorzec

- Operator zwykle nie ma czystego obrazu tego samego typu naczepy.
- Program sam dobiera wzorzec z katalogu (podpis „dobrany: typ …, podobieństwo …”).
- Gdy dobór jest niepewny, nie ukrywa różnic: pokazuje ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec”.
- Operator wskazuje wzorzec z listy typów albo wgrywa plik wzorca.

*Co pokazać:* ekran makiety z podpisem dobranego wzorca; drugi zrzut z ostrzeżeniem „wzorzec niepewny” (do dorobienia w makiecie).

## 5. Rodzaj towaru

- Przed analizą operator wybiera rodzaj zgłoszonego towaru: sprzęt i AGD, odzież i tekstylia, żywność i napoje, materiały budowlane, inne, „pusta naczepa” albo „nie wiem”.
- Towar zgodny ze zgłoszeniem nie dostaje ramki; dodatek ukryty w ładunku ma nadal dawać ramkę (rozpoznanie „zgodny” dopiero mierzymy).
- Dodatek poza ładownią (podłoga, ściana przy kabinie, rama, dach) jest zawsze alarmem.
- „Pusta naczepa”: alarmem jest każdy przedmiot w ładowni. „Nie wiem”: zaznaczamy każdą różnicę.

*Co pokazać:* ekran makiety z listą rozwijaną „Rodzaj zgłoszonego towaru” (pole do dodania w makiecie wariantu 3).

## 6. Wyniki

- Zbędne alarmy na obrazach czystych: **TODO**
- Przeoczone dodatki: **TODO**
- Czas na obraz: **TODO**
- Skalowalność (pełny obraz ok. 50 MB, partia z wiersza poleceń): czas, pamięć i liczba obrazów na minutę — **TODO**
- Skalowalność mierzymy, nie obiecujemy: partia z wiersza poleceń (folder `.bmp` → JSON i PNG na obraz + CSV zbiorczy) na pełnych obrazach; liczby podamy po pomiarze.
- Zbędne alarmy i przeoczenia liczymy osobno; przeoczenie jest gorsze.
- Pomiar na własnym, sztucznym zbiorze: wynik nie przesądza o jakości na prawdziwych obrazach.

*Co pokazać:* tabela wyników z `wyniki/bazowy/tabela.md`, gdy będzie pomiar; do tego czasu slajd z polami TODO.

## 7. Jak liczymy

- Zdjęć KAS nie mamy: własny sztuczny zbiór naczep (czyste i z dodatkami, 4 typy dodatków, maski).
- Cały model liczy na małej karcie graficznej (GTX 1050, 4 GB), nigdy na procesorze.
- Model uczony tylko na obrazach czystych, bez przykładów przemytu (cel, jeszcze niezmierzony).
- Skalowanie: ten sam detektor ma obsłużyć pełny obraz (ok. 50 MB) i partię z wiersza poleceń; cel, jeszcze niezmierzony.
- Cel: praca bez internetu i chmury, jeszcze niezmierzony; pokaz pod linkiem idzie przez sieć (przeglądarka → ksefbot.pl → usługa na OMENie).

*Co pokazać:* zrzut z karty OMENa (przebieg na GPU) albo schemat: przeglądarka → ksefbot.pl → usługa na OMENie → JSON + PNG.

## 8. Narzędzia

- **OpenMausBot** (Apache-2.0): zespół 5 botów: Szef, Projektant, Analityk, Programista, Prezenter.
- **Modele Claude** (Anthropic): kod, specyfikacja, teksty.
- **pm-skills** (MIT): kroki produktowe, nazwa, value proposition, PRD.
- Skill `dummy-dataset` (plan sztucznego zbioru) i generator `anomalie/generator.py`; biblioteki `numpy`, `scipy`, `pillow`, `torch`, `torchvision`.
- GitHub Pages (makieta), Coolify na ksefbot.pl (wersja pokazowa), orkiestrator i karta graficzna OMENa.

*Co pokazać:* zrzut listy botów w OpenMausBot albo sekcja „Użyte narzędzia” z README.

## 9. Co dalej

- Pomiar na zbiorze testowym i wpisanie wyników (zbędne alarmy, przeoczenia, czas, skalowalność na pełnych obrazach i w partii).
- Próba ręczna na makiecie z Arturem: czy z ramek, opisu i powiększenia da się podjąć decyzję w kilka minut.
- Dane KAS: ich nie mamy; jeśli się pojawią, tylko w ramach zasad z zadania (chronione, bez kopiowania poza hackathon), po decyzji Pawła.
- Integracja z repozytorium obrazów skanera jako ścieżka wdrożenia.

*Co pokazać:* link do repo https://github.com/PawelPisarek/hacknation-proba14 i do makiety.

<!-- skill: value-prop-statements -->
