"""SVG üretimi: harfler Sora ExtraBold konturları, siluet yumuşatılmış kontur; XOR iki maske ile, tek renk, şeffaf zemin."""
import json
from PIL import Image, ImageDraw, ImageChops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from logo import layout, sil_box, gs, UPM, STATIC
from PIL import ImageFont

SIL = json.load(open("silhouette.json"))

def sil_segments(L):
    """Catmull-Rom → kübik Bézier. Alt kenar noktaları köşe kalır. Dönen: [(p0, c1, c2, p1)] logo koordinatında."""
    x0, y0, w, h = sil_box(L, (SIL["aspect"], 1.0))
    P = [(x0 + px * w, y0 + py * h, corner) for px, py, corner in SIL["pts"]]
    n = len(P); segs = []
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        if p1[2] and p2[2]:                         # alt kenar: düz çizgi
            segs.append((p1[:2], p1[:2], p2[:2], p2[:2])); continue
        t = 1 / 6.0
        c1 = (p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t) if not p1[2] else p1[:2]
        c2 = (p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t) if not p2[2] else p2[:2]
        segs.append((p1[:2], c1, c2, p2[:2]))
    return segs

def sil_path(L):
    segs = sil_segments(L); f = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")
    d = "M%s %s" % (f(segs[0][0][0]), f(segs[0][0][1]))
    for p0, c1, c2, p1 in segs: d += "C%s %s %s %s %s %s" % tuple(f(v) for v in (*c1, *c2, *p1))
    return d + "Z"

def letters_path(L):
    d = ""
    for pos, left, s, base in ((L["p1"], L["l1"], L["s1"], L["base1"]), (L["p2"], L["l2"], L["s2"], L["base2"])):
        for ch, name, x, b in pos:
            pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
            gs[name].draw(TransformPen(pen, (s, 0, 0, -s, (x - left) * s, base)))       # y ekseni ters
            d += pen.getCommands()
    return d

def bounds(L, pad):
    segs = sil_segments(L); xs = [p[0] for s in segs for p in s] + [0, L["W"]]; ys = [p[1] for s in segs for p in s] + [0, L["H"]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return x0 - pad, y0 - pad, (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad

def svg(L, ink="#1B1A21", pad=40, uid="mg", bg=None, square=False):
    vx, vy, vw, vh = bounds(L, pad)
    if square:
        side = max(vw, vh); vx -= (side - vw) / 2; vy -= (side - vh) / 2; vw = vh = side
    lp, sp = letters_path(L), sil_path(L)
    r = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")
    box = 'x="%s" y="%s" width="%s" height="%s"' % (r(vx), r(vy), r(vw), r(vh))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{r(vx)} {r(vy)} {r(vw)} {r(vh)}" role="img" aria-label="MR GUESS">
<defs>
<path id="{uid}-l" d="{lp}"/>
<path id="{uid}-s" d="{sp}"/>
<mask id="{uid}-a" maskUnits="userSpaceOnUse" {box}><use href="#{uid}-l" fill="#fff"/><use href="#{uid}-s" fill="#000"/></mask>
<mask id="{uid}-b" maskUnits="userSpaceOnUse" {box}><use href="#{uid}-s" fill="#fff"/><use href="#{uid}-l" fill="#000"/></mask>
</defs>
{f'<rect {box} fill="{bg}"/>' if bg else ''}<rect {box} fill="{ink}" mask="url(#{uid}-a)"/><rect {box} fill="{ink}" mask="url(#{uid}-b)"/>
</svg>'''

def raster_check(L, out, px=900, pad=40):
    """SVG ile aynı geometriyi PIL ile çizer (Bézier örneklenir): gözle doğrulama için."""
    vx, vy, vw, vh = bounds(L, pad); k = px / vw
    Wp, Hp = px, int(vh * k)
    letters = Image.new("L", (Wp, Hp), 0); d = ImageDraw.Draw(letters)
    for pos, left, s, base in ((L["p1"], L["l1"], L["s1"], L["base1"]), (L["p2"], L["l2"], L["s2"], L["base2"])):
        f = ImageFont.truetype(STATIC, size=s * k * UPM)
        for ch, name, x, b in pos: d.text((((x - left) * s - vx) * k, (base - vy) * k), ch, font=f, fill=255, anchor="ls")
    poly = []
    for p0, c1, c2, p1 in sil_segments(L):
        for i in range(8):
            t = i / 8.0; u = 1 - t
            poly.append((((u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p1[0]) - vx) * k,
                         ((u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p1[1]) - vy) * k))
    sil = Image.new("L", (Wp, Hp), 0); ImageDraw.Draw(sil).polygon(poly, fill=255)
    xor = ImageChops.difference(letters, sil).point(lambda v: 255 if v > 127 else 0)
    img = Image.new("RGB", (Wp, Hp), (242, 242, 245)); img.paste(Image.new("RGB", (Wp, Hp), (27, 26, 33)), mask=xor); img.save(out); return img

VARIANTS = {
    "figur": dict(sil_k=1.30, sil_dy=0.02, gap=0.035),     # büyük figür: baş harflerin üstüne taşar, eller dışarıda
    "kompakt": dict(sil_k=1.16, gap=0.035),                # figür blokla aynı hizada
    "blok": dict(sil_k=1.02, gap=0.0),                     # figür tamamen bloğun içinde, satırlar yapışık
}
if __name__ == "__main__":
    imgs = []
    for name, kw in VARIANTS.items():
        L = layout(**kw); open(f"mrguess-{name}.svg", "w").write(svg(L, uid="mg" + name[0]))
        imgs.append(raster_check(L, f"check_{name}.png", px=700))
    sheet = Image.new("RGB", (sum(i.width for i in imgs) + 40, max(i.height for i in imgs)), (242, 242, 245)); x = 0
    for i in imgs: sheet.paste(i, (x, 0)); x += i.width + 20
    sheet.save("check_sheet.png")
    import os; print({n: os.path.getsize(f"mrguess-{n}.svg") for n in VARIANTS})
