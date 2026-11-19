# Product Requirements Document: Różnica RTG — wsparcie operatora w wykrywaniu anomalii (krok 2, /write-prd)

**Autor**: Projektant · **Data**: 2026-11-19 · **Status**: Draft (do recenzji przejścia)
Podstawa: `docs/zadanie.md`, `docs/pm/01-competitive-analysis.md`, `docs/pm/02-discover.md`, `docs/pm/03-warianty-ekranu.md`, odpowiedzi P1–P12 w `docs/decyzje.md`. Pełna specyfikacja wykonawcza: `docs/spec.md`.

## 1. Podsumowanie
Narzędzie dla operatora RTG przy stanowisku kontroli: porównuje obraz badanego auta z czystym wzorcem tego samego typu naczepy i wskazuje na obrazie kilka miejsc, które mogą kryć towar niezgłoszony. Operator w kilka minut zleca kontrolę fizyczną wskazanych miejsc albo odrzuca alarm jednym kliknięciem z powodem. Obecne narzędzie KAS (papierosy) słabo radzi sobie z małymi skrytkami w konstrukcji (zadanie, p. 1) — to nasza luka do zagospodarowania.

## 2. Kontakty
Artur — kształt produktu; Paweł — technika, wygląd, użyteczność.

## 3. Tło
Przemytnicy ukrywają towar w konstrukcji pojazdu i w zgłoszonym ładunku (zadanie, p. 1). Operator ocenia obraz sam i decyduje o kontroli fizycznej. Dane do testów: sztuczny zbiór naczep `.bmp` (zdjęć KAS nie mamy), więc wyniki dotyczą sztucznych danych.

## 4. Cel
Operator widzi, **gdzie** obraz różni się od wzorca i **czym**, i w kilka minut na auto podejmuje decyzję (P1, P5). Przeoczony dodatek jest gorszy od zbędnego alarmu (P2), ale na aucie ma być kilka zaznaczeń, nie kilkadziesiąt.
Wyniki kluczowe (mierzone na sztucznym zbiorze; progów liczbowych nie wpisujemy bez źródła — ustala Szef po pierwszym przebiegu, `docs/pm/02-discover.md` E1+E2):
1. Liczba zbędnych alarmów (FP) na czystych obrazach i przeoczeń (FN) na obrazach z dodatkami — raportowane osobno.
2. Liczba ramek na auto — „kilka” (P2).
3. Czas wyniku — kilka sekund w pokazie (P5); twardo < 1 min na obraz (zadanie, p. 7).

## 5. Segment
Operator RTG (funkcjonariusz SCS) przy stanowisku, w trakcie kontroli, kilka minut na auto; kilkadziesiąt aut dziennie na stanowisko (założenie, P5). Pozostałe segmenty (analitycy, administratorzy repozytorium) poza pierwszą wersją.

## 6. Propozycja wartości (operator)
- **Kto:** operator RTG przy stanowisku.
- **Dlaczego:** musi znaleźć niewielkie skrytki (podwójna podłoga, ściana przy kabinie) w ograniczonym czasie.
- **Co dziś:** ocenia obraz sam; narzędzie KAS słabo wykrywa małe skrytki w konstrukcji.
- **Jak:** obraz badany obok wzorca dobranego automatycznie; ramki od najpewniejszej; przy każdym miejscu krótko czym różni się od wzorca; powiększenie miejsca na obu obrazach; decyzja jednym kliknięciem.
- **Co potem:** wie, które miejsca zlecić do kontroli fizycznej; zapis wyniku (miejsce, przedmiot kontroli) jest gotowy do repozytorium.
- **Alternatywy:** narzędzie KAS od papierosów, ocena „na oko”, produkty Nuctech/Multicontrol (`docs/pm/01`); my — porównanie ze wzorcem, praca offline na małej karcie.

## 7. Rozwiązanie
Zakres (pomysły wybrane przez Artura: 1, 2, 3, 4, 6 + powiększenie z 5 + linia „ile miejsc” z 7). Ekran: **wariant 3 (obraz badany obok wzorcowego) z listą miejsc z boku z wariantu 2** (P12), makieta: https://pawelpisarek.github.io/hacknation-proba14/warianty/3/.
- Wzorzec: **dobierany automatycznie** (operator zwykle nie ma pary, P8); tryb z parą — operator wskazuje wzorzec sam (rezerwa i punkt odniesienia).
- Lista miejsc od najpewniejszego, przy każdym krótki opis różnicy (P7, P9); klik w miejsce pokazuje je na obu obrazach.
- Decyzja: „do kontroli” albo „odrzuć” jednym kliknięciem; przy odrzuceniu powód z listy (P3).
- Linia „N miejsc do sprawdzenia” (P10); zapis: miejsce + przedmiot kontroli (zadanie, p. 9).
- Szczegóły (wejście/wyjście, dane, raport, testy akceptacji): `docs/spec.md`.

### Założenia i otwarte pytania
- Liczba aut dziennie nieznana (P5, założenie).
- Najryzykowniejsze (P11, kolejność Artura): dobór wzorca bez pary → skrytka w podłodze/ścianie → ufność operatora w kolejność. Sprawdzane eksperymentami E1–E3 (`docs/pm/02`).
- Inny ładunek zgodny ze zgłoszeniem: czy zaznaczać — P15 (rekomendacja: nie); do odpowiedzi spec zakłada rekomendację i oznacza to jako założenie.
- P13: przyciski przy każdej pozycji listy; P14: układ wariantu 3 zostaje (Artur). P15 (inny ładunek) czeka.

## 8. Wydanie
**Pierwsza wersja (demo ≤ 2 min):** wczytanie badanego obrazu → wzorzec dobrany → ekran obok siebie z ramkami → klik w najpewniejszą (podwójna podłoga) → powiększenie → „do kontroli” → linia „ile miejsc” i zapis.
**Poza pierwszą wersją:** podsumowanie partii poza linią „ile miejsc” (7), przetwarzanie w tle (9), uczenie z odrzuceń (10), ciche pomijanie różnic (8 — odrzucone przez Artura), integracja z repozytorium obrazów Nuctech/Multicontrol (ścieżka wdrożenia, zadanie p. 9), uszkodzenia naczepy (P6), cena/wejście na rynek (nie dotyczy).

<!-- skill: przeplywy-pm -->
<!-- skill: create-prd -->
