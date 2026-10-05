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

import re
INDEX = os.environ.get("KICKOFF_INDEX", "data/index/index.enc")
app = FastAPI(title="kickoff-index")
db: sqlite3.Connection

# ---- kulüp kapsamı (scope) ve tier
BIG5 = {"GB1", "ES1", "IT1", "L1", "FR1"}
TOP_RE = re.compile(r"^[A-Z]{1,4}1[A-Z]?$")          # GB1, TR1, BRA1, MLS1, EC1N…
TOP_EXTRA = {"ARGC", "MEXA", "URUC", "QSL", "CLPD"}   # kodu 1 ile bitmeyen üst ligler
SCOPES = ("all", "top", "big5")
PROGRESSION = [(1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (3, 4), (4, 4)]   # merdiven basamak tipleri
TIER_SIZES = (40, 120, 400)                           # T1, T2, T3 büyüklükleri; T4 gerisi
scope_clubs: dict = {}    # scope -> set(club_id)
tier_of: dict = {}        # scope -> {club_id: tier}
tiers: dict = {}          # scope -> {tier: [club_id...]} (fame sırasıyla)

def club_scope_flags(comp):
    comp = comp or ""
    top = comp in BIG5 or comp in TOP_EXTRA or bool(TOP_RE.match(comp))
    return top, comp in BIG5

def _build_scopes():
    rows = db.execute("SELECT id, competition_id FROM clubs WHERE national=0 AND fame>0 ORDER BY fame DESC").fetchall()
    for sc in SCOPES:
        ids = []
        for cid, comp in rows:
            top, big5 = club_scope_flags(comp)
            if sc == "all" or (sc == "top" and top) or (sc == "big5" and big5): ids.append(cid)
        ids = ids[:3000]                       # çok silik kulüpler merdivene girmesin
        scope_clubs[sc] = set(ids)
        t = {}; by = {1: [], 2: [], 3: [], 4: []}
        n1, n2, n3 = TIER_SIZES
        if len(ids) < 200: n1, n2, n3 = max(10, len(ids) // 5), max(10, len(ids) // 3), len(ids)   # dar kapsam (big5)
        for i, cid in enumerate(ids):
            tier = 1 if i < n1 else 2 if i < n1 + n2 else 3 if i < n1 + n2 + n3 else 4
            t[cid] = tier; by[tier].append(cid)
        tier_of[sc] = t; tiers[sc] = by

def tier_pair_for(step: int, per: int, sc: str):
    a, b = PROGRESSION[min(step // per, len(PROGRESSION) - 1)]
    # boş tier'lara düşme (big5'te T4 yok)
    avail = [k for k in (1, 2, 3, 4) if tiers[sc][k]]
    a = min(a, max(avail)); b = min(b, max(avail))
    return a, b

def pick_pair(rng, sc: str, ta: int, tb: int, used: set, min_n: int, max_n: int = 10**9):
    """ta tier'ından rastgele A, tb tier'ından ortak oyuncusu min_n..max_n olan rastgele B."""
    cand_a = [c for c in tiers[sc][ta] if c not in used]
    rng.shuffle(cand_a)
    tb_set = set(tiers[sc][tb])
    for a in cand_a[:40]:
        rows = db.execute("""SELECT club_b AS other, n FROM pair_counts WHERE club_a=? AND n BETWEEN ? AND ?
                             UNION ALL
                             SELECT club_a, n FROM pair_counts WHERE club_b=? AND n BETWEEN ? AND ?""", (a, min_n, max_n, a, min_n, max_n)).fetchall()
        opts = [(o, n) for o, n in rows if o in tb_set and o not in used and o != a]
        if opts:
            b, n = rng.choice(opts)
            return a, b, n
    return None

@app.on_event("startup")
def _load():
    global db
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.deserialize(decrypt_bytes(INDEX, key_from_env()))   # diske düz kopya yazılmaz
    db.execute("CREATE INDEX IF NOT EXISTS ix_pair_b ON pair_counts(club_b)")   # bellekte; club_b aramaları tam tarama yapmasın
    db.execute("PRAGMA query_only=1")
    _build_scopes()

def fts_prefix(q: str) -> str:
    toks = [t for t in normalize(q).split() if t]
    if not toks: return ""
    return " ".join(f'"{t}"*' for t in toks)

@app.get("/teams/suggest")
def teams_suggest(q: str = Query(min_length=2), limit: int = 8, scope: str = "all"):
    n = normalize(q); sc = scope if scope in SCOPES else "all"
    rows = db.execute("SELECT id, name FROM clubs WHERE national=0 AND (norm LIKE ? OR norm LIKE ?) ORDER BY fame DESC LIMIT 40",
                      (n + "%", "% " + n + "%")).fetchall()
    out = [{"id": i, "name": nm, "in_scope": sc == "all" or i in scope_clubs[sc]} for i, nm in rows]
    out.sort(key=lambda x: not x["in_scope"])
    return out[:limit]

@app.get("/club/{club_id}")
def club(club_id: int, scope: str = "all"):
    row = db.execute("SELECT id, name, competition_id FROM clubs WHERE id=?", (club_id,)).fetchone()
    if not row: raise HTTPException(404)
    sc = scope if scope in SCOPES else "all"
    top, big5 = club_scope_flags(row[2])
    return {"id": row[0], "name": row[1], "competition": row[2], "top": top, "big5": big5,
            "in_scope": sc == "all" or row[0] in scope_clubs[sc], "tier": tier_of["all"].get(row[0], 4)}

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
def ladder(day: str = "", steps: int = 30, seed: str = "", scope: str = "all"):
    """Klasik merdiven: basamak tipi T1×T1 → T1×T2 → T2×T2 → … → T4×T4 (her tip 3 basamak). Kulüp koşuda bir kez."""
    sc = scope if scope in SCOPES else "all"
    rng = _seeded(seed or day, "ladder:" + sc)
    out, used = [], set()
    for i in range(steps):
        ta, tb = tier_pair_for(i, 3, sc)
        min_n = 2 if max(ta, tb) <= 3 else 1
        got = pick_pair(rng, sc, ta, tb, used, min_n) or pick_pair(rng, sc, ta, tb, used, 1) \
              or pick_pair(rng, sc, min(ta, tb), min(ta, tb), used, 1)
        if not got: break
        a, b, n = got; used.update((a, b))
        out.append({"a": a, "b": b, "n": n, "tiers": [ta, tb]})
    names = dict(db.execute(f"SELECT id, name FROM clubs WHERE id IN ({','.join(str(c) for c in used) or '0'})").fetchall())
    for st in out: st["a_name"], st["b_name"] = names[st["a"]], names[st["b"]]
    return {"day": day, "scope": sc, "steps": out}

@app.get("/blitz/pack")
def blitz_pack(day: str = "", n: int = 40, reveal: int = 0, seed: str = "", scope: str = "all"):
    """5 isim: 2 yalnız A, 2 yalnız B, 1 ikisi. Çift tier ilerleyişiyle seçilir; çeldiriciler ≥3 kulüplü ünlü oyunculardan."""
    sc = scope if scope in SCOPES else "all"
    rng = _seeded(seed or day, "blitz:" + sc)
    qs, used = [], set()
    only_sql = """SELECT p.id, p.name FROM player_clubs x JOIN players p ON p.id=x.player_id
                  WHERE x.club_id=? AND p.n_clubs>=3 AND NOT EXISTS(SELECT 1 FROM player_clubs y WHERE y.player_id=x.player_id AND y.club_id=?)
                  ORDER BY p.fame DESC LIMIT 40"""
    tries = 0
    while len(qs) < n and tries < n * 6:
        tries += 1
        ta, tb = tier_pair_for(len(qs), 6, sc)
        got = pick_pair(rng, sc, ta, tb, used, 2, 60) or pick_pair(rng, sc, ta, tb, used, 1, 200)
        if not got: break
        ca, cb, _ = got
        both = db.execute("""SELECT p.id, p.name FROM player_clubs x JOIN player_clubs y ON x.player_id=y.player_id JOIN players p ON p.id=x.player_id
                             WHERE x.club_id=? AND y.club_id=? AND p.n_clubs>=3 ORDER BY p.fame DESC LIMIT 20""", (ca, cb)).fetchall()
        oa, ob = db.execute(only_sql, (ca, cb)).fetchall(), db.execute(only_sql, (cb, ca)).fetchall()
        if not both or len(oa) < 2 or len(ob) < 2:
            used.update((ca, cb)); continue
        used.update((ca, cb))
        ans = rng.choice(both); opts = [ans] + rng.sample(oa, 2) + rng.sample(ob, 2); rng.shuffle(opts)
        qid = f"{seed or day}-{len(qs)}"
        qs.append({"id": qid, "a": ca, "b": cb, "options": [o[1] for o in opts], "tiers": [ta, tb],
                   "answer_hash": hashlib.sha256(f"{qid}:{ans[0]}".encode()).hexdigest(), "_answer_id": ans[0], "_answer": opts.index(ans)})
    names = dict(db.execute(f"SELECT id, name FROM clubs WHERE id IN ({','.join(str(c) for c in used) or '0'})").fetchall())
    for q in qs: q["a_name"], q["b_name"] = names[q["a"]], names[q["b"]]
    # reveal=1 yalnızca oyun sunucusu için (localhost); cevap indeksi istemciye asla iletilmez
    return {"day": day, "scope": sc, "questions": [{k: v for k, v in q.items() if not k.startswith("_") or (reveal and k == "_answer")} for q in qs]}

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
