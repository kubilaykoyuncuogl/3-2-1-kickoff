"""Index servisi: şifreli index'i belleğe çözer, oyun sunucusuna (Godot headless) localhost üzerinden HTTP ile cevap verir.

Oyuncu→kulüp ilişkisi hiçbir uç noktadan toplu olarak dışarı çıkmaz:
  - /teams/suggest, /players/suggest   yalnızca ad listesi (prefix, en çok 8 sonuç)
  - /check                              bir isim + iki kulüp → doğru/yanlış (sunucu-sunucu; istemciye açılmaz)
  - /pair/answers                       tur sonu "olası cevaplar" (yalnızca tur bittikten sonra çağrılır)
  - /ladder, /blitz/pack                tek oyunculu paketler (cevap SHA-256 hash'li)
Başlatma:
  KICKOFF_INDEX_KEY=... uvicorn server.index_service:app --host 127.0.0.1 --port 9081
"""
import hashlib, os, random, sqlite3, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from fastapi import FastAPI, HTTPException, Query
from encrypt_index import decrypt_bytes, key_from_env
from normalize import normalize

INDEX = os.environ.get("KICKOFF_INDEX", "data/index/index.enc")
app = FastAPI(title="kickoff-index")
db: sqlite3.Connection

@app.on_event("startup")
def _load():
    global db
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.deserialize(decrypt_bytes(INDEX, key_from_env()))   # diske düz kopya yazılmaz
    db.execute("PRAGMA query_only=1")

def fts_prefix(q: str) -> str:
    toks = [t for t in normalize(q).split() if t]
    if not toks: return ""
    return " ".join(f'"{t}"*' for t in toks)

@app.get("/teams/suggest")
def teams_suggest(q: str = Query(min_length=2), limit: int = 8):
    n = normalize(q)
    rows = db.execute("SELECT id, name FROM clubs WHERE national=0 AND (norm LIKE ? OR norm LIKE ?) ORDER BY fame DESC LIMIT ?",
                      (n + "%", "% " + n + "%", limit)).fetchall()
    return [{"id": i, "name": nm} for i, nm in rows]

@app.get("/players/suggest")
def players_suggest(q: str = Query(min_length=2), limit: int = 8):
    m = fts_prefix(q)
    if not m: return []
    rows = db.execute("""SELECT p.id, p.name, p.birth_year FROM names n JOIN players p ON p.id = n.player_id
                         WHERE names MATCH ? ORDER BY p.fame DESC LIMIT ?""", (m, limit)).fetchall()
    return [{"id": i, "name": nm, "born": by} for i, nm, by in rows]

@app.get("/check")
def check(player_id: int, club_a: int, club_b: int):
    ok = db.execute("SELECT 1 FROM player_clubs x JOIN player_clubs y ON x.player_id=y.player_id WHERE x.player_id=? AND x.club_id=? AND y.club_id=?",
                    (player_id, club_a, club_b)).fetchone() is not None
    return {"ok": ok}

@app.get("/pair/answers")
def pair_answers(club_a: int, club_b: int, limit: int = 12):
    rows = db.execute("""SELECT p.name FROM player_clubs x JOIN player_clubs y ON x.player_id=y.player_id JOIN players p ON p.id=x.player_id
                         WHERE x.club_id=? AND y.club_id=? ORDER BY p.fame DESC LIMIT ?""", (club_a, club_b, limit)).fetchall()
    total = db.execute("SELECT n FROM pair_counts WHERE club_a=? AND club_b=?", (min(club_a, club_b), max(club_a, club_b))).fetchone()
    return {"names": [r[0] for r in rows], "total": total[0] if total else 0}

def _seeded(day: str, salt: str) -> random.Random:
    return random.Random(hashlib.sha256(f"{day}:{salt}:{os.environ.get('KICKOFF_DAILY_SALT','')}".encode()).digest())

