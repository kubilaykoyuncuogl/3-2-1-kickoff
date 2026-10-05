"""Index servisi: şifreli index'i belleğe çözer, oyun sunucusuna (Godot headless) localhost üzerinden HTTP ile cevap verir.

Oyuncu→kulüp ilişkisi hiçbir uç noktadan toplu olarak dışarı çıkmaz:
  - /teams/suggest, /players/suggest   yalnızca ad listesi (prefix, en çok 8 sonuç)
  - /check                              bir isim + iki kulüp → doğru/yanlış (sunucu-sunucu; istemciye açılmaz)
  - /pair/answers                       tur sonu "olası cevaplar" (yalnızca tur bittikten sonra çağrılır)
  - /ladder, /blitz/pack                tek oyunculu paketler (cevap SHA-256 hash'li)
Başlatma:
  KICKOFF_INDEX_KEY=... uvicorn server.index_service:app --host 127.0.0.1 --port 9081
"""
import hashlib, os, random, sqlite3, sys, pathlib, threading, time, functools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from fastapi import FastAPI, HTTPException, Query
from encrypt_index import decrypt_bytes, key_from_env
from normalize import normalize

import re
INDEX = os.environ.get("KICKOFF_INDEX", "data/index/index.enc")
app = FastAPI(title="kickoff-index")
try:
    from server import accounts as _accounts
except ImportError:      # doğrudan çalıştırma
    import accounts as _accounts
app.include_router(_accounts.router)
db: sqlite3.Connection

