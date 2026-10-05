# 321-kickoff — 3-2-1 Kickoff (Godot 4)

Kubilay'ın kişisel projesi. **3-2-1**: iki oyuncu birer kulüp söyler, 3'ten geri sayılır, 15 saniyede iki kulüpte de oynamış futbolcuyu bulan puan alır. 2 kişilik online versiyon. Hedef: **Android + iOS (telefon ve tablet) + Web**. PC hedef değil; Linux build yalnızca headless sunucu ve yerel test için. iOS build için Mac + Xcode gerekir (bu makineden çıkmaz).

## Kurallar (ürün)
- 2 oyuncu bağlanır (oda kodu ile). Her biri bir takım yazar; yazdıkça autocomplete listesi gelir.
- İkisi de hazır → 3-2-1 geri sayım → 15 sn tur.
- Tur içinde iki takımda da oynamış oyuncu yazan +1 alır, tur biter.
- Yanlış tahmin → o oyuncu 5 sn yazamaz (input kilidi).
- 3 puan alan maçı kazanır.
- Bir maçta bir takım yalnızca bir kez seçilebilir (iki oyuncu için ortak). Futbolcular tekrar söylenebilir.
- Ortak oyuncusu olmayan çift reddedilmez, tur boş geçer; art arda 3 geçersiz çift → maç berabere biter.
- Rakibin yanlış tahmini isimle birlikte karşı tarafa gösterilir.
- Takım seçiminde süre sınırı yok. Ekran akışı: `docs/screens.md`. Tek oyunculu modlar (Klasik merdiven, Blitz 5 isim, günlük koşu, skor tablosu): `docs/single-modes.md`.
- Oyuncu adı eşleştirme: Türkçe karakter/aksan duyarsız, prefix autocomplete (isim listesi iki takımın kesişimi DEĞİL, tüm oyuncular; yoksa cevap sızar).

## Mimari (karar)
- **Tek Godot projesi** (`game/`): istemci ve `--headless --server` ile çalışan otorite sunucu. Godot high-level multiplayer + `WebSocketMultiplayerPeer`: hem mobil/NAT için en sorunsuz hem de tarayıcıda çalışan tek seçenek (ENet web'de yok). Prod'da sunucu `wss://` arkasında (reverse proxy + TLS) olmalı, tarayıcı düz `ws://` kabul etmez.
- Sunucu otoritedir: zamanlayıcı, puan, doğrulama, ceza hep sunucuda; istemci sadece UI.
- **Veri katmanı Python index servisi** (`server/index_service.py`, FastAPI, yalnızca 127.0.0.1:9081). Godot headless 1 M oyuncuyu tutamaz; Godot oyun sunucusu oda/durum/zamanlayıcıyı yönetir, doğrulama/öneri/paket için servise HTTP ile sorar. İstemci servise doğrudan erişemez. Detay ve kurallar: `docs/data.md`.
- Dataset: Transfermarkt dökümü `all_data/` (git dışı, 3,1 GB). `pg_restore --data-only` ile `data/raw/tsv/` (9 GB) → `tools/build_index.py` → `data/index/index.sqlite` (583 MB, 90 sn; 1.048.321 oyuncu, 62.833 kıdemli kulüp, 4,5 M kariyer dönemi, 3,8 M kulüp çifti) → `tools/encrypt_index.py` → `index.enc` (AES-256-GCM, anahtar `.env`'de `KICKOFF_INDEX_KEY`). Servis şifreli dosyayı belleğe çözer; düz `index.sqlite` sunucuya hiç gitmez.
- Oyuncu→kulüp ilişkisi istemciye hiç gitmez: yalnızca ad önerisi (≤8), doğru/yanlış, tur sonu olası cevaplar (≤12), Blitz cevapları hash.
- Dil: GDScript (oyun), Python (`tools/`, `server/`).

## Çalıştırma
```
# bir kez: tabloları çıkar (all_data/all_data/database.dump → data/raw/tsv/*.sql), index üret, şifrele
python tools/build_index.py && set -a && . ./.env && set +a && python tools/encrypt_index.py --in data/index/index.sqlite --out data/index/index.enc
# index servisi (.venv: fastapi uvicorn cryptography)
set -a && . ./.env && set +a && .venv/bin/uvicorn server.index_service:app --host 127.0.0.1 --port 9081
# oyun sunucusu
godot --headless --path game -- --server --port 9080
# istemci
godot --path game
```
Godot 4.7.2 stable kurulu: `~/.local/bin/godot` (2026-10-05). Export template'leri henüz indirilmedi (Android/macOS/Web build için gerekir: Editor > Manage Export Templates).

## Notlar
- **Dil paketleri** `game/lang/<kod>.json` (anahtar → metin). Kodda görünen metin yazma, `T.t("anahtar")` kullan (`game/scripts/t.gd`); yeni metin eklerken önce `tr.json` ve `en.json`'a anahtar ekle. Sunucu hata mesajı olarak `err.*` anahtarı gönderir, istemci çevirir. Kontrol: `python3 tools/check_lang.py`. Yeni dil = yeni json dosyası, Ayarlar > Dil'de kendiliğinden çıkar.
- **Duman testi**: `godot --headless --path game -- --smoke` her ekranı her dilde ve iki temada kurar; arayüz değişikliğinden sonra çalıştır, çıktıda SCRIPT ERROR olmamalı (`--check-only` autoload'ları tanımadığı için hataları kaçırır).
- Export preset'lerinde `include_filter="*.json, *.txt"` şart; yoksa dil dosyaları ve `assets/room_words.txt` pakete girmez.
- Veriden mod fikirleri (kariyer yolu, kiralık/satış, ücret, sıralama): `docs/data.md` tablosu. Milli takım verisi transferlerde yok, milli takım modu bu veriyle yapılamaz.
- Takım adı ve oyuncu adı normalizasyonu `tools/normalize.py` ve `game/scripts/normalize.gd`'de **aynı** olmalı (ş→s, ı→i, apostrof/nokta sil, lower).
- Autocomplete sunucu tarafı (FTS5 prefix, <1 ms). Çalhanoğlu Galatasaray'da oynamadı; örneklerde GS–Inter için Sneijder/Icardi kullan.
- Web export: Godot 4 web build SharedArrayBuffer ister → hosting `Cross-Origin-Opener-Policy: same-origin` ve `Cross-Origin-Embedder-Policy: require-corp` header'larını vermeli (Godot'nun kendi export "head include"u + sunucu header'ı). Mobil tarayıcıda da (iOS Safari dahil) çalışır; Godot 4.3+ ile "threads" kapalı export daha uyumlu.
