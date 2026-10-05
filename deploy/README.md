# Sunucuya kurulum

Gereken: Linux x86_64 VPS (≥2 GB RAM, index 583 MB belleğe alınır), alan adı A kaydı sunucuya, 80/443 açık, root SSH.

1. Sunucuda: `git clone` ya da `rsync` ile repo `/opt/kickoff` altına (deploy klasörü yeter), sonra `bash /opt/kickoff/deploy/setup_host.sh kickoff.example.com`
2. `/opt/kickoff/.env`: yereldeki `.env` ile aynı iki satır (`KICKOFF_INDEX_KEY`, `KICKOFF_DAILY_SALT`). Düz `index.sqlite` sunucuya gitmez, yalnızca `index.enc`.
3. Yerelden: `./deploy/deploy.sh root@kickoff.example.com`
4. Tarayıcı: `https://kickoff.example.com`. İstemci https altında otomatik `wss://domain/ws` kullanır (Caddy → 9080).

Güncelleme: sadece 3. adım. Loglar: `journalctl -u kickoff-game -f`, `journalctl -u kickoff-index -f`.

## Cloudron / dış proxy'li sunucu (tek konteyner)
80/443 başka bir Nginx'teyse Caddy'yi kurma; tek konteyner kullan:
```
# yerelde: build/web ve build/server güncel olmalı (run_local.sh export + Linux Server export)
rsync -az --exclude .venv --exclude all_data --exclude 'data/raw' --exclude 'data/index/index.sqlite' ./ root@SUNUCU:/opt/kickoff/
ssh root@SUNUCU 'cd /opt/kickoff && docker compose -f deploy/compose.yaml up -d --build'
```
Konteyner 127.0.0.1:8080'de HTTP verir (statik + `/ws`). Dış proxy `kickoff.<alanadi>` → `127.0.0.1:8080`, WebSocket upgrade açık (`/ws`). Bellek ~650 MB.
`.env` sunucuda `/opt/kickoff/.env` (anahtar + tuz), `index.enc` volume ile bağlı. Yerel test: `docker run --env-file .env -p 8090:8080 -v $PWD/data/index/index.enc:/app/data/index/index.enc:ro kickoff:latest`.
