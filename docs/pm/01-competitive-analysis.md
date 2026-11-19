# Analiza konkurencji: wykrywanie anomalii w obrazach RTG środków przewozowych

**Data**: 2026-11-19 · **Przeanalizowano**: 5 bezpośrednich + 3 pośrednich rozwiązań · **Etap**: `/competitive-analysis` (krok 1a łańcucha pm-skills)
Podstawa: `docs/zadanie.md`, `docs/decyzje.md`. Źródła z sieci zebrane dziś (lista na końcu); liczby producentów to deklaracje, niezależnie niezweryfikowane. Liczby bez źródła oznaczono „założenie”.

## Kontekst (z zadania — ustalone, bez pytań do Artura)
- Produkt: narzędzie AI porównujące obraz RTG środka przewozowego z wzorcowym i wskazujące różnice (możliwy przemyt) — zadanie, p. 1–3.
- Ocena: skuteczność (fałszywe alarmy FP i przeoczenia FN), innowacyjność, skalowalność — p. 6.
- Działanie bez chmury/internetu — p. 9; u nas dodatkowo mała karta (GTX 1050, 4 GB) i własny sztuczny zbiór (uwaga zespołu).
- Soczewka porównania: skuteczność na obrazach czystych/z dodatkami, wymóg offline, praca ze zdjęciem wzorcowym, duże pliki (~50 MB .bmp).

## Przegląd rynku
Rynek skanerów cargo/pojazdów dominują Nuctech, Smiths Detection, Rapiscan i Leidos; raporty rynkowe wskazują wzrost automatyzacji i AI, ale bez niezależnych miar skuteczności (źródła komercyjne). Producenci sprzętu dokładają warstwę AI do własnych skanerów (zamknięte, wiązane ze sprzętem). Dla KAS ważne: obecne narzędzie wykrywa papierosy, ale słabo małe skrytki w konstrukcji — luka, w którą celuje nasz produkt.

## Krajobraz konkurencji
| Rozwiązanie | Kategoria | Kto kupuje | Pozycjonowanie | Mocna strona | Słaba strona |
|---|---|---|---|---|---|
| **Nuctech** (Intelligent Inspection Platform, warstwa deep learning) | bezpośredni | służby celne, porty | AI wbudowane w własne skanery | integracja ze sprzętem, który KAS ma | zamknięte; walidacja własna producenta (deklaracja z wywiadu prasowego); warunki licencji i pracy offline nieznane (założenie) |
| **Rapiscan** (anomaly detection, cargo characterization, change detection vs historyczne skany) | bezpośredni | służby celne, granice | wykrywanie anomalii z intensywności, tekstury, kształtu + porównanie z historią | porównanie do poprzednich skanów — najbliższe naszemu pomysłowi | reguły/cechy ręczne; ograniczone do własnych skanerów |
| **Smiths Detection** (algorytmy wykrywania zagrożeń) | bezpośredni | lotniska, granice (założenie: także cargo) | algorytmy poddane certyfikacji ECAC — dotyczy bagażu lotniskowego, nie cargo (wywiad prasowy; do potwierdzenia) | certyfikacje, zaufanie | wywodzi się z wykrywania znanych zagrożeń, nie „różnicy od wzorca”; zamknięte |
| **Multicontrol** | bezpośredni | służby celne (też KAS) | sprzęt RTG z oprogramowaniem analizy | dostawca urządzeń KAS (zadanie, p. 1) | brak publicznych danych o AI porównującej do wzorca (do potwierdzenia — założenie) |
| **Obecne narzędzie KAS (detektor papierosów)** | bezpośredni (status quo) | operatorzy KAS | wykrywa konkretny towar | działa produkcyjnie | słabe dla małych ilości w konstrukcji pojazdu (zadanie, p. 1) |
| Ręczna ocena operatora (bez AI) | pośredni | KAS | doświadczenie | elastyczność | zmęczenie, czas, brak powtarzalności |
| Akademicki framework wykrywania anomalii na łatkach obrazu (CNN, SPIE) | pośredni | badania | uczenie bez „złych” przykładów | pokazuje, że podejście działa dla cargo | prototyp, nie produkt |
| Otwarte biblioteki anomalii przemysłowych (PatchCore, PaDiM, EfficientAD) | pośredni | przemysł | wykrywanie wad na produkcie | działają offline, darmowe | trenowane na wadach powierzchni, nie na RTG naczep |

