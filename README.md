# Üç İki Bir (3-2-1)

Erman Yaşar & Hasan Arda Kaşıkçı'nın YouTube'da oynadığı **3-2-1** oyununun 2 kişilik mobil/masaüstü versiyonu. Godot 4, Android + macOS.

## Oyun kuralı
1. İki oyuncu bağlanır, her biri bir takım seçer (yazdıkça öneri listesi).
2. İkisi de "hazır" deyince 3-2-1 geri sayım.
3. 15 saniye içinde **iki takımda da oynamış** bir futbolcu yazmaya çalışırlar.
4. Doğru bulan +1. Yanlış tahmin eden 5 saniye yazamaz (ceza).
5. 3 puana ulaşan kazanır.

## Klasörler
| Klasör | Ne |
|---|---|
| `game/` | Godot 4 projesi (istemci + headless sunucu aynı proje) |
| `server/` | Sunucu çalıştırma notları / Dockerfile |
| `tools/` | Dataset → oyun index'i dönüştürme script'leri (Python) |
| `data/raw/` | Ham dataset (git dışı) |
| `game/data/` | Türetilmiş sıkıştırılmış index (`teams.json`, `pairs.db` vb.) |
| `docs/` | Tasarım notları |

Detay: `CLAUDE.md`, `docs/design.md`.
