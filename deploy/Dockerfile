# Tek konteyner: Caddy (HTTP :8080, web build + /ws proxy) + tek Python süreci (index servisi, hesaplar, oyun sunucusu).
# TLS ve 80/443 dış proxy'de (Cloudron Nginx). Build bağlamı repo kökü: docker build -f deploy/Dockerfile .
# Önce yerelde web build alınmış olmalı: cd app && npx expo export --platform web   (app/dist/ rsync ile sunucuya gider)
FROM caddy:2 AS caddybin

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server/requirements.txt server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt
COPY --from=caddybin /usr/bin/caddy /usr/bin/caddy
COPY server/ server/
COPY tools/normalize.py tools/encrypt_index.py tools/
COPY app/dist/ web/
COPY deploy/Caddyfile.container /etc/caddy/Caddyfile
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# index.enc build'e gömülmez; /app/data/index/index.enc olarak volume ile verilir
ENV KICKOFF_INDEX=/app/data/index/index.enc PORT=8080 HOME=/app
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
