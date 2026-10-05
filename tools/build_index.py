"""Transfermarkt dökümü (pg_restore --data-only metin çıktıları) → oyun index'i (SQLite).

Girdi: data/raw/tsv/{players,player_core_json,player_transfer_history_json,reference_entities}.sql
  (üretimi: pg_restore --data-only -t <tablo> -f <dosya> database.dump)
Çıktı: data/index/index.sqlite  (düz; git dışı)  → tools/encrypt_index.py ile şifrelenir.

Tablolar:
  clubs(id, name, norm, country_id, competition_id, national, fame)
  players(id, name, short, norm, birth_year, nat_id, position, mv_max, n_clubs, fame)
  stints(player_id, seq, club_id, from_club_id, date, season, kind, fee, mv, age)
      kind: std | loan | loan_end | internal | first (kariyerin ilk kulübü, transferden türetildi)
  player_clubs(player_id, club_id)   -- kıdemli kulüp seti (kesişim sorguları bunun üstünden)
  names(fts5: player_id, text)       -- autocomplete (isim, kısa ad, takma adlar; normalize)
  pair_counts(club_a, club_b, n)     -- yalnızca n>=1 çiftler (merdiven zorluk ölçütü)

Kurallar (bkz. docs/data.md):
  - Kıdemli kulüp: clubTypeId ∈ {0,1}, ad altyapı/rezerv kalıbına uymuyor, sahte kulüp değil, milli takım ayrı işaretli.
  - Tarihi ad (mainClubId ≠ id, mainClubId ≠ 0) ana kulübe birleştirilir.
"""
import argparse, json, re, sqlite3, sys, time, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from normalize import normalize

PSEUDO = {"123", "515", "75", "2113", "2077", "3160"}   # Retired, Without Club, Unknown, Career break, Disqualification, None
YOUTH = re.compile(r"(\b(U-?\d{2}|II|III|IV|B|C|Jgd\.?|Jugend|Youth|Juvenil|Amateure|Amateurs|Reserves?|Academy|Primavera|Jong|Giovanili|Under\s?\d{2}|Olympic Team|Olympia)\b|\bUEFA U\d{2}\b)", re.I)
SENIOR_TYPES = {0, 1}

def copy_rows(path):
    """pg_restore COPY ... FROM stdin bloğunu satır satır verir (alanlar \\t ile ayrılmış, \\N = NULL)."""
    with open(path, "rb") as f:
        for line in f:
            if line.startswith(b"COPY "): break
        for line in f:
            if line.startswith(b"\\."): break
            yield line.rstrip(b"\n").split(b"\t")

def unescape(b: bytes) -> str:
    return b.replace(b"\\\\", b"\\").decode("utf-8", "replace")

