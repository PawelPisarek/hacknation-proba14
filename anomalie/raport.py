"""Raport dla operatora: obraz z ponumerowanymi ramkami (od najpewniejszej), powiększenia
podejrzanych miejsc i jedna linia „ile miejsc do sprawdzenia” (P7, P10 Artura).
Rysowanie gotowych ramek (bez liczenia modelu)."""
from __future__ import annotations

import json
import os

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None


def raport(sciezka_bmp, ramki, oceny, opisy, katalog, szer=1600, maks_powiekszen=6):
    os.makedirs(katalog, exist_ok=True)
    nazwa = os.path.splitext(os.path.basename(sciezka_bmp))[0]
    img = Image.open(sciezka_bmp).convert("L")
    W, H = img.size
    s = szer / W
    podg = img.resize((szer, max(1, round(H * s)))).convert("RGB")
    d = ImageDraw.Draw(podg)
    for i, r in enumerate(ramki, 1):
        x0, y0, x1, y1 = [v * s for v in r]
        d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], outline=(255, 40, 40), width=2)
        d.text((x0, max(0, y0 - 12)), str(i), fill=(255, 40, 40))
    linia = f"Miejsc do sprawdzenia: {len(ramki)}"
    d.text((8, 8), linia, fill=(255, 40, 40))
    podg.save(os.path.join(katalog, f"{nazwa}_raport.png"))
    pow_pliki = []
    for i, r in enumerate(ramki[:maks_powiekszen], 1):
        x0, y0, x1, y1 = r
        m = max(x1 - x0, y1 - y0)
        wyc = img.crop((max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m)))
        sk = 400 / max(wyc.size)
        wyc = wyc.resize((max(1, round(wyc.width * sk)), max(1, round(wyc.height * sk)))).convert("RGB")
        ImageDraw.Draw(wyc).rectangle([(x0 - max(0, x0 - m)) * sk, (y0 - max(0, y0 - m)) * sk,
                                       (x1 - max(0, x0 - m)) * sk, (y1 - max(0, y0 - m)) * sk],
                                      outline=(255, 40, 40), width=2)
        p = os.path.join(katalog, f"{nazwa}_miejsce{i}.png")
        wyc.save(p)
        pow_pliki.append(os.path.basename(p))
    json.dump(dict(obraz=os.path.basename(sciezka_bmp), linia=linia,
                   miejsca=[dict(nr=i, ramka=r, ocena=o, opis=op) for i, (r, o, op) in enumerate(zip(ramki, oceny, opisy), 1)],
                   powiekszenia=pow_pliki), open(os.path.join(katalog, f"{nazwa}_raport.json"), "w"),
              ensure_ascii=False, indent=1)
    return linia
