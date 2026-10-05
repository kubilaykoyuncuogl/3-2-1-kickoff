"""Index'in son hali: kaynak izlerini temizler. build_index → build_stats → build_geo → finalize_index → encrypt_index.

1. Kulüp adlarındaki dönem ekleri silinir: "Aldershot FC (- 1992)", "Dunarea Galati (1970-2014)" → ad sade kalır, clubs.defunct = 1 olur
   (oyunda adın yanında küçük bir ikonla gösterilir). "(MG)", "(Bangui)" gibi ayırt edici ekler kalır.
2. Kulüp ve oyuncu kimlikleri kendi numaralarımıza çevrilir: 1..N, sıra bilgi taşımayan karışık bir düzen (çarpımsal özet; ün ya da değer sırası değil).
   Kaynak kimlikler hiçbir tabloda kalmaz. Ülke ve lig kodları istemciye gitmediği için dokunulmaz.
    python tools/finalize_index.py [--index data/index/index.sqlite] [--force]
"""
import argparse, re, sqlite3, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from normalize import normalize

ERA = re.compile(r"\s*\(\s*(?:\d{4})?\s*-\s*\d{4}\s*\)\s*$")
ap = argparse.ArgumentParser(); ap.add_argument("--index", default="data/index/index.sqlite"); ap.add_argument("--force", action="store_true")
a = ap.parse_args()
db = sqlite3.connect(a.index); t0 = time.time()
db.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA temp_store=MEMORY; PRAGMA cache_size=-1000000; CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);")
done = db.execute("SELECT value FROM meta WHERE key='ids'").fetchone()
if done and not a.force: sys.exit("zaten işlenmiş (meta.ids = %s); yeniden için --force" % done[0])

# ---- 1. dönem ekleri → defunct
cols = [r[1] for r in db.execute("PRAGMA table_info(clubs)")]
if "defunct" not in cols: db.execute("ALTER TABLE clubs ADD COLUMN defunct INTEGER NOT NULL DEFAULT 0")
n = 0
for cid, name in db.execute("SELECT id, name FROM clubs").fetchall():
    clean = ERA.sub("", name)
    if clean != name and clean.strip():
        db.execute("UPDATE clubs SET name = ?, norm = ?, defunct = 1 WHERE id = ?", (clean.strip(), normalize(clean), cid)); n += 1
db.commit(); print(f"dönem eki silinen kulüp: {n} ({time.time()-t0:.0f}s)", flush=True)

