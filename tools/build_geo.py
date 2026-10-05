"""Ülke ve lig adlarını mevcut index.sqlite'a ekler: countries(id, name), competitions(id, name).
Ülke id→ad eşlemesi dökümde hazır yok; profili olan oyuncuların (uyruk id'si ↔ uyruk adı) ve (doğum ülkesi id'si ↔ ad) çiftlerinden çoğunluk oyuyla çıkarılır.
    python tools/build_geo.py    (sonra yeniden şifrele)"""
import json, sqlite3, collections, pathlib
T = pathlib.Path("data/raw/tsv")
def rows(name):
    with open(T / name, "rb") as f:
        for line in f:
            if line.startswith(b"COPY "): break
        for line in f:
            if line.startswith(b"\\."): break
            yield line.rstrip(b"\n").split(b"\t")
J = lambda b: json.loads(b.replace(b"\\\\", b"\\"))
prof = {}                                   # source_id -> (ilk uyruk adı, doğum ülkesi adı)
for r in rows("players.sql"):
    if r[5] == b"\\N": continue
    p = J(r[5]); cit = p.get("citizenship") or []; pob = (p.get("placeOfBirth") or {}).get("country")
    prof[r[2].decode()] = (cit[0] if cit else None, pob)
votes = collections.defaultdict(collections.Counter)
for r in rows("player_core_json.sql"):
    sid = r[0].decode()
    if sid not in prof: continue
    p = J(r[1]); cit, pob = prof[sid]
    nid = ((p.get("nationalityDetails") or {}).get("nationalities") or {}).get("nationalityId")
    bid = (p.get("birthPlaceDetails") or {}).get("countryOfBirthId")
    if nid and cit: votes[int(nid)][cit] += 1
    if bid and pob: votes[int(bid)][pob] += 1
countries = {cid: c.most_common(1)[0][0] for cid, c in votes.items()}
countries.setdefault(137, "Qatar")      # profillerde yok, elle
comps = {}
for r in rows("reference_entities.sql"):
    if r[0] != b"competition" or r[3] == b"\\N": continue
    p = J(r[3]); comps[r[1].decode()] = p.get("name") or p.get("shortName")
db = sqlite3.connect("data/index/index.sqlite")
db.executescript("DROP TABLE IF EXISTS countries; DROP TABLE IF EXISTS competitions; CREATE TABLE countries(id INTEGER PRIMARY KEY, name TEXT); CREATE TABLE competitions(id TEXT PRIMARY KEY, name TEXT);")
db.executemany("INSERT INTO countries VALUES(?,?)", countries.items()); db.executemany("INSERT INTO competitions VALUES(?,?)", [(k, v) for k, v in comps.items() if v]); db.commit()
cov = db.execute("SELECT COUNT(*), SUM(co.name IS NOT NULL) FROM clubs c LEFT JOIN countries co ON co.id=c.country_id WHERE c.fame > 500").fetchone()
print("ülke:", len(countries), "lig:", len(comps), "| ünlü kulüplerde ülke adı bulunan:", cov)
print(db.execute("SELECT c.name, co.name, cp.name FROM clubs c LEFT JOIN countries co ON co.id=c.country_id LEFT JOIN competitions cp ON cp.id=c.competition_id WHERE c.name IN ('Galatasaray','Bayern Munich','CA Boca Juniors','Al-Nassr FC','Celtic FC','Los Angeles Galaxy','AFC Ajax','Ajax Amsterdam')").fetchall())
print("eksik ülkeli ünlü kulüpler:", db.execute("SELECT c.name, c.country_id FROM clubs c LEFT JOIN countries co ON co.id=c.country_id WHERE co.name IS NULL AND c.fame>800 ORDER BY c.fame DESC LIMIT 12").fetchall())
