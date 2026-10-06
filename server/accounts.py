"""Hesaplar: kalıcı SQLite (KICKOFF_STATE, varsayılan data/state/kickoff.sqlite). Yalnızca oyun sunucusu çağırır (localhost).

Kavramlar
  kullanıcı : misafir (linked_at boş) ya da hesap (linked_at dolu). Elo, maç sayısı ve mod başına en iyi skor kullanıcıya bağlıdır.
  cihaz     : istemcinin gizli kimliği → bir kullanıcı. Bir hesaba birden çok cihaz bağlanabilir.
  kimlik    : (sağlayıcı, özne) → kullanıcı. Google / Apple girişi buraya yazılacak; `verified` o zaman 1 olur. (yapılacak, bkz. docs/TODO.md)

Akışlar
  /acct/create     misafir → hesap. Takma ad hesaplar arasında benzersiz olmalı. Kurtarma kodu bir kez döner (özeti saklanır).
  /acct/link_code  hesaplı cihaz 6 haneli, 10 dk geçerli, tek kullanımlık kod alır …
  /acct/link       … başka cihaz bu kodla aynı hesaba bağlanır.
  /acct/recover    takma ad + kurtarma koduyla bağlanma (cihaz kaybı).
  /acct/logout     cihazı hesaptan ayırır (cihaz yeni bir misafir olur).
  /acct/delete     hesabı ve tüm verisini siler.
"""
import hashlib, os, pathlib, random, secrets, sqlite3, sys, threading, time
from fastapi import APIRouter, Body
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from normalize import normalize

router = APIRouter(prefix="/acct")
PATH = pathlib.Path(os.environ.get("KICKOFF_STATE", "data/state/kickoff.sqlite"))
SALT = os.environ.get("KICKOFF_DAILY_SALT", "kickoff")
LINK_TTL = 600; MAX_TRIES = 8; TRY_WINDOW = 600
lock = threading.Lock()
_db = None
link_codes: dict = {}      # kod -> (user_id, son_kullanma)
tries: dict = {}           # cihaz -> [zaman]
_words = [w for w in (pathlib.Path(__file__).with_name("words.txt").read_text().split() if pathlib.Path(__file__).with_name("words.txt").exists() else []) if w.isalpha()] or ["zidane", "pirlo", "xavi", "henry"]

