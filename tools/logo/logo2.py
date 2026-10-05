"""MR GUESS, ikinci deneme: harfler mor + amber (MR / GUESS), siluet tek renk ve dolu, etrafında kontur çizgisi (siyah-beyaz ikilisi).
Çalıştır: python3 logo2.py  → game/assets/logo/mrguess2-*.svg ve kontrol PNG'si."""
import pathlib
from PIL import Image, ImageDraw, ImageFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from logo import layout, gs, UPM, STATIC
from logo_svg import sil_path, sil_segments, bounds

VIO_L, AMB_L, VIO_D, AMB_D = "#5E4BC9", "#E9A23B", "#8C7CF0", "#F0B45A"
BLACK, WHITE, PAPER_L, PAPER_D = "#1B1A21", "#FFFFFF", "#F2F2F5", "#131218"
OUT = pathlib.Path(__file__).resolve().parents[2] / "game" / "assets" / "logo"

def line_paths(L):
    out = []
    for pos, left, s, base in ((L["p1"], L["l1"], L["s1"], L["base1"]), (L["p2"], L["l2"], L["s2"], L["base2"])):
        d = ""
        for ch, name, x, b in pos:
            pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
            gs[name].draw(TransformPen(pen, (s, 0, 0, -s, (x - left) * s, base)))
            d += pen.getCommands()
        out.append(d)
    return out

def svg2(L, c1, c2, fill, stroke, stroke_w=16, pad=40, bg=None, square=False, layered=False):
    """c1 = MR rengi, c2 = GUESS rengi, fill = siluet, stroke = kontur. Kontur dolgunun dışına taşar (paint-order).
    layered=True: sıra MR → siluet → GUESS. Figür MR'nin önünde, GUESS'in arkasında durur; GUESS tam okunur ve o da konturlu."""
    vx, vy, vw, vh = bounds(L, pad + stroke_w)
    if square:
        side = max(vw, vh); vx -= (side - vw) / 2; vy -= (side - vh) / 2; vw = vh = side
    r = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")
    l1, l2 = line_paths(L)
    box = 'x="%s" y="%s" width="%s" height="%s"' % (r(vx), r(vy), r(vw), r(vh))
    sil = f'<path d="{sil_path(L)}" fill="{fill}" stroke="{stroke}" stroke-width="{r(stroke_w * 2)}" stroke-linejoin="round" paint-order="stroke fill"/>'
    mr = f'<path d="{l1}" fill="{c1}"/>'
    if layered:
        guess = f'<path d="{l2}" fill="{c2}" stroke="{stroke}" stroke-width="{r(stroke_w * 2)}" stroke-linejoin="round" paint-order="stroke fill"/>'
        body = mr + "\n" + sil + "\n" + guess
    else:
        body = mr + f'<path d="{l2}" fill="{c2}"/>' + "\n" + sil
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{r(vx)} {r(vy)} {r(vw)} {r(vh)}" role="img" aria-label="MR GUESS">
{f'<rect {box} fill="{bg}"/>' if bg else ''}{body}
</svg>'''

def check(L, c1, c2, fill, stroke, bg, out, stroke_w=16, px=640, pad=40, layered=False):
    vx, vy, vw, vh = bounds(L, pad + stroke_w); k = px / vw
    img = Image.new("RGB", (px, int(vh * k)), bg); d = ImageDraw.Draw(img)
    def draw_line(idx, col, outline=None):
        pos, left, s, base = ((L["p1"], L["l1"], L["s1"], L["base1"]), (L["p2"], L["l2"], L["s2"], L["base2"]))[idx]
        f = ImageFont.truetype(STATIC, size=s * k * UPM)
        for ch, name, x, b in pos:
            d.text((((x - left) * s - vx) * k, (base - vy) * k), ch, font=f, fill=col, anchor="ls",
                   stroke_width=int(stroke_w * k) if outline else 0, stroke_fill=outline)
    draw_line(0, c1)
    if not layered: draw_line(1, c2)
    poly = []
    for p0, q1, q2, p1 in sil_segments(L):
        for i in range(8):
            t = i / 8.0; u = 1 - t
            poly.append((((u**3 * p0[0] + 3 * u * u * t * q1[0] + 3 * u * t * t * q2[0] + t**3 * p1[0]) - vx) * k,
                         ((u**3 * p0[1] + 3 * u * u * t * q1[1] + 3 * u * t * t * q2[1] + t**3 * p1[1]) - vy) * k))
    w = int(stroke_w * 2 * k)
    d.line(poly + [poly[0]], fill=stroke, width=w, joint="curve")
    for x, y in poly[::2]: d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=stroke)
    d.polygon(poly, fill=fill)
    if layered: draw_line(1, c2, stroke)
    img.save(out); return img

LAYOUTS = {"figur": dict(sil_k=1.30, sil_dy=0.02, gap=0.035), "kompakt": dict(sil_k=1.16, gap=0.035)}
# ad: (MR, GUESS, siluet, kontur, zemin)
SCHEMES = {
    "acik-siyah": (VIO_L, AMB_L, BLACK, WHITE, PAPER_L),      # açık zemin, siyah siluet, beyaz kontur
    "acik-beyaz": (VIO_L, AMB_L, WHITE, BLACK, PAPER_L),      # açık zemin, beyaz siluet, siyah kontur
    "koyu-beyaz": (VIO_D, AMB_D, WHITE, PAPER_D, PAPER_D),    # koyu zemin, beyaz siluet, zemin renginde kontur
    "koyu-siyah": (VIO_D, AMB_D, BLACK, WHITE, PAPER_D),      # koyu zemin, siyah siluet, beyaz kontur
}
if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True); imgs = []
    for old in OUT.glob("mrguess2-*.svg"): old.unlink()
    for lname, kw in LAYOUTS.items():
        L = layout(**kw)
        for sname, (c1, c2, fill, stroke, bg) in SCHEMES.items():
            for layered in (False, True):
                tag = "katman" if layered else "ustte"
                (OUT / f"mrguess2-{lname}-{tag}-{sname}.svg").write_text(svg2(L, c1, c2, fill, stroke, layered=layered))
                if lname == "figur" and layered: imgs.append(check(L, c1, c2, fill, stroke, bg, f"/tmp/check2_{sname}.png", layered=True))
    sheet = Image.new("RGB", (imgs[0].width * 2 + 20, imgs[0].height * 2 + 20), "#808080")
    for i, im in enumerate(imgs): sheet.paste(im, ((i % 2) * (im.width + 20), (i // 2) * (im.height + 20)))
    sheet.save("/tmp/claude-1000/-home-vector-workspace/d3817e1e-d2b9-482f-a35f-ba46950a3961/scratchpad/check2_sheet.png"); print("ok", len(list(OUT.glob("mrguess2-*.svg"))), "svg")
