# Discover: narzędzie RTG dla operatora (krok 1b)

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

## Wybór Artura (P8–P10)
- Wybrane: 1 (obraz obok wzorcowego z ramkami), 2 (od najpewniejszego alarmu, przy każdym miejscu krótko czym różni się od wzorca — P7), 3 (odrzucenie jednym kliknięciem z powodem z listy), 4 (automatyczny dobór wzorca — „operator zwykle nie ma pary”), 6 (raport z miejscem i przedmiotem kontroli).
- Z odrzuconych w części: z 5 powiększenie podejrzanego miejsca (bez niego nie widać podwójnej podłogi); z 7 jedna linia „ile miejsc do sprawdzenia” na aucie.
- Odrzucone: 8 (woli zbędny alarm niż ciche pominięcie), 9, 10.
- Zmiany w wybranych: brak poza opisem różnicy przy miejscu (P9).

## Założenia (wartość / użyteczność / opłacalność / wykonalność)
- Wartość: operator traci więcej na przeoczeniu niż na zbędnym alarmie (P2); skrytki w konstrukcji i ładunek są realnym problemem (P4).
- Użyteczność: operator zdąży ocenić kilka ramek w kilka minut i ufa kolejności od najpewniejszej (P1, P7).
- Opłacalność: nie dotyczy (narzędzie dla urzędu, ocena w konkursie — decyzja Szefa 11:29).
- Wykonalność: model na karcie GTX 1050 4 GB, bez internetu, na sztucznych obrazach; wynik w kilka sekund (P5).

## Najryzykowniejsze założenia (potwierdził Artur, P11), w jego kolejności
1. **Dobór wzorca bez pary:** system sam dobierze dobry czysty wzorzec tego typu naczepy.
2. **Skrytka w podwójnej podłodze / ścianie przy kabinie** zostanie wskazana, przy kilku ramkach na auto, z powiększeniem miejsca. Sprawdzane jednym przebiegiem razem z 1 (Artur).
3. **Operator** oceni ramki w kilka minut i zaufa kolejności od najpewniejszej.

## Macierz wpływ × ryzyko
| Założenie | Wpływ | Ryzyko | Decyzja |
|---|---|---|---|
| 1 dobór wzorca | wysoki (bez niego nic nie działa) | wysokie | testować pierwsze |
| 2 skrytka w konstrukcji | wysoki (główne demo) | wysokie | z 1, jeden przebieg |
| 3 ufność operatora | średni | średnie | po makiecie, z ludźmi |

## Eksperymenty (tanie, na sztucznym zbiorze)
- E1+E2 (jeden przebieg, ≥ 2 hipotezy naraz — decyzja Szefa): na sztucznych naczepach dobrać wzorzec z zestawu czystych bez pary, potem porównać; mierzyć trafność doboru, przeoczone dodatki (FN), zbędne ramki na czystych (FP) i liczbę ramek na auto. Kryterium akceptacji: kilka ramek na auto (nie kilkadziesiąt), przeoczeń jak najmniej; próg liczbowy ustalamy z Szefem po pierwszym przebiegu (liczby bez źródła nie wpisujemy).
- E3: pokaz makiety Arturowi: czy z ramek, opisu różnicy i powiększenia da się podjąć decyzję „do kontroli / odrzuć” w kilka minut (próba ręczna).

## Plan i kolejność
Dobór wzorca → wskazanie skrytki (razem) → ekran operatora z kolejnością i odrzucaniem → raport (miejsce, przedmiot kontroli) → linia „ile miejsc”. Drzewo: jeśli E1 zawodzi, tryb pary (wzorzec podaje operator) jest pierwszy i wystarcza do demo (decyzja Szefa: tryb pary pierwszy).

## Wejście do /write-prd
Zakres: pomysły 1, 2, 3, 4, 6 + powiększenie + linia „ile miejsc”. Wyjęte: 8, 9, 10. Ryzyka i kryteria akceptacji z E1–E3 wracają w specu.

<!-- skill: przeplywy-pm -->
<!-- skill: brainstorm-ideas-new -->
<!-- skill: identify-assumptions-new -->
<!-- skill: prioritize-assumptions -->
<!-- skill: brainstorm-experiments-new -->
