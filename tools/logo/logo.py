"""MR GUESS logosu: Sora ExtraBold harfler (üstte MR, altta GUESS, aynı genişlikte, bitişik) + siluet, kesişimde renk ters (XOR).
Çıktı: önizleme PNG (PIL) ve tek renk, şeffaf zeminli SVG."""
import sys, math, json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

FONT_VAR = "/home/vector/workspace/321-kickoff/game/assets/fonts/Sora[wght].ttf"
STATIC = "Sora-ExtraBold.ttf"
import os
if not os.path.exists(STATIC):
    f = instancer.instantiateVariableFont(TTFont(FONT_VAR), {"wght": 800}); f.save(STATIC)
font = TTFont(STATIC); gs = font.getGlyphSet(); cmap = font.getBestCmap(); UPM = font["head"].unitsPerEm

def glyph(ch):
    name = cmap[ord(ch)]; bp = BoundsPen(gs); gs[name].draw(bp)
    return name, gs[name].width, bp.bounds        # (xMin, yMin, xMax, yMax)

def line_metrics(text, track):
    """Harflerin kalem konumları (font birimi) ve sıkı genişlik (ilk harfin sol kenarından son harfin sağ kenarına)."""
    pos = []; x = 0
    for ch in text:
        name, adv, b = glyph(ch); pos.append((ch, name, x, b)); x += adv + track
    left = pos[0][2] + pos[0][3][0]; right = pos[-1][2] + pos[-1][3][2]
    return pos, left, right - left

CAP = glyph("E")[2][3]

def layout(W=1000.0, track1=-10, track2=-18, gap=0.035, sil_k=1.16, sil_dy=0.0, sil_dx=0.0):
    p1, l1, w1 = line_metrics("MR", track1); p2, l2, w2 = line_metrics("GUESS", track2)
    s1 = W / w1; s2 = W / w2
    base1 = CAP * s1; base2 = base1 + gap * CAP * s2 + CAP * s2
    return dict(W=W, p1=p1, l1=l1, s1=s1, base1=base1, p2=p2, l2=l2, s2=s2, base2=base2, H=base2, sil_k=sil_k, sil_dy=sil_dy, sil_dx=sil_dx)

def sil_box(L, mask_size):
    mw, mh = mask_size; w = L["W"] * L["sil_k"]; h = w * mh / mw
    x = (L["W"] - w) / 2 + L["sil_dx"] * L["W"]; y = L["H"] - h + L["sil_dy"] * L["H"]
    return x, y, w, h

def preview(L, mask, out, pad=0.14, px=1100, ink=(27, 26, 33), paper=(242, 242, 245)):
    k = px / (L["W"] * (1 + 2 * pad)); ox = L["W"] * pad * k; oy = L["W"] * pad * k
    Wp = px; Hp = int((L["H"] + 2 * L["W"] * pad) * k)
    letters = Image.new("L", (Wp, Hp), 0); d = ImageDraw.Draw(letters)
    for pos, left, s, base in ((L["p1"], L["l1"], L["s1"], L["base1"]), (L["p2"], L["l2"], L["s2"], L["base2"])):
        f = ImageFont.truetype(STATIC, size=s * k * UPM)
        for ch, name, x, b in pos:
            d.text((ox + (x - left) * s * k, oy + base * k), ch, font=f, fill=255, anchor="ls")
    x, y, w, h = sil_box(L, mask.size)
    sil = Image.new("L", (Wp, Hp), 0)
    sil.paste(mask.resize((int(w * k), int(h * k)), Image.LANCZOS), (int(ox + x * k), int(oy + y * k)))
    xor = ImageChops.difference(letters, sil).point(lambda v: 255 if v > 127 else 0)
    img = Image.new("RGB", (Wp, Hp), paper); img.paste(Image.new("RGB", (Wp, Hp), ink), mask=xor); img.save(out)
    return img

if __name__ == "__main__":
    mask = Image.open("mask_big.png").convert("L")
    variants = {"a": dict(), "b": dict(sil_k=1.3, sil_dy=0.02), "c": dict(sil_k=1.02, gap=0.0)}
    imgs = []
    for name, kw in variants.items():
        L = layout(**kw); imgs.append(preview(L, mask, f"logo_prev_{name}.png", px=700))
    sheet = Image.new("RGB", (sum(i.width for i in imgs) + 40, max(i.height for i in imgs)), (242, 242, 245))
    x = 0
    for i in imgs: sheet.paste(i, (x, 0)); x += i.width + 20
    sheet.save("logo_sheet.png"); print("CAP", CAP, "UPM", UPM, "sheet", sheet.size)
