#!/usr/bin/env bash
# Ekran görüntüleri: ./shots.sh [light|dark] [tr|en]  → /tmp/kickoff-shots/<tema>/*.png ve sheet-*.png
cd "$(dirname "$0")"; TH=${1:-light}; LG=${2:-tr}; OUT=/tmp/kickoff-shots/$TH
rm -rf "$OUT"; timeout 120 godot --path game --resolution 400x880 --position 40,40 -- --shots "$OUT" --theme "$TH" --lang "$LG" 2>&1 | grep -E "SCRIPT ERROR|ERROR:" | head -8
python3 tools/sheet.py "$OUT" "$OUT/sheet-menus.png" 7 01_ 02_ 03_ 04_ 05_ 06_ 07_ >/dev/null
python3 tools/sheet.py "$OUT" "$OUT/sheet-account.png" 6 08 09 >/dev/null
python3 tools/sheet.py "$OUT" "$OUT/sheet-match.png" 7 10_ 11_ 12_ 13_ 14_ 15_ 16_ >/dev/null
python3 tools/sheet.py "$OUT" "$OUT/sheet-single.png" 7 20_ 21_ 22_ 23_ 24_ 25_ 26_ >/dev/null
ls "$OUT" | wc -l
