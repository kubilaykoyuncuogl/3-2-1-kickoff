#!/usr/bin/env bash
# Yerel geliştirme: index servisi (9081) + Godot oyun sunucusu (9080) + web build sunucusu (8080)
# Kullanım: ./run_local.sh            → üçünü başlatır, loglar data/*.log
#           ./run_local.sh stop       → durdurur
#           ./run_local.sh export     → sadece Web export alır (build/web)
set -e
cd "$(dirname "$0")"
case "${1:-}" in
  stop)
    pkill -f "uvicorn server.index_service" || true
    pkill -f "while true; do godot" || true
    pkill -f "godot --headless --path game -- --server" || true
    pkill -f "server/serve_web.py" || true
    echo "durduruldu"; exit 0;;
  export)
    godot --headless --path game --export-release "Web" ../build/web/index.html 2>&1 | grep -vE "^$|Godot Engine" | tail -5
    ls -la build/web | head; exit 0;;
esac
set -a; . ./.env; set +a
pgrep -f "uvicorn server.index_service" >/dev/null || (nohup .venv/bin/uvicorn server.index_service:app --host 127.0.0.1 --port 9081 > data/service.log 2>&1 &)
for i in $(seq 1 60); do curl -sf localhost:9081/health >/dev/null && break; sleep 1; done
# oyun sunucusu: düşerse 2 sn sonra yeniden başlar (watchdog)
pgrep -f "godot --headless --path game -- --server" >/dev/null || (nohup bash -c 'while true; do godot --headless --path game -- --server --port 9080 >> data/server.log 2>&1; echo "[watchdog] sunucu çıktı, yeniden başlıyor" >> data/server.log; sleep 2; done' > /dev/null 2>&1 &)
pgrep -f "server/serve_web.py" >/dev/null || (nohup python3 server/serve_web.py 8080 build/web > data/web.log 2>&1 &)
sleep 1
echo "index   : http://127.0.0.1:9081/health → $(curl -s localhost:9081/health)"
echo "oyun    : ws://127.0.0.1:9080"
echo "web     : http://localhost:8080  (aynı makinede iki sekme aç, ikisinde de Online oyna → Ara)"
