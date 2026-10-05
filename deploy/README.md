# Sunucuya kurulum

Gereken: Linux x86_64 VPS (≥2 GB RAM, index 583 MB belleğe alınır), alan adı A kaydı sunucuya, 80/443 açık, root SSH.

1. Sunucuda: `git clone` ya da `rsync` ile repo `/opt/kickoff` altına (deploy klasörü yeter), sonra `bash /opt/kickoff/deploy/setup_host.sh kickoff.example.com`
2. `/opt/kickoff/.env`: yereldeki `.env` ile aynı iki satır (`KICKOFF_INDEX_KEY`, `KICKOFF_DAILY_SALT`). Düz `index.sqlite` sunucuya gitmez, yalnızca `index.enc`.
3. Yerelden: `./deploy/deploy.sh root@kickoff.example.com`
4. Tarayıcı: `https://kickoff.example.com`. İstemci https altında otomatik `wss://domain/ws` kullanır (Caddy → 9080).

Güncelleme: sadece 3. adım. Loglar: `journalctl -u kickoff-game -f`, `journalctl -u kickoff-index -f`.
