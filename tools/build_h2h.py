#!/usr/bin/env python3
"""Haftanın maçı için iki kulübün birbirine karşı oynadığı maçlardaki oyuncu istatistiklerini çıkarır.

  python3 tools/build_h2h.py --a "Trabzonspor" --b "Beşiktaş JK" --slug ts-bjk [--title "Trabzonspor – Beşiktaş"] [--date 2026-10-10]
  → server/weekly/<slug>.json   (oyuncu adı, taraf(lar), maç, gol, asist, dakika, kart, galibiyet; kaynak kimliği yazılmaz)

Kaynak: dökümdeki football.match_records (oyuncu × maç; kulüp, rakip, o maçtaki istatistikler). Tablo akıtılarak okunur,
yalnızca iki kulübün karşılaştığı satırlar ayrıştırılır. Kulüp adları kaynak adla tam eşleşmeli (reference_entities).
Not: kaynak her maçı / her oyuncuyu kapsamayabilir (eski sezonlarda eksik olur); çıktı başındaki özet kapsamı gösterir."""
import argparse, collections, json, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True); ap.add_argument("--b", required=True); ap.add_argument("--slug", required=True)
ap.add_argument("--title", default=""); ap.add_argument("--date", default="")
ap.add_argument("--dump", default=str(ROOT / "all_data/all_data/database.dump"))
A = ap.parse_args()

def club_id(name: str) -> str:
    key = ("club\t", "\t" + name + "\t")
    with open(ROOT / "data/raw/tsv/reference_entities.sql", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(key[0]) and key[1] in line[:120]:
                return line.split("\t", 3)[1]
    sys.exit(f"kulüp bulunamadı: {name!r} (reference_entities'teki adıyla yaz)")

ida, idb = club_id(A.a), club_id(A.b)
print(f"{A.a} = {ida} · {A.b} = {idb}", flush=True)
needles = [(f'"clubId": "{ida}"'.encode(), f'"clubId": "{idb}"'.encode())]

t0 = time.time(); n = 0; hit = 0
P = collections.defaultdict(lambda: {"apps": 0, "starts": 0, "goals": 0, "assists": 0, "minutes": 0, "yellow": 0, "red": 0, "wins": 0, "sides": set(), "years": set()})
matches = set(); card_keys = set()
proc = subprocess.Popen(["pg_restore", "--data-only", "-t", "match_records", "-f", "-", A.dump], stdout=subprocess.PIPE, bufsize=1 << 22)
started = False
for raw in proc.stdout:
    if not started:
        started = raw.startswith(b"COPY "); continue
    if raw.startswith(b"\\."): break
    n += 1
    if n % 2_000_000 == 0: print(f"  {n} satır, {hit} eşleşme ({time.time()-t0:.0f}s)", flush=True)
    if needles[0][0] not in raw or needles[0][1] not in raw: continue
    f = raw.rstrip(b"\n").split(b"\t")
    try: p = json.loads(f[6].replace(b"\\\\", b"\\"))
    except (ValueError, IndexError): continue
    ci = p.get("clubsInformation") or {}; club = ci.get("club") or {}; opp = ci.get("opponent") or {}
    pair = {str(club.get("clubId")), str(opp.get("clubId"))}
    if pair != {ida, idb}: continue
    st = p.get("statistics") or {}
    mins = int((st.get("playingTimeStatistics") or {}).get("playedMinutes") or 0)
    if mins <= 0: continue                                    # kadroda ama oynamadı
    hit += 1; matches.add(f[1])
    g = st.get("goalStatistics") or {}; c = st.get("cardStatistics") or {}
    d = P[int(f[0])]
    d["apps"] += 1; d["minutes"] += mins
    d["starts"] += 1 if (st.get("playingTimeStatistics") or {}).get("isStarting") else 0
    d["goals"] += int(g.get("goalsScoredTotal") or 0); d["assists"] += int(g.get("assists") or 0)
    d["yellow"] += int(c.get("yellowCardGross") or 0)
    # kırmızı / ikinci sarı: alan yalnızca kart varsa gelir ve sayı ya da ayrıntı sözlüğü olabilir
    d["red"] += 1 if any(v and not k.endswith("Rescinded") and (k.lower().startswith("red") or "secondyellow" in k.lower() or "yellowred" in k.lower())
                         for k, v in c.items()) else 0
    card_keys.update(k for k, v in c.items() if v)
    d["wins"] += 1 if int(club.get("goalsTotal") or 0) > int(club.get("opponentGoalsTotal") or 0) else 0
    d["sides"].add("a" if str(club.get("clubId")) == ida else "b")
    d["years"].add(f[5][:4].decode())
proc.kill()
print(f"tarama bitti: {n} satır, {len(matches)} maç, {len(P)} oyuncu ({time.time()-t0:.0f}s) · kart alanları: {sorted(card_keys)}", flush=True)

# oyuncu adları ve doğum yılı (players tablosu: iç kimlik → ad)
names = {}
with open(ROOT / "data/raw/tsv/players.sql", encoding="utf-8", errors="replace") as fh:
    on = False
    for line in fh:
        if not on:
            on = line.startswith("COPY football.players "); continue
        if line.startswith("\\."): break
        f = line.split("\t", 6)
        try: pid = int(f[0])
        except ValueError: continue
        if pid in P:
            born = None
            try: born = int(str(json.loads(f[5].replace("\\\\", "\\")).get("dateOfBirth") or "")[:4])
            except (ValueError, TypeError): pass
            names[pid] = (f[3], born)

players = []
for pid, d in P.items():
    if pid not in names: continue
    nm, born = names[pid]
    players.append({"name": nm, "born": born, "side": "".join(sorted(d["sides"])), "apps": d["apps"], "starts": d["starts"], "goals": d["goals"],
                    "assists": d["assists"], "minutes": d["minutes"], "yellow": d["yellow"], "red": d["red"], "wins": d["wins"],
                    "first": min(d["years"]), "last": max(d["years"])})
players.sort(key=lambda x: (-x["apps"], -x["goals"], x["name"]))
years = sorted({y for d in P.values() for y in d["years"]})
out = {"slug": A.slug, "title": A.title or f"{A.a} – {A.b}", "date": A.date, "a": A.a, "b": A.b, "matches": len(matches),
       "years": [years[0], years[-1]] if years else [], "players": players}
path = ROOT / "server" / "weekly" / f"{A.slug}.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n")
print(f"yazıldı: {path.relative_to(ROOT)} · {len(players)} oyuncu · {len(matches)} maç · {out['years']}")
for key in ("apps", "goals", "assists", "yellow", "red", "wins"):
    top = sorted(players, key=lambda x: -x[key])[:6]
    print(f"  {key:8}", ", ".join(f"{x['name']} {x[key]}" for x in top))
