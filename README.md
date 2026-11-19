# Różnica RTG

**Pokazuje na obrazie RTG naczepy to, czego nie ma we wzorcu — zaczynając od najpewniejszego miejsca.**

Narzędzie dla operatora RTG na granicy: pokazuje obraz kontrolowanej naczepy obok wzorcowego i listę miejsc od najpewniejszego, z opisem różnicy i pewnością. Operator zleca „do kontroli” albo odrzuca z powodem, a zapis kontroli zawiera obraz naczepy z ramkami. Wzorzec można podać (para) albo program dobiera go sam; gdy niepewny, ostrzega. Obrazy .bmp (~50 MB) mają być przetwarzane partiami (w planie), a całość jest budowana tak, by działać bez internetu i chmury (cel — do czasu pomiaru nie jest to zmierzony stan). Decyzję o kontroli fizycznej zawsze podejmuje operator.

**Dla kogo:** operator RTG (Służba Celno-Skarbowa) przy stanowisku w trakcie kontroli — ma kilka minut na jedno auto (ustalenie z Arturem, `docs/decyzje.md`).

Zadanie: [docs/zadanie.md](docs/zadanie.md). Wersja robocza, tekst do zgłoszenia: [docs/hacktribe.md](docs/hacktribe.md).

## Demo

- Makieta R3 (zamknięta; ekran operatora, dane udawane): https://pawelpisarek.github.io/hacknation-proba14/makieta/
- MVP na ksefbot.pl (prawdziwy wynik z karty graficznej OMENa; gdy karta nie odpowiada — „wynik zapisany” z wcześniejszego przebiegu, z podpisem): https://hacknation.ksefbot.pl/

## Jak uruchomić lokalnie

**MVP (ekran operatora):**
- usługa na karcie (CUDA): `python usluga/serwer.py --port 8770 --dane ~/dane/proba14/gen-v2` (`--sprawdz` — 8 prób bez serwera);
- aplikacja (Node 22, bez zależności): `OMEN_URL=http://<host usługi>:8770 PORT=3000 node aplikacja/serwer.mjs`, albo `docker build -t rtg . && docker run -p 3000:3000 -e OMEN_URL=… rtg`;
- zapis wyników do trybu „wynik zapisany”: `node skrypty/mvp/zapisz_wyniki.mjs <adres>/api <wzorzec.bmp>` (zmienna `WARIANTY`);
- przeklik (przeglądarka bez okna): `node skrypty/mvp/przeklik_mvp.mjs <adres> docs/zrzuty <katalog pobrań> <badany.bmp> <wzorzec.bmp>`.



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
- **Wynik bazowy** (sztuczny zbiór: 30 czystych + 30 z dodatkami, 60 dodatków, 33 w konstrukcji; karta GTX 1050; źródło: wpis Programisty 12:09 w `docs/decyzje.md`, tabela `wyniki/bazowy/tabela.md`):

| metoda | czyste z alarmem | dodatki przeoczone | uwagi |
|---|---|---|---|
| A (piksele, para) | 2/30 | 0/60 (konstrukcja 0/33) | 1,3 miejsca na auto; pełny obraz 50,4 MB: 0,49 s (źródło: `wyniki/bazowy/przebieg.log`) |
| B (cechy, para) | 0/30 | 23/60 (konstrukcja 15/33) | |
| C (model typu) | 15/30 | 3/60 (konstrukcja 3/33) | dobór wzorca 60/60 |

  Wynik nie przesądza o jakości na prawdziwych obrazach. Kolejne pomiary dopiszemy, gdy będą.

## Architektura

TODO (uzupełnia Programista): przepływ obraz wzorcowy + badany → różnice → raport (obraz z ramkami, plik ze współrzędnymi, podsumowanie partii — przetwarzanie partią z wiersza poleceń w planie, dopóki nie zadziała); praca bez internetu (cel budowy, jeszcze niezmierzony).

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
- **dummy-dataset** — skill, z którego Programista ułożył plan sztucznego zbioru; obrazy tworzy nasz generator `anomalie/generator.py` na karcie graficznej.
- **Biblioteki z `requirements.txt` i kodu:** `numpy` i `scipy` — obliczenia i przetwarzanie obrazów, `pillow` — wczytywanie i zapis obrazów .bmp/.png, `torch` i `torchvision` (z indeksu CUDA) — liczenie na karcie graficznej i cechy ResNet18.
- **GitHub Pages** — publikacja makiety ekranu (warianty i wersja końcowa) pod publicznym adresem.
- **Coolify na ksefbot.pl** — hosting aplikacji (w przygotowaniu — adres dziś nie odpowiada).
- **Orkiestrator i karta graficzna OMENa** (GTX 1050, 4 GB) — całe liczenie (generator, uczenie, ocena) idzie na karcie, uruchamiane przez orkiestrator (`--klasa gpu-tlo`), nigdy na procesorze.

## Licencja

Kod na licencji MIT — zob. [LICENSE](LICENSE). Narzędzia zewnętrzne na licencjach podanych w sekcji „Użyte narzędzia”.
