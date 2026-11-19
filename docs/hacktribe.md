# Zgłoszenie HackTribe — DRAFT

> DRAFT: tekst do dopasowania do opisu produktu (docs/spec.md). Limity znaków sprawdzone skryptem.

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

## Opis krótki (≤ 300 znaków) [195/300]

Narzędzie dla operatora RTG: porównuje obraz kontrolowanej naczepy z obrazem wzorcowym i zaznacza miejsca, które się różnią — możliwe skrytki i towar niezgłoszony. Działa lokalnie, bez internetu.

## Opis średni (≤ 1000 znaków) [666/1000]

Operator RTG na granicy ogląda setki obrazów, a przemytnicy ukrywają towar w drobnych przeróbkach konstrukcji. Nasze narzędzie porównuje obraz kontrolowanego środka przewozowego z obrazem wzorcowym (czystym) i zaznacza na nim miejsca, których we wzorcu nie ma — operator od razu widzi, gdzie spojrzeć dokładniej.

Po każdej analizie powstaje raport z zaznaczonymi obszarami. Obrazy .bmp (~50 MB) przetwarzamy partiami, więc ten sam mechanizm obsłuży większy zbiór. Model uczy się na obrazach prawidłowych i działa bez internetu i chmury. Mamy własny, sztuczny zbiór obrazów naczep (czyste i z dodatkami), a skuteczność mierzymy liczbą fałszywych alarmów i przeoczeń.

## Opis pełny (≤ 2000 znaków) [1313/2000]

Problem. Operatorzy RTG Służby Celno-Skarbowej oceniają obrazy kontenerów, ciężarówek i wagonów i decydują o kontroli fizycznej. Przemytnicy ukrywają towar w elementach konstrukcji oraz w deklarowanym ładunku; istniejące narzędzie do wykrywania papierosów słabo radzi sobie z małymi ilościami w skrytkach.

Rozwiązanie. Aplikacja porównuje analizowany obraz z obrazem wzorcowym tego samego typu środka przewozowego i wskazuje różnice, które mogą oznaczać skrytkę lub towar niezgłoszony. Operator dostaje obraz z zaznaczonymi miejscami oraz raport z listą wykrytych anomalii — decyzja zostaje po jego stronie, narzędzie tylko kieruje uwagę.

Jak to działa. Model uczy się wyglądu obrazu prawidłowego (bez anomalii) na plikach .bmp. Duże pliki (~50 MB) są przetwarzane partiami, z kompresją, dzięki czemu rozwiązanie skaluje się na kolejne zbiory. Docelowo całość działa bez internetu i silnika AI w chmurze; AI służyła nam do napisania kodu.

Dane i pomiar. Zdjęć KAS nie mamy, więc przygotowaliśmy własny, sztuczny zbiór obrazów naczep: czyste oraz z dodatkowym ładunkiem. Na czystych liczymy fałszywe alarmy, na obrazach z dodatkami — przeoczenia. Obliczenia idą na karcie graficznej.

Demo i kod: makieta i wersja na ksefbot.pl (linki w README), repozytorium: https://github.com/PawelPisarek/hacknation-proba14.

## Narzędzia przygotowane wcześniej

- **OpenMausBot** — zespół botów (github.com/milind-soni/OpenMausBot, Apache-2.0), który pracował nad projektem.
- **Modele Claude** (Anthropic) — pisanie kodu i tekstów.
- **pm-skills** (github.com/phuryn/pm-skills, MIT) — skille produktowe (m.in. nazwa produktu, value proposition).

<!-- skill: product-name -->
