# Discover: narzędzie RTG dla operatora (krok 1b) — SZKIC, czeka na wybór Artura (P8)

**Data**: 2026-11-19 · **Etap produktu**: nowy · **Pytanie odkrywania**: jak pomóc operatorowi RTG zobaczyć, gdzie obraz auta różni się od wzorca, tak by podjął decyzję o kontroli fizycznej w kilka minut.
Podstawa: `docs/zadanie.md`, `docs/pm/00-niewiadome.md`, `docs/pm/01-competitive-analysis.md`, odpowiedzi P1–P5 w `docs/decyzje.md`.

## Co już wiemy (z odpowiedzi Artura)
- Użytkownik: operator RTG przy stanowisku, w trakcie kontroli, kilka minut na auto (P1).
- Przeoczony dodatek gorszy od zbędnego alarmu, ale zaznaczeń na aucie kilka, nie kilkadziesiąt (P2).
- Operator zleca kontrolę zaznaczonych miejsc albo odrzuca alarm jednym kliknięciem z krótkim powodem z listy (P3).
- Obejmujemy skrytki w konstrukcji i towar w ładunku; w demo najpierw skrytka w konstrukcji (podwójna podłoga, ściana przy kabinie) (P4).
- Wynik w kilka sekund; liczba aut dziennie nieznana — założenie: kilkadziesiąt na stanowisko (P5).
- Z zadania: wynik zapisuje miejsce i przedmiot kontroli; praca offline; sztuczne dane (uwaga zespołu).

## Pomysły (10) — wysłane do Artura jako P8
1. Obraz badany obok wzorcowego, różnice zaznaczone ramkami.
2. Miejsca ułożone od najpewniejszego alarmu.
3. Odrzucenie alarmu jednym kliknięciem z powodem z listy.
4. Automatyczny dobór najbliższego czystego wzorca danego typu naczepy.
5. Powiększenie podejrzanego miejsca w konstrukcji z podpowiedzią „zmiana w konstrukcji”.
6. Raport z miejscem i przedmiotem kontroli, do zapisu.
7. Podsumowanie partii (ile czystych, ile do sprawdzenia).
8. Ciche pomijanie nieistotnych różnic (inny zgłoszony ładunek, szum, przesunięcie).
9. Przetwarzanie dużej partii w tle.
10. Uczenie się z odrzuceń operatora.

## Wybór Artura
(czeka na P8; po wyborze: pytanie, co zmienić i czy któryś odrzucony wziąć w części)

## Dalsze sekcje (po wyborze)
Założenia (wartość, użyteczność, wykonalność, opłacalność), macierz wpływ × ryzyko, najryzykowniejsze założenia do potwierdzenia przez Artura, eksperymenty, plan i drzewo decyzji.

<!-- skill: przeplywy-pm -->
