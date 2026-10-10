#!/usr/bin/env python3
"""Haftanın maçı kartının stadyum çizimi: sol tribün A kulübünün, sağ tribün B kulübünün renklerinde boyanır.

  python3 tools/weekly_art.py
  → design/weekly/stadyum.svg (şablon; renk yuvaları __A0__ __A1__ __B0__ __B1__: kulüp zemin / yazı rengi)
    design/weekly/stadyum-<slug>.svg (server/weekly/*.json içindeki haftalarla boyanmış örnekler)
    app/src/ui/stadium.ts (uygulamanın SvgXml ile çizdiği şablon; elle düzenleme)

Tek kaynak bu dosyadaki STADIUM; çizimi değiştirince yeniden çalıştır. Zemin yok (kart rengi görünür), çim ve gök temadan bağımsız koyu."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
W, H = 360, 180

def rows(x0, y0, x1, y1, n, color, op=".35"):
    """tribün koltuk sıraları: (x0,y0)-(x1,y1) üst kenarı ile alt kenar arasında n çizgi"""
    out = []
    for i in range(1, n + 1):
        f = i / (n + 1)
        out.append(f'<line x1="{x0}" y1="{y0[0] + (y0[1] - y0[0]) * f:.1f}" x2="{x1}" y2="{y1[0] + (y1[1] - y1[0]) * f:.1f}" stroke="{color}" stroke-opacity="{op}" stroke-width="1.6"/>')
    return "".join(out)

def stand(side, c0, c1):
    """side: 'l' ya da 'r'. Çatı, koltuk bloğu (sıralı), ön duvar; sağ taraf aynalanır."""
    g = f'<g fill="{c0}">' \
        f'<polygon points="0,28 150,60 150,69 0,41"/>' \
        f'<polygon points="0,28 150,60 150,69 0,41" fill="#fff" fill-opacity=".22"/>' \
        f'<polygon points="0,44 150,72 150,93 0,100"/>' \
        f'{rows(0, (44, 100), 150, (72, 93), 5, c1)}' \
        f'<polygon points="0,100 150,93 150,97 0,105" fill="#000" fill-opacity=".35"/>' \
        f'<polygon points="0,96 150,90 150,93 0,100" fill="{c1}" fill-opacity=".5"/>' \
        f'</g>'
    return g if side == "l" else f'<g transform="translate({W} 0) scale(-1 1)">{g}</g>'

def pitch():
    g = [f'<polygon points="118,92 242,92 {W},{H} 0,{H}" fill="#1F6A42"/>']
    # biçme şeritleri: ufukta dar, önde geniş
    for i in range(0, 8, 2):
        t0, t1 = i / 8, (i + 1) / 8
        g.append(f'<polygon points="{118 + 124 * t0:.1f},92 {118 + 124 * t1:.1f},92 {W * t1:.1f},{H} {W * t0:.1f},{H}" fill="#fff" fill-opacity=".05"/>')
    g.append('<g fill="none" stroke="#DCEBDF" stroke-opacity=".55" stroke-width="1.2">'
             f'<polygon points="118,92 242,92 {W},{H} 0,{H}"/>'                   # kenar çizgileri
             '<polygon points="155,92 205,92 215,101 145,101"/>'                 # uzak ceza sahası
             f'<line x1="40" y1="{H}" x2="122" y2="113"/><line x1="320" y1="{H}" x2="238" y2="113"/>'   # orta çizgi hissi: ön köşelerden gelen çizgiler yerine yan oklar
             '<ellipse cx="180" cy="123" rx="26" ry="7"/>'                        # orta yuvarlak
             '</g>')
    g.append('<g stroke="#F2F2F5" stroke-width="1.4" fill="none"><rect x="170" y="84" width="20" height="8"/><path d="M172 85v6M175 85v6M178 85v6M181 85v6M184 85v6M187 85v6" stroke-opacity=".6" stroke-width=".8"/></g>')   # kale
    return "".join(g)

def far_stand():
    return ('<polygon points="118,78 242,78 242,92 118,92" fill="#2A2F3A"/>'
            '<polygon points="118,78 242,78 242,81 118,81" fill="#fff" fill-opacity=".15"/>'
            + rows(118, (81, 92), 242, (81, 92), 3, "#fff", ".18"))

def sky():
    return (f'<rect width="{W}" height="{H}" fill="#0F2A20"/>'      # gece göğü: temadan bağımsız, kart açıkken de koyu
            '<circle cx="268" cy="34" r="13" fill="#E6E27C"/>'
            '<g fill="#D7DEE3" fill-opacity=".9"><ellipse cx="210" cy="56" rx="16" ry="5"/><ellipse cx="218" cy="52" rx="9" ry="5"/>'
            '<ellipse cx="300" cy="60" rx="22" ry="5"/><ellipse cx="292" cy="56" rx="11" ry="6"/></g>')

def floodlight():
    dots = "".join(f'<circle cx="{124 + i * 3.2:.1f}" cy="{22 + j * 3.2:.1f}" r="1.1"/>' for i in range(4) for j in range(3))
    return ('<line x1="130" y1="30" x2="132" y2="80" stroke="#C9D3C8" stroke-width="1.6"/>'
            f'<g fill="#FFF7C2">{dots}</g>')

STADIUM = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice">'
           f'{sky()}{far_stand()}{floodlight()}{pitch()}{stand("l", "__A0__", "__A1__")}{stand("r", "__B0__", "__B1__")}</svg>')

out = ROOT / "design/weekly"; out.mkdir(parents=True, exist_ok=True)
(out / "stadyum.svg").write_text(STADIUM + "\n")
for p in sorted((ROOT / "server/weekly").glob("*.json")):
    d = json.loads(p.read_text())
    if "a" not in d or p.stem in ("current", "active"): continue
    s = STADIUM.replace("__A0__", d["a"]["colors"][0]).replace("__A1__", d["a"]["colors"][1]).replace("__B0__", d["b"]["colors"][0]).replace("__B1__", d["b"]["colors"][1])
    (out / f"stadyum-{p.stem}.svg").write_text(s + "\n")
    print("örnek:", p.stem, d["a"]["colors"], d["b"]["colors"])
ts = ROOT / "app/src/ui/stadium.ts"
ts.write_text("// Haftanın maçı stadyumu: tools/weekly_art.py üretir, elle düzenleme. Renk yuvaları __A0__ __A1__ __B0__ __B1__ (kulüp zemin / yazı).\n"
              f"export const STADIUM = {json.dumps(STADIUM)};\nexport const STADIUM_RATIO = {H / W:.4f};\n")
print("yazıldı:", out.relative_to(ROOT), ts.relative_to(ROOT), f"{len(STADIUM)} bayt")