def jload(b: bytes):
    return json.loads(unescape(b))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="data/raw/tsv")
    ap.add_argument("--out", default="data/index/index.sqlite")
    ap.add_argument("--limit", type=int, default=0, help="test için oyuncu sayısı sınırı")
    a = ap.parse_args()
    inp = pathlib.Path(a.inp); out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists(): out.unlink()
    db = sqlite3.connect(out)
    db.executescript("""
    PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA cache_size=-2000000;
    CREATE TABLE clubs(id INTEGER PRIMARY KEY, name TEXT, norm TEXT, country_id INT, competition_id TEXT, national INT, fame REAL DEFAULT 0);
    CREATE TABLE players(id INTEGER PRIMARY KEY, name TEXT, short TEXT, norm TEXT, birth_year INT, nat_id INT, position TEXT, mv_max INT, n_clubs INT, fame REAL DEFAULT 0);
    CREATE TABLE stints(player_id INT, seq INT, club_id INT, from_club_id INT, date TEXT, season INT, kind TEXT, fee INT, mv INT, age INT);
    CREATE TABLE player_clubs(player_id INT, club_id INT, PRIMARY KEY(player_id, club_id)) WITHOUT ROWID;
    CREATE VIRTUAL TABLE names USING fts5(player_id UNINDEXED, text, tokenize='unicode61');
    CREATE TABLE pair_counts(club_a INT, club_b INT, n INT, PRIMARY KEY(club_a, club_b)) WITHOUT ROWID;
    """)
    t0 = time.time()

    # ---- kulüpler ----
    clubs = {}          # id -> dict
    canon = {}          # id -> canonical id (tarihi ad → ana kulüp)
    for row in copy_rows(inp / "reference_entities.sql"):
        kind, sid, name, payload = row[0], row[1].decode(), row[2], row[3]
        if kind != b"club" or payload == b"\\N": continue
        p = jload(payload); bd = p.get("baseDetails", {}) or {}
        nm = p.get("name") or (unescape(name) if name != b"\\N" else None)
        if not nm: continue
        ctype = bd.get("clubTypeId"); national = bool(bd.get("isNationalTeam"))
        senior = ctype in SENIOR_TYPES and not YOUTH.search(nm) and sid not in PSEUDO
        main_id = str(bd.get("mainClubId") or "0")
        clubs[sid] = dict(name=nm, country=bd.get("countryId"), comp=bd.get("primaryCompetitionId") or None,
                          national=national, senior=senior, main=main_id if main_id not in ("0", sid) else None)
    # canonical: tarihi ad → ana kulüp (ana kulüp de kıdemliyse)
    for sid, c in clubs.items():
        m = c["main"]
        canon[sid] = m if (m and m in clubs and clubs[m]["senior"] and c["senior"]) else sid
    senior_ids = {sid for sid, c in clubs.items() if c["senior"] and canon[sid] == sid}
    db.executemany("INSERT INTO clubs(id,name,norm,country_id,competition_id,national) VALUES(?,?,?,?,?,?)",
                   [(int(sid), c["name"], normalize(c["name"]), c["country"], c["comp"], int(c["national"])) for sid, c in clubs.items() if sid in senior_ids])
    print(f"clubs: {len(clubs)} total, {len(senior_ids)} senior canonical  ({time.time()-t0:.0f}s)", flush=True)

    def club_ok(cid: str):
        """ham kulüp id → kanonik kıdemli kulüp id (int) ya da None"""
        c = canon.get(cid)
        return int(c) if c in senior_ids else None

    # ---- oyuncu adları (players tablosu: name, aliases) ----
    pname = {}; palias = collections.defaultdict(set)
    for row in copy_rows(inp / "players.sql"):
        sid = row[2].decode(); nm = unescape(row[3]) if row[3] != b"\\N" else None
        if nm: pname[sid] = nm
        al = unescape(row[4])
        if al not in ("{}", "\\N"):
            for x in re.findall(r'"([^"]+)"|([^,{}]+)', al):
                v = (x[0] or x[1]).strip()
                if v and v != nm: palias[sid].add(v)
    print(f"players table: {len(pname)} names ({time.time()-t0:.0f}s)", flush=True)

    # ---- core profil ----
    core = {}
    for i, row in enumerate(copy_rows(inp / "player_core_json.sql")):
        sid = row[0].decode(); p = jload(row[1])
        ld = p.get("lifeDates") or {}; dob = ld.get("dateOfBirth") or ""
        attrs = p.get("attributes") or {}; pos = (attrs.get("position") or {}).get("shortName")
        mvd = p.get("marketValueDetails") or {}; mv_max = ((mvd.get("highest") or {}).get("value")) or 0
        nat = ((p.get("nationalityDetails") or {}).get("nationalities") or {}).get("nationalityId")
        core[sid] = (p.get("name") or pname.get(sid), p.get("shortName"), int(dob[:4]) if dob[:4].isdigit() else None, nat, pos, int(mv_max))
        if a.limit and i >= a.limit: break
    print(f"core: {len(core)} ({time.time()-t0:.0f}s)", flush=True)

    # ---- transferler → stints, player_clubs ----
    n_players = 0; n_stints = 0; pc_batch = []; st_batch = []; pl_batch = []; nm_batch = []
    pair = collections.Counter()
    def flush():
        db.executemany("INSERT OR IGNORE INTO player_clubs VALUES(?,?)", pc_batch); pc_batch.clear()
        db.executemany("INSERT INTO stints VALUES(?,?,?,?,?,?,?,?,?,?)", st_batch); st_batch.clear()
        db.executemany("INSERT INTO players VALUES(?,?,?,?,?,?,?,?,?,0)", pl_batch); pl_batch.clear()
        db.executemany("INSERT INTO names(player_id,text) VALUES(?,?)", nm_batch); nm_batch.clear()
    for i, row in enumerate(copy_rows(inp / "player_transfer_history_json.sql")):
        sid = row[0].decode(); p = jload(row[1])
        if a.limit and i >= a.limit: break
        hist = (p.get("history") or {}).get("terminated") or []
        clubset = set()
        for raw in p.get("clubIds") or []:
            c = club_ok(str(raw))
            if c: clubset.add(c)
        moves = []
        for t in hist:
            d = t.get("details") or {}; td = t.get("typeDetails") or {}
            src = club_ok(str((t.get("transferSource") or {}).get("clubId"))); dst = club_ok(str((t.get("transferDestination") or {}).get("clubId")))
            typ = td.get("type") or ""
            kind = {"ACTIVE_LOAN_TRANSFER": "loan", "RETURNED_FROM_PREVIOUS_LOAN": "loan_end", "INTERNAL_TRANSFER": "internal"}.get(typ, "std")
            fee = ((d.get("fee") or {}).get("value")); mv = ((d.get("marketValue") or {}).get("value"))
            moves.append((d.get("date") or "", d.get("seasonId"), dst, src, kind, fee, mv, d.get("age")))
            if src: clubset.add(src)
            if dst: clubset.add(dst)
        if not clubset: continue
        moves.sort(key=lambda m: m[0])
        seq = 0
        if moves and moves[0][3]:   # ilk transferin kaynağı = kariyerin ilk kulübü
            st_batch.append((int(sid), seq, moves[0][3], None, None, None, "first", None, None, None)); seq += 1
        for (date, season, dst, src, kind, fee, mv, age) in moves:
            if not dst: continue
            st_batch.append((int(sid), seq, dst, src, date[:10] or None, season, kind, fee, mv, age)); seq += 1
        n_stints += seq
        name, short, by, nat, pos, mv_max = core.get(sid, (pname.get(sid), None, None, None, None, 0))
        if not name: continue
        pl_batch.append((int(sid), name, short, normalize(name), by, nat, pos, mv_max, len(clubset)))
        texts = {name, short or "", *palias.get(sid, ())}
        nm_batch.append((int(sid), " | ".join(normalize(x) for x in texts if x)))
        for c in clubset: pc_batch.append((int(sid), c))
        cl = sorted(clubset)
        for x in range(len(cl)):
            for y in range(x + 1, len(cl)): pair[(cl[x], cl[y])] += 1
        n_players += 1
        if len(pl_batch) >= 20000:
            flush(); print(f"  {n_players} players, {n_stints} stints, {len(pair)} pairs ({time.time()-t0:.0f}s)", flush=True)
    flush()
    print(f"transfers done: {n_players} players, {n_stints} stints, {len(pair)} pairs ({time.time()-t0:.0f}s)", flush=True)
    db.executemany("INSERT INTO pair_counts VALUES(?,?,?)", ((a_, b_, n) for (a_, b_), n in pair.items())); pair.clear()

    # ---- fame ----
    db.executescript("""
    CREATE INDEX ix_pc_club ON player_clubs(club_id);
    CREATE INDEX ix_st_player ON stints(player_id, seq);
    CREATE INDEX ix_st_club ON stints(club_id);
    CREATE INDEX ix_pair_b ON pair_counts(club_b);
    UPDATE players SET fame = (mv_max/1000000.0) + n_clubs*0.5;
    UPDATE clubs SET fame = COALESCE((SELECT SUM(p.mv_max)/1000000.0 + COUNT(*)*0.2 FROM player_clubs pc JOIN players p ON p.id=pc.player_id WHERE pc.club_id=clubs.id), 0);
    DELETE FROM clubs WHERE fame = 0;
    """)
    db.commit()
    for t in ("clubs", "players", "stints", "player_clubs", "pair_counts"):
        print(t, db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
    print("top clubs:", db.execute("SELECT name, ROUND(fame) FROM clubs ORDER BY fame DESC LIMIT 15").fetchall())
    db.execute("VACUUM"); db.close()
    print(f"ok → {out} ({out.stat().st_size/1e6:.0f} MB, {time.time()-t0:.0f}s)")

if __name__ == "__main__":
    main()
