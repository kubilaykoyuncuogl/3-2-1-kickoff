#!/bin/bash
# Üç süreci başlatır; biri düşerse konteyner çıkar (dış orkestratör yeniden başlatır).
set -e
: "${KICKOFF_INDEX_KEY:?KICKOFF_INDEX_KEY gerekli}"
[ -f "$KICKOFF_INDEX" ] || { echo "index.enc yok: $KICKOFF_INDEX"; exit 1; }
cd /app
python -m uvicorn server.index_service:app --host 127.0.0.1 --port 9081 &
for i in $(seq 1 90); do python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:9081/health',timeout=2)" 2>/dev/null && break; sleep 1; done
./bin/kickoff-server.x86_64 --headless -- --server --port 9080 --index http://127.0.0.1:9081 &
caddy run --config /etc/caddy/Caddyfile &
wait -n
exit 1
