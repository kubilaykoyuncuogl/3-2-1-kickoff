"""Tek süreç: index servisi (+ hesaplar) ve oyun sunucusu (/ws).
Çalıştırma: set -a; . ./.env; set +a; .venv/bin/uvicorn server.main:app --host 127.0.0.1 --port 9081
Caddy /ws'yi buraya yönlendirir; HTTP uçları (index, /acct) dış dünyaya açılmaz."""
import asyncio

from server.telemetry import initialize, watch_task

initialize()

from server import index_service, accounts, ws      # yedek içe aktarma yok: eksik dosyada asıl hata görünsün (2026-10-06'da server/game eksikken yanlış modülü suçladı)

app = index_service.app
app.include_router(ws.router)
engine = ws.setup(index_service, accounts)


@app.on_event("startup")
async def _start_engine():
    app.state.engine_task = asyncio.create_task(engine.run())
    watch_task(app.state.engine_task, "engine.run")
