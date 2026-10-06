#!/usr/bin/env python3
"""Bot ayarı: botları birbirine on binlerce maç oynatır ve davranış parametrelerini, Elo farkı ile kazanma oranı
Elo formülüne uyacak şekilde seçer (200 Elo fark ≈ %76). Sonucu server/game/bot_params.json'a yazar.

  set -a; . ./.env; set +a; .venv/bin/python tools/bot_sim.py              # ızgara araması + doğrulama (yaklaşık 100 bin maç)
  ... tools/bot_sim.py --check                                             # yalnızca mevcut parametrelerle doğrulama tablosu
  ... tools/bot_sim.py --scope TR1 --check                                 # başka kapsamda davranış

Gerçek kulüp çiftleri ve gerçek ortak oyuncu verisi kullanılır (index bellekte açılır, ~15 sn). Kurallar maçla aynı:
15 sn tur, yanlışta 5 sn kilit, 3 puan, bir takım bir kez, ortak oyuncusuz çift oynanmaz (art arda 3 → berabere).
Sınır: bu, botların kendi içinde tutarlı olmasını sağlar. Bir botun "1000 Elo"su gerçek bir 1000 Elo oyuncuya denk mi,
onu ancak canlı sonuçlar gösterir (bot_params.json OFFSET; sunucu logunda "[bot] result" satırları)."""
import argparse, json, pathlib, random, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server import index_service as ix          # noqa: E402
from server.game import bots                    # noqa: E402
from server.game.consts import MAX_INVALID_PAIRS, ROUND_MS, WIN_SCORE   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--scope", default="all"); ap.add_argument("--check", action="store_true"); ap.add_argument("--round", type=int, default=15, help="tur süresi (sn): 10, 15, 30")
ap.add_argument("--grid-matches", type=int, default=250); ap.add_argument("--final-matches", type=int, default=2500)
A = ap.parse_args()

t0 = time.time(); ix._load(); print(f"index açıldı ({time.time()-t0:.0f}s)", flush=True)
TIERS = ix.tiers[A.scope]
AVAIL = [t for t in range(1, ix.N_TIERS + 1) if TIERS[t]]
_info: dict = {}
stats = {"rounds": 0, "nobody": 0, "no_common": 0, "t_sum": 0.0, "t_n": 0}


def pick(theta: float, used: set, rng: random.Random):
    avail = AVAIL[:max(1, bots.max_tier(theta))]
    for _ in range(12):
        t = rng.choices(avail, weights=[1.0 / (1 + k) for k in range(len(avail))])[0]
        cand = [c for c in TIERS[t] if c not in used]
        if cand: return rng.choice(cand)
    return None


def info(a: int, b: int):
    k = (a, b) if a < b else (b, a)
    v = _info.get(k)
    if v is None:
        r = ix.bot_pair_info(k[0], k[1], 0); v = (r["best_rank"], r["total"]); _info[k] = v
    return v


def first_right(events):
    return next((t for t, kind in events if kind == "right"), None)


def match(ta: float, tb: float, P: dict, rng: random.Random, tr=bots.traits_of("")) -> float:
    """A'nın sonucu: 1 kazandı, 0 kaybetti, 0.5 berabere."""
    used: set = set(); sa = sb = 0; invalid = 0
    for _ in range(40):
        ca = pick(ta, used, rng); cb = pick(tb, used | {ca}, rng)
        if ca is None or cb is None: break
        rank, total = info(ca, cb)
        if total == 0:
            invalid += 1; stats["no_common"] += 1
            if invalid >= MAX_INVALID_PAIRS: return 0.5
            continue
        invalid = 0; used.update((ca, cb))
        d = bots.difficulty(rank, total)
        fa = first_right(bots.plan_round(ta, d, tr, rng, P, A.round * 1000)); fb = first_right(bots.plan_round(tb, d, tr, rng, P, A.round * 1000))
        stats["rounds"] += 1
        if fa is None and fb is None: stats["nobody"] += 1; continue
        w = min(x for x in (fa, fb) if x is not None); stats["t_sum"] += w; stats["t_n"] += 1
        if fb is None or (fa is not None and fa <= fb): sa += 1
        else: sb += 1
        if sa >= WIN_SCORE: return 1.0
        if sb >= WIN_SCORE: return 0.0
    return 0.5 if sa == sb else (1.0 if sa > sb else 0.0)


DIFFS = [0, 100, 200, 300, 400, 600]
CENTERS = [900, 1100, 1300, 1600]
expected = lambda d: 1.0 / (1.0 + 10.0 ** (-d / 400.0))


def evaluate(P: dict, n: int, seed: int):
    rng = random.Random(seed); rows = []; sse = 0.0
    for d in DIFFS:
        tot = 0.0; cnt = 0
        for c in CENTERS:
            for _ in range(n):
                tot += match(c + d / 2, c - d / 2, P, rng); cnt += 1
        share = tot / cnt; rows.append((d, share, expected(d))); sse += (share - expected(d)) ** 2
    return sse, rows


def table(rows):
    print("  Elo farkı   güçlü taraf kazanma   Elo beklentisi")
    for d, share, exp in rows: print(f"  {d:8d}   {share*100:18.1f}%   {exp*100:13.1f}%")


if A.check:
    P = bots.load_params()
else:
    best = None; n_total = 0
    print("ızgara araması…", flush=True)
    for s_k in (250.0, 350.0, 450.0, 600.0, 800.0):
        for t_el in (500.0, 800.0, 1200.0, 2000.0):
            P = dict(bots.DEFAULT_PARAMS, S_K=s_k, T_EL=t_el)
            sse, _rows = evaluate(P, A.grid_matches, 1); n_total += A.grid_matches * len(DIFFS) * len(CENTERS)
            print(f"  S_K={s_k:5.0f} T_EL={t_el:5.0f}  hata={sse:.4f}", flush=True)
            if best is None or sse < best[0]: best = (sse, P)
    P = best[1]; print(f"seçilen: S_K={P['S_K']:.0f} T_EL={P['T_EL']:.0f}  ({n_total} maç, {time.time()-t0:.0f}s)")
    old = bots.load_params(); P["OFFSET"] = old.get("OFFSET", 0.0)      # canlı ayarı ezme
    bots.PARAMS_PATH.write_text(json.dumps(P, indent=1) + "\n"); print("yazıldı:", bots.PARAMS_PATH.relative_to(ROOT))

for k in stats: stats[k] = 0
sse, rows = evaluate(P, A.final_matches, 7)
print(f"\ndoğrulama ({A.final_matches * len(DIFFS) * len(CENTERS)} maç, kapsam {A.scope}, tur {A.round} sn, hata {sse:.4f}):"); table(rows)
print(f"  tur başına: kimse bilemedi %{100*stats['nobody']/max(1,stats['rounds']):.0f} · ortalama doğru cevap süresi {stats['t_sum']/max(1,stats['t_n'])/1000:.1f} sn"
      f" · ortak oyuncusuz çift %{100*stats['no_common']/max(1,stats['rounds']+stats['no_common']):.0f} · farklı çift {len(_info)}")
print("  güç başına (eşit rakibe karşı tur davranışı):")
rng = random.Random(3)
for th in (850, 1000, 1150, 1300, 1480, 1800):
    for k in stats: stats[k] = 0
    for _ in range(600): match(th, th, P, rng)
    print(f"    {th}: en derin tier {bots.max_tier(th)} · kimse bilemedi %{100*stats['nobody']/max(1,stats['rounds']):.0f} · süre {stats['t_sum']/max(1,stats['t_n'])/1000:.1f} sn")
