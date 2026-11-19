# Scenariusze testów akceptacji A1–A18 i A15b (krok 4, test-scenarios)

Wejście: `docs/spec.md` §3, §4, §7 (kryteria A1–A18, A15b), `docs/decyzje.md` (P1–P17, 11:46 Szef — zbiór kontrolny, 11:49 Szef — strefy, A17, A18, 11:51 Szef — A15b), `docs/pm/05-zalozenia.md` (sondy S1–S4, E3). Skrypt oceny: `anomalie/ocena.py`, `skrypty/bazowy.py`, generator `anomalie/generator.py` (gen-v2) — stan repo po `dc21a1f`.
Dane i ekrany są sztuczne (spec §8 p. 2): wyniki FP/FN nie przenoszą się na dane KAS. **Liczenie tylko na karcie (OMEN, `--klasa gpu-tlo`), nigdy na procesorze;** liczby progowe ustala Szef po pierwszym przebiegu (spec §7) — do tego czasu scenariusz mierzy i podaje, a warunek „nie przechodzi” opiera się na spec, nie na wymyślonych progach.

## Przyjęte w całym pliku

**Zbiory (podzbiory generatora).** Istnieją w gen-v2: `nauka` (3 typy × 6 pustych), `kalib` (12 czystych par), `test` (30 czystych + 30 z dodatkami, 1200×420), `pelny` (3+3 pary 12000×4200, ~50 MB). Wg spec §3 i decyzji Szefa mają powstać (dziś **nie ma ich w generatorze** — pozycje w „brakuje w ocenie”, B1–B3):

| Skrót | Zbiór | Skład | Źródło |
|---|---|---|---|
| **KL** | kontrolny „inny ładunek zgodny ze zgłoszeniem” | 6 par: ładunek badanego inny niż we wzorcu, rodzaj towaru w metadanych zgodny z ładunkiem; w 3 parach dodatkowo mały dodatek w konstrukcji | spec §3; Szef 11:46 |
| **KW** | kontrolny „dodatek ukryty w ładunku” | 6 par: ładunek zgodny ze zgłoszeniem + dodatek typu `w_ladunku` lub `duzy_w_ladunku` | spec §3; Szef 11:51 |
| **KP** | pusta naczepa | pary z pustą ładownią we wzorcu i w badanym; część z przedmiotem w ładowni, część bez. Liczność nieustalona w spec — **założenie: 6 par (3 z przedmiotem, 3 bez)**, do potwierdzenia przez Szefa | spec A17 |
| **KS** | typ spoza katalogu | KL + 2 pary typu naczepy, którego nie ma w `nauka` (typ D) | spec §4c, A18; Szef 11:49 (3) |
| **KM** | mały dodatek w konstrukcji, dwie rozdzielczości | te same sceny (to samo ziarno) zapisane w 1200×420 i 12000×4200; liczność nieustalona — **założenie: 6 par z `maly_konstrukcja`** | spec A12 |

Gdzie w kolumnie „Tryb” stoi „para” — wzorzec podany (metody A, A0, B); „bez pary” — dobór wzorca z `nauka` (metoda C). Wg Szefa 11:46 zbiory kontrolne ocenia się w obu trybach.

**Miary — nazwy.** `FP` = liczba obrazów czystych (bez dodatku) z jakimkolwiek alarmem + liczba obszarów na nich; `FN` = dodatki bez ramki (IoU ≥ 0,1 z maską lub środek dodatku w ramce — `ocena.PROG_IOU`); **FP i FN podawane zawsze osobno, nigdy jedną liczbą (P2: przeoczenie gorsze).** `alarm na ładunku` = ramka w strefie „ładownia” niewskazująca żadnego dodatku (dla par z dodatkiem w konstrukcji obraz nie jest „czysty”, więc zwykłe FP go nie złapie — B4). Czas = od odczytu `.bmp` do ramek (`bazowy.mapy_zbioru`), pamięć = szczyt pamięci karty (`torch.cuda.max_memory_allocated`).

**Pewność wyniku.** Każdy scenariusz kończy się wpisem: komenda, zbiór, liczby (FP, FN, czas, pamięć), linia wyniku ze skryptu. Brak wyniku = nie wykonany, nie „przeszedł”.

