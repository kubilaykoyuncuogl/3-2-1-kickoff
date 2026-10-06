"""Sezon istatistiklerini (football.player_season_performance_gzip.summary) mevcut index.sqlite'a player_stats tablosu olarak ekler.

Dökümden akıtarak okur (diske ara dosya yazmaz):
    python tools/build_stats.py [--dump all_data/all_data/database.dump] [--index data/index/index.sqlite]
Sonra yeniden şifrele: python tools/encrypt_index.py --in data/index/index.sqlite --out data/index/index.enc

player_stats(player_id, apps, goals, assists, minutes, yellow, red, own_goals, pens, best_season_goals, seasons,
             apps_league, apps_top, apps_big5, goals_top, goals_big5, apps_tr, goals_tr, decades)
  *_league: lig kodu gibi görünen müsabakalar · *_top: üst ligler · *_big5: GB1 ES1 IT1 L1 FR1 · *_tr: Süper Lig (TR1)
  decades: en az bir maça çıktığı on yılların bit maskesi (1 = 1980'ler, 2 = 1990'lar, 4 = 2000'ler, 8 = 2010'lar, 16 = 2020'ler; sezonun başlangıç yılına göre)
club_leagues(club_id, comp, seasons): kulübün bir üst ligde kaç sezon oynadığı (oyuncu sezon kayıtlarından)
Not: kaynak her oyuncuda tüm kariyeri kapsamayabilir (eski oyuncularda eksik sezon olur).
"""
import argparse, json, re, sqlite3, subprocess, sys, time, collections

BIG5 = {"GB1", "ES1", "IT1", "L1", "FR1"}
TOP_RE = re.compile(r"^[A-Z]{1,4}1[A-Z]?$")
TOP_EXTRA = {"ARGC", "MEXA", "URUC", "QSL", "CLPD"}
LEAGUE_RE = re.compile(r"^[A-Z]{1,4}\d[A-Z]?$")

ap = argparse.ArgumentParser()
ap.add_argument("--dump", default="all_data/all_data/database.dump")
ap.add_argument("--index", default="data/index/index.sqlite")
a = ap.parse_args()

