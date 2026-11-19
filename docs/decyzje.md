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