# ---- kulüp kapsamı (scope) ve tier
BIG5 = {"GB1", "ES1", "IT1", "L1", "FR1"}
TOP_RE = re.compile(r"^[A-Z]{1,4}1[A-Z]?$")          # GB1, TR1, BRA1, MLS1, EC1N…
TOP_EXTRA = {"ARGC", "MEXA", "URUC", "QSL", "CLPD"}   # kodu 1 ile bitmeyen üst ligler
SCOPES = ("all", "top", "big5")
N_TIERS = 14
# merdiven tipleri: (1,1),(1,2),(2,2),(2,3)…(14,14) = 27 tip
PROGRESSION = [(t, t) if k % 2 == 0 else (t, t + 1) for k in range(2 * N_TIERS - 1) for t in [k // 2 + 1]]
TIER_SIZES = [10, 14, 30, 45, 65, 90, 130, 180, 250, 350, 480, 650, 900]   # T1..T13; T14 gerisi (en çok 4000. kulübe kadar)
MAX_RANKED = 4000
CURATED = pathlib.Path(__file__).with_name("tiers_curated.txt")
BOOST_COMP = {"TR1": 1}            # yerel ayar: Süper Lig kulüpleri bir tier yukarı
STRONG_TOP = {"PO1", "NL1", "TR1", "BE1", "BRA1", "ARGC", "MEXA", "MLS1", "SA1", "RU1", "SC1", "GR1", "A1", "C1", "DK1", "UKR1"}
club_tier: dict = {}      # club_id -> tier (1..14), kapsamdan bağımsız
club_score: dict = {}

def min_common_for(ta: int, tb: int) -> int:
    t = max(ta, tb)
    return 3 if t <= 5 else 2 if t <= 9 else 1

def _league_weight(comp):
    comp = comp or ""
    if comp in BIG5: return 1.0
    if comp in STRONG_TOP: return 0.8
    if TOP_RE.match(comp) or comp in TOP_EXTRA: return 0.6
    return 0.4 if comp else 0.2

def _compute_tiers():
    """Popülerlik puanı: ücret 0.35 + gelen piyasa değeri 0.30 + yıldız 0.20 + oyuncu sayısı 0.10 + yıl aralığı 0.05 (log10) + lig katsayısı.
    İlk tier'lar kürate listeden; gerisi puan sırasıyla TIER_SIZES'a bölünür; TR1 kulüpleri bir tier yukarı."""
    import math
    L = lambda x: math.log10(1 + max(0, x))
    fees = dict(db.execute("SELECT club_id, SUM(fee) FROM stints WHERE fee>0 GROUP BY club_id"))
    mv = dict(db.execute("SELECT club_id, SUM(mv) FROM stints WHERE mv>0 GROUP BY club_id"))
    stars = dict(db.execute("SELECT pc.club_id, COUNT(*) FROM player_clubs pc JOIN players p ON p.id=pc.player_id WHERE p.mv_max>=20000000 GROUP BY pc.club_id"))
    npl = dict(db.execute("SELECT club_id, COUNT(*) FROM player_clubs GROUP BY club_id"))
    span = dict(db.execute("SELECT club_id, MAX(CAST(substr(date,1,4) AS INT))-MIN(CAST(substr(date,1,4) AS INT)) FROM stints WHERE date IS NOT NULL GROUP BY club_id"))
    comps = dict(db.execute("SELECT id, competition_id FROM clubs WHERE national=0"))
    for cid, comp in comps.items():
        club_score[cid] = (0.35 * L(fees.get(cid, 0) / 1e6) + 0.30 * L(mv.get(cid, 0) / 1e6) + 0.20 * L(stars.get(cid, 0))
                           + 0.10 * L(npl.get(cid, 0)) + 0.05 * L(span.get(cid) or 0) + 0.6 * _league_weight(comp))
    curated = {}
    if CURATED.exists():
        for line in CURATED.read_text().splitlines():
            if line.startswith("#") or "|" not in line: continue
            t, name = line.split("|", 1)
            row = db.execute("SELECT id FROM clubs WHERE name = ? AND national = 0 ORDER BY fame DESC LIMIT 1", (name.strip(),)).fetchone()
            if row: curated[row[0]] = int(t)
            else: print("kürate listede bulunamadı:", name)
    ranked = sorted((c for c in comps if c not in curated), key=lambda c: -club_score[c])[:MAX_RANKED]
    club_tier.update(curated)
    # kürate kulüpler ilgili tier kotasından düşer
    quota = list(TIER_SIZES)
    for t in curated.values():
        if t - 1 < len(quota): quota[t - 1] = max(0, quota[t - 1] - 1)
    t = 1; filled = 0
    for cid in ranked:
        while t <= len(quota) and filled >= quota[t - 1]: t += 1; filled = 0
        club_tier[cid] = min(t, N_TIERS); filled += 1
    for cid, comp in comps.items():
        if comp in BOOST_COMP and cid in club_tier and cid not in curated:
            club_tier[cid] = max(1, club_tier[cid] - BOOST_COMP[comp])

scope_clubs: dict = {}    # scope -> set(club_id)
tier_of: dict = {}        # scope -> {club_id: tier}
tiers: dict = {}          # scope -> {tier: [club_id...]} (fame sırasıyla)

def club_scope_flags(comp):
    comp = comp or ""
    top = comp in BIG5 or comp in TOP_EXTRA or bool(TOP_RE.match(comp))
    return top, comp in BIG5

def _build_scopes():
    _compute_tiers()
    rows = db.execute("SELECT id, competition_id FROM clubs WHERE national=0 AND fame>0").fetchall()
    for sc in SCOPES:
        ids = []
        for cid, comp in rows:
            if cid not in club_tier: continue
            top, big5 = club_scope_flags(comp)
            if sc == "all" or (sc == "top" and top) or (sc == "big5" and big5): ids.append(cid)
        scope_clubs[sc] = set(ids)
        by = {k: [] for k in range(1, N_TIERS + 1)}
        for cid in ids: by[club_tier[cid]].append(cid)
        tier_of[sc] = {cid: club_tier[cid] for cid in ids}; tiers[sc] = by

def tier_pair_for(step: int, per: int, sc: str, rng=None):
    """step → (tierA, tierB). Kapsamda boş tier'lar atlanır (big5'te 14 tier yok); rng verilirse %25 bir önceki tip."""
    k = step // per
    if rng is not None and k > 0 and rng.random() < 0.25: k -= 1
    avail = [t for t in range(1, N_TIERS + 1) if tiers[sc][t]]
    # kapsamın mevcut tier sayısına göre ilerleyişi sıkıştır
    n_types = 2 * len(avail) - 1
    k = min(k, n_types - 1)
    a_i, b_i = (k // 2, k // 2) if k % 2 == 0 else (k // 2, k // 2 + 1)
    return avail[min(a_i, len(avail) - 1)], avail[min(b_i, len(avail) - 1)]

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
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS team_names USING fts5(club_id UNINDEXED, text, tokenize='unicode61')")
    if db.execute("SELECT COUNT(*) FROM team_names").fetchone()[0] == 0:
        db.execute("INSERT INTO team_names(club_id, text) SELECT id, norm FROM clubs WHERE national=0")
    db.execute("PRAGMA query_only=1")
    _build_scopes()
    _build_famous()
    threading.Thread(target=_pool_worker, daemon=True).start()

def fts_prefix(q: str) -> str:
    toks = [t for t in normalize(q).split() if t]
    if not toks: return ""
    return " ".join(f'"{t}"*' for t in toks)

@functools.lru_cache(maxsize=50000)
def _teams_suggest(n: str, sc: str, limit: int):
    m = fts_prefix(n)
    if not m: return []
    rows = db.execute("""SELECT c.id, c.name, c.defunct FROM team_names t JOIN clubs c ON c.id = t.club_id
                         WHERE team_names MATCH ? ORDER BY c.fame DESC LIMIT 40""", (m,)).fetchall()
    out = [{"id": i, "name": nm, "in_scope": sc == "all" or i in scope_clubs[sc], "defunct": bool(df)} for i, nm, df in rows]
    out.sort(key=lambda x: not x["in_scope"])
    return out[:limit]

@app.get("/teams/suggest")
def teams_suggest(q: str = Query(min_length=2), limit: int = 8, scope: str = "all"):
    return _teams_suggest(normalize(q), scope if scope in SCOPES else "all", limit)

@app.get("/club/{club_id}")
def club(club_id: int, scope: str = "all"):
    row = db.execute("SELECT id, name, competition_id, defunct FROM clubs WHERE id=?", (club_id,)).fetchone()
    if not row: raise HTTPException(404)
    sc = scope if scope in SCOPES else "all"
    top, big5 = club_scope_flags(row[2])
    return {"id": row[0], "name": row[1], "competition": row[2], "top": top, "big5": big5, "defunct": bool(row[3]),
            "in_scope": sc == "all" or row[0] in scope_clubs[sc], "tier": club_tier.get(row[0], N_TIERS)}

@functools.lru_cache(maxsize=100000)
def _players_suggest(n: str, limit: int):
    m = fts_prefix(n)
    if not m: return []
    rows = db.execute("""SELECT p.id, p.name, p.birth_year FROM names n JOIN players p ON p.id = n.player_id
                         WHERE names MATCH ? ORDER BY p.fame DESC LIMIT ?""", (m, limit)).fetchall()
    return [{"id": i, "name": nm, "born": by} for i, nm, by in rows]

@app.get("/players/suggest")
def players_suggest(q: str = Query(min_length=2), limit: int = 8):
    return _players_suggest(normalize(q), limit)

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

POOL_SIZE = 20
pools = {("ladder", sc): [] for sc in SCOPES} | {("blitz", sc): [] for sc in SCOPES}
pool_lock = threading.Lock()

def _pool_worker():
    """Her kapsam için hazır paket havuzu; istek anında üretim beklenmez."""
    rnd = random.Random()
    while True:
        try:
            for (kind, sc), lst in list(pools.items()):
                while len(lst) < POOL_SIZE:
                    seed = f"pool-{time.time_ns()}-{rnd.random()}"
                    pack = _ladder(seed, 27, sc) if kind == "ladder" else _blitz(seed, 40, sc)
                    with pool_lock: lst.append(pack)
        except Exception as e:
            print("pool error", e)
        time.sleep(0.5)

def _pool_take(kind: str, sc: str):
    with pool_lock:
        lst = pools[(kind, sc)]
        return lst.pop() if lst else None

@app.get("/ladder")
def ladder(day: str = "", steps: int = 27, seed: str = "", scope: str = "all"):
    sc = scope if scope in SCOPES else "all"
    if not seed and not day and steps == 27:
        got = _pool_take("ladder", sc)
        if got: return got
    return _ladder(seed or day, steps, sc)

def _ladder(seed: str, steps: int, sc: str):
    """Klasik merdiven: basamak tipi T1×T1 → T1×T2 → T2×T2 → … → T4×T4 (her tip 3 basamak). Kulüp koşuda bir kez."""
    rng = _seeded(seed, "ladder:" + sc)
    out, used = [], set()
    for i in range(steps):
        ta, tb = tier_pair_for(i, 1, sc, rng)
        min_n = min_common_for(ta, tb)
        got = pick_pair(rng, sc, ta, tb, used, min_n) or pick_pair(rng, sc, ta, tb, used, 1) \
              or pick_pair(rng, sc, min(ta, tb), min(ta, tb), used, 1)
        if not got: break
        a, b, n = got; used.update((a, b))
        out.append({"a": a, "b": b, "n": n, "tiers": [ta, tb]})
    info = {i: (nm, bool(df)) for i, nm, df in db.execute(f"SELECT id, name, defunct FROM clubs WHERE id IN ({','.join(str(c) for c in used) or '0'})")}
    for st in out:
        st["a_name"], st["a_defunct"] = info[st["a"]]; st["b_name"], st["b_defunct"] = info[st["b"]]
    return {"seed": seed, "scope": sc, "steps": out}

@app.get("/blitz/pack")
def blitz_pack(day: str = "", n: int = 40, reveal: int = 0, seed: str = "", scope: str = "all"):
    sc = scope if scope in SCOPES else "all"
    qs = None
    if not seed and not day and n == 40:
        qs = _pool_take("blitz", sc)
    if qs is None: qs = _blitz(seed or day, n, sc)
    # reveal=1 yalnızca oyun sunucusu için (localhost); cevap indeksi istemciye asla iletilmez
    return {"scope": sc, "questions": [{k: v for k, v in q.items() if not k.startswith("_") or (reveal and k == "_answer")} for q in qs]}

def _blitz(seed: str, n: int, sc: str):
    """5 isim: 2 yalnız A, 2 yalnız B, 1 ikisi. Çift tier ilerleyişiyle seçilir; çeldiriciler ≥3 kulüplü ünlü oyunculardan."""
    rng = _seeded(seed, "blitz:" + sc)
    qs, used = [], set()
    only_sql = """SELECT p.id, p.name FROM player_clubs x JOIN players p ON p.id=x.player_id
                  WHERE x.club_id=? AND p.n_clubs>=3 AND NOT EXISTS(SELECT 1 FROM player_clubs y WHERE y.player_id=x.player_id AND y.club_id=?)
                  ORDER BY p.fame DESC LIMIT 40"""
    tries = 0
    while len(qs) < n and tries < n * 6:
        tries += 1
        ta, tb = tier_pair_for(len(qs), 2, sc, rng)
        got = pick_pair(rng, sc, ta, tb, used, max(2, min_common_for(ta, tb)), 60) or pick_pair(rng, sc, ta, tb, used, 1, 200)
        if not got: break
        ca, cb, _ = got
        both = db.execute("""SELECT p.id, p.name FROM player_clubs x JOIN player_clubs y ON x.player_id=y.player_id JOIN players p ON p.id=x.player_id
                             WHERE x.club_id=? AND y.club_id=? AND p.n_clubs>=3 ORDER BY p.fame DESC LIMIT 20""", (ca, cb)).fetchall()
        oa, ob = db.execute(only_sql, (ca, cb)).fetchall(), db.execute(only_sql, (cb, ca)).fetchall()
        if not both or len(oa) < 2 or len(ob) < 2:
            used.update((ca, cb)); continue
        used.update((ca, cb))
        ans = rng.choice(both); opts = [ans] + rng.sample(oa, 2) + rng.sample(ob, 2); rng.shuffle(opts)
        qid = f"{seed}-{len(qs)}"
        qs.append({"id": qid, "a": ca, "b": cb, "options": [o[1] for o in opts], "tiers": [ta, tb],
                   "answer_hash": hashlib.sha256(f"{qid}:{ans[0]}".encode()).hexdigest(), "_answer_id": ans[0], "_answer": opts.index(ans)})
    info = {i: (nm, bool(df)) for i, nm, df in db.execute(f"SELECT id, name, defunct FROM clubs WHERE id IN ({','.join(str(c) for c in used) or '0'})")}
    for q in qs:
        q["a_name"], q["a_defunct"] = info[q["a"]]; q["b_name"], q["b_defunct"] = info[q["b"]]
    return qs

@app.get("/player/{player_id}/career")
def career(player_id: int):
    """Kariyer sırası / kiralık-satış modları için (yalnızca oyun sunucusu çağırır)."""
    rows = db.execute("""SELECT s.seq, c.name, s.date, s.kind, s.fee, s.mv, s.age FROM stints s JOIN clubs c ON c.id=s.club_id
                         WHERE s.player_id=? ORDER BY s.seq""", (player_id,)).fetchall()
    if not rows: raise HTTPException(404)
    return [{"seq": a, "club": b, "date": c, "kind": d, "fee": e, "mv": f, "age": g} for a, b, c, d, e, f, g in rows]

@app.get("/quick_picks")
def quick_picks(scope: str = "all", n: int = 5, exclude: str = ""):
    """Takım seçiminde geç kalan oyuncuya önerilecek popüler kulüpler (T1-T3, kapsam içi, kullanılmamış)."""
    sc = scope if scope in SCOPES else "all"
    ex = {int(x) for x in exclude.split(",") if x.strip().isdigit()}
    pool = [c for t in (1, 2, 3) for c in tiers[sc][t] if c not in ex]
    rng = random.Random()
    pick = rng.sample(pool, min(n, len(pool))) if pool else []
    names = dict(db.execute(f"SELECT id, name FROM clubs WHERE id IN ({','.join(map(str, pick)) or '0'}) AND defunct = 0").fetchall())
    return [{"id": c, "name": names[c]} for c in pick if c in names]

# ============================================================ ünlü oyuncu havuzu ve yeni tek oyunculu modlar
famous: list = []          # player id'leri, ün sırasıyla (kariyeri çoğunlukla üst liglerde geçmiş bilinen oyuncular)
fame2: dict = {}
pinfo: dict = {}           # pid -> (name, birth_year, position)
CATS = {                   # O mu bu mu kategorileri: anahtar -> (SQL ifadesi, biçim)
    "goals": ("s.goals", "int"), "apps": ("s.apps", "int"), "assists": ("s.assists", "int"), "yellow": ("s.yellow", "int"),
    "red": ("s.red", "int"), "best_season": ("s.best_season_goals", "int"), "goals_big5": ("s.goals_big5", "int"), "pens": ("s.pens", "int"),
    "max_fee": ("(SELECT MAX(fee) FROM stints WHERE player_id=p.id)", "money"),      # piyasa değeri kategorisi bilerek yok (kaynağa özgü tahmin)
    "fee_sum": ("(SELECT SUM(fee) FROM stints WHERE player_id=p.id)", "money"), "n_clubs": ("p.n_clubs", "int"),
}
VERSUS_POOL = 400       # yalnızca en tanınan isimler
cat_values: dict = {}      # cat -> {pid: değer}
cat_sorted: dict = {}      # cat -> [pid] büyükten küçüğe
cat_rank: dict = {}

MIN_BIRTH = 1965           # bugünün oyuncusunun tanıyacağı dönem
HOME_APP_W, HOME_GOAL_W = 0.6, 1.8   # Süper Lig: diğer üst liglerden (0.4 / 1.2) biraz fazla, 5 büyük ligden (1.0 / 3.0) az. Global odak, Türkler de girer.
FAMOUS_SIZE = 5000

def _build_famous():
    """Ün puanı: 5 büyük lig (+Süper Lig) maçı ve golü, diğer üst lig maçı/golü, zirve piyasa değeri, T1-T3 kulüp sayısı.
    Şart: üst liglerde ≥120 maç, lig maçlarının ≥%60'ı üst liglerde, doğum ≥ MIN_BIRTH."""
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='player_stats'").fetchone() is None:
        print("player_stats yok: kariyer / zincir / o mu bu mu modları kapalı (tools/build_stats.py çalıştır)"); return
    global PATH_SQL
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='countries'").fetchone():        # tools/build_geo.py
        PATH_SQL = """SELECT s.club_id, c.name, s.date, s.kind, s.fee, co.name, cp.name, c.defunct FROM stints s JOIN clubs c ON c.id = s.club_id
                      LEFT JOIN countries co ON co.id = c.country_id LEFT JOIN competitions cp ON cp.id = c.competition_id
                      WHERE s.player_id = ? ORDER BY s.seq"""
    cols = {r[1] for r in db.execute("PRAGMA table_info(player_stats)")}
    tr_cols = "s.apps_tr, s.goals_tr" if "apps_tr" in cols else "0, 0"
    top_ids = ",".join(str(c) for c, t in club_tier.items() if t <= 3) or "0"
    in_top = dict(db.execute(f"SELECT player_id, COUNT(*) FROM player_clubs WHERE club_id IN ({top_ids}) GROUP BY player_id"))
    rows = db.execute(f"""SELECT p.id, p.name, p.birth_year, p.position, p.mv_max, s.apps_league, s.apps_top, s.apps_big5, s.goals_top, s.goals_big5, {tr_cols}
                          FROM players p JOIN player_stats s ON s.player_id = p.id
                          WHERE s.apps_top >= 120 AND s.apps_top * 10 >= s.apps_league * 6 AND p.birth_year >= ?""", (MIN_BIRTH,)).fetchall()
    for pid, name, by, pos, mv, al, at, a5, gt, g5, atr, gtr in rows:
        atr = atr or 0; gtr = gtr or 0
        fame2[pid] = (a5 * 1.0 + atr * HOME_APP_W + (at - a5 - atr) * 0.4 + g5 * 3.0 + gtr * HOME_GOAL_W + (gt - g5 - gtr) * 1.2
                      + (mv or 0) / 1e6 * 3.0 + in_top.get(pid, 0) * 80)
        pinfo[pid] = (name, by, pos)
    famous.extend(sorted(fame2, key=lambda x: -fame2[x])[:FAMOUS_SIZE])
    pool = famous[:VERSUS_POOL]; ids = ",".join(map(str, pool))
    for cat, (expr, _fmt) in CATS.items():
        vals = {pid: int(v) for pid, v in db.execute(f"SELECT p.id, {expr} FROM players p JOIN player_stats s ON s.player_id=p.id WHERE p.id IN ({ids})") if v}
        cat_values[cat] = vals
        cat_sorted[cat] = sorted(vals, key=lambda x: -vals[x])
        cat_rank[cat] = {pid: i for i, pid in enumerate(cat_sorted[cat])}

PATH_SQL = """SELECT s.club_id, c.name, s.date, s.kind, s.fee, NULL, NULL, c.defunct FROM stints s JOIN clubs c ON c.id = s.club_id
              WHERE s.player_id = ? ORDER BY s.seq"""      # ülke/lig tabloları varsa _build_famous içinde genişletilir

def _path(pid: int) -> list:
    """Oyuncunun kıdemli kulüp yolu: kiralık dönüşleri atılır, art arda aynı kulüp birleştirilir."""
    out = []
    for cid, name, date, kind, fee, country, league, defunct in db.execute(PATH_SQL, (pid,)):
        if kind == "loan_end": continue
        if out and out[-1]["club_id"] == cid: continue
        k = "start" if not out else ("loan" if kind == "loan" else ("sale" if (fee or 0) > 0 else "free"))
        out.append({"club_id": cid, "club": name, "year": int(date[:4]) if date else None, "kind": k, "fee": fee if (fee or 0) > 0 else None,
                    "country": country, "league": league, "defunct": bool(defunct)})
    return out

def _fame_buckets(rng, n: int, ok) -> list:
    """Ünlüden az ünlüye: ilk üçte biri ilk 300'den, sonraki 300-1200'den, kalanı 1200-5000'den."""
    out, seen = [], set()
    for lo, hi, share in ((0, 300, 1 / 3), (300, 1200, 1 / 3), (1200, FAMOUS_SIZE, 1 / 3)):
        cand = [p for p in famous[lo:hi] if p not in seen]; rng.shuffle(cand)
        take = 0; want = max(1, round(n * share))
        for pid in cand:
            if take >= want: break
            item = ok(pid)
            if item: out.append(item); seen.add(pid); take += 1
    return out

@app.get("/career/pack")
def career_pack(n: int = 30, seed: str = ""):
    """Kariyer yolu: kulüpler sırayla açılır, oyuncu tahmin edilir. Yalnızca oyun sunucusu çağırır (cevap içerir)."""
    rng = random.Random(seed or None)
    def ok(pid):
        path = _path(pid)
        if not (4 <= len(path) <= 11): return None
        return {"_player_id": pid, "_name": pinfo[pid][0], "clubs": [{"club": x["club"], "year": x["year"], "kind": x["kind"], "country": x["country"], "defunct": x["defunct"]} for x in path]}
    return _fame_buckets(rng, n, ok)

@app.get("/chain/pack")
def chain_pack(n: int = 15, seed: str = ""):
    """Sıradaki kulüp: oyuncu verilir; ilk kulüp, sonra her transferin hedefi tahmin edilir (yıl, tür, bedel ipucu)."""
    rng = random.Random(seed or None)
    def ok(pid):
        path = _path(pid)
        if not (3 <= len(path) <= 9): return None
        if any(club_tier.get(x["club_id"], 99) > 10 for x in path): return None   # tahmin edilemeyecek kadar silik kulüp varsa alma
        name, by, pos = pinfo[pid]
        return {"name": name, "born": by, "pos": pos, "_steps": path}
    return _fame_buckets(rng, n, ok)

TOP_RESET_RANK = 3     # kalan oyuncu listenin ilk 3'üne girince kategori değişir
STREAK_RESET = 5       # ya da aynı oyuncu 5 tur üst üste kalınca

@app.get("/versus/pack")
def versus_pack(rounds: int = 80, seed: str = ""):
    """O mu bu mu: iki oyuncu, bir kategori. Kazanan (değeri büyük olan) yerinde kalır, karşısına yenisi gelir.
    Kalan oyuncu zirveye ulaşınca (ilk 3) ya da 5 tur üst üste kalınca kategori değişir.
    Doğru cevap hep büyük olan olduğundan tüm koşu önceden üretilir."""
    if not cat_sorted: return []
    rng = random.Random(seed or None)
    cats = [c for c in CATS if len(cat_sorted.get(c, [])) >= 40]; rng.shuffle(cats)
    out = []; ci = 0
    while len(out) < rounds:
        cat = cats[ci % len(cats)]; ci += 1
        order, vals, rank = cat_sorted[cat], cat_values[cat], cat_rank[cat]
        stayer = rng.choice(order[len(order) // 3:]); side = rng.randint(0, 1); used = {stayer}; first = True; streak = 0
        while len(out) < rounds:
            r = rank[stayer]
            near = [p for p in order[max(0, r - 50): r + 50] if p not in used and vals[p] != vals[stayer]]
            anyw = [p for p in order if p not in used and vals[p] != vals[stayer]]
            cand = near if (near and rng.random() < 0.75) else anyw
            if not cand: break
            ch = rng.choice(cand); used.add(ch)
            pair = [None, None]; pair[side] = stayer; pair[1 - side] = ch
            v = [vals[pair[0]], vals[pair[1]]]
            ans = 0 if v[0] > v[1] else 1
            out.append({"cat": cat, "fmt": CATS[cat][1], "names": [pinfo[x][0] for x in pair], "born": [pinfo[x][1] for x in pair],
                        "shown": [None if (first or i != side) else v[i] for i in (0, 1)], "new_cat": first and len(out) > 0,
                        "_values": v, "_answer": ans})
            first = False
            streak = streak + 1 if pair[ans] == stayer else 1
            stayer = pair[ans]; side = ans
            if rank[stayer] < TOP_RESET_RANK or streak >= STREAK_RESET: break
    return out

@app.get("/famous")
def famous_list(offset: int = 0, limit: int = 30):
    return {"count": len(famous), "players": [pinfo[p][0] for p in famous[offset: offset + limit]]}

@app.get("/tiers")
def tiers_list(tier: int = 1, limit: int = 30):
    ids = [c for c, t in club_tier.items() if t == tier]
    ids.sort(key=lambda c: -club_score.get(c, 0))
    names = dict(db.execute(f"SELECT id, name FROM clubs WHERE id IN ({','.join(map(str, ids[:limit])) or '0'})").fetchall())
    return {"tier": tier, "count": len(ids), "clubs": [names.get(c) for c in ids[:limit]]}

@app.get("/health")
def health():
    return {"players": db.execute("SELECT COUNT(*) FROM players").fetchone()[0]}