---

## Zbiór A: jakość detekcji (A1–A5, A12)

### A1 — Czyste obrazy testowe
- **Zbiór:** `test`, 30 czystych (`c000…c029`); próg `k` z `kalib` (12 czystych), zamrożony przed testem.
- **Kroki:** 1) generator `--maly`; 2) kalibracja progu na `kalib` (`bazowy.py`: najmniejsze k bez alarmu); 3) predykcje na 30 czystych, każda metoda (A, A0, B, C); 4) `ocena --badane test/badane --maski test/maski --opis test/opis.json`.
- **Oczekiwany wynik:** liczba obrazów czystych z alarmem (FP) zmierzona i podana; cel 0 (H1).
- **Miara:** FP = `czyste_z_alarmem`/30 i `obszary_na_czystych`, osobno dla każdej metody; FN tu nie dotyczy (brak dodatków). Czas/obraz.
- **Nie przechodzi:** FP nie podane, albo próg wybrany na zbiorze `test` (podglądanie), albo FP ≠ 0 bez zapisanego powodu i bez wpisu do Szefa (cel 0 to hipoteza H1, nie próg — spec §7: próg ustala Szef).

### A2 — Obrazy z dodatkami
- **Zbiór:** `test`, 30 obrazów z dodatkami (`d000…d029`; 1–3 dodatki każdy, typy `maly_konstrukcja`, `sredni_konstrukcja`, `w_ladunku`, `duzy_w_ladunku`).
- **Kroki:** jak A1 (ten sam przebieg, te same predykcje); ocena na obrazach z maskami.
- **Oczekiwany wynik:** FN zmierzone i podane osobno od FP; rozbicie na typ dodatku i na miejsce w konstrukcji.
- **Miara:** FN = `przeoczone`/`dodatki`; `obrazy_z_przeoczeniem`/30; FN wg typu (`fn_typ`/`n_typ`); osobno zbędne obszary (`zbedne_obszary`).
- **Nie przechodzi:** FN podane razem z FP jedną liczbą; brak rozbicia na typ; dodatek w maskach bez wpisu w ocenie (liczba dodatków ≠ liczbie w `opis.json`).

### A3 — Ramki na auto
- **Zbiór:** `test` (60 obrazów), te same predykcje co A1/A2.
- **Kroki:** policzyć liczbę ramek na każdy obraz przy progu z kalibracji; osobno dla czystych i z dodatkami.
- **Oczekiwany wynik:** „kilka, nie kilkadziesiąt” (P2); do czasu decyzji Szefa podajemy średnią i maksimum.
- **Miara:** średnia i maksimum ramek na obraz (`ramki_na_auto`); osobno czyste (= FP-obszary) i z dodatkami. FP/FN osobno — wg A1, A2.
- **Nie przechodzi:** średnia i maksimum nie podane; maksimum ≫ liczby dodatków na obraz bez komentarza (liczba graniczna — decyzja Szefa po pierwszym przebiegu E1+E2).

### A4 — Dobór wzorca bez pary
- **Zbiór:** `test` (60) i `pelny` (6), tryb bez pary (metoda C); katalog `nauka`.
- **Kroki:** 1) analiza bez wzorca; 2) odczyt typu rozpoznanego i pewności doboru (`typ_rozpoznany`, `pewnosc_wzorca`); 3) porównanie z `typ_naczepy` w `opis.json`.
- **Oczekiwany wynik:** typ rozpoznany = właściwy typ; odsetek trafień zmierzony (E1, H4).
- **Miara:** trafione/wszystkie (test i pełny osobno); pewność doboru min/mediana; liczba flag „wzorzec niepewny” wśród trafnych i wśród błędnych. FP/FN przy tym doborze — osobno wg A1/A2 (metoda C).
- **Nie przechodzi:** odsetek trafień niepodany; pewność doboru niezapisana; błędny dobór bez flagi „wzorzec niepewny” (ramki ma pokazać z ostrzeżeniem — P16; ciche błędne ramki to wada).

