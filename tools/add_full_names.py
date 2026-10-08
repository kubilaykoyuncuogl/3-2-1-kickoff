#!/usr/bin/env python3
"""Oyuncu aramasına tam adları ekler: kaynakta adı tek kelime olan oyuncular (Pedro, Kaká, Hulk…) soyadıyla da bulunsun.

  python3 tools/add_full_names.py [--index data/index/index.sqlite] [--in data/raw/tsv]
  ("pedro rodriguez" → Pedro · 1987; ekranda görünen ad değişmez, yalnızca arama metni eklenir)

Kaynak: player_core_json.sql içindeki displayName (tam ad) ve passportName. Index'te kaynak kimliği kalmadığı için eşleşme
(ad, doğum yılı, milliyet, mevki, en yüksek değer) beşlisiyle yapılır; bu beşli index'te tek değilse o oyuncu atlanır.
Yalnızca Latin harfli adlar eklenir. Tam adlar ayrı bir arama tablosuna (names_full) yazılır: sunucu önce asıl adlarda arar,
yer kalırsa buradan tamamlar. Aynı tabloya yazılsaydı "pedro" yazınca tam adında Pedro geçen herkes (Pedri, João Neves…) öne geçerdi.
Yeniden çalıştırmak güvenlidir (tablo baştan kurulur).
Index hattındaki yeri: build_index → build_stats → build_geo → finalize_index → add_full_names → encrypt_index."""
import argparse, collections, json, pathlib, re, sqlite3, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from normalize import normalize      # noqa: E402
from build_index import copy_rows, jload      # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--index", default=str(ROOT / "data/index/index.sqlite")); ap.add_argument("--in", dest="inp", default=str(ROOT / "data/raw/tsv"))
A = ap.parse_args()

db = sqlite3.connect(A.index)
t0 = time.time()
by_key = collections.defaultdict(list)
for pid, name, by, nat, pos, mv in db.execute("SELECT id, name, birth_year, nat_id, position, mv_max FROM players"):
    by_key[(name, by, nat, pos, mv or 0)].append(pid)
have = collections.defaultdict(set)
for pid, text in db.execute("SELECT player_id, text FROM names"): have[int(pid)].add(text)
print(f"index: {sum(len(v) for v in by_key.values())} oyuncu, {sum(len(v) > 1 for v in by_key.values())} belirsiz anahtar ({time.time()-t0:.0f}s)", flush=True)

LATIN = re.compile(r"^[a-z0-9 \-']+$")
add = []; seen = 0; skipped = 0
for row in copy_rows(pathlib.Path(A.inp) / "player_core_json.sql"):
    p = jload(row[1]); seen += 1
    full = [x for x in (p.get("displayName"), (p.get("nationalityDetails") or {}).get("passportName")) if x]
    if not full: continue
    ld = p.get("lifeDates") or {}; dob = ld.get("dateOfBirth") or ""
    attrs = p.get("attributes") or {}; pos = (attrs.get("position") or {}).get("shortName")
    mv = ((p.get("marketValueDetails") or {}).get("highest") or {}).get("value") or 0
    nat = ((p.get("nationalityDetails") or {}).get("nationalities") or {}).get("nationalityId")
    ids = by_key.get((p.get("name"), int(dob[:4]) if dob[:4].isdigit() else None, nat, pos, int(mv)))
    if not ids: continue
    if len(ids) > 1: skipped += 1; continue
    pid = ids[0]
    for x in full:
        n = normalize(x)
        if not n or not LATIN.match(n) or len(n.split()) > 7 or n in have[pid]: continue
        have[pid].add(n); add.append((pid, n))
db.executescript("DROP TABLE IF EXISTS names_full; CREATE VIRTUAL TABLE names_full USING fts5(player_id UNINDEXED, text, tokenize='unicode61');")
db.executemany("INSERT INTO names_full(player_id, text) VALUES(?, ?)", add); db.commit()
print(f"tarandı: {seen} · eklenen arama metni: {len(add)} · belirsiz olduğu için atlanan: {skipped} ({time.time()-t0:.0f}s)")
for q in ("pedro rodriguez", "ricardo izecson", "givanildo"):
    m = " ".join(f'"{t}"*' for t in normalize(q).split())
    print(" ", q, "→", db.execute("SELECT p.name, p.birth_year FROM names_full n JOIN players p ON p.id = n.player_id WHERE names_full MATCH ? GROUP BY p.id ORDER BY p.fame DESC LIMIT 3", (m,)).fetchall())
