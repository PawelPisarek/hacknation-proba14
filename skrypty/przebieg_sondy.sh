#!/bin/sh
# Sondy na karcie OMENa: środowisko → dane gen-v3 (raz, w ~/dane) → przebieg 1 (kalibracja 60, scalanie, S1, S2) → S3.
# PRZEBIEGI="p1 s3" (domyślnie oba, po kolei).
set -e
sh skrypty/srodowisko_omen.sh
DANE=${DANE:-$HOME/dane/proba14/gen-v3}
G="python -m anomalie.generator --wyjscie $DANE"
[ -f "$DANE/kalib60/opis.json" ] || $G --maly
[ -f "$DANE/towar/opis.json" ] || $G --kontrolne
[ -f "$DANE/pelny/opis.json" ] || $G --pelny
[ -f "$DANE/kalib_pelny/opis.json" ] || $G --km
df -h ~ | tail -1
du -sh "$DANE"
for p in ${PRZEBIEGI:-p1 s3}; do
  python skrypty/sondy.py --dane "$DANE" --przebieg "$p" --wyniki wyniki/sondy
done
