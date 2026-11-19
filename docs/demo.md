# Scenariusz pokazu — „Różnica RTG” (SZKIELET po R1, ≤ 120 s)

Stan: szkielet po recenzji R1 (Analityk, 5 braków; rozstrzygnięcia Szefa w `docs/decyzje.md`). Pokaz nagrywa człowiek. Źródła: `docs/spec.md` §6, `docs/pm/09-pre-mortem.md` (kroki K1–K6, cztery warstwy), `docs/decyzje.md` (P27–P36).
Miejsca „[z prawdziwego wyniku]” uzupełniamy po wyborze obrazu pokazowego i jego przebiegu (ryzyko R10; Programista zapisuje wynik w `docs/decyzje.md`). Liczb i nazw z makiety nie przepisujemy — to dane udawane.
Linki: warstwa 1 — ksefbot.pl, **jeszcze niewdrożony** (ostatnio HTTP 530; link wpiszemy po kodzie 200); warstwa 3 — makieta, dane udawane: https://pawelpisarek.github.io/hacknation-proba14/makieta/.

## Kolejność pokazu (wprost)
1. **Jeden przebieg: K1 → K4 → K3 → K6.** Rodzaj zgłoszonego towaru wybieramy **na starcie**: **[z prawdziwego wyniku: rodzaj towaru]** (nie „nie wiem”; dzięki temu powstają pominięte różnice dla K4). Zapis K6 pochodzi z tego przebiegu, z decyzjami z K3.
2. **Po zapisie, osobno i bez zapisu do kontroli:** K2 to tylko zmiana rodzaju towaru na „pusta naczepa”, przeliczona na tym samym wyniku, bez ponownego wgrania obrazu. K5 to wgranie tylko pliku wzorca; kończy się podglądem zapisu z linią „wzorzec: plik … (wskazany ręcznie)” (P36). Zmiana rodzaju towaru przelicza ramki i kasuje decyzje z K3, dlatego K2 i K5 idą dopiero po K6. Czasy K2 i K5 sprawdzamy w próbie.

## Tabela pokazu (suma 120 s)
| Sekunda | Krok | Co widać na ekranie | Co mówimy |
|---|---|---|---|
| 0–10 | start | Ekran startowy, dwa pola na obrazy; pole „Rodzaj zgłoszonego towaru” ustawiamy na **[z prawdziwego wyniku: rodzaj towaru]** | „Operator RTG ma kilka minut na jedno auto. Narzędzie pokazuje, co różni obraz badany od wzorca, i podpowiada, gdzie patrzeć najpierw. Zaczynam od zgłoszonego towaru.” |
| 10–20 | K1 | Wgranie pary: obraz badany **[z prawdziwego wyniku: plik]** i wzorzec; po analizie lista miejsc z numerowanymi ramkami (czas: **[z prawdziwego wyniku: czas]**, nie obiecujemy liczby) | „Wgrywam parę obrazów. Lista idzie od najpewniejszego miejsca.” |
| 20–32 | K1 | **[z prawdziwego wyniku: liczba]** miejsc; pierwsze: **[nazwa miejsca]**, **[pewność]%**; kliknięcie → powiększenie na wzorcu i badanym obok siebie | „Nazwa miejsca, opis różnicy i pewność. Powiększenie pokazuje to samo miejsce na wzorcu i na badanym.” |
| 32–42 | K4 | Komunikat „pominięto N różnic” (**[z prawdziwego wyniku: N]**), przycisk „Pokaż pominięte”; po kliknięciu jedną różnicę zlecamy do kontroli, „zostało” rośnie | „Różnice zgodne ze zgłoszonym towarem są domyślnie pominięte, ale można je zobaczyć i zlecić do kontroli.” |
| 42–67 | K3 | „do kontroli” i „odrzuć” z powodem; „Następne miejsce” przeskakuje po nierozstrzygniętych; linia „zostało N” maleje do „zostało 0”, okno zamyka się po ostatnim | „Każde miejsce: do kontroli albo odrzuć z powodem. „Następne miejsce” prowadzi dalej, aż zostanie 0.” |
| 67–80 | K6 | Zapis kontroli z tego przebiegu: decyzje z miejscem i przedmiotem, linia „pominięte (towar zgodny ze zgłoszeniem): **[N]**” (P29), obraz z ramkami (PNG); linii „wzorzec: plik” tu nie ma | „Zapis z obrazem z ramkami trafia do kontroli fizycznej jako dowód. Sprawdzane na sztucznych danych — prawdziwych obrazów KAS nie mamy.” |
| 80–95 | K2 | **Ten sam wynik, bez ponownego wgrywania obrazu:** zmieniamy tylko rodzaj towaru na „pusta naczepa”; ramki przeliczone; nagłówek „najpierw alarmy z reguły”, flaga **„alarm z reguły: pusta naczepa”** przy miejscach w ładowni **[z prawdziwego wyniku: które]** (P27, P34). Czas sprawdzamy w próbie | „Gdy zgłoszono pustą naczepę, każdy przedmiot w ładowni to alarm z reguły — idzie na górę listy.” |
| 95–120 | K5 | **Wgrywamy tylko plik wzorca** (obrazu badanego nie ruszamy): „Wgraj plik wzorca” **[nazwa pliku]**, znacznik „wskazany ręcznie”, ramki i pewności przeliczone (**[z prawdziwego wyniku: pewność przed → po]**); na końcu podgląd zapisu z linią „wzorzec: plik **[nazwa]** (wskazany ręcznie)” (P36). Czas sprawdzamy w próbie | „Gdy dobór wzorca jest niepewny, operator wskazuje wzorzec ręcznie, z pliku. Zapis zapamiętuje, skąd wzorzec.” |