### A5 — Skrytka w konstrukcji
- **Zbiór:** `test` i `pelny`, dodatki w miejscach `podwojna_podloga` i `sciana_przy_kabinie` (P4; wagi 0,4/0,4), oba tryby.
- **Kroki:** 1) analiza; 2) dla każdego takiego dodatku sprawdzić ramkę (IoU/środek); 3) sprawdzić, że raport ma powiększenie wokół ramki na obu obrazach (wzorzec i badany); 4) zapisać nazwę strefy ramki.
- **Oczekiwany wynik:** każda skrytka w konstrukcji wskazana ramką, z powiększeniem; strefa = „podłoga” albo „ściana przednia” (spec §4a).
- **Miara:** FN konstrukcja (`fn_miejsce` dla `podwojna_podloga`, `sciana_przy_kabinie`) osobno od FP; trafność nazwy strefy (ramka z dodatkiem w strefie X nazwana X); liczba powiększeń = liczbie ramek.
- **Nie przechodzi:** jakakolwiek skrytka w podłodze lub ścianie przy kabinie bez ramki i bez wpisu do wyniku (demo P4/P11 opiera się na tym); brak powiększenia; strefa ramki inna niż strefa dodatku w większości trafionych ramek (kryterium zabicia z `docs/pm/05`, atak 6).

### A12 — Zmniejszenie obrazu
- **Zbiór:** KM (mały dodatek w konstrukcji, te same sceny 1200 px i 12000 px).
- **Kroki:** 1) analiza po zmniejszeniu do 1200 px (domyślnie: `SZER_ROBOCZA`); 2) analiza tych samych scen bez zmniejszenia (pełny obraz); 3) FN i FP w obu wariantach, ten sam próg.
- **Oczekiwany wynik:** mały dodatek w konstrukcji wykrywany po zmniejszeniu; porównanie FN: zmniejszenie vs pełny obraz (decyzja Q7).
- **Miara:** FN(zmniejszony) i FN(pełny) na tych samych dodatkach; FP osobno w obu; czas i pamięć w obu (z A6).
- **Nie przechodzi:** FN(zmniejszony) > FN(pełny) i różnica nie zapisana jako wynik; porównanie na różnych scenach (nie ta sama para); FN i FP zsumowane.

## Zbiór B: kolejność, decyzje, ścieżka (A7–A11, A14)

### A7 — Kolejność listy
- **Zbiór:** `test` (z dodatkami) i `pelny`; wynik w JSON (`ramki`, `oceny`, pewność w skali 50–99%, spec §5).
- **Kroki:** 1) wczytać listę z JSON jednego obrazu; 2) sprawdzić, że pewność maleje wzdłuż listy; 3) zliczyć obrazy, w których pierwsza pozycja wskazuje prawdziwy dodatek, i obrazy, w których skrytka w konstrukcji jest przed ładunkiem i przed zbędnym obszarem.
- **Oczekiwany wynik:** lista od najpewniejszej (P7); skrytka w konstrukcji pierwsza w większości aut (atak 5, Z10).
- **Miara:** odsetek obrazów z monotoniczną pewnością (powinno 100%); odsetek „pierwsza ramka = prawdziwy dodatek”; mediana pozycji prawdziwych dodatków. FP/FN osobno — wg A1/A2.
- **Nie przechodzi:** pewność rośnie gdziekolwiek wzdłuż listy; „pierwsza ramka prawdziwa” nie policzona; skrytka nie jest pierwsza w większości aut i opis różnicy nie został zawężony do strefy i wielkości (kryterium z `docs/pm/05`, atak 5).

### A8 — Decyzja i zapis kontroli
- **Zbiór:** 1 obraz z `test` z ≥ 3 ramkami (albo obraz z makiety z danymi udawanymi do czasu usługi); makieta/aplikacja + zapis JSON na serwerze (spec §4d).
- **Kroki:** 1) wczytać obraz; 2) przy pozycji 1: „do kontroli”; 3) przy pozycji 2: „odrzuć” z powodem z listy (np. „znany element konstrukcji”); 4) przy pozycji 3: „odrzuć” bez powodu (próba negatywna); 5) zapisać kontrolę; 6) pobrać plik zapisu i odczytać.
- **Oczekiwany wynik:** zapis zawiera dla każdej pozycji: miejsce (strefa), przedmiot kontroli (strefa + przód/środek/tył), decyzję i powód; „odrzuć” bez powodu nie zapisuje się albo prosi o powód (P3).
- **Miara:** liczba pozycji w zapisie = liczbie ramek; wszystkie pola wypełnione; liczba odrzuceń bez powodu w zapisie (powinno 0). Czas zapisu. FP/FN — nie dotyczy (ten test nie mierzy detekcji).
- **Nie przechodzi:** brak miejsca lub przedmiotu kontroli w którejkolwiek pozycji; „odrzuć” zapisane bez powodu; zapis niepobieralny; zapis różni się od decyzji na ekranie.

