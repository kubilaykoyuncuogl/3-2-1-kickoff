"""Dil paketlerini karşılaştırır: tr.json'a göre eksik/fazla anahtar ve yer tutucu uyuşmazlığı."""
import json, pathlib, re, sys
d = pathlib.Path(__file__).resolve().parents[1] / "app" / "lang"      # asıl kopya Expo uygulamasında; game/lang Godot sürümüyle birlikte kalkacak
base = json.loads((d / "tr.json").read_text())
spec = lambda s: re.findall(r"%[\.\d]*[sdf]", s)
bad = 0
for f in sorted(d.glob("*.json")):
    if f.name == "tr.json": continue
    o = json.loads(f.read_text())
    miss = sorted(set(base) - set(o)); extra = sorted(set(o) - set(base))
    fmt = [k for k in base if k in o and spec(base[k]) != spec(o[k])]
    print(f"{f.name}: {len(o)} anahtar, eksik {len(miss)}, fazla {len(extra)}, yer tutucu hatası {len(fmt)}")
    for k in miss: print("  eksik:", k)
    for k in extra: print("  fazla:", k)
    for k in fmt: print("  yer tutucu:", k, spec(base[k]), "≠", spec(o[k]))
    bad += len(miss) + len(fmt)
sys.exit(1 if bad else 0)
