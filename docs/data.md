# Veri: Transfermarkt dökümü → oyun index'i (2026-10-05)

## Kaynak paket (`all_data/`, git dışı, 3,1 GB)
PostgreSQL custom dump (`database.dump`, 2,9 GB) + ham gzip yanıtlar. 1.458.300 oyuncu. Docker gerekmez: `pg_restore --data-only -t <tablo> -f <dosya>` ile tablolar düz metne çıkar (`data/raw/tsv/`, 9 GB).

Kullanılan tablolar:
| Tablo | Ne |
|---|---|
| `football.player_transfer_history_json` | `clubIds` (oynadığı kulüp id'leri) + `history.terminated[]` (tarih, kaynak/hedef kulüp, tip, ücret, piyasa değeri, yaş) |
| `football.player_core_json` | ad, kısa ad, doğum, uyruk, mevki, en yüksek piyasa değeri |
| `football.players` | ad + takma adlar (autocomplete) |
| `football.reference_entities` | kulüp adı, `clubTypeId`, `mainClubId`, `isNationalTeam`, ülke, lig |

Ölçümler (örneklem): oyuncuların %97'sinde transfer geçmişi var, ortalama 8,3 hareket; transfer uçlarının %98,3'ü adlı kulüp. Transfer tipleri: `STANDARD` %80, `INTERNAL_TRANSFER` %7,5 (altyapı→A takım), `ACTIVE_LOAN_TRANSFER` %6,3, `RETURNED_FROM_PREVIOUS_LOAN` %6,2. Ücret yalnızca ödenen transferlerde (`details.fee.value`).

## Kurallar (`tools/build_index.py`)
- **Kıdemli kulüp**: `clubTypeId ∈ {0,1}`; ad altyapı/rezerv kalıbına uymuyor (`U19`, `II`, `B`, `Youth`, `Jugend`, `Primavera`, `Jong`, `Reserves`, `Olympic Team`…); sahte kulüp değil (`123 Retired`, `515 Without Club`, `75 Unknown`, `2113 Career break`, `2077 Disqualification`).
- Altyapı/rezerv dönemleri **sayılmaz** (Galatasaray U19'da oynamak Galatasaray'da oynamak değildir).
- **Tarihi ad** (`mainClubId` ≠ id, ör. "Atlètic Catalunya CF (- 1970)" → Espanyol) ana kulübe birleştirilir.
- **Milli takımlar** index'te `national=1` ile ayrı; çift seçiminde varsayılan dışı (sonra mod olabilir).
- Oyuncunun kulüp seti = `clubIds` ∪ transfer uçları (filtre sonrası). Kariyer sırası = transferler tarihe göre; ilk transferin kaynağı `first` olarak ilk dönem.
- `fame`: oyuncu = en yüksek piyasa değeri (M€) + kulüp sayısı × 0,5; kulüp = oyuncularının piyasa değeri toplamı + oyuncu sayısı × 0,2. Merdiven ve çeldirici seçimi bunu kullanır.
- `pair_counts(club_a, club_b, n)`: ortak oyuncu sayısı; merdiven zorluğu bununla sıralanır (n ≥ 15 kolay … n = 1 en zor).

## Şifreleme ve sızdırmazlık
Düz gerçek: istemciye giden her şey çıkarılabilir. Koruma iki katmanlı:
1. **Oyuncu→kulüp ilişkisi istemciye hiç gitmez.** İstemci yalnızca ad önerisi (en çok 8), doğru/yanlış sonucu ve tur sonu "olası cevaplar" (en çok 12) görür. Oran sınırı: oyuncu başına saniyede 5 öneri isteği, dakikada 20 tahmin. Blitz günlük paketinde cevap `SHA-256(soru_id:oyuncu_id)` olarak gider, skor sunucuda yeniden doğrulanır.
2. **Index dosyası diskte şifreli** (`data/index/index.enc`): AES-256-GCM, 1 MiB parça, parça başına rastgele nonce + doğrulama etiketi, başlık AAD. Anahtar `KICKOFF_INDEX_KEY` ortam değişkeninde (64 hex), repoda ve sunucu diskinde düz anahtar yok. Servis dosyayı **belleğe** çözer (`sqlite3.deserialize`), diske düz kopya yazmaz. Anahtar olmadan dosya 2^256 denemeye karşı güvenli; "veri madenciliği ile geri alma" ancak sunucuya sızarak mümkün, dosyayı ele geçirerek değil.
Üretim: `python tools/encrypt_index.py --gen-key` → `.env`; `python tools/encrypt_index.py --in data/index/index.sqlite --out data/index/index.enc`; düz `index.sqlite` sunucuya hiç kopyalanmaz.

## Mimari güncellemesi
Godot headless 1,4 M oyuncuyu GDScript sözlüklerinde tutamaz. Veri katmanı Python **index servisi** (`server/index_service.py`, FastAPI, yalnızca 127.0.0.1): Godot oyun sunucusu oda/durum/zamanlayıcıyı yönetir, doğrulama ve öneri için servise HTTP ile sorar. İstemci servise doğrudan erişemez.

## Veriden çıkan oyun modları
| Mod | Veri | Mekanik |
|---|---|---|
| **3-2-1** (ana) | `player_clubs`, `pair_counts` | iki kulüp → ortak oyuncu |
| **Klasik merdiven / Blitz** | `pair_counts`, `fame` | zorluk sıralı çiftler; Blitz'te 2+2+1 isim |
| **Kariyer yolu** | `stints` sıralı | kulüpler tek tek açılır (ilk kulüpten başlayarak), oyuncuyu erken bilen çok puan alır; yaş/yıl ipucu |
| **Kiralık mı, satış mı?** | `stints.kind` | "X, 2019'da A'dan B'ye" → kiralık / satış / bedelsiz; 3 şık, hızlı tur |
| **Ücret: hangisi pahalı?** | `stints.fee` | iki transfer, dokun: hangisi daha pahalı; kombo |
| **Kariyeri sırala** | `stints` | 4 kulüp karışık, doğru sıraya sürükle |
| Milli takım + kulüp (sonra) | `clubs.national` | "Hem Brezilya hem Barcelona" |

## Çalıştırma
```
python tools/build_index.py                      # data/raw/tsv → data/index/index.sqlite (~3 dk, 30 GB RAM yeter)
python tools/encrypt_index.py --gen-key          # anahtar üret → .env
KICKOFF_INDEX_KEY=... python tools/encrypt_index.py --in data/index/index.sqlite --out data/index/index.enc
KICKOFF_INDEX_KEY=... uvicorn server.index_service:app --port 9081
```