### A9 — Linia „N miejsc do sprawdzenia”
- **Zbiór:** jak A8.
- **Kroki:** 1) po analizie odczytać linię „N miejsc do sprawdzenia · zostało M”; 2) porównać N z liczbą ramek w JSON; 3) po każdej decyzji (A8) odczytać M.
- **Oczekiwany wynik:** N = liczba ramek; M maleje o 1 po każdej decyzji (do kontroli albo odrzuć); po ostatniej M = 0.
- **Miara:** N − liczba ramek (0); ciąg M po kolejnych decyzjach.
- **Nie przechodzi:** N ≠ liczbie ramek; M nie maleje po decyzji lub maleje bez decyzji; linia z podsumowaniem partii (poza zakresem, P10).

### A10 — Demo ≤ 2 min
- **Zbiór:** auto demonstracyjne (z S1/S3; do czasu wyniku detektora dane udawane z makiety — oznaczone); przepływ przeglądarka → ksefbot.pl → usługa na OMENie (spec §4d).
- **Kroki:** wg §1 „Demo ≤ 2 min”: wczytanie → wzorzec dobrany → ramka na podwójnej podłodze pierwsza → klik → powiększenie na obu obrazach → „do kontroli” → ściana przy kabinie → „do kontroli” → trzecie (ładunek) → „odrzuć” z powodem → zapis → „zostało 0”.
- **Oczekiwany wynik:** cała ścieżka wykonalna w ≤ 2 min (P4, P11); wynik analizy w kilka sekund (P5).
- **Miara:** czas całej ścieżki (stoper, 3 powtórzenia, osoba, która nie zna makiety, i autor), czas od wysłania pliku do wyniku (z A6). FP/FN: z użytego auta — podane obok.
- **Nie przechodzi:** czas ścieżki > 2 min w którymkolwiek powtórzeniu; krok ścieżki niewykonalny (np. brak pola rodzaju towaru, którego makieta wariantu 3 jeszcze nie ma — spec §6); wynik analizy nie w kilka sekund bez planu B (nagrany wynik, spec §8 p. 5).

### A11 — Praca bez internetu
- **Zbiór:** `test` (próbka 6 obrazów: 3 czyste, 3 z dodatkami) i jeden z `pelny`; detektor lokalnie na OMENie (CLI i usługa na tej samej maszynie), bez sieci (rozstrzygnięcie Szefa, krok 3).
- **Kroki:** 1) odciąć sieć dla procesu (przestrzeń sieciowa bez zewnętrznego dostępu); 2) uruchomić analizę na próbce; 3) uruchomić z czystym cache wag (sprawdzenie, czy jakiś model nie wymaga pobrania — `D._siec()` ładuje wagi ResNet18 przy pierwszym użyciu).
- **Oczekiwany wynik:** wynik z karty OMENa, taki sam jak z siecią (te same ramki).
- **Miara:** liczba prób połączenia sieciowego podczas analizy (0); różnica wyniku z siecią i bez (FP i FN osobno, identyczne).
- **Nie przechodzi:** jakiekolwiek pobieranie z sieci w trakcie analizy; wynik różny od wyniku z siecią; start niemożliwy bez sieci (brak wag w lokalnym cache). Pokaz przez ksefbot.pl zależy od sieci — to test A10, nie A11.