db = sqlite3.connect(a.index)
db.executescript("""
PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
DROP TABLE IF EXISTS player_stats;
CREATE TABLE player_stats(player_id INTEGER PRIMARY KEY, apps INT, goals INT, assists INT, minutes INT, yellow INT, red INT, own_goals INT, pens INT,
  best_season_goals INT, seasons INT, apps_league INT, apps_top INT, apps_big5 INT, goals_top INT, goals_big5 INT, apps_tr INT, goals_tr INT, decades INT NOT NULL DEFAULT 0);
""")
known = {r[0] for r in db.execute("SELECT id FROM players")}
proc = subprocess.Popen(["pg_restore", "--data-only", "-t", "player_season_performance_gzip", "-f", "-", a.dump], stdout=subprocess.PIPE, bufsize=1 << 22)
t0 = time.time(); n = 0; kept = 0; batch = []; started = False
club_seasons = collections.defaultdict(set)     # (kulüp, üst lig kodu) -> o ligde maç oynadığı sezonlar ("tek lig" kapsamı için)
for raw in proc.stdout:
    if not started:
        started = raw.startswith(b"COPY "); continue
    if raw.startswith(b"\\."): break
    # alanlar: source_id \t body_gzip \t summary \t ...   (body_gzip çok uzun; bölmeyi sınırla)
    try:
        sid, _body, rest = raw.split(b"\t", 2)
        summary = rest.split(b"\t", 1)[0]
    except ValueError:
        continue
    n += 1
    pid = int(sid)
    if pid not in known: continue
    s = json.loads(summary.replace(b"\\\\", b"\\"))
    apps = goals = assists = minutes = yellow = red = og = 0
    al = at = a5 = gt = g5 = atr = gtr = 0; decades = 0
    per_season = collections.Counter()
    for st in s.get("stats") or []:
        ap_ = st.get("appearances") or 0; g = st.get("goals") or 0; comp = st.get("competitionId") or ""
        apps += ap_; goals += g; assists += st.get("assists") or 0; minutes += st.get("minutesPlayed") or 0
        yellow += st.get("yellowCards") or 0; red += (st.get("redCards") or 0) + (st.get("secondYellowCards") or 0); og += st.get("ownGoals") or 0
        per_season[st.get("seasonId")] += g
        yr = str(st.get("seasonId") or "")
        if ap_ > 0 and yr.isdigit() and 1980 <= int(yr) <= 2029: decades |= 1 << ((int(yr) - 1980) // 10)
        if ap_ > 0 and st.get("clubId") and st.get("seasonId") and (comp in TOP_EXTRA or TOP_RE.match(comp)):
            club_seasons[(str(st["clubId"]), comp)].add(str(st["seasonId"]))
        if LEAGUE_RE.match(comp) or comp in TOP_EXTRA:
            al += ap_
            if comp in BIG5 or comp in TOP_EXTRA or TOP_RE.match(comp): at += ap_; gt += g
            if comp in BIG5: a5 += ap_; g5 += g
            if comp == "TR1": atr += ap_; gtr += g
    if apps == 0: continue
    pens = (((s.get("aggregated") or {}).get("goalStatistics") or {}).get("penaltyShooterGoalsScored")) or 0
    batch.append((pid, apps, goals, assists, minutes, yellow, red, og, pens, max(per_season.values() or [0]), len(per_season), al, at, a5, gt, g5, atr, gtr, decades)); kept += 1
    if len(batch) >= 50000:
        db.executemany("INSERT OR REPLACE INTO player_stats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", batch); batch.clear()
        print(f"  {n} satır, {kept} oyuncu ({time.time()-t0:.0f}s)", flush=True)
db.executemany("INSERT OR REPLACE INTO player_stats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", batch)
# club_leagues(club_id, comp, seasons): kulübün o üst ligde (en az bir oyuncusu maça çıkmış) kaç sezonu var
known_clubs = {r[0] for r in db.execute("SELECT id FROM clubs")}
db.executescript("DROP TABLE IF EXISTS club_leagues; CREATE TABLE club_leagues(club_id INT NOT NULL, comp TEXT NOT NULL, seasons INT NOT NULL, PRIMARY KEY(club_id, comp)) WITHOUT ROWID;")
db.executemany("INSERT OR REPLACE INTO club_leagues VALUES(?,?,?)", [(int(c), comp, len(v)) for (c, comp), v in club_seasons.items() if c.isdigit() and int(c) in known_clubs])
db.commit(); proc.kill()
for comp in ("GB1", "ES1", "IT1", "L1", "FR1", "TR1", "NL1", "PO1"):
    print(f"  {comp}: en az 3 sezon {db.execute('SELECT COUNT(*) FROM club_leagues WHERE comp=? AND seasons>=3', (comp,)).fetchone()[0]} kulüp")
print(f"bitti: {n} satır okundu, {kept} oyuncu yazıldı ({time.time()-t0:.0f}s)")
print("on yıl dağılımı (80,90,00,10,20):", [db.execute("SELECT COUNT(*) FROM player_stats WHERE decades & ?", (1 << i,)).fetchone()[0] for i in range(5)], "| hiçbiri:", db.execute("SELECT COUNT(*) FROM player_stats WHERE decades = 0").fetchone()[0])
for name in ("Lionel Messi", "Cristiano Ronaldo", "Robert Lewandowski", "Hakan Şükür", "Burak Yılmaz", "Zlatan Ibrahimović"):
    r = db.execute("SELECT p.name, s.apps, s.goals, s.assists, s.goals_big5, s.best_season_goals, s.seasons FROM players p JOIN player_stats s ON s.player_id=p.id WHERE p.name=? ORDER BY s.apps DESC LIMIT 1", (name,)).fetchone()
    print(" ", r)
