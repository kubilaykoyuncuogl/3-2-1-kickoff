"""Ham dataset → game/data index. Kolon adları dataset incelenince doldurulacak (bkz. inspect_dataset.py).

Çıktılar:
  game/data/teams.json        [{id, name, norm, aliases[], country}]
  game/data/index.sqlite      players(id, name, norm), player_teams(player_id, team_id)
"""
import argparse, json, sqlite3, pathlib
import pandas as pd
from normalize import normalize

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", default="data/raw")
ap.add_argument("--out", default="game/data")
args = ap.parse_args()
out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)

# TODO: dataset şemasına göre doldur
# df = pd.read_csv(pathlib.Path(args.inp) / "....csv", usecols=[...])
raise SystemExit("build_index.py: dataset şeması henüz tanımlı değil, önce inspect_dataset.py çalıştır.")