### A14 — Ocena przez operatora (E3)
- **Zbiór:** makieta z danymi udawanymi (`docs/makieta/warianty/wspolne.js`) — **wynik oznaczony „na danych udawanych”** (Szef 11:51 b); powtórka na wyniku detektora po S1/S3.
- **Kroki:** 1) Artur (rola operatora) dostaje auto z 3 ramkami; 2) bez wyjaśnień ma dla każdej ramki podjąć „do kontroli” albo „odrzuć” z powodem; 3) mierzymy czas; 4) pytanie: czy pomogły opis różnicy, powiększenie, kolejność.
- **Oczekiwany wynik:** wszystkie decyzje w kilka minut.
- **Miara:** czas całości i na ramkę; liczba decyzji, przy których operator pytał o znaczenie; tak/nie + uwagi. FP/FN: nie dotyczy, na danych udawanych test nie mierzy detektora.
- **Nie przechodzi:** czas > kilku minut (progu liczbowego nie wpisujemy — „kilka” z P11 do zapytania do Artura; do tego czasu podajemy wynik); operator nie potrafi odrzucić ramki bez wyjaśnienia; wynik podany jako jakość detektora.

## Zbiór C: wydajność (A6, A13)

### A6 — Czas i pamięć
- **Zbiór:** `pelny` (3+3 pary, ~50 MB); karta GTX 1050, 4 GB.
- **Kroki:** 1) `torch.cuda.reset_peak_memory_stats()`; 2) analiza pojedynczego pełnego obrazu od odczytu `.bmp` do JSON i PNG, powtórzona 3× (pierwszy = start zimny, kolejne = ciepłe); 3) odczyt szczytu pamięci karty.
- **Oczekiwany wynik:** czas na obraz < 60 s; pamięć karty < 4 GB (H5; zadanie p. 7); na pokazie wynik w kilka sekund (P5).
- **Miara:** czas każdego powtórzenia (zimny, ciepły), maksimum z 6 obrazów; szczyt pamięci karty (MiB) na obraz i na przebieg. FP/FN — wg A1/A2 dla tego zbioru, osobno.
- **Nie przechodzi:** którykolwiek obraz ≥ 60 s; szczyt pamięci ≥ 4 GB (lub błąd braku pamięci karty); czas zmierzony bez odczytu pliku; pamięć podana jako średnia zamiast szczytu.

### A13 — Partia i duże pliki
- **Zbiór:** `pelny` (3+3 pary 12000×4200); komenda partii: folder `.bmp` → JSON i PNG na obraz + CSV zbiorczy (spec §4d).
- **Kroki:** 1) uruchomić partię na wszystkich 6 obrazach (i na kopii powtórzonej do 12, dla przepustowości); 2) zmierzyć czas na obraz i całkowity; 3) szczytowa pamięć karty; 4) otworzyć CSV zbiorczy.
- **Oczekiwany wynik:** wynik zapisany (czas na obraz, szczytowa pamięć, obrazy/min), „bez obietnic” (spec §7 A13).
- **Miara:** czas/obraz (średnia, maksimum), obrazy/min, szczyt pamięci karty (MiB); liczba plików JSON/PNG = liczbie obrazów; wiersze CSV = liczbie obrazów. FP/FN na `pelny` — osobno.
- **Nie przechodzi:** partia przerwana (błąd pamięci, `kod 75`) bez zapisu wyniku częściowego; brak któregokolwiek z JSON/PNG/CSV; obietnica przepustowości w README ponad zmierzoną.

## Zbiór D: ładunek zgodny, dodatek w ładunku, pusta naczepa, typ spoza katalogu (A15–A18)

### A15 — Ładunek zgodny ze zgłoszeniem, rodzaj towaru podany
- **Zbiór:** KL (6 par; 3 z małym dodatkiem w konstrukcji); oba tryby (para, bez pary); pole rodzaju towaru = rodzaj zgodny z ładunkiem pary.
- **Kroki:** 1) analiza z podanym rodzajem towaru; 2) zliczyć ramki na ładowni (alarm na ładunku); 3) w 3 parach z dodatkiem sprawdzić ramkę na dodatku w konstrukcji.
- **Oczekiwany wynik:** brak alarmu na ładunku; dodatek w konstrukcji wykryty.
- **Miara:** FP-ładunek = liczba ramek w strefie „ładownia” niewskazujących dodatku (par z alarmem na ładunku / 6); FN = przeoczone dodatki w konstrukcji / 3. Osobno, osobno od zbioru `test`; osobno dla obu trybów.
- **Nie przechodzi:** którakolwiek ramka na różnicy ładunku zgodnego przy podanym rodzaju towaru, bez wpisu; którykolwiek z 3 dodatków w konstrukcji bez ramki; FP-ładunek policzone razem z FP z `test`.

