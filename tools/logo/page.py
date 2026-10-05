"""Önizleme sayfası: docs/logo-preview.html (ikinci deneme üstte, ilk XOR denemesi altta)."""
import pathlib
from logo import layout
from logo_svg import svg, VARIANTS
from logo2 import svg2, SCHEMES, LAYOUTS, VIO_L, AMB_L, VIO_D, AMB_D, BLACK, WHITE, PAPER_L, PAPER_D
L1 = {n: layout(**kw) for n, kw in VARIANTS.items()}; L2 = {n: layout(**kw) for n, kw in LAYOUTS.items()}
n = 0
def x(name, ink, **kw):
    global n; n += 1; return svg(L1[name], ink=ink, uid=f"m{n}", **kw)
def card(lname, sname, layered, cls=""):
    c1, c2, fill, stroke, bg = SCHEMES[sname]
    return f'<div class="sw {cls}" style="background:{bg}">{svg2(L2[lname], c1, c2, fill, stroke, layered=layered)}</div>'
names = {"acik-siyah": "Açık zemin · siyah siluet, beyaz kontur", "acik-beyaz": "Açık zemin · beyaz siluet, siyah kontur",
         "koyu-beyaz": "Koyu zemin · beyaz siluet, koyu kontur", "koyu-siyah": "Koyu zemin · siyah siluet, beyaz kontur"}
grid = lambda lname, layered: "".join(f'<figure>{card(lname, s, layered)}<figcaption>{t}</figcaption></figure>' for s, t in names.items())
icon = lambda size, sname, bg: f'<div class="icon"><div style="width:{size}px;height:{size}px;background:{bg}">{svg2(L2["kompakt"], *SCHEMES[sname][:4], layered=True, square=True, pad=70)}</div>{size} px</div>'
html = f'''<title>MR GUESS Logo</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&display=swap">
<style>
/* Layout: hero, sonra dört renk şeması (katmanlı), siluet üstte karşılaştırması, ikon, ilk deneme */
:root{{--bg:#F2F2F5;--surface:#FFFFFF;--fg:#1B1A21;--muted:#5F5D6B;--line:#C9C8D3;--font:"Sora",system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#131218;--surface:#1C1B23;--fg:#ECEBF2;--muted:#A09EAD;--line:#3A3946;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#131218;--surface:#1C1B23;--fg:#ECEBF2;--muted:#A09EAD;--line:#3A3946;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font-family:var(--font);padding-inline:16px;padding-block:28px 56px;line-height:1.5;font-size:14px}}
main{{max-width:1000px;margin:0 auto;display:grid;gap:36px}}
h1{{font-size:clamp(24px,5vw,34px);font-weight:800;margin:0;letter-spacing:-.02em;text-wrap:balance}}
h2{{font-size:18px;font-weight:700;margin:0}}
p{{margin:0;color:var(--muted);max-width:62ch}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600}}
section{{display:grid;gap:14px}}
.grid{{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}}
figure{{margin:0;display:grid;gap:6px;min-width:0}} figcaption{{font-size:12px;color:var(--muted)}}
.sw{{border-radius:14px;padding:22px;display:grid;place-items:center;border:1.5px solid var(--line)}}
.sw svg{{width:100%;max-width:420px;height:auto;display:block}}
.hero .sw{{padding:clamp(20px,6vw,48px)}} .hero .sw svg{{max-width:560px}}
.icons{{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-end}}
.icon{{display:grid;gap:6px;justify-items:center;font-size:11px;color:var(--muted)}}
.icon div{{border-radius:22%;display:grid;place-items:center;overflow:hidden;border:1.5px solid var(--line)}}
.icon svg{{width:100%;height:100%;display:block}}
ul{{margin:0;padding-left:18px;color:var(--muted);display:grid;gap:6px;max-width:62ch}} ul b{{color:var(--fg);font-weight:600}}
</style>
<main>
<header style="display:grid;gap:10px">
  <span class="eyebrow">Logo · ikinci deneme · 2026-10-06</span>
  <h1>MR GUESS</h1>
  <p>MR mor, GUESS amber. Siluet tek renk ve dolu, etrafında kontur çizgisi var. Figür MR'nin önünde, GUESS'in arkasında duruyor; böylece kelime tam okunuyor ve derinlik oluşuyor.</p>
</header>
<section class="hero">{card("figur", "acik-siyah", True)}</section>
<section><h2>Dört renk şeması</h2><p>Siluet siyah-beyaz ikilisinde, yazı mor-amber ikilisinde. Koyu zeminde mor ve amber, oyunun koyu tema tonlarına geçiyor.</p><div class="grid">{grid("figur", True)}</div></section>
<section><h2>Karşılaştırma: siluet en üstte</h2><p>Siluet iki satırın da önünde olunca GUESS'in U ve E harfleri kapanıyor, kelime okunmuyor. Bu yüzden katmanlı hali öneriyorum.</p><div class="grid">{card("figur", "acik-siyah", False)}{card("figur", "koyu-beyaz", False)}</div></section>
<section><h2>Uygulama ikonu</h2><div class="icons">{icon(144, "acik-siyah", PAPER_L)}{icon(96, "koyu-beyaz", PAPER_D)}{icon(64, "acik-siyah", PAPER_L)}{icon(40, "koyu-beyaz", PAPER_D)}</div>
<p>İki satır ve figür 64 pikselin altında sıkışıyor. Küçük ikon için ayrı bir işaret gerekir: yalnızca siluet ya da "MR" ve siluet.</p></section>
<section><h2>İlk deneme: ters renk</h2><div class="grid"><div class="sw" style="background:{PAPER_L}">{x("figur", BLACK)}</div><div class="sw" style="background:{PAPER_D}">{x("figur", "#ECEBF2")}</div></div></section>
<section><h2>Notlar</h2><ul>
<li><b>Kaynak:</b> siluet indirdiğin fotoğraftan çıkarıldı. Forma yazısı ve numara silüette yok.</li>
<li><b>Hak durumu:</b> kaynak bir basın fotoğrafı ve poz tanınan bir oyuncuya ait. Mağazaya çıkacak logoda risk taşır; yayından önce aynı duruş sıfırdan çizilmeli ya da poz değişmeli.</li>
<li><b>Dosyalar:</b> her şema ayrı SVG, harfler kontura çevrili, font gerekmez.</li>
</ul></section>
</main>'''
out = pathlib.Path(__file__).resolve().parents[2] / "docs" / "logo-preview.html"; out.write_text(html); print(len(html))
