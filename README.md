# Różnica RTG

**Pokazuje na obrazie RTG naczepy to, czego nie ma we wzorcu — zaczynając od najpewniejszego miejsca.**

Narzędzie dla operatora RTG na granicy: porównuje obraz kontrolowanej naczepy z obrazem wzorcowym i zaznacza miejsca, które się różnią — możliwe skrytki i towar niezgłoszony. Po analizie powstaje raport z zaznaczonymi obszarami. Obrazy .bmp (~50 MB) przetwarzamy partiami, a całość jest budowana tak, by działać bez internetu i chmury (cel — do czasu pomiaru nie jest to zmierzony stan). Decyzję o kontroli fizycznej zawsze podejmuje operator.

**Dla kogo:** operator RTG (Służba Celno-Skarbowa) przy stanowisku w trakcie kontroli — ma kilka minut na jedno auto (ustalenie z Arturem, `docs/decyzje.md`).

Zadanie: [docs/zadanie.md](docs/zadanie.md). Wersja robocza, tekst do zgłoszenia: [docs/hacktribe.md](docs/hacktribe.md).

## Demo

- Makieta: TODO — link wkrótce (do uzupełnienia przed 20:00)
- Wersja na ksefbot.pl: TODO — link wkrótce

## Jak uruchomić lokalnie



Wykrywanie dodatków w obrazach RTG naczepy (para wzorzec–badany albo model czystego obrazu typu).

- `anomalie/generator.py` — sztuczny zbiór .bmp (naczepa z boku, dodatki 4 typów, maski PNG + `opis.json`):
  `python -m anomalie.generator --wyjscie dane/gen-v2 --maly [--pelny]`
- `anomalie/ocena.py` — skrypt oceny (dowolny katalog .bmp + opcjonalne maski): FP (czyste z alarmem, liczba obszarów),
  FN (dodatek wskazany: IoU ≥ 0,1 albo środek w ramce), zbędne obszary, czas/obraz:
  `python -m anomalie.ocena --badane DIR/badane --maski DIR/maski --predykcje P.json`
- `anomalie/detektor.py` — metody (tylko karta CUDA): A piksele_para, A0 ablacja, B cechy_para (ResNet18), C model_typu.
- `skrypty/przebieg_bazowy.sh` — całość na OMENie (środowisko, dane, wynik bazowy → `wyniki/bazowy/tabela.md`).
- `testy/test_dymny.py` — test generatora i oceny bez modeli.

Duże obrazy nie trafiają do repo (`dane/`, `*.bmp` w `.gitignore`).

## Jak sprawdzamy wynik

- **Zbiór obrazów „czystych”** — narzędzie nie powinno zaznaczać nic; każde zaznaczenie to zbędny alarm (false positive).
- **Zbiór obrazów z „dodatkami”** — narzędzie powinno wskazać ich miejsce; brak wskazania to przeoczenie (false negative).
- **Dane są sztuczne.** Zdjęć RTG od KAS nie mamy, a dane organizatora są chronione i nie wolno ich dalej udostępniać, więc przygotowujemy własny zbiór obrazów naczep (czyste i z dodatkowym ładunkiem).
- Skrypt oceny przyjmuje dowolny katalog .bmp (opcjonalnie z maskami) i wypisuje liczbę zbędnych alarmów i przeoczeń, więc można go użyć na obcych obrazach.
- Wyniki: TODO (liczby dopiszemy po pomiarze — bez zgadywania).

## Architektura

TODO (uzupełnia Programista): przepływ obraz wzorcowy + badany → różnice → raport (obraz z ramkami, plik ze współrzędnymi, podsumowanie partii); przetwarzanie partiami; praca bez internetu (cel budowy, jeszcze niezmierzony).

## Użyte narzędzia

Narzędzia przygotowane wcześniej i użyte w projekcie (każde w jednym zdaniu: do czego służyło):

- **OpenMausBot** ([github.com/milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot), Apache-2.0) — platforma, na której przed startem przygotowaliśmy zespół 5 botów:
  - Szef — rozdzielał pracę i rozmawiał z człowiekiem (Pawłem),
  - Projektant — pisał personę, ścieżkę użytkownika i specyfikację (rozmawiał z Arturem),
  - Analityk — czytał materiały zadania, wskazywał ryzyka i robił recenzje,
  - Programista — pisał kod, makietę i wdrożenia,
  - Prezenter — pisał README, zgłoszenie i slajdy.
- **Modele Claude** (Anthropic) — napędzają boty: pisanie kodu, specyfikacji i tekstów.
- **pm-skills** ([github.com/phuryn/pm-skills](https://github.com/phuryn/pm-skills), MIT) — skille produktowe, które prowadziły kolejne kroki pracy (m.in. nazwa produktu, value proposition, PRD, analiza konkurencji, /discover).
- **dummy-dataset** (skill z pm-skills) — pomógł zaplanować sztuczne dane; sam zbiór obrazów generuje nasz kod (`anomalie/generator.py`).
- **Biblioteki z `requirements.txt` i kodu:** `numpy` i `scipy` — obliczenia i przetwarzanie obrazów, `pillow` — wczytywanie i zapis obrazów .bmp/.png, `torch` i `torchvision` (z indeksu CUDA) — liczenie na karcie graficznej i cechy ResNet18.
- **GitHub Pages** — publikacja makiety ekranu (warianty i wersja końcowa) pod publicznym adresem.
- **Coolify na ksefbot.pl** — hosting aplikacji (wersja pokazowa dostępna w przeglądarce).
- **Orkiestrator i karta graficzna OMENa** (GTX 1050, 4 GB) — całe liczenie (generator, uczenie, ocena) idzie na karcie, uruchamiane przez orkiestrator (`--klasa gpu-tlo`), nigdy na procesorze.

## Licencja

Kod na licencji MIT — zob. [LICENSE](LICENSE). Narzędzia zewnętrzne na licencjach podanych w sekcji „Użyte narzędzia”.
