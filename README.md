# 3-2-1 Kickoff

İki oyuncu birer kulüp seçer, 3'ten geri sayılır, 15 saniyede iki kulüpte de oynamış futbolcuyu bulan puan alır. 2 kişilik online oyun. Godot 4; Android + iOS + Web (mobil, tablet, tarayıcı).

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
