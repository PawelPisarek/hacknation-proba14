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
| **Nuctech** (Intelligent Inspection Platform, warstwa deep learning) | bezpośredni | służby celne, porty | AI wbudowane w własne skanery | integracja ze sprzętem, który KAS ma | zamknięte; walidacja własna producenta; chmura/licencja zależne od producenta |
| **Rapiscan** (anomaly detection, cargo characterization, change detection vs historyczne skany) | bezpośredni | służby celne, granice | wykrywanie anomalii z intensywności, tekstury, kształtu + porównanie z historią | porównanie do poprzednich skanów — najbliższe naszemu pomysłowi | reguły/cechy ręczne; ograniczone do własnych skanerów |
| **Smiths Detection** (algorytmy wykrywania zagrożeń) | bezpośredni | lotniska, granice | certyfikowane algorytmy (ECAC) | certyfikacje, zaufanie | wywodzi się z wykrywania znanych zagrożeń, nie „różnicy od wzorca”; zamknięte |
| **Multicontrol** | bezpośredni | służby celne (też KAS) | sprzęt RTG z oprogramowaniem analizy | obecny w KAS | brak publicznych danych o AI porównującej do wzorca (do potwierdzenia — założenie) |
| **Obecne narzędzie KAS (detektor papierosów)** | bezpośredni (status quo) | operatorzy KAS | wykrywa konkretny towar | działa produkcyjnie | słabe dla małych ilości w konstrukcji pojazdu (zadanie, p. 1) |
| Ręczna ocena operatora (bez AI) | pośredni | KAS | doświadczenie | elastyczność | zmęczenie, czas, brak powtarzalności |
| Akademicki framework wykrywania anomalii na łatkach obrazu (CNN, SPIE) | pośredni | badania | uczenie bez „złych” przykładów | pokazuje, że podejście działa dla cargo | prototyp, nie produkt |
| Otwarte biblioteki anomalii przemysłowych (PatchCore, PaDiM, EfficientAD) | pośredni | przemysł | wykrywanie wad na produkcie | działają offline, darmowe | trenowane na wadach powierzchni, nie na RTG naczep |

## Przegląd podejść do porównywania obrazów i wykrywania anomalii (offline, mała karta)
Wymagania: tylko obrazy czyste do nauki (dane „wzorcowe”), mapa różnic jako zaznaczone obszary, < 1 min na obraz, ~50 MB .bmp, GTX 1050 4 GB.

| Podejście | Jak działa | Offline / mała karta | Zalety | Wady / ryzyko |
|---|---|---|---|---|
| **Różnica pikselowa po dopasowaniu** (rejestracja pary + odjęcie, progi) | porównuje wzorzec z badanym | tak, nawet bez karty | proste, przejrzyste, dobre dla par „przed/po” | wrażliwe na przesunięcie, skalę, szum; wiele fałszywych alarmów |
| **Odjęcie od średniego/„czystego” modelu** (statystyka z wielu czystych obrazów, lokalne odchylenie) | uczy rozkład normalny pikseli/łatek | tak | tanie, wyjaśnialne | słabe przy dużej zmienności naczep |
| **PaDiM** (rozkład cech łatek z sieci pretrenowanej) | model normalnych cech na pozycję | tak; ok. 60 klatek/s w jednym teście, średnia pamięć | szybki, lekki | niższa jakość (obraz AUROC ok. 95% na MVTec) |
| **PatchCore** (pamięć cech łatek, najbliższy sąsiad) | porównuje łatki z bankiem normalnych | tak, ale pamięć GPU rośnie z liczbą obrazów (rzędu 6–9 GB wg zestawień — nie zmierzone u nas) | najwyższa dokładność w benchmarkach (ok. 99% na MVTec) | ciężki; 4 GB wymaga zmniejszenia banku (coreset) i cięcia na kafelki |
| **EfficientAD** (uczeń–nauczyciel + autoenkoder) | uczeń uczy się odtwarzać cechy nauczyciela | tak; ok. 2–5 ms/obraz w publikacji (inne karty) | szybki, lekki, dobry kompromis | wymaga treningu; obrazy 50 MB trzeba kafelkować |
| **Autoenkoder / rekonstrukcja** | błąd odtworzenia = anomalia | tak | proste | rozmywa szczegóły; małe skrytki mogą się „odtworzyć” |
| **Segmentacja nadzorowana (np. U-Net) na „dodatkach”** | uczy się wskazywać obiekty | tak | wprost mapa obiektów | wymaga oznaczonych przykładów; u nas sztuczne dane — ryzyko, że uczy się artefaktów generatora |
| **Detektor obiektów (np. YOLO)** | rysuje ramki na znanych klasach | tak | ramki gotowe do raportu | nie wykrywa nieznanych skrytek; jak obecne narzędzie na papierosy |

