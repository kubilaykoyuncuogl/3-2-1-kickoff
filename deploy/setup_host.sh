#!/usr/bin/env bash
# Sunucuda bir kez, root olarak: Ubuntu/Debian. Caddy + Python + kullanıcı + dizinler.
set -e
DOMAIN="${1:?kullanım: setup_host.sh kickoff.example.com}"
apt-get update && apt-get install -y python3 python3-venv curl rsync debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
apt-get update && apt-get install -y caddy
id kickoff >/dev/null 2>&1 || useradd -r -m -d /opt/kickoff -s /usr/sbin/nologin kickoff
mkdir -p /opt/kickoff/{web,bin,server,tools,data/index}
chown -R kickoff:kickoff /opt/kickoff
sed "s/DOMAIN/$DOMAIN/" /opt/kickoff/deploy/Caddyfile > /etc/caddy/Caddyfile
cp /opt/kickoff/deploy/kickoff-*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable kickoff-index kickoff-game caddy
echo "hazır: /opt/kickoff/.env içine KICKOFF_INDEX_KEY ve KICKOFF_DAILY_SALT koy, sonra deploy.sh çalıştır"
