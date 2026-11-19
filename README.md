# Różnica RTG (tytuł roboczy)

Narzędzie dla operatora RTG na granicy: porównuje obraz kontrolowanej naczepy z obrazem wzorcowym i zaznacza miejsca, które się różnią — możliwe skrytki i towar niezgłoszony. Po analizie powstaje raport z zaznaczonymi obszarami. Obrazy .bmp (~50 MB) przetwarzamy partiami, a całość jest budowana tak, by działać bez internetu i chmury (cel — do czasu pomiaru nie jest to zmierzony stan). Decyzję o kontroli fizycznej zawsze podejmuje operator.

**Dla kogo:** operator RTG (Służba Celno-Skarbowa) przy stanowisku w trakcie kontroli — ma kilka minut na jedno auto (ustalenie z Arturem, `docs/decyzje.md`).

Zadanie: [docs/zadanie.md](docs/zadanie.md). Wersja robocza, tekst do zgłoszenia: [docs/hacktribe.md](docs/hacktribe.md).

## Demo

- Makieta: TODO — link wkrótce
- Wersja na ksefbot.pl: TODO — link wkrótce

## Jak uruchomić lokalnie

TODO (uzupełnia Programista): wymagania, instalacja, uruchomienie analizy pary i partii, uruchomienie oceny.

## Jak sprawdzamy wynik

- **Zbiór obrazów „czystych”** — narzędzie nie powinno zaznaczać nic; każde zaznaczenie to zbędny alarm (false positive).
- **Zbiór obrazów z „dodatkami”** — narzędzie powinno wskazać ich miejsce; brak wskazania to przeoczenie (false negative).
- **Dane są sztuczne.** Zdjęć RTG od KAS nie mamy, a dane organizatora są chronione i nie wolno ich dalej udostępniać, więc przygotowujemy własny zbiór obrazów naczep (czyste i z dodatkowym ładunkiem).
- Skrypt oceny przyjmuje dowolny katalog .bmp (opcjonalnie z maskami) i wypisuje liczbę zbędnych alarmów i przeoczeń, więc można go użyć na obcych obrazach.
- Wyniki: TODO (liczby dopiszemy po pomiarze — bez zgadywania).

## Architektura

TODO (uzupełnia Programista): przepływ obraz wzorcowy + badany → różnice → raport (obraz z ramkami, plik ze współrzędnymi, podsumowanie partii); przetwarzanie partiami; praca bez internetu (cel budowy, jeszcze niezmierzony).

## Użyte narzędzia

Narzędzia przygotowane wcześniej i użyte w projekcie:

- **OpenMausBot** ([github.com/milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot), Apache-2.0) — zespół 5 botów, który pracował nad projektem:
  - Szef — rozdział pracy i rozmowa z człowiekiem,
  - Projektant — persona, ścieżka użytkownika, specyfikacja,
  - Analityk — materiały zadania, ryzyka, recenzje,
  - Programista — kod, makieta, wdrożenia,
  - Prezenter — README i teksty.
- **Modele Claude** (Anthropic) — pisanie kodu i tekstów przez boty.
- **pm-skills** ([github.com/phuryn/pm-skills](https://github.com/phuryn/pm-skills), MIT) — skille produktowe (m.in. nazwa produktu, value proposition, notatki zmian).
- **Biblioteki z kodu:** TODO (lista od Programisty).

## Licencja

Kod na licencji MIT — zob. [LICENSE](LICENSE). Narzędzia zewnętrzne na licencjach podanych w sekcji „Użyte narzędzia”.
