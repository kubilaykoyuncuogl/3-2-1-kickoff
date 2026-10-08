#!/usr/bin/env python3
"""Haftanın maçı, kariyer yolu biçimi: iki kulübün her biri için, verilen yıllarda o kulüpte bulunmuş tanınır oyuncuların kulüp yolları.
Oyuncu tarafını seçer ve yalnızca o kulüpten geçmiş oyuncular sorulur (kulüpler sırayla açılır, oyuncu tahmin edilir).

  python3 tools/build_weekly_career.py --a "Manchester City" --b "Liverpool FC" --slug mci-liv --date 2026-10-17 \\
      --a-short "Man City" --b-short Liverpool --a-colors "#6CABDD,#1C2C5B" --b-colors "#C8102E,#FFFFFF" [--from 2000 --to 2026] [--no-current]
  → server/weekly/<slug>.json (+ current.json: sunucunun okuduğu etkin hafta)

Kaynak: data/index/index.sqlite (kulüp adları index'teki adla tam eşleşmeli). Oyuncu kimlikleri index'in kendi numaralarıdır; dosya istemciye gitmez.
Yol kuralı index_service._path ile aynı: kiralık dönüşleri atılır, art arda aynı kulüp birleşir.
Not: index'te kulüp bazında maç sayısı yok; "tanınır" ölçüsü oyuncunun toplam maç sayısıdır, kulüpte hiç oynamadan ayrılmış biri de girebilir."""
import argparse, json, pathlib, shutil, sqlite3, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True); ap.add_argument("--b", required=True); ap.add_argument("--slug", required=True)
ap.add_argument("--a-short", default=""); ap.add_argument("--b-short", default="")
ap.add_argument("--a-colors", default="#5E4BC9,#FFFFFF", help="zemin,yazı"); ap.add_argument("--b-colors", default="#E9A23B,#1B1A21")
ap.add_argument("--date", default=""); ap.add_argument("--from", dest="y0", type=int, default=2000); ap.add_argument("--to", dest="y1", type=int, default=2026)
ap.add_argument("--min-apps", type=int, default=150, help="toplam maç (tanınırlık)"); ap.add_argument("--min-apps-short", type=int, default=350, help="2-3 kulüplü kısa yollar için")
ap.add_argument("--index", default=str(ROOT / "data/index/index.sqlite")); ap.add_argument("--no-current", action="store_true")
A = ap.parse_args()

db = sqlite3.connect(A.index)
def club(name: str) -> int:
    r = db.execute("SELECT id FROM clubs WHERE name = ?", (name,)).fetchall()
    if len(r) != 1: sys.exit(f"kulüp bulunamadı ya da birden çok: {name!r} (index'teki adıyla yaz)")
    return r[0][0]

PATH_SQL = """SELECT s.club_id, c.name, s.date, s.kind, s.fee, co.name, c.defunct FROM stints s JOIN clubs c ON c.id = s.club_id
              LEFT JOIN countries co ON co.id = c.country_id WHERE s.player_id = ? ORDER BY s.seq"""
def path(pid: int) -> list:
    out = []
    for cid, name, date, kind, fee, country, defunct in db.execute(PATH_SQL, (pid,)):
        if kind == "loan_end": continue
        if out and out[-1]["club_id"] == cid:
            if out[-1]["kind"] == "loan" and kind != "loan": out[-1]["kind"] = "sale" if (fee or 0) > 0 else "free"      # kiralık geldi, sonra bonservisi alındı
            continue
        k = "start" if not out else ("loan" if kind == "loan" else ("sale" if (fee or 0) > 0 else "free"))
        out.append({"club_id": cid, "club": name, "year": int(date[:4]) if date else None, "kind": k, "country": country, "defunct": bool(defunct)})
    return out

def side(cid: int) -> list:
    rows = db.execute("""SELECT p.id, p.name, p.birth_year, COALESCE(ps.apps, 0) FROM players p JOIN player_clubs pc ON pc.player_id = p.id
                         LEFT JOIN player_stats ps ON ps.player_id = p.id WHERE pc.club_id = ? AND COALESCE(ps.apps, 0) >= ?""", (cid, A.min_apps)).fetchall()
    out = []
    for pid, name, born, apps in rows:
        p = path(pid)
        if not (2 <= len(p) <= 11) or (len(p) < 4 and apps < A.min_apps_short): continue
        # kulüpte bulunduğu dönem istenen yıllarla kesişmeli (dönem: geliş yılı → sonraki kulübe geçiş yılı)
        hit = False
        for i, st in enumerate(p):
            if st["club_id"] != cid or st["year"] is None: continue
            # son kulübüyse bitiş bilinmez: futbolu en geç 40 yaşında bıraktığı varsayılır (yoksa 1977'de gelen biri "hâlâ orada" görünür)
            end = next((x["year"] for x in p[i + 1:] if x["year"] is not None), (born + 40) if born else st["year"] + 15)
            if st["year"] <= A.y1 and end >= A.y0: hit = True
        if not hit: continue
        out.append({"id": pid, "name": name, "born": born, "apps": apps, "clubs": [{k: v for k, v in st.items() if k != "club_id"} for st in p]})
    out.sort(key=lambda x: -x["apps"])
    return out

col = lambda s: [c.strip() for c in s.split(",")][:2]
ca, cb = side(club(A.a)), side(club(A.b))
out = {"slug": A.slug, "date": A.date, "format": "career", "years": [A.y0, A.y1],
       "a": {"name": A.a, "short": A.a_short or A.a, "colors": col(A.a_colors)}, "b": {"name": A.b, "short": A.b_short or A.b, "colors": col(A.b_colors)},
       "careers": {"a": ca, "b": cb}}
wd = ROOT / "server" / "weekly"; wd.mkdir(exist_ok=True)
p = wd / f"{A.slug}.json"; p.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n")
if not A.no_current: shutil.copyfile(p, wd / "current.json")
print(f"yazıldı: {p.relative_to(ROOT)}" + ("" if A.no_current else " (+ current.json)"))
for nm, c in ((A.a, ca), (A.b, cb)):
    print(f"{nm}: {len(c)} oyuncu · kısa yol (2-3 kulüp) {sum(len(x['clubs']) < 4 for x in c)}")
    print("  baş:", ", ".join(x["name"] for x in c[:14]))
    print("  son:", ", ".join(x["name"] for x in c[-8:]))
