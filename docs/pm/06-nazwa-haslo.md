# 06 — Nazwa i hasło (product-name, value-prop-statements)

Podstawa: docs/spec.md, ustalenia Artura P1–P17 w docs/decyzje.md. Bez obietnic liczbowych — do czasu pomiaru (wyniki: docs/hacktribe.md, pole TODO).
Wybór nazwy należy do Szefa (wpis w docs/decyzje.md); docs/hacktribe.md zmieniam dopiero po tym wpisie.

## Kontekst w skrócie

- Użytkownik: operator RTG przy stanowisku, kilka minut na auto (P1, P5).
- Co robi: porównuje obraz naczepy ze wzorcem i zaznacza różnice, od najpewniejszej (P7), z krótkim opisem różnicy.
- Wyróżnik: sam dobiera wzorzec, gdy nie ma pary „czysta tego samego typu” (P8, P11); uczy się tylko z czystych obrazów.
- Decyzja zostaje po operatorze: „do kontroli” albo „odrzuć” (P3, P13).
- Zasady: gorszy jest przeoczony dodatek niż zbędny alarm (P2); zaznaczamy dodatkowe przedmioty i przeróbki, nie uszkodzenia (P6).

## Propozycje nazwy (≤ 50 znaków)

| # | Nazwa | Znaki | Uzasadnienie | Uwaga (domena/znak) |
|---|-------|-------|--------------|---------------------|
| 1 | **Różnica RTG** | 11 | Mówi wprost, co robi: pokazuje różnicę między obrazami RTG. Łatwa do wymówienia i zapamiętania; to obecna nazwa robocza. | Nazwa opisowa — słaba ochrona znakiem; domeny nie sprawdzano. |
| 2 | **Drugie Oko RTG** | 14 | Oddaje rolę: wspiera operatora, nie zastępuje go (P3). Ciepła, dobrze brzmi na slajdzie. | Częste wyrażenie; domeny nie sprawdzano. |
| 3 | **Wzorzec RTG** | 13 | Podkreśla wyróżnik — dobór wzorca bez pary (P8, P11). Dobra dla kierownika stanowiska. | Opisowa; mniej jasne, że chodzi o różnice. |
| 4 | **Znajdź Skrytkę** | 14 | Mówi o celu użytkownika (podwójna podłoga, ściana przy kabinie, P4). | Obiecuje „znajdowanie” — mocniej, niż pokaże pomiar; ryzyko oczekiwań. |
| 5 | **RTG Obok** | 9 | Odwołuje się do układu ekranu: obraz badany obok wzorcowego (P12). | Mało jasna bez kontekstu. |

**Rekomendacja: 1. Różnica RTG** (zostaje obecna nazwa). Powód: jedyna, która od razu mówi, co produkt robi, nie obiecuje wykrycia (zgodnie z P2 i brakiem pomiaru) i jest już w docs/hacktribe.md i zgłoszeniu. Na drugim miejscu **Drugie Oko RTG** — jeśli wolimy nazwę z charakterem. Sprawdzenie domeny/znaku towarowego nie było wykonane (brak dostępu do rejestrów).

## Hasło — 3 warianty (≤ 120 znaków)

| # | Hasło | Znaki |
|---|-------|-------|
| A | Pokazuje na obrazie RTG naczepy to, czego nie ma we wzorcu — zaczynając od najpewniejszego miejsca. | 102 |
| B | Sam dobiera wzorzec i wskazuje operatorowi kilka miejsc do sprawdzenia na jednym aucie. | 87 |
| C | Dwa obrazy obok siebie, różnice zaznaczone, decyzja o kontroli zawsze po stronie operatora. | 93 |

**Rekomendacja: A** na slajd tytułowy i do formularza (jedno zdanie o korzyści); B — gdy trzeba podkreślić wyróżnik (bez pary); C — do opisu ekranu. „Kilka miejsc” pochodzi z P2 (Artur: kilka, nie kilkadziesiąt) — to cel, nie wynik pomiaru.

## Wartość dla odbiorców (value-prop-statements)

**Dla operatora RTG.** Różnica RTG pokazuje obok siebie obraz badanej naczepy i wzorcowej, zaznacza miejsca, które się różnią, i ustawia je od najpewniejszego. Przy każdym miejscu jest krótki opis różnicy, powiększenie i dwa przyciski: „do kontroli” albo „odrzuć” (z powodem z listy). Operator z kilkoma minutami na auto zaczyna od najważniejszego i nie szuka różnic samemu. Gdy nie ma pary „czysta naczepa tego samego typu”, narzędzie samo dobiera wzorzec; jeśli nie jest pewne — ostrzega i prosi o wskazanie (P16). Towar zgodny ze zgłoszeniem można pominąć, wybierając rodzaj towaru z listy (P15, P17).

**Dla kierownika stanowiska.** Różnica RTG daje spójny sposób oceny obrazów: każde zaznaczenie ma zapisane miejsce, przedmiot kontroli i decyzję operatora (zlecona kontrola albo odrzucenie z powodem), więc widać, co sprawdzono i dlaczego alarm był zbędny. Narzędzie działa także tam, gdzie operator nie ma pary obrazów, a decyzja o kontroli fizycznej zostaje u człowieka. Skuteczność (zbędne alarmy, przeoczenia, czas na obraz) podamy po pomiarze na zbiorze testowym — do tego czasu nie składamy obietnic liczbowych.

<!-- skill: product-name -->
<!-- skill: value-prop-statements -->