### A16 — Ten sam zbiór, bez rodzaju towaru („nie wiem”)
- **Zbiór:** KL (te same 6 par co A15, te same predykcje poza polem rodzaju towaru), oba tryby.
- **Kroki:** 1) analiza z rodzajem „nie wiem”; 2) zliczyć ramki na ładunku; 3) sprawdzić dodatki w konstrukcji; 4) zestawić z A15 para po parze.
- **Oczekiwany wynik:** alarm na ładunku jest (zaznaczamy wszystko, co różni się od wzorca; P15, P2); dodatek w konstrukcji nadal wykryty.
- **Miara:** FP-ładunek (par z alarmem/6) i FN dodatków w konstrukcji (/3) osobno; różnica A16 − A15 w alarmach na ładunku (ma być dodatnia).
- **Nie przechodzi:** brak alarmu na ładunku różnym od wzorca przy „nie wiem” (cicha reguła bez zgłoszenia, P15); FN w konstrukcji większe niż przy A15; rodzaj „nie wiem” zadziałał jak rodzaj podany.

### A15b — Dodatek ukryty w ładunku przy podanym rodzaju towaru
- **Zbiór:** KW (6 par z dodatkiem `w_ladunku` lub `duzy_w_ladunku`), rodzaj towaru = ładunek zgodny; oba tryby.
- **Kroki:** 1) analiza z podanym rodzajem towaru; 2) FN dodatków w ładunku; 3) ta sama analiza z „nie wiem” na tych samych 6 parach; 4) porównanie FN para po parze.
- **Oczekiwany wynik:** dodatek w ładunku wykryty mimo wygaszania towaru zgodnego (P4 + P15); FN przy rodzaju towaru ≤ FN przy „nie wiem”.
- **Miara:** FN(rodzaj podany)/6 i FN(nie wiem)/6; FP osobno (alarmy poza dodatkiem). Osobno dla obu trybów.
- **Nie przechodzi:** FN(rodzaj podany) > FN(nie wiem) — reguła do wycofania („zwiń”, nie „ukryj”), ale tylko po pytaniu Projektanta do Artura (P15/P17: towar zgodny nie jest zaznaczany; decyduje Artur, nie ten test); FN i FP zsumowane; porównanie na różnych parach.

### A17 — Pusta naczepa
- **Zbiór:** KP (założenie: 6 par — 3 z przedmiotem w ładowni, 3 bez), rodzaj towaru „pusta naczepa”.
- **Kroki:** 1) analiza z rodzajem „pusta naczepa”; 2) dla każdego przedmiotu w ładowni sprawdzić ramkę i jej strefę; 3) dla 3 par bez przedmiotu sprawdzić brak alarmu.
- **Oczekiwany wynik:** każdy przedmiot w ładowni daje ramkę w strefie „ładownia” (spec §4b).
- **Miara:** FN przedmiotów w ładowni (przeoczone/3) i FP (pary czyste z alarmem/3, obszary na nich) osobno; trafność strefy „ładownia” u trafionych ramek.
- **Nie przechodzi:** jakikolwiek przedmiot w ładowni bez ramki (gasimy ładunek zgodny, nie przy „pusta naczepa”: P17); strefa inna niż ładownia; reguła gaszenia towaru zgodnego zadziałała przy „pusta naczepa”.

