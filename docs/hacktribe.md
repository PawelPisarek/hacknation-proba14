# Zgłoszenie HackTribe — DRAFT (R2)

> DRAFT: do dopasowania do docs/spec.md. Limity znaków sprawdzone skryptem. Poprawiono po recenzji R1.

## Nazwa projektu (≤ 50 znaków)

Propozycje:
1. Rentgenowski Różnicownik (24 zn.)
2. Różnica RTG (11 zn.)
3. SkrytkaScan (11 zn.)

**Wybór: Różnica RTG** — krótka, mówi wprost, że chodzi o różnicę między obrazami RTG. [11/50]

## Nazwa zespołu

Hackathon (do potwierdzenia przez ludzi)

## Link do repo

https://github.com/PawelPisarek/hacknation-proba14

## Opis krótki (≤ 300 znaków) [236/300]

Pomaga operatorowi RTG: porównuje obraz naczepy z wzorcowym albo z wyuczonym obrazem czystej naczepy i zaznacza różnice — możliwe skrytki. Uczy się tylko z czystych obrazów, jest budowane do pracy bez chmury, na małej karcie graficznej.

## Opis średni (≤ 1000 znaków) [725/1000]

Przemytnicy ukrywają towar w drobnych przeróbkach konstrukcji, a operator RTG ma kilka minut na jedno auto. Nasze narzędzie porównuje obraz kontrolowanej naczepy na dwa sposoby: z obrazem wzorcowym (para wzorzec–badany) albo z wyuczonym obrazem czystej naczepy tego typu. Różnice zaznacza na obrazie, a po analizie powstaje raport.

Wyróżnik: uczy się wyłącznie z obrazów czystych, bez przykładów przemytu. Jest budowane tak, by działać bez internetu i chmury, na małej karcie graficznej, oraz przetwarzać duże pliki .bmp (~50 MB) partiami i skalować się na większe zbiory.

Sprawdzamy na własnym, sztucznym zbiorze obrazów naczep, bo prawdziwych obrazów nie mamy. Wyniki: [TODO: zbędne alarmy / przeoczenia / czas na obraz].

## Opis pełny (≤ 2000 znaków) [1439/2000]

Problem. Operatorzy RTG Służby Celno-Skarbowej oceniają obrazy kontenerów, ciężarówek i wagonów i decydują o kontroli fizycznej. Przemytnicy ukrywają towar w elementach konstrukcji oraz w deklarowanym ładunku; istniejące narzędzie do wykrywania papierosów słabo radzi sobie z małymi ilościami w skrytkach. Operator przy stanowisku ma kilka minut na jedno auto.

Rozwiązanie. Aplikacja porównuje analizowany obraz na dwa sposoby: (1) para — obraz wzorcowy i badany, (2) porównanie z wyuczonym obrazem czystej naczepy tego typu. Różnice, które mogą oznaczać skrytkę lub towar niezgłoszony, zaznacza na obrazie i opisuje w raporcie. Decyzja zostaje po stronie operatora.

Wyróżnik. Model uczy się tylko z obrazów czystych (bez anomalii), więc nie potrzebuje przykładów przemytu. Narzędzie jest budowane do pracy bez chmury i internetu, na małej karcie graficznej.

Cele techniczne (budowane, jeszcze niezmierzone): obsługa obrazów .bmp ~50 MB, przetwarzanie partiami, kompresja i skalowanie na większe zbiory.

Pomiar. Zdjęć KAS nie mamy, więc sprawdzamy na własnym, sztucznym zbiorze obrazów naczep (czyste i z dodatkowym ładunkiem); wyniki na nim nie przesądzają o jakości na prawdziwych obrazach. Na czystych liczymy zbędne alarmy, na obrazach z dodatkami — przeoczenia. Wyniki: [TODO: zbędne alarmy / przeoczenia / czas na obraz].

Kod: https://github.com/PawelPisarek/hacknation-proba14 (makieta i wersja na ksefbot.pl — linki w README).

## Narzędzia przygotowane wcześniej

- **OpenMausBot** — zespół botów (github.com/milind-soni/OpenMausBot, Apache-2.0), który pracował nad projektem.
- **Modele Claude** (Anthropic) — pisanie kodu i tekstów.
- **pm-skills** (github.com/phuryn/pm-skills, MIT) — skille produktowe (m.in. nazwa produktu, value proposition).

<!-- skill: product-name -->