def db() -> sqlite3.Connection:
    global _db
    if _db is None:
        PATH.parent.mkdir(parents=True, exist_ok=True)
        _db = sqlite3.connect(PATH, check_same_thread=False)
        _db.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, nick TEXT NOT NULL DEFAULT '', nick_norm TEXT NOT NULL DEFAULT '',
            elo INTEGER NOT NULL DEFAULT 1000, games INTEGER NOT NULL DEFAULT 0, linked_at INTEGER, verified INTEGER NOT NULL DEFAULT 0,
            recovery_hash TEXT, created_at INTEGER NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_nick ON users(nick_norm) WHERE linked_at IS NOT NULL;
        CREATE TABLE IF NOT EXISTS devices(device TEXT PRIMARY KEY, user_id INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS ix_devices_user ON devices(user_id);
        CREATE TABLE IF NOT EXISTS identities(provider TEXT NOT NULL, subject TEXT NOT NULL, user_id INTEGER NOT NULL, PRIMARY KEY(provider, subject));
        CREATE TABLE IF NOT EXISTS bests(user_id INTEGER NOT NULL, mode TEXT NOT NULL, score INTEGER NOT NULL, PRIMARY KEY(user_id, mode));
        CREATE TABLE IF NOT EXISTS weekly_side(slug TEXT NOT NULL, side TEXT NOT NULL, total INTEGER NOT NULL DEFAULT 0, runs INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(slug, side));
        CREATE TABLE IF NOT EXISTS weekly_user(slug TEXT NOT NULL, device TEXT NOT NULL, side TEXT NOT NULL, points INTEGER NOT NULL DEFAULT 0, runs INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(slug, device));
        """)
    return _db

def _h(code: str) -> str:
    return hashlib.sha256((SALT + ":" + code).encode()).hexdigest()

def _clean_code(s: str) -> str:
    return "-".join(normalize(s.replace("-", " ")).split())

def _clean_nick(s: str) -> str:
    return " ".join(str(s or "").split())[:16]

def _user(device: str, create=True):
    d = db(); row = d.execute("SELECT u.* FROM devices x JOIN users u ON u.id = x.user_id WHERE x.device = ?", (device,)).fetchone()
    if row or not create: return row
    cur = d.execute("INSERT INTO users(created_at) VALUES(?)", (int(time.time()),))
    d.execute("INSERT OR REPLACE INTO devices VALUES(?, ?)", (device, cur.lastrowid)); d.commit()
    return d.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()

COLS = ("id", "nick", "nick_norm", "elo", "games", "linked_at", "verified", "recovery_hash", "created_at")
def _profile(row, **extra) -> dict:
    u = dict(zip(COLS, row))
    bests = dict(db().execute("SELECT mode, score FROM bests WHERE user_id = ?", (u["id"],)).fetchall())
    devices = db().execute("SELECT COUNT(*) FROM devices WHERE user_id = ?", (u["id"],)).fetchone()[0]
    providers = [r[0] for r in db().execute("SELECT provider FROM identities WHERE user_id = ?", (u["id"],))]
    return {"ok": True, "user_id": u["id"], "nick": u["nick"], "elo": u["elo"], "games": u["games"], "linked": u["linked_at"] is not None,
            "verified": bool(u["verified"]), "bests": bests, "devices": devices, "providers": providers, **extra}

def _err(code: str, device: str = "") -> dict:
    out = {"ok": False, "error": code}
    if device:
        row = _user(device, create=False)
        if row: out["profile"] = _profile(row)
    return out

# Bot rakiplerin görünen adları: gerçek oyuncular hesap adı olarak alamaz (yoksa botla karışır)
_bot_names = pathlib.Path(__file__).with_name("bot_names.txt")
RESERVED = {normalize(w) for w in (_bot_names.read_text().splitlines() if _bot_names.exists() else []) if w.strip() and not w.startswith("#")}

def nick_registered(norm: str) -> bool:
    """Bu ad bir hesaba ait mi? (bot adı seçerken sorulur)"""
    with lock:
        return db().execute("SELECT 1 FROM users WHERE nick_norm = ? AND linked_at IS NOT NULL", (norm,)).fetchone() is not None

def _nick_taken(norm: str, except_id: int) -> bool:
    if norm in RESERVED: return True
    return db().execute("SELECT 1 FROM users WHERE nick_norm = ? AND linked_at IS NOT NULL AND id != ?", (norm, except_id)).fetchone() is not None

def _too_many(device: str) -> bool:
    now = time.time(); arr = [t for t in tries.get(device, []) if now - t < TRY_WINDOW]
    arr.append(now); tries[device] = arr
    return len(arr) > MAX_TRIES

def _attach(device: str, target_id: int):
    """Cihazı hedef hesaba taşır. Cihazın eski misafir kullanıcısının en iyi skorları hesaba aktarılır, sahipsiz misafir silinir."""
    d = db(); old = _user(device, create=False)
    if old and old[0] != target_id:
        for mode, score in d.execute("SELECT mode, score FROM bests WHERE user_id = ?", (old[0],)).fetchall():
            d.execute("INSERT INTO bests VALUES(?,?,?) ON CONFLICT(user_id, mode) DO UPDATE SET score = MAX(score, excluded.score)", (target_id, mode, score))
    d.execute("INSERT OR REPLACE INTO devices VALUES(?, ?)", (device, target_id))
    if old and old[0] != target_id and old[5] is None and d.execute("SELECT 1 FROM devices WHERE user_id = ?", (old[0],)).fetchone() is None:
        d.execute("DELETE FROM bests WHERE user_id = ?", (old[0],)); d.execute("DELETE FROM users WHERE id = ?", (old[0],))
    d.commit()
    return d.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()

@router.post("/hello")
def hello(p: dict = Body(...)):
    """Cihaz bağlandı. Takma ad verilmişse günceller; hesaplıda ad başkasına aitse eski ad kalır ve hata döner."""
    device = str(p.get("device") or ""); nick = _clean_nick(p.get("nick"))
    if not device: return {"ok": False, "error": "no_device"}
    with lock:
        u = _user(device); err = None
        if nick and nick != u[1]:
            norm = normalize(nick)
            if u[5] is not None and (len(norm) < 3 or _nick_taken(norm, u[0])): err = "nick_taken" if len(norm) >= 3 else "nick_short"
            else:
                db().execute("UPDATE users SET nick = ?, nick_norm = ? WHERE id = ?", (nick, norm, u[0])); db().commit(); u = _user(device)
        return _profile(u, **({"error": err} if err else {}))

@router.post("/create")
def create(p: dict = Body(...)):
    device = str(p.get("device") or "")
    with lock:
        u = _user(device)
        if u[5] is not None: return _err("already_linked", device)
        norm = normalize(u[1])
        if len(norm) < 3: return _err("nick_short", device)
        if _nick_taken(norm, u[0]): return _err("nick_taken", device)
        rng = random.SystemRandom()
        code = "-".join(rng.sample(_words, 3)) + "-%04d" % rng.randrange(10000)
        db().execute("UPDATE users SET linked_at = ?, nick_norm = ?, recovery_hash = ? WHERE id = ?", (int(time.time()), norm, _h(code), u[0])); db().commit()
        return _profile(_user(device), recovery=code)

@router.post("/link_code")
def link_code(p: dict = Body(...)):
    device = str(p.get("device") or "")
    with lock:
        u = _user(device)
        if u[5] is None: return _err("not_linked", device)
        now = time.time()
        for k in [k for k, v in link_codes.items() if v[1] < now or v[0] == u[0]]: link_codes.pop(k, None)
        while True:
            code = "%06d" % secrets.randbelow(1000000)
            if code not in link_codes: break
        link_codes[code] = (u[0], now + LINK_TTL)
        return _profile(u, code=code, ttl=LINK_TTL)

@router.post("/link")
def link(p: dict = Body(...)):
    device = str(p.get("device") or ""); code = "".join(ch for ch in str(p.get("code") or "") if ch.isdigit())
    with lock:
        if _too_many(device): return _err("too_many", device)
        ent = link_codes.get(code)
        if not ent or ent[1] < time.time(): return _err("bad_code", device)
        link_codes.pop(code, None)
        return _profile(_attach(device, ent[0]))

@router.post("/recover")
def recover(p: dict = Body(...)):
    device = str(p.get("device") or ""); norm = normalize(str(p.get("nick") or "")); code = _clean_code(str(p.get("recovery") or ""))
    with lock:
        if _too_many(device): return _err("too_many", device)
        row = db().execute("SELECT * FROM users WHERE nick_norm = ? AND linked_at IS NOT NULL", (norm,)).fetchone()
        if not row or not row[7] or not secrets.compare_digest(row[7], _h(code)): return _err("bad_recovery", device)
        return _profile(_attach(device, row[0]))

@router.post("/logout")
def logout(p: dict = Body(...)):
    """Cihaz hesaptan ayrılır; aynı takma adla yeni bir misafir olur. Hesap ve diğer cihazları durur."""
    device = str(p.get("device") or "")
    with lock:
        u = _user(device)
        if u[5] is None: return _profile(u)
        d = db(); d.execute("DELETE FROM devices WHERE device = ?", (device,))
        cur = d.execute("INSERT INTO users(nick, nick_norm, created_at) VALUES(?,?,?)", (u[1], u[2], int(time.time())))
        d.execute("INSERT INTO devices VALUES(?, ?)", (device, cur.lastrowid)); d.commit()
        return _profile(_user(device))

@router.post("/delete")
def delete(p: dict = Body(...)):
    """Kullanıcıyı ve tüm verisini siler (mağaza gereği). Bağlı tüm cihazlar bir sonraki bağlantıda sıfır misafir olur."""
    device = str(p.get("device") or "")
    with lock:
        u = _user(device); d = db()
        for t in ("bests", "identities"): d.execute(f"DELETE FROM {t} WHERE user_id = ?", (u[0],))
        d.execute("DELETE FROM devices WHERE user_id = ?", (u[0],)); d.execute("DELETE FROM users WHERE id = ?", (u[0],)); d.commit()
        for k in [k for k, v in link_codes.items() if v[0] == u[0]]: link_codes.pop(k, None)
        return _profile(_user(device))

@router.post("/save")
def save(p: dict = Body(...)):
    """Maç sonrası Elo ve maç sayısı (oyun sunucusu hesaplar)."""
    with lock:
        u = _user(str(p.get("device") or ""))
        db().execute("UPDATE users SET elo = ?, games = ? WHERE id = ?", (int(p.get("elo", u[3])), int(p.get("games", u[4])), u[0])); db().commit()
        return {"ok": True}

@router.post("/best")
def best(p: dict = Body(...)):
    """Tek oyunculu koşu bitti: mod başına en iyi skor (yalnızca yükselir)."""
    with lock:
        u = _user(str(p.get("device") or "")); mode = str(p.get("mode") or "")[:16]; score = int(p.get("score") or 0)
        db().execute("INSERT INTO bests VALUES(?,?,?) ON CONFLICT(user_id, mode) DO UPDATE SET score = MAX(score, excluded.score)", (u[0], mode, score)); db().commit()
        return {"ok": True, "best": db().execute("SELECT score FROM bests WHERE user_id = ? AND mode = ?", (u[0], mode)).fetchone()[0]}

@router.post("/import")
def import_legacy(p: dict = Body(...)):
    """Eski accounts.json (cihaz → {elo, games}) bir kez içe alınır."""
    n = 0
    with lock:
        for device, acc in (p.get("accounts") or {}).items():
            u = _user(str(device))
            if u[4] == 0:
                db().execute("UPDATE users SET elo = ?, games = ? WHERE id = ?", (int(acc.get("elo", 1000)), int(acc.get("games", 0)), u[0])); n += 1
        db().commit()
    return {"ok": True, "imported": n}

# ---- haftanın maçı: taraf toplamları (oyun sunucusu doğrudan çağırır; HTTP ucu yok)
def weekly_state(slug: str, device: str = "") -> dict:
    """İki tarafın toplam puanı ve koşu sayısı; cihaz taraf seçtiyse onun tarafı ve katkısı."""
    with lock:
        d = db()
        totals = {"a": {"total": 0, "runs": 0}, "b": {"total": 0, "runs": 0}}
        for side, total, runs in d.execute("SELECT side, total, runs FROM weekly_side WHERE slug = ?", (slug,)):
            if side in totals: totals[side] = {"total": total, "runs": runs}
        me = d.execute("SELECT side, points, runs FROM weekly_user WHERE slug = ? AND device = ?", (slug, device)).fetchone() if device else None
        return {"totals": totals, "me": {"side": me[0], "points": me[1], "runs": me[2]} if me else None}

def weekly_add(slug: str, device: str, side: str, points: int) -> None:
    """Koşu puanını tarafın toplamına ekler. Cihazın tarafı ilk koşuda sabitlenir; sonraki koşular hep o tarafa yazılır."""
    if side not in ("a", "b") or points <= 0 or not device: return
    with lock:
        d = db()
        row = d.execute("SELECT side FROM weekly_user WHERE slug = ? AND device = ?", (slug, device)).fetchone()
        if row: side = row[0]
        d.execute("INSERT INTO weekly_user VALUES(?,?,?,?,1) ON CONFLICT(slug, device) DO UPDATE SET points = points + excluded.points, runs = runs + 1", (slug, device, side, points))
        d.execute("INSERT INTO weekly_side VALUES(?,?,?,1) ON CONFLICT(slug, side) DO UPDATE SET total = total + excluded.total, runs = runs + 1", (slug, side, points))
        d.commit()
