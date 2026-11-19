# 01 — MVP z makiety (ksefbot.pl)

Cel: pierwsza prawdziwa wersja pod ksefbot.pl (aplikacja Coolify `hacknation`), z wynikiem z usługi na karcie OMENa (sieć lokalna), robiąca to, co makieta R3: https://pawelpisarek.github.io/hacknation-proba14/makieta/

Źródła: `docs/spec.md`, `docs/pm/08-historyjki.md`, `docs/decyzje.md` (P1–P37), makieta `docs/makieta/index.html`.

## Decyzje do przeniesienia (każda = zrzut lub test w działającej aplikacji)

| P | co | status |
|---|---|---|
| P3, P13, P14, P21, P22 | „Do kontroli” / „Odrzuć” z powodem z listy, przy pozycji i w powiększeniu | — |
| P7, P10, P12, P18, P19 | lista od najpewniejszego, nazwa = strefa + położenie, opis bez miar, linia „N miejsc · zostało M”, badany obok wzorca, klik pokazuje miejsce na obu | — |
| P8, P9, P16, P24, P28 | tryb bez pary (sam dobiera wzorzec), flaga „wzorzec niepewny — wskaż wzorzec”, pewność ×0,8 (min. 50%), wskazanie ręczne i z pliku | — |
| P15, P17, P23, P29, P30 | rodzaj towaru z listy, pominięte różnice + „Pokaż pominięte”, zlecanie pominiętych, pominięte w zapisie, odmiana | — |
| P27 | pusta naczepa: pewność z wyniku, flaga reguły, na górze listy | — |
| P25, P26 | numery ramek z obwódką 16/22 px, odmiana liczby miejsc, bez czasu analizy na ekranie | — |
| P31 | „Następne miejsce” w powiększeniu | — |
| P32 | zapis kontroli: JSON + PNG z ramkami | — |
| P34 | pusta naczepa: flaga przy każdym miejscu w ładowni, nagłówek „najpierw alarmy z reguły” | — |
| P35 | „Następne miejsce” → następne nierozstrzygnięte, po ostatnim zamyka okno | — |
| P36 | wzorzec z pliku: w zapisie linia „wzorzec: plik <nazwa> (wskazany ręcznie)” | — |
| P37 | niczego z ekranu nie wyrzucamy | — |

## Gotowe, gdy
- https://ksefbot.pl (adres aplikacji) zwraca 200, analizuje prawdziwy obraz z danych przez usługę na karcie OMENa;
- każdy wiersz tabeli ma status „działa” + zrzut `docs/zrzuty/mvp-*.png` albo nazwę testu;
- przeklik ścieżki pokazu (4 pozycje, spec §6) na adresie produkcyjnym: wynik skryptu w meldunku.

## Dopisane po pre-mortem (docs/pm/09)
| wiersz | status |
|---|---|
| R2: test, że usługa na OMENie odpowiada z ksefbot.pl (jeśli nie — tunel), przed resztą | — |
| R1: pierwsze wdrożenie od razu (choćby statyczna strona), żeby ksefbot.pl dawał 200 | — |
| tryb „wynik zapisany”: ksefbot.pl pokazuje ścieżkę pokazu z zapisanego wyniku karty, gdy karta albo sieć nie odpowiada | — |
| R10: obraz demo wybrany i jego prawdziwy wynik spisany (docs/demo-wynik.md) — teksty i pokaz idą za nim | — |
| tryb „wynik zapisany”: zapisane przebiegi zwykły, pusta naczepa, wzorzec z pliku — z polami P29, P32, P36 | — |
| zrzuty docs/zrzuty/mvp-*.png wg listy w docs/pm/09 (warstwa 4) | — |
