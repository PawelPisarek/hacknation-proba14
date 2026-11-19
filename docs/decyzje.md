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