### A18 — Typ spoza katalogu
- **Zbiór:** KS: KL (6 par, typ w katalogu) + 2 pary typu spoza katalogu (nieobecnego w `nauka`); tryb bez pary, potem z parą (operator wskazuje wzorzec).
- **Kroki:** 1) analiza bez pary: odczytać flagę „wzorzec niepewny” i pewność doboru (`PROG_PEWNOSCI` = 0,2, założenie P16); 2) sprawdzić, że ramki są pokazane; 3) w ekranie: wskazać wzorzec z listy typów w katalogu; 4) w ekranie: wgrać plik wzorca; 5) powtórzyć analizę w trybie z parą.
- **Oczekiwany wynik:** flaga i ramki są (P16, P2); operator może wskazać wzorzec z listy i z pliku; po wskazaniu poprawnego wzorca flaga znika.
- **Miara:** flagi na 2 parach spoza katalogu (/2) oraz fałszywe flagi na 6 parach z katalogu (/6); ramki na 2 parach (>0); FP i FN w trybie z parą po wskazaniu wzorca, osobno.
- **Nie przechodzi:** brak flagi na którejkolwiek z 2 par; ramki ukryte przy fladze (P16 B odrzucone); brak jednej z dwóch dróg wskazania wzorca; flaga na ≥ 1 z 6 par z katalogu bez wpisu (spada zaufanie do flagi).

---

## Brakuje w ocenie (lista dla Programisty, po kroku 0P)

Sprawdzone: `anomalie/ocena.py` (`ocen`, `linia`, `linia_dluga`), `skrypty/bazowy.py`, `anomalie/generator.py`, `anomalie/detektor.py` (stan po `dc21a1f`). **Liczą dziś:** FP (obrazy czyste z alarmem i obszary), FN (dodatki) wg typu i miejsca w konstrukcji, zbędne obszary, ramki na auto (średnia, maks), czas na obraz (średnia, maks), trafność doboru typu (w `bazowy.py`), szczyt pamięci karty dla całego przebiegu pełnego (`bazowy.py`). Czego brakuje, żeby policzyć miary ze scenariuszy:

