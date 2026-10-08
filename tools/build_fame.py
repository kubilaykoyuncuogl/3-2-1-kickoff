#!/usr/bin/env python3
"""Oyuncu ün puanı (players.fame): piyasa değeri + kariyer. Arama önerilerinin, "olası cevaplar" listesinin ve Beşte Bir şıklarının sırası buna bakar.

  python3 tools/build_fame.py [--index data/index/index.sqlite]

build_index puanı yalnızca en yüksek piyasa değerinden kurar; piyasa değeri 2004'ten önce tutulmadığı için eski yıldızlar dipte kalır
(Maradona 3, adaşı genç bir oyuncu 10). Burada üst lig kariyeri eklenir: 5 büyük ligde maç 1, gol 3 · Süper Lig'de maç 0,6, gol 1,8 ·
diğer üst liglerde maç 0,4, gol 1,2 (index_service'teki ünlü havuzu formülüyle aynı ağırlıklar), toplam 8'e bölünür.
player_stats ister (build_stats.py). Yeniden çalıştırmak güvenlidir (puan her seferinde baştan hesaplanır).
Index hattındaki yeri: build_index → build_stats → build_fame → build_geo → finalize_index → add_full_names → encrypt_index."""
import argparse, pathlib, sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument("--index", default=str(ROOT / "data/index/index.sqlite")); A = ap.parse_args()
db = sqlite3.connect(A.index)
CAREER_DIV = 8.0
db.executescript(f"""
UPDATE players SET fame = (COALESCE(mv_max, 0) / 1000000.0) + n_clubs * 0.5;
UPDATE players SET fame = fame + (SELECT (s.apps_big5 * 1.0 + COALESCE(s.apps_tr, 0) * 0.6 + MAX(0, s.apps_top - s.apps_big5 - COALESCE(s.apps_tr, 0)) * 0.4
                                        + s.goals_big5 * 3.0 + COALESCE(s.goals_tr, 0) * 1.8 + MAX(0, s.goals_top - s.goals_big5 - COALESCE(s.goals_tr, 0)) * 1.2) / {CAREER_DIV}
                                 FROM player_stats s WHERE s.player_id = players.id)
  WHERE id IN (SELECT player_id FROM player_stats WHERE apps_top > 0);
""")
db.commit()
print("en ünlü 15:", [(n, round(f)) for n, f in db.execute("SELECT name, fame FROM players ORDER BY fame DESC LIMIT 15")])
for n in ("Hakan Şükür", "Hakan Çalhanoğlu", "Diego Maradona", "Roberto Baggio", "Pedro", "Pedro Neto", "Arda Güler", "Arda Turan"):
    print(" ", n, [(by, round(f)) for by, f in db.execute("SELECT birth_year, fame FROM players WHERE name = ? ORDER BY fame DESC LIMIT 2", (n,))])
