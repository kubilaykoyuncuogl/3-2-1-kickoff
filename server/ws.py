"""WebSocket ucu (/ws): bağlantı başına pid, mesajlar JSON {"t": ...}. Sunucu→istemci zarfları engine.py'de.
Mesajlar bağlantı başına sırayla işlenir (Godot'daki güvenilir-sıralı RPC gibi). IP başına hello/acct oran sınırı."""
import asyncio, itertools, json, time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

try:
    from server.game.engine import Engine
except ImportError:      # doğrudan çalıştırma
    from game.engine import Engine

router = APIRouter()
_ids = itertools.count(1)
_conns: dict[int, WebSocket] = {}
_tasks: set[asyncio.Task] = set()
_ip_rate: dict[str, list[float]] = {}
IP_MAX, IP_WINDOW = 60, 60.0        # hello + acct: IP başına dakikada (okul/ofis NAT'ı arkasında onlarca oyuncu aynı IP'den gelebilir)
MAX_MSG = 4096
engine: Engine | None = None


def _send(pid: int, msg: dict) -> None:
    ws = _conns.get(pid)
    if ws is None: return
    async def go():
        try: await ws.send_text(json.dumps(msg, ensure_ascii=False, separators=(",", ":")))
        except Exception: pass
    t = asyncio.create_task(go()); _tasks.add(t); t.add_done_callback(_tasks.discard)


def setup(index_mod, accounts_mod) -> Engine:
    global engine
    engine = Engine(_send, index_mod, accounts_mod)
    return engine


def _client_ip(ws: WebSocket) -> str:
    fwd = ws.headers.get("x-forwarded-for", "")
    if fwd: return fwd.split(",")[0].strip()
    return ws.client.host if ws.client else "?"


def _ip_allow(ip: str) -> bool:
    now = time.monotonic()
    arr = [t for t in _ip_rate.get(ip, []) if now - t < IP_WINDOW]
    if len(arr) >= IP_MAX: _ip_rate[ip] = arr; return False
    arr.append(now); _ip_rate[ip] = arr; return True


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    pid = next(_ids); _conns[pid] = ws; ip = _client_ip(ws)
    engine.on_connect(pid)
    try:
        while True:
            raw = await ws.receive_text()
            if len(raw) > MAX_MSG: continue
            try: m = json.loads(raw)
            except ValueError: continue
            if not isinstance(m, dict): continue
            if m.get("t") in ("hello", "acct") and not _ip_allow(ip):
                _send(pid, {"t": "err", "key": "err.too_many"}); continue
            try: await engine.handle(pid, m)
            except Exception as e:
                print("[ws] handle error pid=%d t=%s: %r" % (pid, m.get("t"), e), flush=True)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("[ws] connection error pid=%d: %r" % (pid, e), flush=True)
    finally:
        _conns.pop(pid, None)
        engine.on_disconnect(pid)
