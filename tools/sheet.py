"""Ekran görüntülerini tek sayfada birleştirir: python3 tools/sheet.py <klasör> <çıktı.png> [sütun=6] [ad filtresi…]"""
import sys, pathlib
from PIL import Image
d = pathlib.Path(sys.argv[1]); out = sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6; flt = sys.argv[4:]
files = [f for f in sorted(d.glob("*.png")) if not flt or any(x in f.name for x in flt)]
ims = [Image.open(f).convert("RGB") for f in files]; w, h = ims[0].size; g = 12
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + g) + g, rows * (h + g) + g), (128, 128, 128))
for i, im in enumerate(ims): sheet.paste(im, (g + (i % cols) * (w + g), g + (i // cols) * (h + g)))
sheet.save(out); print(len(ims), "görüntü →", out, sheet.size)