## Cena, ślad rynkowy, ostatnie ruchy (krok 3 skilla)
Ceny: wszystkie rozwiązania komercyjne są sprzedawane w ofercie z dostawą sprzętu — ceny niepubliczne (w przeszukanych źródłach brak cen). Ślad rynkowy i ruchy — tylko to, co w źródłach.

| Rozwiązanie | Cena | Ślad rynkowy | Ostatnie ruchy |
|---|---|---|---|
| Nuctech | niepubliczna | wymieniany wśród liderów rynku cargo (raport rynkowy, źródło komercyjne) | warstwa deep learning w platformie inspekcyjnej (deklaracja producenta) |
| Rapiscan | niepubliczna | lider rynku cargo (raport rynkowy) | wykrywanie anomalii i porównanie z historycznymi skanami, wykrywanie broni i papierosów (strona producenta) |
| Smiths Detection | niepubliczna | lider rynku (raport rynkowy) | brak danych o cargo w źródłach |
| Multicontrol | niepubliczna | dostawca urządzeń KAS (zadanie, p. 1); w raportach rynkowych nie ustalono | brak danych w źródłach (założenie: nie ma publicznie opisanej AI porównującej do wzorca) |
| Narzędzie KAS | wewnętrzne | używane w kontroli nieinwazyjnej (zadanie, p. 1) | brak danych |

## Przegląd podejść do porównywania obrazów i wykrywania anomalii (offline, mała karta)
Wymagania: tylko obrazy czyste do nauki (dane „wzorcowe”), mapa różnic jako zaznaczone obszary, < 1 min na obraz, ~50 MB .bmp, GTX 1050 4 GB.

