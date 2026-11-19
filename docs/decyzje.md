# Decyzje

11:24 Szef: start próby 14. Zadanie: KAS — wyszukiwarka anomalii w obrazach RTG (docs/zadanie.md). Typ A — wynik mierzony na zbiorze (FP/FN).
11:24 Szef: dane — własny, sztuczny zbiór obrazów naczep .bmp (czyste / z dodatkami), bo zdjęć KAS nie mamy (od ludzi).
11:24 Szef: liczenie tylko na karcie OMENa przez orkiestrator (--klasa gpu-tlo, GTX 1050 4 GB), nigdy na procesorze; każdy przebieg sprawdza ≥ 2 hipotezy naraz.
11:24 Szef: aplikacja pod linkiem bierze wynik z usługi na karcie OMENa (sieć lokalna); model działa bez internetu (z zadania, p. 9).
11:25 Projektant: pominięte (produkt i kategoria analizy konkurencji) — z zadania: narzędzie AI porównujące obrazy RTG z wzorcowymi i wskazujące różnice (p. 1–2)
11:25 Projektant: pominięte (perspektywa porównania) — z zadania: skuteczność FP/FN, innowacyjność, skalowalność (p. 6); dodatkowo działanie offline na małej karcie (p. 9 + uwaga zespołu)
11:25 Projektant: pominięte (do czego analiza) — z zadania: wybór podejścia do porównywania obrazów i wykrywania anomalii dla naszego produktu
11:25 Projektant: konkurentów szukamy sami (przegląd rozwiązań i podejść), bez pytania Artura — z zadania nie wynika lista konkurentów
P1 11:25 Artur: Kto pierwszy patrzy na wynik: operator RTG przy stanowisku na granicy, w trakcie kontroli (rekomendacja), czy ktoś po fakcie, np. analityk przeglądający zapisane wyniki? — czeka
11:26 Szef: (Q1 Analityka) ocena liczy i raportuje FP i FN osobno, bez łączenia w jedną liczbę; FP na obraz czysty (jakikolwiek zaznaczony obszar = alarm) + liczba obszarów (Q4 przyjęte).
11:26 Szef: (Q3) dodatek wskazany = ramka nakłada się na maskę dodatku (IoU ≥ 0,1 albo środek dodatku w ramce); obszar poza dodatkami na obrazie z dodatkiem liczony osobno jako zbędny obszar.
11:26 Szef: (Q5) generator: naczepa w widoku z boku, skala szarości, dodatki 4 typów: mały w konstrukcji (rama/podłoga/ściana), średni w konstrukcji, w ładunku, duży w ładunku — każdy z maską; zmiany nieistotne na czystych: szum, przesunięcie, jasność, inny ładunek zgłoszony nie jest dodatkiem tylko w trybie bez pary — do potwierdzenia przez Artura (P przez Projektanta).
11:26 Szef: (Q6) z zadania (p. 3 „pary lub grupy”, p. 5 „nauczona na wzorcowych”): obsługujemy oba tryby — para wzorzec–badany i porównanie z modelem czystego obrazu tego typu; tryb pary pierwszy.
11:26 Szef: (Q7, Q8) przechowywanie bezstratne, analiza na kafelkach/zmniejszeniu z pomiarem wpływu na przeoczenia; raport: obraz z ramkami + plik ze współrzędnymi + podsumowanie partii.
11:26 Szef: (Q9) skrypt oceny przyjmuje dowolny katalog .bmp (+ opcjonalnie maski) i wypisuje FP/FN — gotowy na obce obrazy.
11:26 Szef: (Q2) co ważniejsze dla operatora (zbędne alarmy czy przeoczenia) — pyta Artura Projektant (jego pozycja 4 w docs/pm/00-niewiadome.md).
11:27 Analityk: recenzja 1a R1 — 5 braków
P1 11:27 odpowiedź: tak — operator przy stanowisku w trakcie kontroli, ma kilka minut na jedno auto (Artur w pokoju)
P2 11:27 Artur: Co gorsze dla operatora: zbędny alarm na czystej naczepie czy przeoczony dodatek? (rekomendacja: najpierw mało zbędnych alarmów) — czeka
P3 11:27 Artur: Co operator robi z wynikiem: zleca kontrolę fizyczną miejsca, zapisuje, czy odrzuca alarm? (rekomendacja: zleca kontrolę tylko zaznaczonych miejsc albo odrzuca jednym kliknięciem) — czeka
11:27 Analityk: recenzja hacktribe R1 — 5 braków
11:28 Szef: recenzja 1a R1 (5 braków) → Projektant poprawia cały docs/pm/01, potem R2.
11:28 Szef: recenzja hacktribe R1 (5 braków) → Prezenter poprawia cały docs/hacktribe.md: bez obietnic jako stanu (offline/skalowanie/kompresja — jako cel, do czasu pomiaru), bez „setek obrazów”, dwa tryby porównania (Q6), zastrzeżenie o sztucznym zbiorze, miejsca na liczby FP/FN i czas (TODO), wyróżnik: uczenie tylko na czystych obrazach, mała karta, offline. Braki produktowe (2, 5) nie idą do Artura — usuwamy niepotwierdzone zdania; P3 i ilość obrazów pyta Projektant.
P2 11:28 odpowiedź: odwrotnie niż rekomendacja — gorszy jest przeoczony dodatek (przemyt = realna szkoda), zbędny alarm to minuta więcej przy aucie; byle zaznaczeń na jednym aucie było kilka, nie kilkadziesiąt (Artur w pokoju)
11:29 Szef: licencja kodu MIT (repo publiczne) — plik LICENSE dodaje Prezenter razem z README. Tytuł „Różnica RTG” roboczy do kroku 6 (nazwa).
P3 11:29 odpowiedź: tak — operator zleca kontrolę zaznaczonych miejsc albo odrzuca jednym kliknięciem; przy odrzuceniu krótki powód z listy (np. znany element konstrukcji), żeby było wiadomo, czemu alarm był zbędny (Artur w pokoju)
P4 11:29 Artur: Co boli najbardziej: małe skrytki w konstrukcji pojazdu (rama, podłoga, ściana) czy towar ukryty w ładunku? (rekomendacja: oba, w demo najpierw skrytka w konstrukcji) — czeka
11:29 Szef: (1a R1 brak 1) z zadania p. 9: każdy wynik zapisuje miejsce i przedmiot kontroli (pola w raporcie); integracja z repozytorium obrazów Nuctech/Multicontrol — poza MVP, opisana jako ścieżka wdrożenia; produkt nie zależy od producenta urządzenia.
11:29 Szef: (1a R1 brak 2) cena i wejście na rynek — nie dotyczy (narzędzie dla urzędu, ocena w konkursie).
11:29 Szef: (1a R1 brak 4) liczenie tylko na karcie dotyczy też różnicy pikselowej — „bez karty” usunąć.
11:29 Szef: (1a R1 brak 5) „raport z priorytetem” i „mało czasu operatora” — tylko jeśli potwierdzi Artur (P7); czy zaznaczać też uszkodzenia konstrukcji (p. 2 zadania) — pyta Artura Projektant.
P4 11:30 odpowiedź: zgoda — oba (skrytki w konstrukcji i towar w ładunku), w demo najpierw skrytka w konstrukcji; najczęściej to podwójna podłoga albo ściana przy kabinie (Artur w pokoju)
P5 11:30 Artur: Ile obrazów dziennie przechodzi przez stanowisko i ile czasu operator ma na jeden? (rekomendacja: do kilku minut na auto, pokazujemy wynik w sekundach) — czeka
11:30 Szef: krok 1a zamknięty (Analityk R3: brak braków); przed 1b Projektant nanosi w 01 rozstrzygnięcia Szefa z 11:29 (usunąć „nawet bez karty”, integracja z p. 9 jako ścieżka wdrożenia). Zlecony krok 1b /discover.
P6 11:31 Artur: Czy narzędzie ma też zaznaczać uszkodzenia naczepy, czy tylko dodatkowe przedmioty i przeróbki? (rekomendacja: tylko dodatkowe przedmioty i przeróbki — tego dotyczy sprawdzanie) — czeka
P5 11:31 odpowiedź: zgoda — wynik w kilka sekund; liczby aut dziennie Artur nie zna, zakładamy kilkadziesiąt na stanowisko (założenie) (Artur w pokoju)
P7 11:31 Artur: Czy raport ma pokazywać miejsca w kolejności ważności (najpewniejszy alarm pierwszy), żeby operator z kilkoma minutami zaczął od najważniejszego? (rekomendacja: tak) — czeka
11:31 Szef: właściciel praw w LICENSE — „Zespół Hackathon” zostaje.
11:31 Analityk: recenzja hacktribe R2 — 2 braków
11:32 Szef: hacktribe R2 — 2 braki (TODO z liczbami, linki) to miejsca na wyniki, nie błąd treści: DRAFT zamknięty na teraz; Prezenter wpisuje liczby po wyniku bazowym Programisty i link makiety przed 20:00, ostatecznie przed 10:30.
P8 11:32 Artur: Wybierz 3–5 pomysłów z listy 10 (ekran, raport, odrzucanie, wzorzec, partia…) do dalszej pracy lub „wszystkie” (rekomendacja: 1, 2, 3, 6, 7) — czeka
P6 11:32 odpowiedź: tak — tylko dodatkowe przedmioty i przeróbki, bez uszkodzeń naczepy (Artur w pokoju)
P7 11:32 odpowiedź: tak — od najpewniejszego alarmu; przy każdym miejscu krótko, czym różni się od wzorca (Artur w pokoju)
11:33 Programista: założenia techniczne (łatwe do zmiany): Python + torch (CUDA, karta OMENa); obraz 8-bit .bmp; analiza na zmniejszeniu do szer. 1200 px (pełny 12000×4200 → ×10), ramki przeliczane na układ obrazu badanego w pełnej rozdzielczości; próg każdej metody z osobnego zbioru kalib (same czyste) — najmniejszy bez alarmu, bez podglądania testu.
11:33 Programista: generator (gen-v1): 3 typy naczep, para = ta sama konstrukcja i ten sam ładunek zgłoszony; badany: szum, przesunięcie ±1%, skala skanu X ±1,5% / Y ±0,3%, jasność ±15%; dodatki 4 typów z maskami PNG. Zbiory: nauka 3×6 pustych, kalib 12 czystych par, test 30 czystych + 30 z dodatkami (1200×420), pełny 3+3 pary 12000×4200 (~50 MB). Generowanie danych na procesorze OMENa (to nie model ani odczyt skanu).
11:33 Programista: przebieg bazowy na karcie (gpu-tlo) sprawdza naraz: H1 A (wyrównanie + różnica tłumienia względem filtru maksimum wzorca) daje FP 0 na czystych przy małym FN; H2 B (cechy ResNet18) gubi małe dodatki w konstrukcji częściej niż A; H3 ablacja A0 (bez filtru maksimum) — więcej FP niż A; H4 C (model czystego typu, bez pary) działa na pustych naczepach, na załadowanych daje alarmy na ładunku zgłoszonym; H5 czas na obraz pełnowymiarowy < 60 s i pamięć karty < 4 GB.
P8 11:33 odpowiedź: wybrane pomysły 1, 2, 3, 4, 6 (zamiast 7 bierze 4 — operator zwykle nie ma pary „czysta tego samego typu”, więc bez dobierania wzorca narzędzie nie zadziała); 8 odrzucone — woli zbędny alarm niż ciche pominięcie (P2) (Artur w pokoju)
P9 11:33 Artur: Co zmienić w wybranych pomysłach 1, 2, 3, 4, 6? (rekomendacja: nic poza dopisaniem do 2 krótkiego opisu różnicy przy każdym miejscu) — czeka
P10 11:33 Artur: Czy któryś odrzucony pomysł (5, 7, 8, 9, 10) warto wziąć choć w części? (rekomendacja: z 7 tylko jedna linia „ile miejsc do sprawdzenia” na aucie; reszta nie) — czeka
11:33 Szef: cofnięte przez Szefa — „Generowanie danych na procesorze OMENa” (11:33 Programista): liczenie na OMENie tylko na karcie, także generator (torch na CUDA przez orkiestrator --klasa gpu-tlo); reszta założeń 11:33 przyjęta.
P9 11:34 odpowiedź: zgoda, nic więcej do zmiany w wybranych pomysłach (1, 2, 3, 4, 6) (Artur w pokoju)
P10 11:34 odpowiedź: z 7 tylko jedna linia „ile miejsc do sprawdzenia” na aucie — tak; z 5 bierzemy powiększenie podejrzanego miejsca (bez niego operator nie zobaczy podwójnej podłogi); 8, 9, 10 nie (Artur w pokoju)
P11 11:34 Artur: Najryzykowniejsze założenia do sprawdzenia w pierwszej kolejności: (1) narzędzie wskaże skrytkę w podwójnej podłodze/ścianie przy kabinie, dając kilka ramek na auto; (2) bez pary „czysta tego samego typu” system sam dobierze dobry wzorzec; (3) operator zdąży ocenić ramki w kilka minut i będzie ufał kolejności od najpewniejszej. Potwierdzasz? (rekomendacja: tak, w tej kolejności) — czeka
P11 11:35 odpowiedź: tak, ale w kolejności 2, 1, 3 (dobór wzorca → skrytka w podłodze/ścianie → ocena operatora) — bez doboru wzorca punkt 1 nie ma na czym stać; 1 i 2 sprawdzać jednym przebiegiem (Artur w pokoju)
11:36 Szef: zlecone Programiście 3 makiety wariantów ekranu (docs/pm/03) na gh-pages przed /write-prd; P11 przekazane do przebiegu 0P (dobór wzorca + skrytka w konstrukcji jednym przebiegiem).
11:38 Programista: makiety 3 wariantów ekranu (udawane dane, sztuczny RTG w SVG, 3 ramki: podwójna podłoga, ściana przy kabinie, paleta): https://pawelpisarek.github.io/hacknation-proba14/warianty/1/ · https://pawelpisarek.github.io/hacknation-proba14/warianty/2/ · https://pawelpisarek.github.io/hacknation-proba14/warianty/3/ (źródło docs/makieta/warianty/)
11:39 Szef: warianty https://pawelpisarek.github.io/hacknation-proba14/warianty/1/ https://pawelpisarek.github.io/hacknation-proba14/warianty/2/ https://pawelpisarek.github.io/hacknation-proba14/warianty/3/
P12 11:39 Artur: Który ekran główny: 1 (jeden obraz na cały ekran), 2 (najpierw lista miejsc) czy 3 (obraz badany obok wzorcowego)? (rekomendacja: 3 — operator od razu widzi „jest / nie ma” w tym samym miejscu, tak jak szuka podwójnej podłogi) — czeka
P12 11:40 odpowiedź: wariant 3 (obraz badany obok wzorcowego) + z wariantu 2 lista miejsc z boku, od najpewniejszego (P7); klik w miejsce na liście pokazuje je na obu obrazach (Artur w pokoju)
P13 11:40 Artur: Gdzie mają być przyciski „do kontroli” i „odrzuć”: przy każdej pozycji listy z boku (rekomendacja — decyzja bez szukania, jednym kliknięciem przy opisie różnicy) czy pod obrazami dla wybranego miejsca? Makieta: https://pawelpisarek.github.io/hacknation-proba14/warianty/3/ — czeka
P14 11:40 Artur: Co w wariancie 3 ci się nie podoba lub brakuje na ekranie? Makieta: https://pawelpisarek.github.io/hacknation-proba14/warianty/3/ (rekomendacja: nic — zostawiamy układ: dwa obrazy + lista z boku) — czeka
P15 11:42 Artur: Czy towar w ładunku, który jest inny niż na obrazie wzorcowym, ale zgodny ze zgłoszeniem celnym, ma być zaznaczany? (rekomendacja: nie — zaznaczamy tylko to, czego nie ma ani w konstrukcji, ani w zgłoszonym towarze) — czeka
11:43 Szef: kto jest kim (Paweł): do Szefa pisze Paweł, w pokoju Produkt odpowiada Artur, nikt trzeci; podpis urządzenia nieważny — docs/zespol.md zamknięty.
P13 11:43 odpowiedź: A — przyciski „do kontroli” i „odrzuć” przy każdej pozycji listy z boku (Artur w pokoju)
P14 11:43 odpowiedź: układ wariantu 3 zostaje; do makiety dodać trzy już ustalone rzeczy: powiększenie podejrzanego miejsca (P10), linię „ile miejsc do sprawdzenia” przy aucie (P10), powód z listy przy „odrzuć” (P3) (Artur w pokoju)
P15 11:44 odpowiedź: nie zaznaczamy towaru zgodnego ze zgłoszeniem — ale tylko gdy narzędzie zna zgłoszenie (operator wybiera rodzaj towaru z listy); bez tego zaznaczamy wszystko, co różni się od wzorca (P2: woli zbędny alarm) (Artur w pokoju)
P16 11:45 Artur: Gdy system nie jest pewny doboru wzorca, ma (A) pokazać ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec” czy (B) nie pokazywać ramek, dopóki operator nie wskaże wzorca? (rekomendacja: A — przy P2 lepiej zbędny alarm niż ciche pominięcie) — czeka
11:45 Projektant: braki recenzji przejścia 2 (R1): A12–A14 (zmniejszenie, partia, próba z operatorem), P15 spójne, wyrównanie PRD ze specem; „podsumowanie partii” (Q8) zastąpione linią „ile miejsc” — z P10 Artura (wybrał z 7 tylko tę linię).
P17 11:46 Artur: Jakie rodzaje zgłoszonego towaru operator ma mieć na liście przed analizą? (rekomendacja: krótka lista — sprzęt i AGD, odzież i tekstylia, żywność i napoje, materiały budowlane, inne — oraz „nie wiem”, wtedy zaznaczamy wszystko) — czeka
11:46 Projektant: R2 recenzji przejścia, brak 2 (P15 a Q5 i generator) — pytanie techniczne do Szefa: jak generator ma tworzyć przypadek „inny ładunek zgodny ze zgłoszeniem”; spec zakłada: osobny mały zbiór kontrolny w trybie bez pary.
P16 11:46 odpowiedź: A — gdy system nie jest pewny doboru wzorca, pokazuje ramki z ostrzeżeniem „wzorzec niepewny — wskaż wzorzec” (Artur w pokoju)
