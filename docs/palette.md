# Renk paleti (karar: 2026-10-05)

Kaynak: `game/scripts/palette.gd`. Buradaki değerler oradakiyle aynı tutulur.

## İlke
- İki taraf **Mor** (soğuk) ve **Amber** (sıcak): zıt sıcaklık, zıt ton. Kırmızı ve yeşil taraflara verilmedi; onlar yalnızca doğru/yanlış anlamı taşır.
- Nötrler hafif mor eğilimli gri (saf gri değil). Arka plan saf beyaz/saf siyah değil, uzun oturumda göz yormasın diye.
- Her taraf rengi 3 rolde kullanılır: `fill` (buton/kart dolgusu), `ink` (zemin üstü yazı/çizgi), `soft` (ince zemin tonu). Dark temada `fill` daha açık, üstüne koyu yazı.
- Doğru = mint yeşil, yanlış/ceza = gül kırmızısı. Timer son 5 sn'de gül kırmızısına döner.

## Light
| Token | Hex | Rol |
|---|---|---|
| bg | #F2F2F5 | sayfa zemini |
| surface | #FFFFFF | kart |
| fg | #1B1A21 | ana yazı |
| muted | #5F5D6B | ikincil yazı |
| line | #DCDBE3 | ayraç |
| violet.fill / ink / soft | #5E4BC9 / #4A3AAE / #E9E5FA | A tarafı (fill üstü yazı: beyaz) |
| amber.fill / ink / soft | #E9A23B / #9A6207 / #FBEFD8 | B tarafı (fill üstü yazı: fg) |
| ok / ok.soft | #167A52 / #DCF3E8 | doğru |
| no / no.soft | #C2334F / #FBE1E7 | yanlış, ceza, son 5 sn |

## Dark
| Token | Hex | Rol |
|---|---|---|
| bg | #131218 | |
| surface | #1C1B23 | |
| fg | #ECEBF2 | |
| muted | #A09EAD | |
| line | #2E2D38 | |
| violet.fill / ink / soft | #8C7CF0 / #B3A7FF / #272443 | fill üstü yazı: bg |
| amber.fill / ink / soft | #F0B45A / #F4C77A / #3A2D14 | fill üstü yazı: bg |
| ok / ok.soft | #4FCF93 / #163528 | |
| no / no.soft | #FF7D96 / #3C1B25 | |

Önizleme: `docs/palette-preview.html` (tarayıcıda aç) · https://claude.ai/artifact/KBPRJPtGvdWx8Y1fbzdRPV

Kontrast: yazı rolleri zemin üstünde ≥4.5 (AA), fill üstü yazılar ≥5.5. Hesap: `tools/contrast.py`.

## Karar notu (2026-10-05)
Orkide (sıcak mor) alternatifi denendi, Kubilay mor + amber ikilisini tercih etti. Mavi-sarı okunma riski kabul edildi; gerekçe: mor amber'dan net ayrışıyor ve taraf ayrımı ayrıca konum (sol/sağ) ve "Sen / Rakip" etiketiyle de taşınıyor. Renk körlüğü için bu konum/etiket kuralı zorunlu.

## Tipografi (karar: 2026-10-05)
Tek aile: **Sora** (Google Fonts, OFL). İlham ITC Eras (France 98 logosu); lisans (£160) yerine Sora + 3° eğim.
- Display (başlık, geri sayım, sayaç, skor): Sora 800, 3° sağa eğim → `game/assets/fonts/sora_display.tres`
- Body (gövde, buton, autocomplete listesi): Sora 500, düz → `game/assets/fonts/sora_body.tres`
- Rakamlarda `tabular_nums` (Sora'da `tnum` özelliği var; Godot'ta FontVariation `opentype_features` ile aç).
