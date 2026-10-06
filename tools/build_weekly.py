#!/usr/bin/env python3
"""Haftanın maçı verisi: iki kulübün oyuncularının O kulüp formasıyla istatistikleri (maç, gol, asist, sarı kart, sezon).

  python3 tools/build_weekly.py --a "Trabzonspor" --b "Beşiktaş JK" --slug ts-bjk --date 2026-10-10 \\
      --a-short Trabzonspor --b-short Beşiktaş --a-colors "#7A1230,#62B5E5" --b-colors "#111111,#FFFFFF"
  → server/weekly/<slug>.json ve server/weekly/current.json (sunucunun okuduğu etkin hafta)

Kaynak: dökümdeki player_season_performance_gzip.summary (oyuncu × sezon × kulüp × müsabaka). Yalnızca iki kulübün satırları toplanır.
Bir oyuncu iki kulüpte de oynadıysa daha çok maça çıktığı tarafa yazılır (soru hep "bir A'lı, bir B'li" gelir).
Eski sezonlarda gol / asist kaynakta boş olabilir: o oyuncu gol ve asist sorularına girmez (goals / assists = null).
Çıktıda kaynak kimliği yoktur. Kulüp adları kaynak adla tam eşleşmeli (data/raw/tsv/reference_entities.sql)."""
import argparse, collections, json, pathlib, shutil, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True); ap.add_argument("--b", required=True); ap.add_argument("--slug", required=True)
ap.add_argument("--a-short", default=""); ap.add_argument("--b-short", default="")
ap.add_argument("--a-colors", default="#5E4BC9,#FFFFFF", help="zemin,yazı"); ap.add_argument("--b-colors", default="#E9A23B,#1B1A21")
ap.add_argument("--date", default=""); ap.add_argument("--min-apps", type=int, default=15)
ap.add_argument("--dump", default=str(ROOT / "all_data/all_data/database.dump")); ap.add_argument("--no-current", action="store_true")
A = ap.parse_args()

def club_id(name: str) -> str:
    with open(ROOT / "data/raw/tsv/reference_entities.sql", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("club\t") and ("\t" + name + "\t") in line[:120]: return line.split("\t", 3)[1]
    sys.exit(f"kulüp bulunamadı: {name!r} (reference_entities'teki adıyla yaz)")

ida, idb = club_id(A.a), club_id(A.b)
print(f"{A.a} = {ida} · {A.b} = {idb}", flush=True)
na, nb = f'"clubId": "{ida}"'.encode(), f'"clubId": "{idb}"'.encode()
new = lambda: {"apps": 0, "goals": 0, "assists": 0, "yellow": 0, "red": 0, "minutes": 0, "seasons": set(), "gaps": False}
S = collections.defaultdict(lambda: {"a": new(), "b": new()})
t0 = time.time(); n = 0
proc = subprocess.Popen(["pg_restore", "--data-only", "-t", "player_season_performance_gzip", "-f", "-", A.dump], stdout=subprocess.PIPE, bufsize=1 << 22)
started = False
for raw in proc.stdout:
    if not started:
        started = raw.startswith(b"COPY "); continue
    if raw.startswith(b"\\."): break
    n += 1
    if n % 300000 == 0: print(f"  {n} oyuncu, {len(S)} eşleşme ({time.time()-t0:.0f}s)", flush=True)
    try:
        sid, _body, rest = raw.split(b"\t", 2)
    except ValueError: continue
    summary = rest.split(b"\t", 1)[0]
    if na not in summary and nb not in summary: continue
    try: s = json.loads(summary.replace(b"\\\\", b"\\"))
    except ValueError: continue
    for st in s.get("stats") or []:
        cid = str(st.get("clubId") or "")
        if cid not in (ida, idb) or st.get("isNationalTeam"): continue
        ap_ = st.get("appearances") or 0
        if ap_ <= 0: continue
        d = S[int(sid)]["a" if cid == ida else "b"]
        d["apps"] += ap_; d["minutes"] += st.get("minutesPlayed") or 0
        if st.get("goals") is None or st.get("assists") is None: d["gaps"] = True
        d["goals"] += st.get("goals") or 0; d["assists"] += st.get("assists") or 0
        d["yellow"] += st.get("yellowCards") or 0; d["red"] += (st.get("redCards") or 0) + (st.get("secondYellowCards") or 0)
        if st.get("seasonId"): d["seasons"].add(str(st["seasonId"]))
proc.kill()
print(f"tarama bitti: {n} oyuncu, {len(S)} eşleşme ({time.time()-t0:.0f}s)", flush=True)

# adlar: players tablosu (source_id → ad, doğum yılı)
info = {}
with open(ROOT / "data/raw/tsv/players.sql", encoding="utf-8", errors="replace") as fh:
    on = False
    for line in fh:
        if not on:
            on = line.startswith("COPY football.players "); continue
        if line.startswith("\\."): break
        f = line.split("\t", 6)
        try: sid = int(f[2])
        except (ValueError, IndexError): continue
        if sid in S:
            born = None
            try: born = int(str(json.loads(f[5].replace("\\\\", "\\")).get("dateOfBirth") or "")[:4])
            except (ValueError, TypeError): pass
            info[sid] = (f[3], born)

players = []
for sid, sides in S.items():
    if sid not in info: continue
    side = "a" if sides["a"]["apps"] >= sides["b"]["apps"] else "b"
    d = sides[side]
    if d["apps"] < A.min_apps: continue
    nm, born = info[sid]
    ys = sorted(d["seasons"])
    players.append({"name": nm, "born": born, "side": side, "apps": d["apps"], "goals": None if d["gaps"] else d["goals"], "assists": None if d["gaps"] else d["assists"],
                    "yellow": d["yellow"], "red": d["red"], "minutes": d["minutes"], "seasons": len(ys), "first": ys[0] if ys else None, "last": ys[-1] if ys else None,
                    "both": bool(sides["a"]["apps"] and sides["b"]["apps"])})
players.sort(key=lambda x: (x["side"], -x["apps"]))
col = lambda s: [c.strip() for c in s.split(",")][:2]
out = {"slug": A.slug, "date": A.date,
       "a": {"name": A.a, "short": A.a_short or A.a, "colors": col(A.a_colors)}, "b": {"name": A.b, "short": A.b_short or A.b, "colors": col(A.b_colors)},
       "players": players}
wd = ROOT / "server" / "weekly"; wd.mkdir(exist_ok=True)
path = wd / f"{A.slug}.json"; path.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n")
if not A.no_current: shutil.copyfile(path, wd / "current.json")
print(f"yazıldı: {path.relative_to(ROOT)}" + ("" if A.no_current else " (+ current.json)"))
for side, nm in (("a", A.a), ("b", A.b)):
    ps = [p for p in players if p["side"] == side]
    print(f"{nm}: {len(ps)} oyuncu · gol/asist verisi olan {sum(p['goals'] is not None for p in ps)}")
    for key in ("apps", "goals", "assists", "yellow", "seasons"):
        top = sorted((p for p in ps if p[key] is not None), key=lambda x: -x[key])[:7]
        print(f"  {key:8}", ", ".join(f"{x['name']} {x[key]}" for x in top))
