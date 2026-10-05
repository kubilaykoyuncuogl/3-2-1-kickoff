from logo import layout
from logo_svg import svg, VARIANTS
L = {n: layout(**kw) for n, kw in VARIANTS.items()}
n = 0
def s(name, ink, square=False, pad=40):
    global n; n += 1
    return svg(L[name], ink=ink, uid=f"m{n}", square=square, pad=pad)
INK_L, INK_D, VIO, VIO_D, AMB, AMB_D = "#1B1A21", "#ECEBF2", "#5E4BC9", "#B3A7FF", "#9A6207", "#F0B45A"
names = {"figur": ("Figür", "Siluet bloktan büyük. Baş harflerin üstüne taşar, eller iki yandan dışarı çıkar. En okunaklı figür."),
         "kompakt": ("Kompakt", "Siluet blokla aynı hizada. Daha derli toplu, küçük boyutta daha sağlam."),
         "blok": ("Blok", "Satırlar yapışık, siluet tamamen içeride. En sıkı kütle, uygulama ikonuna en yakın.")}
cards = ""
for key, (title, desc) in names.items():
    cards += f'''<article class="v"><div class="pair"><div class="sw light">{s(key, INK_L)}</div><div class="sw dark">{s(key, INK_D)}</div></div>
<h3>{title}</h3><p>{desc}</p></article>'''
html = f'''<title>MR GUESS Logo</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&display=swap">
<style>
/* Layout: hero logo, then three layout variants each on light+dark, then color and icon trials */
:root{{--bg:#F2F2F5;--surface:#FFFFFF;--fg:#1B1A21;--muted:#5F5D6B;--line:#C9C8D3;--paper-l:#F2F2F5;--paper-d:#131218;--font:"Sora",system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#131218;--surface:#1C1B23;--fg:#ECEBF2;--muted:#A09EAD;--line:#3A3946;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#131218;--surface:#1C1B23;--fg:#ECEBF2;--muted:#A09EAD;--line:#3A3946;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font-family:var(--font);padding-inline:16px;padding-block:28px 56px;line-height:1.5;font-size:14px}}
main{{max-width:1000px;margin:0 auto;display:grid;gap:36px}}
h1{{font-size:clamp(24px,5vw,34px);font-weight:800;margin:0;letter-spacing:-.02em;text-wrap:balance}}
h2{{font-size:18px;font-weight:700;margin:0}} h3{{font-size:15px;font-weight:700;margin:0}}
p{{margin:0;color:var(--muted);max-width:62ch}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600}}
section{{display:grid;gap:14px}}
.hero{{background:var(--paper-l);border:1.5px solid var(--line);border-radius:20px;padding:clamp(20px,6vw,56px);display:grid;place-items:center}}
.hero svg{{width:min(100%,520px);height:auto;display:block}}
.grid{{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}}
.v{{display:grid;gap:8px;min-width:0;align-content:start}}
.pair{{display:grid;gap:8px}}
.sw{{border-radius:14px;padding:22px;display:grid;place-items:center;border:1.5px solid var(--line)}}
.sw svg{{width:100%;max-width:300px;height:auto;display:block}}
.light{{background:var(--paper-l)}} .dark{{background:var(--paper-d)}} .vio{{background:#E9E5FA}} .amb{{background:#3A2D14}} .solidv{{background:#5E4BC9}} .solida{{background:#E9A23B}}
.icons{{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-end}}
.icon{{display:grid;gap:6px;justify-items:center;font-size:11px;color:var(--muted)}}
.icon div{{border-radius:22%;display:grid;place-items:center;overflow:hidden}}
.icon svg{{width:100%;height:100%;display:block}}
ul{{margin:0;padding-left:18px;color:var(--muted);display:grid;gap:6px;max-width:62ch}} ul b{{color:var(--fg);font-weight:600}}
</style>
<main>
<header style="display:grid;gap:10px">
  <span class="eyebrow">Logo denemesi · 2026-10-06</span>
  <h1>MR GUESS</h1>
  <p>Üstte MR, altta GUESS, ikisi aynı genişlikte ve bitişik. Harfler Sora ExtraBold. Kolları açık siluet bloğun üstünden geçiyor; harfle kesiştiği yerde renk ters dönüyor. Tek renk, şeffaf zeminli SVG.</p>
</header>
<section><div class="hero">{s("figur", INK_L)}</div></section>
<section><h2>Üç yerleşim</h2><div class="grid">{cards}</div></section>
<section><h2>Renk denemeleri</h2>
<div class="grid">
<div class="sw vio">{s("figur", VIO)}</div><div class="sw amb">{s("figur", AMB_D)}</div>
<div class="sw solidv">{s("figur", "#FFFFFF")}</div><div class="sw solida">{s("figur", INK_L)}</div>
</div></section>
<section><h2>Uygulama ikonu</h2>
<div class="icons">
<div class="icon"><div style="width:144px;height:144px;background:#5E4BC9">{s("blok", "#FFFFFF", square=True, pad=110)}</div>144 px</div>
<div class="icon"><div style="width:96px;height:96px;background:#1B1A21">{s("blok", "#F0B45A", square=True, pad=110)}</div>96 px</div>
<div class="icon"><div style="width:64px;height:64px;background:#F2F2F5;border:1.5px solid var(--line)">{s("blok", INK_L, square=True, pad=110)}</div>64 px</div>
<div class="icon"><div style="width:40px;height:40px;background:#5E4BC9">{s("blok", "#FFFFFF", square=True, pad=110)}</div>40 px</div>
</div>
<p>40 pikselde siluet artık okunmuyor, yalnızca harf kütlesi kalıyor. İkon için ya yalnızca "MR" ve siluet, ya da sadece siluet daha iyi çalışır.</p></section>
<section><h2>Notlar</h2><ul>
<li><b>Kaynak:</b> siluet indirdiğin fotoğraftan çıkarıldı (renk ayrımı, delik doldurma, yumuşatma, vektör izleme). Forma yazısı ve numara silüette yok.</li>
<li><b>Hak durumu:</b> fotoğraf bir basın fotoğrafı ve poz tanınan bir oyuncuya ait. Mağazaya çıkacak bir logoda bu, fotoğrafın telifi ve kişilik hakkı açısından risk taşır. Yayından önce aynı duruşu sıfırdan çizdirmek ya da pozu değiştirmek gerekir.</li>
<li><b>Dosyalar:</b> her yerleşim ayrı SVG, harfler kontura çevrili, font gerekmez.</li>
</ul></section>
</main>'''
open("mrguess-logo.html", "w").write(html); print(len(html))
