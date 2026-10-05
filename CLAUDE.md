# ucikibir — 3-2-1 oyunu (Godot 4)

Kubilay'ın kişisel projesi. YouTube'daki 3-2-1 oyununun (Erman Yaşar & Hasan Arda Kaşıkçı) 2 kişilik online mobil versiyonu. Hedef: Android + macOS. Başlangıç: 2026-10-05.

## Kurallar (ürün)
- 2 oyuncu bağlanır (oda kodu ile). Her biri bir takım yazar; yazdıkça autocomplete listesi gelir.
- İkisi de hazır → 3-2-1 geri sayım → 15 sn tur.
- Tur içinde iki takımda da oynamış oyuncu yazan +1 alır, tur biter.
- Yanlış tahmin → o oyuncu 5 sn yazamaz (input kilidi).
- 3 puan alan maçı kazanır.
- Oyuncu adı eşleştirme: Türkçe karakter/aksan duyarsız, prefix autocomplete (isim listesi iki takımın kesişimi DEĞİL, tüm oyuncular; yoksa cevap sızar).

## Mimari (karar)
- **Tek Godot projesi** (`game/`): istemci ve `--headless --server` ile çalışan otorite sunucu. Godot high-level multiplayer + `WebSocketMultiplayerPeer` (mobil/NAT için en sorunsuz).
- Sunucu otoritedir: zamanlayıcı, puan, doğrulama, ceza hep sunucuda; istemci sadece UI.
- Dataset ham hali `data/raw/` (git dışı, çok büyük). `tools/build_index.py` bunu `game/data/` altına sıkıştırılmış index'e çevirir:
  - `teams.json`: takım id → ad(lar), ülke, lig (autocomplete için).
  - `players.json` veya SQLite: oyuncu id → normalize ad(lar).
  - `player_teams`: oyuncu → takım seti. Sunucu bu seti belleğe alır; "A ve B'de oynadı mı" = set kesişimi.
  - İstemciye sadece takım listesi + oyuncu ad listesi (autocomplete) gider; oyuncu→takım ilişkisi **sadece sunucuda**.
- Dil: GDScript. Python sadece `tools/`.

## Çalıştırma
```
# index üret (dataset data/raw/ içindeyken)
python tools/build_index.py --in data/raw --out game/data
# sunucu
godot --headless --path game -- --server --port 9080
# istemci
godot --path game
```
Godot bu makinede kurulu değil (2026-10-05); indir: https://godotengine.org/download (4.3+).

## Notlar
- Dataset formatı henüz incelenmedi; `tools/build_index.py` kolon adlarını doğrulamadan önce `tools/inspect_dataset.py` ile şemaya bak.
- Takım adı ve oyuncu adı normalizasyonu `tools/normalize.py` ve `game/scripts/normalize.gd`'de **aynı** olmalı (ş→s, ı→i, apostrof/nokta sil, lower).
- Yayınlamadan önce: oyuncu ad listesi istemciye gidiyorsa boyutu (milyonlarca satır → muhtemelen sunucu tarafı autocomplete gerekir; `docs/design.md`'deki açık soru).