| # | Brakuje | Potrzebne w | Co dodać |
|---|---|---|---|
| B1 | Zbiory KL, KW, KP, KM, KS nie powstają: `generator.py` ma tylko `nauka/kalib/test/pelny`; `opis.json` nie ma pola rodzaju towaru, ładunku zgodnego ani typu spoza katalogu | A12, A15, A15b, A16, A17, A18 | tryby generatora (jak `--maly`, `--pelny`): `--kontrolne` ze zbiorami z tabeli wyżej; w `opis.json`: `rodzaj_towaru`, `ladunek_inny_niz_wzorzec`, `w_katalogu` (bool); KM: te same sceny w dwóch rozdzielczościach |
| B2 | Rodzaj towaru nie wchodzi do analizy: `ModelTypu.mapa(..., rodzaj_towaru)` bez wpływu; `bazowy.py` go nie przekazuje; w trybie z parą (A, A0, B) pola w ogóle nie ma | A15, A15b, A16, A17 | pole `rodzaj_towaru` w wejściu obu trybów i w predykcjach (zapisane w JSON); przebieg tych samych par dla „nie wiem” i dla rodzaju podanego |
| B3 | Brak mapy stref (ładownia · podłoga · ściana przednia · rama/osie · dach) w generatorze i w wyniku detektora; ramka ma tylko opis „gęstsze niż wzorzec … px” (bez strefy, bez „rzadziej”) | A5, A15–A17, A8 | strefa ramki (największe pokrycie, spec §4a) w predykcji; opis wg szablonu §5; w `opis.json` strefa każdego dodatku (dziś `miejsce` tylko dla dodatków w konstrukcji, ładunek = „ladunek”) |
| B4 | Brak miary „alarm na ładunku” osobno od FP: pary z dodatkiem w konstrukcji nie są czyste, więc ramka na ładunku trafia tylko do „zbędnych obszarów” i nie ma podziału na strefy | A15, A16, A17 | liczyć ramki niewskazujące dodatku wg strefy (ładownia vs konstrukcja) i pary z alarmem na ładunku |
| B5 | Brak porównania dwóch przebiegów para po parze (A15 vs A16; A15b: rodzaj podany vs „nie wiem”; A12: zmniejszony vs pełny) — `ocena` przyjmuje wiele predykcji, ale każdą liczy osobno | A12, A15b, A16 | tryb `--porownaj A.json B.json`: różnica FN i alarmów na ładunku na tych samych parach |
| B6 | Brak miary flagi „wzorzec niepewny” w `ocena.py`: predykcja ją zawiera (`wzorzec_niepewny`, `pewnosc_wzorca`), skrypt jej nie liczy; `bazowy.py` liczy tylko „niepewnych” w teście | A4, A18 | flagi na parach spoza katalogu (/2) i fałszywe flagi na parach z katalogu (/6); ramki przy fladze (>0) |
| B7 | Kolejność (A7) niemierzona: brak pewności 50–99% (spec §5) w predykcjach (są `oceny` z mapy, nie skala), brak miar „monotoniczność” i „pierwsza ramka = prawdziwy dodatek” | A7 | pewność wg §5 w JSON; w ocenie: odsetek monotonicznych list, odsetek „pierwsza trafna”, mediana pozycji prawdziwych |
| B8 | Trafność nazwy strefy ramki względem dodatku niemierzona | A5, A15, A17 | po B3: porównanie strefy ramki z strefą dodatku (z `opis.json`) |
| B9 | Pamięć: tylko jeden szczyt dla całego przebiegu `pelny`; czas nie rozróżnia startu zimnego i ciepłego; brak pamięci na obraz | A6, A13 | `max_memory_allocated` po każdym obrazie (reset przed), czas pierwszego obrazu osobno; wpis do JSON |
| B10 | Brak obrazów/min i sprawdzenia kompletu wyjść partii (JSON, PNG, CSV zbiorczy); polecenie partii z wiersza poleceń jest w spec §4d, nie w repo | A13 | czas całkowity i obrazy/min; liczenie plików wyjściowych; samo polecenie partii (CLI) |
| B11 | Analiza bez zmniejszenia niemożliwa: `D.wczytaj` zmniejsza do `SZER_ROBOCZA` (`f = ceil(W/SZER_ROBOCZA)`), brak przełącznika | A12 | parametr szerokości roboczej (pełna rozdzielczość) i czas/pamięć w obu wariantach |
| B12 | Brak testu offline: `D._siec()` pobiera wagi ResNet18 przy pierwszym użyciu (`~/.cache`); brak skryptu sprawdzającego brak ruchu sieciowego | A11 | wagi lokalnie (ścieżka, bez pobierania); uruchomienie w przestrzeni bez sieci i porównanie wyniku |
| B13 | Zapis kontroli, linia „N · zostało M”, powód przy „odrzuć”, powiększenie wokół ramki w JSON: brak w repo kodu zapisu; `raport.py` robi PNG z powiększeniami, nie ma JSON z polami `{id, nazwa, ramka, pewność, opis, przedmiot kontroli, decyzja, powód}` | A5, A8, A9 | format JSON wg spec §2 z polami decyzji i powodu; test automatyczny (A8, A9: liczba pozycji, M maleje) |
| B14 | Wynik oceny nie podaje liczb pomocniczych: **ile obrazów z dodatkiem w danym typie miało ramkę** w trybie para vs bez pary dla zbiorów kontrolnych (ocena na `--badane` jednego katalogu; `bazowy.py` ocenia tylko `test`, `pelny`) | A15–A18 | przebieg `bazowy.py` (lub osobny) dla zbiorów kontrolnych w obu trybach; wynik FP i FN osobno w tabeli |
| B15 | Liczby bez progów: skrypt nie sprawdza warunków „nie przechodzi” (60 s, 4 GB, kolejność monotoniczna, N = liczba ramek) | A6, A7, A9 | linia `PRZECHODZI/NIE` dla warunków ze spec, tam gdzie spec podaje próg (A6: 60 s, 4 GB; A7, A9); tam gdzie próg ustala Szef — tylko liczba |

**Uwaga o stanie ocen:** liczby w tym pliku są celami i warunkami ze spec; żadnych wyników modelu tu nie ma (nie uruchamiałem niczego na karcie ani na procesorze).

**Oddane Programiście** (zlecenie po kroku 0P, `docs/decyzje.md`): B1–B15, w kolejności: B1+B2+B3 (bez nich A15–A18 nie da się uruchomić), B4–B8, B9–B12, B13–B15. Każdy scenariusz do uruchomienia na karcie (jeden przebieg może obalić kilka punktów: A15, A15b, A16, A17 i A18 jednym skryptem z kilkoma trybami, ale każdy tryb z osobną linią FP i FN).

<!-- skill: test-scenarios -->
