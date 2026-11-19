# Scenariusz pokazu — „Różnica RTG” (SZKIELET, ≤ 120 s)

Stan: szkielet. Pokaz nagrywa człowiek. Źródła: `docs/spec.md` §6, `docs/pm/09-pre-mortem.md` (kroki K1–K6, cztery warstwy), `docs/decyzje.md` (P27–P36).
Miejsca „[z prawdziwego wyniku]” uzupełniamy po wyborze obrazu pokazowego i jego przebiegu (ryzyko R10; Programista zapisuje wynik w `docs/decyzje.md`). Liczb i nazw z makiety nie przepisujemy — to dane udawane.
Link pokazu: **[link warstwy — wpisać]**. Warstwa 1: https://ksefbot.pl (dziś „w przygotowaniu”); warstwa 3: https://pawelpisarek.github.io/hacknation-proba14/makieta/ (makieta, dane udawane).

## Tabela pokazu (suma 120 s)
| Sekunda | Krok | Co widać na ekranie | Co mówimy |
|---|---|---|---|
| 0–10 | — | Ekran startowy, dwa pola na obrazy; pole „Rodzaj zgłoszonego towaru” = „nie wiem” | „Operator RTG ma kilka minut na jedno auto. Narzędzie pokazuje, co różni obraz badany od wzorca, i podpowiada, gdzie patrzeć najpierw.” |
| 10–25 | K1 | Wgranie pary: obraz badany **[z prawdziwego wyniku: plik]** i wzorzec. Po chwili lista miejsc na obrazie z numerowanymi ramkami | „Wgrywam parę. Wynik w kilka sekund. Lista idzie od najpewniejszego miejsca.” |
| 25–40 | K1 | Lista: **[z prawdziwego wyniku: liczba miejsc]** miejsc; pierwsze: **[nazwa miejsca]**, **[pewność]%**; kliknięcie → powiększenie na wzorcu i badanym obok siebie | „Nazwa miejsca, opis różnicy i pewność. Powiększenie pokazuje to samo miejsce na wzorcu i na badanym.” |
| 40–65 | K3 | „do kontroli” przy pierwszym, „odrzuć” z powodem przy kolejnym; przycisk „Następne miejsce” przeskakuje po nierozstrzygniętych; linia „zostało N” maleje do „zostało 0”, okno zamyka się po ostatnim | „Każde miejsce: do kontroli albo odrzuć z powodem. „Następne miejsce” prowadzi dalej, aż zostanie 0.” |
| 65–75 | K4 | Komunikat „pominięto N różnic”, przycisk „Pokaż pominięte” (**[z prawdziwego wyniku: czy są pominięte]**; jeśli nie ma — krok pomijamy, 10 s zapasu) | „Różnice zgodne ze zgłoszonym towarem są domyślnie pominięte, ale można je zobaczyć i zlecić do kontroli.” |
| 75–95 | K2 | Rodzaj towaru → „pusta naczepa”: nagłówek „najpierw alarmy z reguły”, flaga „ładownia pusta wg zgłoszenia” przy miejscach w ładowni **[z prawdziwego wyniku: które]** | „Gdy zgłoszono pustą naczepę, każdy przedmiot w ładowni to alarm z reguły — idzie na górę listy.” |
| 95–110 | K5 | „Wgraj plik wzorca”: wybór pliku **[nazwa pliku]**, znacznik „wskazany ręcznie”; ramki i pewności przeliczone (**[z prawdziwego wyniku: pewność przed → po]**) | „Gdy dobór wzorca jest niepewny, operator wskazuje wzorzec ręcznie, z listy albo z pliku.” |
| 110–120 | K6 | Zapis kontroli: decyzje z miejscem i przedmiotem, linia „wzorzec: plik **[nazwa]** (wskazany ręcznie)”, obraz z ramkami (PNG) | „Zapis z obrazem z ramkami trafia do kontroli fizycznej jako dowód. Sprawdzane na sztucznych danych — prawdziwych obrazów KAS nie mamy.” |

Czas analizy na ekranie nie jest pokazywany (P25–P26); jeśli ktoś zapyta, wynik czasu jest w JSON. Wynik skuteczności (FP/FN) tylko z linii WYNIK w `docs/decyzje.md`, z zastrzeżeniem o sztucznym zbiorze.

## Przed nagraniem (wpisać)
- [ ] Obraz pokazowy wybrany, jego prawdziwy wynik w `docs/decyzje.md`: **[do uzupełnienia]**
- [ ] Wszystkie pola „[z prawdziwego wyniku]” wpisane; zero liczb z makiety
- [ ] Link warstwy 1 daje 200 (`curl -L`), kod: **[wpisać]**
- [ ] Próba na czas ≤ 120 s: **[wynik próby]**
- [ ] Zrzuty i nagranie z działającej wersji w repo (warstwa 4)

## Gdy coś padnie
Cztery warstwy z `docs/pm/09-pre-mortem.md`. Przełączenie = jedna zmiana linku „Demo” w README, slajdach i HackTribe (Prezenter), około minuty. W trakcie pokazu: otworzyć następną warstwę w przygotowanej karcie przeglądarki.

| Warstwa | Kiedy | Co pokazujemy | Które kroki | Przełączenie |
|---|---|---|---|---|
| 1. Wszystko działa | domyślnie | ksefbot.pl, prawdziwy obraz, usługa na karcie OMENa | K1–K6 na żywo | — |
| 2. Padła karta OMENa albo sieć | usługa nie odpowiada | ksefbot.pl w trybie „wynik zapisany z przebiegu <data, godz.>” (Programista: tryb zapisu zbudowany w MVP) | K1–K6 tylko przy zapisanych przebiegach: zwykły (K1, K3, K4, K6), pusta naczepa (K2), plik wzorca (K5); bez nich tylko K1 | włączyć tryb zapisu albo przejść na warstwę 3 |
| 3. Padł ksefbot.pl | adres ≠ 200 | makieta R3, GitHub Pages, **podpis: „makieta zamknięta, dane udawane; P34–P36 dopiero w MVP”** | K1, K4, K6; K2, K3, K5 częściowo | podmiana linku „Demo” na adres makiety |
| 4. Nic z internetu | brak sieci | zrzuty (`docs/zrzuty/mvp-*.png`), nagranie ścieżki, slajdy PDF — lokalnie z repo | K1–K6 jako obrazy (jeśli zrzuty z MVP są zrobione) | otworzyć pliki lokalne |

Zasada mówienia: przy każdej warstwie powiedzieć głośno, co jest „na żywo”, a co „zapisane” albo „makieta”. Nie udawać, że makieta to wynik modelu.

<!-- skill: value-prop-statements -->
