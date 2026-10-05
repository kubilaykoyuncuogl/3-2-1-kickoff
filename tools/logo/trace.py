"""mask_big.png → yumuşatılmış tek kontur (noktalar json). Moore komşuluk izleme + RDP sadeleştirme."""
import json, math
from PIL import Image, ImageFilter
src = Image.open("mask_big.png").convert("L")
S = 3                                                    # izleme çözünürlüğü: 1380x828 → /S
im = src.filter(ImageFilter.GaussianBlur(26)).resize((src.width // S, src.height // S), Image.LANCZOS).point(lambda v: 255 if v > 127 else 0)
W, H = im.size
pad = Image.new("L", (W + 2, H + 2), 0); pad.paste(im, (1, 1)); px = pad.load()
def on(x, y): return 0 <= x < W + 2 and 0 <= y < H + 2 and px[x, y] > 0
# başlangıç: ilk beyaz piksel
start = next((x, y) for y in range(H + 2) for x in range(W + 2) if on(x, y))
N8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]      # saat yönü (y aşağı)
pts = [start]; cur = start; back = 4                     # soldan geldik say
while True:
    found = False
    for i in range(8):
        d = (back + 1 + i) % 8
        nx, ny = cur[0] + N8[d][0], cur[1] + N8[d][1]
        if on(nx, ny):
            back = (d + 4) % 8; cur = (nx, ny); found = True; break
    if not found or cur == start: break
    pts.append(cur)
    if len(pts) > 200000: break
def rdp(p, eps):
    if len(p) < 3: return p
    (x1, y1), (x2, y2) = p[0], p[-1]; dx, dy = x2 - x1, y2 - y1; n = math.hypot(dx, dy) or 1e-9
    imax, dmax = 0, 0.0
    for i in range(1, len(p) - 1):
        d = abs(dy * (p[i][0] - x1) - dx * (p[i][1] - y1)) / n
        if d > dmax: imax, dmax = i, d
    if dmax <= eps: return [p[0], p[-1]]
    return rdp(p[: imax + 1], eps)[:-1] + rdp(p[imax:], eps)
import sys; sys.setrecursionlimit(100000)
half = len(pts) // 2
simp = rdp(pts[: half + 1], 2.2)[:-1] + rdp(pts[half:] + [pts[0]], 2.2)[:-1]
# 0..1 normalize (maskenin kendi kutusuna göre), alt kenardaki noktaları işaretle
out = [((x - 1) / W, (y - 1) / H, (y - 1) >= H - 2) for x, y in simp]
json.dump({"aspect": W / H, "pts": out}, open("silhouette.json", "w"))
print("kontur", len(pts), "→", len(out), "nokta; alt kenarda", sum(1 for p in out if p[2]))