Wnioski do przeglądu (rekomendacja robocza, do rozstrzygnięcia przez Szefa/Programistę po wyniku bazowym): zaczynamy od różnicy po dopasowaniu (wynik bazowy) i ≥ 2 hipotez uczonych tylko na czystych obrazach (EfficientAD i PatchCore z coresetem, kafelkowanie), mierzymy FP/FN na zbiorze. Dopiero pomiar na karcie OMENa rozstrzyga — nie zakładamy z publikacji.

## Macierz funkcji
| Zdolność | Nasz produkt (cel) | Nuctech | Rapiscan | Smiths | Obecne narzędzie KAS |
|---|---|---|---|---|---|
| Porównanie z obrazem wzorcowym | tak | częściowo (założenie) | tak (historia) | nie wprost | nie |
| Wykrywanie nieznanych skrytek | tak | częściowo | częściowo | częściowo | nie |
| Zaznaczone miejsca na obrazie | tak | tak | tak | tak | tak |
| Praca offline | tak | zależy od licencji | zależy | zależy | tak |
| Niezależny od producenta skanera | tak | nie | nie | nie | zależy |
| Duże pliki .bmp, partie | tak (cel) | ? | ? | ? | ? |

## Mapa pozycjonowania (2 osie)
Oś X: wykrywa tylko znany towar ↔ wykrywa dowolną różnicę od wzorca. Oś Y: zamknięte w sprzęcie producenta ↔ niezależne, offline.
- Lewy dół: obecne narzędzie KAS (znany towar, związane ze sprzętem).
- Środek: Nuctech, Smiths (wykrywanie zagrożeń, zamknięte).
- Prawy środek: Rapiscan (zmiana względem historii, zamknięte).
- **Prawy górny róg: nasz cel** — różnica od wzorca, niezależne, offline.

## Szanse różnicowania
1. **Różnica od wzorca bez oznaczonych przykładów skrytek** — uczymy się tylko na czystych obrazach; odpowiada na lukę KAS (małe skrytki w konstrukcji).
2. **Działa na własnym sprzęcie, offline, na małej karcie** — wymóg zadania, niedostępny u zamkniętych producentów.
3. **Raport z zaznaczonymi miejscami i priorytetem** — operator widzi, gdzie patrzeć, i potrzebuje mało czasu.
4. **Przetwarzanie dużych obrazów partiami** — skalowalność wymagana w zadaniu.

## Zagrożenia
1. **Fałszywe alarmy** (FP) — operator przestaje ufać; główne kryterium oceny. Reakcja: próg dobrany na obrazach czystych.
2. **Różnica między sztucznym zbiorem a prawdziwym RTG** — wynik na naszych danych może nie przenieść się do KAS. Reakcja: nie obiecywać skuteczności na prawdziwych danych.
3. **Producenci sprzętu dodają AI porównującą** (Rapiscan już ma porównanie z historią). Reakcja: niezależność i offline.
4. **Mała karta (4 GB)** — ograniczy rozmiar modelu i kafelków.

## Rekomendacje
- **Postawić na**: porównanie z wzorcem, offline, niezależność od producenta, czytelny raport.
- **Dogonić**: niski poziom fałszywych alarmów i szybkość (< 1 min na obraz).
- **Zignorować**: certyfikacje lotniskowe i pełną integrację z wieloma skanerami (poza zakresem hackathonu).

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