@app.get("/ladder")
def ladder(day: str, steps: int = 30):
    """Klasik merdiven: basamak zorluğu = kesişim büyüklüğü ↓ ve kulüp ünü ↓. Aynı gün herkese aynı."""
    rng = _seeded(day, "ladder")
    tiers = [(15, 10**9), (8, 14), (4, 7), (2, 3), (1, 1)]           # (min n, max n) kesişim
    out, used = [], set()
    per = max(1, steps // len(tiers))
    for lo, hi in tiers:
        cands = db.execute("""SELECT p.club_a, p.club_b, p.n FROM pair_counts p JOIN clubs a ON a.id=p.club_a JOIN clubs b ON b.id=p.club_b
                              WHERE p.n BETWEEN ? AND ? AND a.national=0 AND b.national=0 ORDER BY (a.fame+b.fame) DESC LIMIT 400""", (lo, hi)).fetchall()
        rng.shuffle(cands)
        for ca, cb, n in cands:
            if ca in used or cb in used: continue
            used.update((ca, cb)); out.append({"a": ca, "b": cb, "n": n})
            if len(out) % per == 0: break
    names = dict(db.execute(f"SELECT id, name FROM clubs WHERE id IN ({','.join(str(c) for c in used)})").fetchall())
    for s in out: s["a_name"], s["b_name"] = names[s["a"]], names[s["b"]]
    return {"day": day, "steps": out}

@app.get("/blitz/pack")
def blitz_pack(day: str, n: int = 60):
    """5 isim: 2 yalnız A, 2 yalnız B, 1 ikisi. Çeldiriciler ≥3 kulüplü, ünlü oyunculardan; cevap hash olarak gider."""
    rng = _seeded(day, "blitz")
    pairs = db.execute("""SELECT p.club_a, p.club_b FROM pair_counts p JOIN clubs a ON a.id=p.club_a JOIN clubs b ON b.id=p.club_b
                          WHERE p.n BETWEEN 2 AND 40 AND a.national=0 AND b.national=0 ORDER BY (a.fame+b.fame) DESC LIMIT 3000""").fetchall()
    rng.shuffle(pairs); qs = []
    for ca, cb in pairs:
        both = db.execute("""SELECT p.id, p.name FROM player_clubs x JOIN player_clubs y ON x.player_id=y.player_id JOIN players p ON p.id=x.player_id
                             WHERE x.club_id=? AND y.club_id=? AND p.n_clubs>=3 ORDER BY p.fame DESC LIMIT 20""", (ca, cb)).fetchall()
        only = lambda c, o: db.execute("""SELECT p.id, p.name FROM player_clubs x JOIN players p ON p.id=x.player_id
                             WHERE x.club_id=? AND p.n_clubs>=3 AND NOT EXISTS(SELECT 1 FROM player_clubs y WHERE y.player_id=x.player_id AND y.club_id=?)
                             ORDER BY p.fame DESC LIMIT 40""", (c, o)).fetchall()
        oa, ob = only(ca, cb), only(cb, ca)
        if not both or len(oa) < 2 or len(ob) < 2: continue
        ans = rng.choice(both); opts = [ans] + rng.sample(oa, 2) + rng.sample(ob, 2); rng.shuffle(opts)
        qid = f"{day}-{len(qs)}"
        qs.append({"id": qid, "a": ca, "b": cb, "options": [o[1] for o in opts],
                   "answer_hash": hashlib.sha256(f"{qid}:{ans[0]}".encode()).hexdigest(), "_answer_id": ans[0]})
        if len(qs) >= n: break
    names = dict(db.execute("SELECT id, name FROM clubs").fetchall())
    for q in qs: q["a_name"], q["b_name"] = names[q["a"]], names[q["b"]]
    return {"day": day, "questions": [{k: v for k, v in q.items() if not k.startswith("_")} for q in qs]}

@app.get("/player/{player_id}/career")
def career(player_id: int):
    """Kariyer sırası / kiralık-satış modları için (yalnızca oyun sunucusu çağırır)."""
    rows = db.execute("""SELECT s.seq, c.name, s.date, s.kind, s.fee, s.mv, s.age FROM stints s JOIN clubs c ON c.id=s.club_id
                         WHERE s.player_id=? ORDER BY s.seq""", (player_id,)).fetchall()
    if not rows: raise HTTPException(404)
    return [{"seq": a, "club": b, "date": c, "kind": d, "fee": e, "mv": f, "age": g} for a, b, c, d, e, f, g in rows]

@app.get("/health")
def health():
    return {"players": db.execute("SELECT COUNT(*) FROM players").fetchone()[0]}
