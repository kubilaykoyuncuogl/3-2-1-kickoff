#!/usr/bin/env bash
# Expo web ekran görüntüleri (başsız Chrome, 400x880): tools/expo_shots.sh [light|dark] [tr|en]  → /tmp/kickoff-shots/expo/*.png
# Önce `cd app && npx expo start --web --port 8081 --clear` çalışıyor olmalı (kod değişince --clear ile yeniden başlat: Metro eski paketi sunuyor).
# Sayfalar ?nick=…&theme=…&lang=… ile ayarları alır (yalnızca geliştirme, bkz. store.ts load).
TH=${1:-light}; LG=${2:-tr}; OUT=/tmp/kickoff-shots/expo; mkdir -p "$OUT"
shot() { local prof; prof=$(mktemp -d)
  timeout 90 google-chrome --headless=new --no-sandbox --disable-gpu --user-data-dir="$prof" --window-size=400,880 --hide-scrollbars \
    --virtual-time-budget=20000 --screenshot="$OUT/$1.png" "http://localhost:8081$2?nick=kubi&theme=$TH&lang=$LG${3:-}" >/dev/null 2>&1
  rm -rf "$prof"; echo "$1"; }
shot 01_menu /
shot 02_nickname /nickname
shot 07_settings /settings
shot 08_account /account
shot 09_howto /howto
ls "$OUT" | wc -l
