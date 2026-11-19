#!/bin/sh
# Jeden przebieg na karcie OMENa: środowisko → dane (raz, w ~/dane) → metody A, A0, B, C.
set -e
sh skrypty/srodowisko_omen.sh
DANE=${DANE:-$HOME/dane/proba14/gen-v2}
if [ ! -f "$DANE/test/opis.json" ]; then python -m anomalie.generator --wyjscie "$DANE" --maly; fi
if [ ! -f "$DANE/pelny/opis.json" ]; then python -m anomalie.generator --wyjscie "$DANE" --pelny; fi
ls -la "$DANE/pelny/badane" | head -3
python skrypty/bazowy.py --dane "$DANE" --wyniki wyniki/bazowy