# ---- 2. kimlikleri yeniden ata
db.executescript("""
CREATE TEMP TABLE cmap AS SELECT id AS old, ROW_NUMBER() OVER (ORDER BY (id * 2654435761) % 4294967296, id) AS new FROM clubs;
CREATE UNIQUE INDEX temp.ix_cmap ON cmap(old);
CREATE TEMP TABLE pmap AS SELECT id AS old, ROW_NUMBER() OVER (ORDER BY (id * 2654435761) % 4294967296, id) AS new FROM players;
CREATE UNIQUE INDEX temp.ix_pmap ON pmap(old);

CREATE TABLE clubs_new(id INTEGER PRIMARY KEY, name TEXT, norm TEXT, country_id INT, competition_id TEXT, national INT, fame REAL DEFAULT 0, defunct INTEGER NOT NULL DEFAULT 0);
INSERT INTO clubs_new SELECT m.new, c.name, c.norm, c.country_id, c.competition_id, c.national, c.fame, c.defunct FROM clubs c JOIN cmap m ON m.old = c.id;
CREATE TABLE players_new(id INTEGER PRIMARY KEY, name TEXT, short TEXT, norm TEXT, birth_year INT, nat_id INT, position TEXT, mv_max INT, n_clubs INT, fame REAL DEFAULT 0);
INSERT INTO players_new SELECT m.new, p.name, p.short, p.norm, p.birth_year, p.nat_id, p.position, p.mv_max, p.n_clubs, p.fame FROM players p JOIN pmap m ON m.old = p.id;
CREATE TABLE stints_new(player_id INT, seq INT, club_id INT, from_club_id INT, date TEXT, season INT, kind TEXT, fee INT, mv INT, age INT);
INSERT INTO stints_new SELECT pm.new, s.seq, cm.new, fm.new, s.date, s.season, s.kind, s.fee, s.mv, s.age
  FROM stints s JOIN pmap pm ON pm.old = s.player_id JOIN cmap cm ON cm.old = s.club_id LEFT JOIN cmap fm ON fm.old = s.from_club_id;
CREATE TABLE player_clubs_new(player_id INT, club_id INT, PRIMARY KEY(player_id, club_id)) WITHOUT ROWID;
INSERT OR IGNORE INTO player_clubs_new SELECT pm.new, cm.new FROM player_clubs x JOIN pmap pm ON pm.old = x.player_id JOIN cmap cm ON cm.old = x.club_id;
CREATE TABLE pair_counts_new(club_a INT, club_b INT, n INT, PRIMARY KEY(club_a, club_b)) WITHOUT ROWID;
INSERT OR IGNORE INTO pair_counts_new SELECT MIN(x.new, y.new), MAX(x.new, y.new), p.n FROM pair_counts p JOIN cmap x ON x.old = p.club_a JOIN cmap y ON y.old = p.club_b;
CREATE VIRTUAL TABLE names_new USING fts5(player_id UNINDEXED, text, tokenize='unicode61');
INSERT INTO names_new(player_id, text) SELECT pm.new, n.text FROM names n JOIN pmap pm ON pm.old = CAST(n.player_id AS INTEGER);
""")
print(f"ana tablolar yeniden yazıldı ({time.time()-t0:.0f}s)", flush=True)
if db.execute("SELECT 1 FROM sqlite_master WHERE name='player_stats'").fetchone():
    sc = [r[1] for r in db.execute("PRAGMA table_info(player_stats)")]
    rest = ", ".join("s." + c for c in sc[1:])
    db.execute(f"CREATE TABLE player_stats_new AS SELECT pm.new AS player_id, {rest} FROM player_stats s JOIN pmap pm ON pm.old = s.player_id")
    db.executescript("DROP TABLE player_stats; ALTER TABLE player_stats_new RENAME TO player_stats; CREATE UNIQUE INDEX ux_ps ON player_stats(player_id);")
db.executescript("""
DROP TABLE clubs; DROP TABLE players; DROP TABLE stints; DROP TABLE player_clubs; DROP TABLE pair_counts; DROP TABLE names;
ALTER TABLE clubs_new RENAME TO clubs; ALTER TABLE players_new RENAME TO players; ALTER TABLE stints_new RENAME TO stints;
ALTER TABLE player_clubs_new RENAME TO player_clubs; ALTER TABLE pair_counts_new RENAME TO pair_counts; ALTER TABLE names_new RENAME TO names;
CREATE INDEX ix_pc_club ON player_clubs(club_id);
CREATE INDEX ix_st_player ON stints(player_id, seq);
CREATE INDEX ix_st_club ON stints(club_id);
CREATE INDEX ix_pair_b ON pair_counts(club_b);
INSERT OR REPLACE INTO meta VALUES('ids', 'own-shuffled');
""")
db.commit()
for t in ("clubs", "players", "stints", "player_clubs", "pair_counts", "player_stats"): print(t, db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
print("ilk kulüpler:", db.execute("SELECT id, name FROM clubs ORDER BY id LIMIT 4").fetchall())
print("ünlü kulüplerin yeni kimlikleri:", db.execute("SELECT id, name FROM clubs ORDER BY fame DESC LIMIT 5").fetchall())
print("ilk oyuncular:", db.execute("SELECT id, name FROM players ORDER BY id LIMIT 6").fetchall())
print("kapanmış örnek:", db.execute("SELECT id, name FROM clubs WHERE defunct=1 ORDER BY id LIMIT 6").fetchall())
db.execute("VACUUM"); db.close(); print(f"bitti ({time.time()-t0:.0f}s)")
