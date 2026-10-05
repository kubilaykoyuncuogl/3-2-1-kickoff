# Renk paleti (karar: 2026-10-05)

Kaynak: `game/scripts/palette.gd`. Buradaki değerler oradakiyle aynı tutulur.

## İlke
- İki taraf **Mor** (soğuk, indigo yönü, hue ≈250) ve **Orkide** (sıcak, magenta yönü, hue ≈320). İkisi de mor ailesinde, sıcaklıkla ayrışır. Mavi/sarı, kırmızı/beyaz gibi Türkiye kulüp çiftlerinden bilinçli olarak kaçınıldı. Kırmızı ve yeşil taraflara verilmedi; onlar yalnızca doğru/yanlış anlamı taşır. Yanlış rengi orkideden uzak dursun diye gül değil **vermilyon** kırmızı.
- Nötrler hafif mor eğilimli gri (saf gri değil). Arka plan saf beyaz/saf siyah değil, uzun oturumda göz yormasın diye.
- Her taraf rengi 3 rolde kullanılır: `fill` (buton/kart dolgusu), `ink` (zemin üstü yazı/çizgi), `soft` (ince zemin tonu). Dark temada `fill` daha açık, üstüne koyu yazı.
- Doğru = mint yeşil, yanlış/ceza = vermilyon kırmızı. Timer son 5 sn'de kırmızıya döner.

## Light
| Token | Hex | Rol |
|---|---|---|
| bg | #F2F2F5 | sayfa zemini |
| surface | #FFFFFF | kart |
| fg | #1B1A21 | ana yazı |
| muted | #5F5D6B | ikincil yazı |
| line | #DCDBE3 | ayraç |
| violet.fill / ink / soft | #5E4BC9 / #4A3AAE / #E9E5FA | A tarafı (fill üstü yazı: beyaz) |
| orchid.fill / ink / soft | #B83E8E / #9A2E77 / #FAE4F2 | B tarafı (fill üstü yazı: fg) |
| ok / ok.soft | #167A52 / #DCF3E8 | doğru |
| no / no.soft | #BE2F28 / #FBE3E0 | yanlış, ceza, son 5 sn |

## Dark
| Token | Hex | Rol |
|---|---|---|
| bg | #131218 | |
| surface | #1C1B23 | |
| fg | #ECEBF2 | |
| muted | #A09EAD | |
| line | #2E2D38 | |
| violet.fill / ink / soft | #8C7CF0 / #B3A7FF / #272443 | fill üstü yazı: bg |
| orchid.fill / ink / soft | #E57DC2 / #F09BD4 / #3E1F34 | fill üstü yazı: bg |
| ok / ok.soft | #4FCF93 / #163528 | |
| no / no.soft | #FF7A6B / #3E1F1A | |

Önizleme: `docs/palette-preview.html` (tarayıcıda aç) · https://claude.ai/artifact/KBPRJPtGvdWx8Y1fbzdRPV

Kontrast: yazı rolleri zemin üstünde ≥4.5 (AA), fill üstü yazılar ≥5.5. Hesap: `tools/contrast.py`.
