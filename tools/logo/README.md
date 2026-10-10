# 3-2-1 Kickoff logosu (geçerli, 2026-10-10)

`design/logo/`: `kickoff-logo-{acik,koyu}.svg` (dikey), `kickoff-yatay-{acik,koyu}.svg` (tek satır), `kickoff-ikon.svg` (yuvarlak köşe, gösterim) ve `kickoff-ikon-kare.svg` (mağaza kaynağı). "3-2-1" ITC Eras Bold, "KICKOFF" ITC Eras Ultra, tireler amber; harfler çizgiye çevrili, yazı gömülü değil.
Üretim: `python3 tools/logo/eras_logo.py --fonts <Eras .otf klasörü>` (SVG'ler + uygulamadaki `app/src/ui/logo.ts`). Yazı dosyaları repoda yok; ITC Eras lisanslı bir yazıdır, yayından önce lisansı alınmalı.

Aşağısı eski ad ve eski denemeler.

# MR GUESS logosu

`game/assets/logo/mrguess-{figur,kompakt,blok}.svg`: tek renk, şeffaf zemin, harfler kontura çevrili (font gerekmez).
Önizleme: `docs/logo-preview.html` · https://claude.ai/artifact/8t7ucyffuwSo3Ww11NWo78

**İkinci deneme (geçerli yön, 2026-10-06):** `mrguess2-<yerleşim>-<katman|ustte>-<şema>.svg`. MR mor, GUESS amber; siluet tek renk + kontur (siyah-beyaz ikilisi). `katman` = MR → siluet → GUESS sırası (önerilen; GUESS tam okunur), `ustte` = siluet en önde. Üretim: `python3 logo2.py`. İlk deneme (`mrguess-*.svg`) kesişimde ters renkliydi.

Üretim (bu klasörde çalıştır): `python3 logo_svg.py` (SVG'ler) · `python3 page.py` (önizleme sayfası).
- `logo.py`: Sora ExtraBold ölçüleri, yerleşim (MR ve GUESS aynı genişlikte, satır aralığı `gap`, siluet ölçeği `sil_k`).
- `logo_svg.py`: harf konturları + siluet, kesişimde renk ters (iki maske ile XOR). Yerleşimler `VARIANTS` içinde.
- `silhouette.json`: siluetin sadeleştirilmiş konturu (85 nokta). `trace.py` bunu bir maske PNG'sinden üretir.

Siluet bir basın fotoğrafından (tanınan bir oyuncunun pozu) çıkarıldı; kaynak fotoğraf repoda yok. **Yayından önce** aynı duruş sıfırdan çizilmeli ya da poz değiştirilmeli (telif ve kişilik hakkı). Yeni siluet için: beyaz figür / siyah zemin bir `mask_big.png` hazırla, `trace.py` çalıştır.
