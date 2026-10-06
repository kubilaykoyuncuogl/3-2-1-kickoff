#!/bin/bash
# İki süreç: Python (index + hesaplar + oyun sunucusu, 127.0.0.1:9081) ve Caddy (:8080). Biri düşerse konteyner çıkar (compose yeniden başlatır).
set -e
: "${KICKOFF_INDEX_KEY:?KICKOFF_INDEX_KEY gerekli}"
[ -f "$KICKOFF_INDEX" ] || { echo "index.enc yok: $KICKOFF_INDEX"; exit 1; }
cd /app
python -m uvicorn server.main:app --host 127.0.0.1 --port 9081 --no-access-log &
for i in $(seq 1 120); do python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:9081/health',timeout=2)" 2>/dev/null && break; sleep 1; done
caddy run --config /etc/caddy/Caddyfile &
wait -n
exit 1
