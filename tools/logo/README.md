# MR GUESS logosu

`game/assets/logo/mrguess-{figur,kompakt,blok}.svg`: tek renk, şeffaf zemin, harfler kontura çevrili (font gerekmez).
Önizleme: `docs/logo-preview.html` · https://claude.ai/artifact/8t7ucyffuwSo3Ww11NWo78

Üretim (bu klasörde çalıştır): `python3 logo_svg.py` (SVG'ler) · `python3 page.py` (önizleme sayfası).
- `logo.py`: Sora ExtraBold ölçüleri, yerleşim (MR ve GUESS aynı genişlikte, satır aralığı `gap`, siluet ölçeği `sil_k`).
- `logo_svg.py`: harf konturları + siluet, kesişimde renk ters (iki maske ile XOR). Yerleşimler `VARIANTS` içinde.
- `silhouette.json`: siluetin sadeleştirilmiş konturu (85 nokta). `trace.py` bunu bir maske PNG'sinden üretir.

Siluet bir basın fotoğrafından (tanınan bir oyuncunun pozu) çıkarıldı; kaynak fotoğraf repoda yok. **Yayından önce** aynı duruş sıfırdan çizilmeli ya da poz değiştirilmeli (telif ve kişilik hakkı). Yeni siluet için: beyaz figür / siyah zemin bir `mask_big.png` hazırla, `trace.py` çalıştır.
