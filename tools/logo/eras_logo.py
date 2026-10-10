#!/usr/bin/env python3
"""Logoyu yazı dosyalarından çizgiye çevirir: "3-2-1" ITC Eras Bold, "KICKOFF" ITC Eras Ultra, tireler amber.

  python3 tools/logo/eras_logo.py --fonts "<ITC Eras .otf dosyalarının klasörü>"
  → design/logo/*.svg (dikey logo, yatay logo, ikon) + app/src/ui/logo.ts (uygulamadaki Wordmark'ın çizgileri)

Yazı dosyaları repoda yok (lisanslı); çıktılarda yalnızca harflerin çizgileri bulunur, yazı gömülmez.
Dikey logoda iki satır mürekkep kenarlarından hizalıdır: "3"ün solu ile "K"nin solu, "1"in sağı ile son "F"nin sağı aynı çizgide;
KICKOFF harf aralığıyla 3-2-1'in genişliğine yayılır."""
import argparse, json, pathlib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--fonts", required=True); ap.add_argument("--out", default=str(ROOT / "design/logo")); ap.add_argument("--app", default=str(ROOT / "app/src/ui/logo.ts"))
A = ap.parse_args()

K = 0.34            # KICKOFF'un punto oranı (3-2-1 = 1)
DROP = 519          # iki satırın taban çizgileri arası (3-2-1'in 1000 birimlik ölçüsünde)
GAP = 460           # yatay logoda iki parça arası boşluk
THEMES = {"acik": ("#1B1A21", "#E9A23B"), "koyu": ("#ECEBF2", "#F0B45A")}      # yazı, tire (palette.ts fg / amber_fill)
VIOLET, WHITE, AMBER = "#5E4BC9", "#FFFFFF", "#E9A23B"

class Face:
    def __init__(self, path):
        self.f = TTFont(path); self.gs = self.f.getGlyphSet(); self.cm = self.f.getBestCmap()
    def run(self, text, scale=1.0, x=0.0, y=0.0, spacing=0.0):
        """→ [(harf, yol, (x0, y0, x1, y1))]; y aşağı doğru artar, (x, y) ilk harfin taban çizgisindeki başlangıcı"""
        out = []
        for ch in text:
            g = self.gs[self.cm[ord(ch)]]
            t = (scale, 0, 0, -scale, x, y)
            pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip(".")); g.draw(TransformPen(pen, t))
            bp = BoundsPen(self.gs); g.draw(TransformPen(bp, t))
            out.append((ch, pen.getCommands(), bp.bounds)); x += g.width * scale + spacing
        return out

def box(*runs):
    b = [r[2] for run in runs for r in run]
    return min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b)

def parts(num, word):
    return {"digits": " ".join(d for ch, d, _ in num if ch != "-"), "dashes": " ".join(d for ch, d, _ in num if ch == "-"), "word": " ".join(d for _, d, _ in word)}

def group(p, fg, dash):
    return f'<path fill="{fg}" d="{p["digits"]}"/><path fill="{dash}" d="{p["dashes"]}"/><path fill="{fg}" d="{p["word"]}"/>'

def svg(vb, body, title="3-2-1 Kickoff"):
    x0, y0, x1, y1 = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{body}</svg>\n')

bold = Face(pathlib.Path(A.fonts) / "ITC Eras Bold.otf"); ultra = Face(pathlib.Path(A.fonts) / "ITC Eras Ultra Regular.otf")

# dikey: KICKOFF, 3-2-1'in mürekkep genişliğine yayılır
num = bold.run("3-2-1")
nb = box(num)
raw = box(ultra.run("KICKOFF", K))
spacing = ((nb[2] - nb[0]) - (raw[2] - raw[0])) / 6
word = ultra.run("KICKOFF", K, x=nb[0] - raw[0], y=DROP, spacing=spacing)
stacked = parts(num, word); sb = box(num, word)

# yatay: aynı taban çizgisi, aynı punto, doğal harf aralığı
w0 = box(ultra.run("KICKOFF"))
wordh = ultra.run("KICKOFF", x=nb[2] + GAP - w0[0])
flat = parts(num, wordh); fb = box(num, wordh)

out = pathlib.Path(A.out); out.mkdir(parents=True, exist_ok=True)
for name, (fg, dash) in THEMES.items():
    (out / f"kickoff-logo-{name}.svg").write_text(svg(sb, group(stacked, fg, dash)))
    (out / f"kickoff-yatay-{name}.svg").write_text(svg(fb, group(flat, fg, dash)))

# ikon: mor zemin, dikey logo beyaz; kare (mağaza kaynağı, köşeyi mağaza keser) ve yuvarlak köşeli (gösterim)
S = 1024; w = S * 0.70; k = w / (sb[2] - sb[0]); h = (sb[3] - sb[1]) * k
place = f'<g transform="translate({(S - w) / 2 - sb[0] * k:.2f} {(S - h) / 2 - sb[1] * k:.2f}) scale({k:.5f})">{group(stacked, WHITE, AMBER)}</g>'
(out / "kickoff-ikon-kare.svg").write_text(svg((0, 0, S, S), f'<rect width="{S}" height="{S}" fill="{VIOLET}"/>{place}'))
(out / "kickoff-ikon.svg").write_text(svg((0, 0, S, S), f'<rect width="{S}" height="{S}" rx="{S * 0.225:.0f}" fill="{VIOLET}"/>{place}'))

vb = lambda b: [round(b[0], 1), round(b[1], 1), round(b[2] - b[0], 1), round(b[3] - b[1], 1)]
pathlib.Path(A.app).write_text("// Logonun çizgileri: tools/logo/eras_logo.py üretir, elle düzenleme. (3-2-1 ITC Eras Bold, KICKOFF ITC Eras Ultra)\n"
    f"export const LOGO = {json.dumps({'box': vb(sb), **stacked}, indent=2)};\n"
    f"export const LOGO_FLAT = {json.dumps({'box': vb(fb), **flat}, indent=2)};\n")
print(f"dikey {sb[2]-sb[0]:.0f}×{sb[3]-sb[1]:.0f} · yatay {fb[2]-fb[0]:.0f}×{fb[3]-fb[1]:.0f} · harf aralığı {spacing:.1f}")
print("kenarlar: 3-2-1", round(nb[0], 1), round(nb[2], 1), "· KICKOFF", round(box(word)[0], 1), round(box(word)[2], 1))
for p in sorted(out.glob("*.svg")): print(" ", p.relative_to(ROOT), p.stat().st_size)