| Podejście | Jak działa | Offline / mała karta | Zalety | Wady / ryzyko |
|---|---|---|---|---|
| **Różnica pikselowa po dopasowaniu** (rejestracja pary + odjęcie, progi) | porównuje wzorzec z badanym | tak, nawet bez karty | proste, przejrzyste, dobre dla par „przed/po” | wrażliwe na przesunięcie, skalę, szum; wiele fałszywych alarmów |
| **Odjęcie od średniego/„czystego” modelu** (statystyka z wielu czystych obrazów, lokalne odchylenie) | uczy rozkład normalny pikseli/łatek | tak | tanie, wyjaśnialne | słabe przy dużej zmienności naczep |
| **PaDiM** (rozkład cech łatek z sieci pretrenowanej) | model normalnych cech na pozycję | tak; ok. 60 klatek/s w jednym teście na jednej karcie ([IM-IAD, arXiv 2301.13359](https://arxiv.org/pdf/2301.13359) — numer z zestawienia porównawczego wyszukiwarki, do potwierdzenia) | szybki, lekki | niższa jakość (obraz AUROC ok. 95,3% na MVTec wg zestawienia w wynikach wyszukiwania; założenie do sprawdzenia we własnym pomiarze) |
| **PatchCore** (pamięć cech łatek, najbliższy sąsiad) | porównuje łatki z bankiem normalnych | tak, ale pamięć GPU rośnie z liczbą obrazów (rzędu 6–9 GB wg zewnętrznej strony benchmarkowej o niejasnym źródle — założenie, nie zmierzone u nas) | najwyższa dokładność w benchmarkach (ok. 99% na MVTec, [PatchCore arXiv 2106.08265](https://arxiv.org/pdf/2106.08265)) | ciężki; 4 GB wymaga zmniejszenia banku (coreset) i cięcia na kafelki |
| **EfficientAD** (uczeń–nauczyciel + autoenkoder) | uczeń uczy się odtwarzać cechy nauczyciela | tak; ok. 2–5 ms/obraz w publikacji (inne karty) | szybki, lekki, dobry kompromis | wymaga treningu; obrazy 50 MB trzeba kafelkować |
| **Autoenkoder / rekonstrukcja** | błąd odtworzenia = anomalia | tak | proste | rozmywa szczegóły; małe skrytki mogą się „odtworzyć” |
| **Segmentacja nadzorowana (np. U-Net) na „dodatkach”** | uczy się wskazywać obiekty | tak | wprost mapa obiektów | wymaga oznaczonych przykładów; u nas sztuczne dane — ryzyko, że uczy się artefaktów generatora |
| **Detektor obiektów (np. YOLO)** | rysuje ramki na znanych klasach | tak | ramki gotowe do raportu | nie wykrywa nieznanych skrytek; jak obecne narzędzie na papierosy |

Wnioski do przeglądu (rekomendacja robocza, do rozstrzygnięcia przez Szefa/Programistę po wyniku bazowym): zaczynamy od różnicy po dopasowaniu (wynik bazowy) i ≥ 2 hipotez uczonych tylko na czystych obrazach (EfficientAD i PatchCore z coresetem, kafelkowanie), mierzymy FP/FN na zbiorze. Dopiero pomiar na karcie OMENa rozstrzyga — nie zakładamy z publikacji.

## Macierz funkcji
| Zdolność | Nasz produkt (cel) | Nuctech | Rapiscan | Smiths | Multicontrol | Obecne narzędzie KAS |
|---|---|---|---|---|---|---|
| Porównanie z obrazem wzorcowym | tak | częściowo (założenie) | tak (historia, wg strony producenta) | nie wprost (założenie) | nieznane | nie |
| Wykrywanie nieznanych skrytek | tak | częściowo (założenie) | częściowo (założenie) | częściowo (założenie) | nieznane | nie (zadanie, p. 1) |
| Zaznaczone miejsca na obrazie | tak | tak (założenie) | tak (założenie) | tak (założenie) | tak (założenie) | nieznane |
| Praca offline | tak | nieznane | nieznane | nieznane | nieznane | tak (zadanie, p. 9: docelowo bez chmury) |
| Wejście z repozytorium obrazów (.bmp, oba dostawcy skanerów) | tak (cel; zadanie, p. 9) | tak (założenie) | tak (założenie) | tak (założenie) | tak (założenie) | nieznane |
| Duże pliki .bmp, partie | tak (cel) | nieznane | nieznane | nieznane | nieznane | nieznane |

## Mapa pozycjonowania (2 osie)
Oś X: wykrywa tylko znany towar ↔ wykrywa dowolną różnicę od wzorca. Oś Y: zamknięte w sprzęcie jednego producenta ↔ otwarte wejście z plików .bmp z repozytorium (Nuctech i Multicontrol), działające offline (offline to wymóg zadania, nie potwierdzona przewaga).
- Lewy dół: obecne narzędzie KAS (znany towar, związane ze sprzętem).
- Środek: Nuctech, Smiths (wykrywanie zagrożeń, zamknięte).
- Prawy środek: Rapiscan (zmiana względem historii, zamknięte).
- **Prawy górny róg: nasz cel** — różnica od wzorca, wejście z plików .bmp z repozytorium obu dostawców, praca offline (wymóg p. 9).

## Szanse różnicowania
1. **Różnica od wzorca bez oznaczonych przykładów skrytek** — uczymy się tylko na czystych obrazach; odpowiada na lukę KAS (małe skrytki w konstrukcji).
2. **Wejście z plików .bmp z repozytorium obu dostawców (Nuctech, Multicontrol), działanie offline na małej karcie** — wymóg zadania (p. 9); czy konkurenci tego nie oferują — nieznane (założenie), więc to nie jest potwierdzona przewaga.
3. **Raport z kilkoma zaznaczonymi miejscami na aucie (nie kilkadziesiąt — P2) i krótkim czasem oceny** — założenie do potwierdzenia przez P3 (co operator robi z wynikiem) i poz. 5 (kształt raportu).
4. **Przetwarzanie dużych obrazów partiami** — skalowalność wymagana w zadaniu.

## Zagrożenia
1. **Fałszywe alarmy** (FP) — nadmiar zaznaczeń (kilkadziesiąt na aucie) odbiera zaufanie operatora; przeoczenie jest jednak gorsze (P2). Reakcja: próg dobrany tak, by przy zachowanej czułości zaznaczeń było kilka na auto.
2. **Różnica między sztucznym zbiorem a prawdziwym RTG** — wynik na naszych danych może nie przenieść się do KAS. Reakcja: nie obiecywać skuteczności na prawdziwych danych.
3. **Producenci sprzętu dodają AI porównującą** (Rapiscan już ma porównanie z historią). Reakcja: wejście z repozytorium obu dostawców, praca offline (wymóg zadania) i wskazywanie dowolnej różnicy od wzorca.
4. **Mała karta (4 GB)** — ograniczy rozmiar modelu i kafelków.
5. **Przeoczony dodatek (FN)** — wg P2 gorszy od zbędnego alarmu (przemyt = realna szkoda). Reakcja: czułość ustawiona na przeoczenia, a liczbę zaznaczeń ograniczona do kilku na auto.

## Rekomendacje
- **Postawić na**: porównanie z wzorcem, wejście z plików .bmp z repozytorium obu dostawców, praca offline (wymóg zadania), czytelny raport.
- **Dogonić**: nie przeoczyć dodatku (P2: przeoczenie jest gorsze od zbędnego alarmu), przy zaznaczeniach „kilka na auto, nie kilkadziesiąt”, i czas < 1 min na obraz.
- **Zignorować**: certyfikacje lotniskowe i integrację z innymi skanerami niż Nuctech i Multicontrol (poza zakresem hackathonu).

## Założenia do potwierdzenia przez Artura
- Użytkownik: operator przy stanowisku w trakcie kontroli, kilka minut na auto — **potwierdzone (P1, 11:27)**.
- Szansa 1 (małe skrytki w konstrukcji jako główny problem) — założenie do potwierdzenia (poz. 3 w docs/pm/00-niewiadome.md).
- Szansa 3 (raport: kilka miejsc, krótka ocena) — założenie do potwierdzenia: P3 (co operator robi z wynikiem, poz. 2) i poz. 5 (kształt raportu).
- Ocena „porównanie z historią” konkurentów zależy od tego, skąd operator dziś bierze obraz wzorcowy — poz. 6, pytanie do Artura w kolejce.
- **P2 potwierdzone (11:28):** przeoczony dodatek gorszy od zbędnego alarmu, ale na aucie ma być kilka zaznaczeń, nie kilkadziesiąt. Czy zgodny ze zgłoszeniem inny ładunek zaznaczać (poz. 8) — jeszcze bez pytania.

## Czego nie wiem o produkcie
Lista w `docs/pm/00-niewiadome.md` — pytania do Artura idą po kolei (P1…).

## Źródła (sprawdzone 2026-11-19)
- [Rapiscan — technologia (anomaly detection, change detection)](https://rapiscan-ase.com/resource-center/technology)
- [SPIE — anomaly detection w obrazach cargo (Jaccard)](https://journals.spiedigitallibrary.org/profile/Nicolas.Jaccard-250606)
- [EfficientAD (arXiv 2303.14535)](https://arxiv.org/pdf/2303.14535)
- [PatchCore (arXiv 2106.08265)](https://arxiv.org/pdf/2106.08265)
- [IM-IAD benchmark (arXiv 2301.13359)](https://arxiv.org/pdf/2301.13359)
- [Raport rynkowy skanerów cargo](https://www.giiresearch.com/report/go1785941-cargo-scanning-equipment.html)

<!-- skill: przeplywy-pm -->
<!-- skill: competitor-analysis -->