Czasu analizy na ekranie nie pokazujemy (P25–P26); w JSON jest. Zmierzone 0,49 s na obraz nie obejmuje wysyłania ~50 MB, więc na pokazie podajemy czas tylko z prawdziwego przebiegu. Skuteczność (FP/FN) tylko z linii WYNIK w `docs/decyzje.md`, z zastrzeżeniem o sztucznym zbiorze.

## Przed nagraniem (wpisać)
- [ ] Obraz pokazowy wybrany, jego prawdziwy wynik w `docs/decyzje.md`: **[do uzupełnienia]**; rodzaj towaru na starcie: **[wpisać]**
- [ ] Obraz demo i rodzaj towaru dają co najmniej 1 pominiętą różnicę (K4) i co najmniej 1 miejsce w ładowni (K2): **[sprawdzić na prawdziwym wyniku]**
- [ ] Wszystkie pola „[z prawdziwego wyniku]” wpisane; zero liczb z makiety
- [ ] Link warstwy 1 daje 200 (`curl -L`), kod: **[wpisać]**
- [ ] Próba na czas ≤ 120 s: **[wynik próby]**
- [ ] Zrzuty i nagranie z działającej wersji w repo (warstwa 4)

## Gdy coś padnie
Cztery warstwy z `docs/pm/09-pre-mortem.md`. Przełączenie = jedna zmiana linku „Demo” w README, slajdach i HackTribe (Prezenter), około minuty. W trakcie pokazu: otworzyć następną warstwę w przygotowanej karcie przeglądarki.

| Warstwa | Kiedy | Co pokazujemy | Które kroki | Przełączenie |
|---|---|---|---|---|
| 1. Wszystko działa | domyślnie | ksefbot.pl (jeszcze niewdrożony), prawdziwy obraz, usługa na karcie OMENa | K1–K6 na żywo | — |
| 2. Padła karta OMENa albo sieć | usługa nie odpowiada | ksefbot.pl w trybie „wynik zapisany z przebiegu <data, godz.>” (Programista: tryb zapisu w MVP) | K1–K6 tylko przy zapisanych przebiegach: zwykły (K1, K4, K3, K6), pusta naczepa (K2), plik wzorca (K5); bez nich tylko K1 | włączyć tryb zapisu albo przejść na warstwę 3 |
| 3. Padł ksefbot.pl | adres ≠ 200 | makieta R3, GitHub Pages, **podpis: „makieta zamknięta, dane udawane; P34–P36 dopiero w MVP”** | K1, K4, K6; K2, K3, K5 częściowo | podmiana linku „Demo” na adres makiety |
| 4. Nic z internetu | brak sieci | zrzuty (`docs/zrzuty/mvp-*.png`), nagranie ścieżki, slajdy PDF — lokalnie z repo | K1–K6 jako obrazy (jeśli zrzuty z MVP są zrobione) | otworzyć pliki lokalne |

Zasady mówienia:
- Przy każdej warstwie powiedzieć głośno, co jest „na żywo”, a co „zapisane” albo „makieta”.
- **Przy warstwie 3 każdą liczbę z ekranu (miejsca, pewności) mówimy tylko z dopiskiem „dane udawane”.** Nie udajemy, że makieta to wynik modelu.
