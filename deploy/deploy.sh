#!/usr/bin/env bash
# Yerelden: ./deploy/deploy.sh user@host  — web build, sunucu binary'si, index.enc, python kodu; servisleri yeniden başlatır.
set -e
HOST="${1:?kullanım: deploy.sh user@host}"
cd "$(dirname "$0")/.."
godot --headless --path game --export-release "Web" ../build/web/index.html >/dev/null 2>&1
godot --headless --path game --export-release "Linux Server" ../build/server/kickoff-server.x86_64 >/dev/null 2>&1
rsync -az --delete build/web/ "$HOST:/opt/kickoff/web/"
rsync -az build/server/ "$HOST:/opt/kickoff/bin/"
rsync -az server/ tools/ deploy/ "$HOST:/opt/kickoff/" --relative
rsync -az --progress data/index/index.enc "$HOST:/opt/kickoff/data/index/index.enc"
ssh "$HOST" 'cd /opt/kickoff && [ -d .venv ] || python3 -m venv .venv; .venv/bin/pip install -q -r server/requirements.txt; chmod +x bin/kickoff-server.x86_64; chown -R kickoff:kickoff /opt/kickoff; systemctl restart kickoff-index kickoff-game; sleep 3; systemctl --no-pager --lines=3 status kickoff-index kickoff-game | grep -E "Active|kickoff"'
echo "tamam → https://<domain>"
