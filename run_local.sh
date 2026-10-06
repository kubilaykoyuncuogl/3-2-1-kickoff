#!/usr/bin/env bash
# Yerel geliştirme: Python sunucu (index + hesaplar + oyun, 9081) + Expo web (8081)
# Kullanım: ./run_local.sh          → ikisini başlatır, loglar data/service.log ve data/expo_web.log
#           ./run_local.sh stop     → durdurur (bu komutu tek başına çalıştır)
#           ./run_local.sh export   → web build alır (app/dist)
#           ./run_local.sh server   → yalnızca Python sunucu
set -e
cd "$(dirname "$0")"
case "${1:-}" in
  stop)
    pkill -f "[u]vicorn server.main" || true
    pkill -f "[e]xpo start" || true
    echo "durduruldu"; exit 0;;
  export)
    (cd app && CI=1 npx expo export --platform web | tail -3); du -sh app/dist; exit 0;;
esac
set -a; . ./.env; set +a
pgrep -f "[u]vicorn server.main" >/dev/null || (nohup .venv/bin/uvicorn server.main:app --host 127.0.0.1 --port 9081 > data/service.log 2>&1 &)
for i in $(seq 1 90); do curl -sf localhost:9081/health >/dev/null && break; sleep 1; done
echo "sunucu : http://127.0.0.1:9081/health → $(curl -s localhost:9081/health)   (oyun: ws://127.0.0.1:9081/ws)"
[ "${1:-}" = "server" ] && exit 0
# --clear: Metro kod değişikliğinden sonra eski paketi sunabiliyor
pgrep -f "[e]xpo start" >/dev/null || (cd app && CI=1 nohup npx expo start --web --port 8081 --clear > ../data/expo_web.log 2>&1 &)
echo "web    : http://localhost:8081   (telefonda Expo Go: cd app && npx expo start)"
echo "bot    : .venv/bin/python tools/wsbot.py --bot ali --team galatasaray --guess sneijder"
