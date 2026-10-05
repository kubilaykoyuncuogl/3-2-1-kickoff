"""data/raw altındaki dosyaların şemasına hızlı bakış (csv/parquet/json)."""
import sys, pathlib
import pandas as pd

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
for p in sorted(root.rglob("*")):
    if p.suffix.lower() not in {".csv", ".parquet", ".json", ".jsonl"}:
        continue
    print("=" * 80, "\n", p, f"({p.stat().st_size/1e6:.1f} MB)")
    try:
        if p.suffix == ".csv":
            df = pd.read_csv(p, nrows=5)
        elif p.suffix == ".parquet":
            df = pd.read_parquet(p).head()
        else:
            df = pd.read_json(p, lines=p.suffix == ".jsonl", nrows=5 if p.suffix == ".jsonl" else None)
        print(df.dtypes, "\n", df.head(), sep="\n")
    except Exception as e:
        print("okunamadı:", e)
