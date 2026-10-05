# Ekran akışı (taslak: 2026-10-05, Kubilay'ın önerisi + notlar)

İlke: **her oyuncu kendi ekranında üsttedir**, rakip alttadır. Sunucu için A/B; istemci kendini her zaman üste çizer. Sebep: klavye alttan açılır, kendi alanı ve yazı kutusu klavyenin üstünde kalmalı.

Portre kilitli. Masaüstü/web'de aynı düzen, sadece klavye yok.

## 0. Giriş / Lobi
- Oda kur (4 haneli kod) · Koda katıl · (sonra) Rastgele eşleş.
- Takma ad girişi (bir kez, cihazda saklanır).
- Rakip gelince → Takım seçimi.

## 1. Takım seçimi
```
┌──────────────────────────┐
│ Sen            [mor soft]│  ← takım yazısı + autocomplete listesi
│ ▸ Gala|                  │
│   Galatasaray            │
│   Galatasaray (kadın)    │
├──────────────────────────┤
│ Rakip        [amber soft]│  ← "Düşünüyor…" / "Hazır ✓"
└──────────────────────────┘
```
- Listeden seçince kendi panelinde takım kilitlenir, "Hazırım" butonu çıkar. Hazır deyince "Hazır ✓" rakibe gider; takım adı rakibe **hazır olunca** gider (önce gitmez, taktik sızmasın).
- Aynı takım iki kez seçilemez: sunucu reddeder, uyarı: "Rakip bu takımı seçti, başka seç".
- Ortak oyuncusu olmayan çift seçilirse (set kesişimi boş) sunucu "Bu iki takımın ortak oyuncusu yok" der, ikinci seçen yeniden seçer.
- Kısayollar (akışı hızlandırmak için): **Rastgele takım**, **Aynı takımlar** (önceki turun çiftiyle), son 5 seçim.

## 2. Geri sayım (3 sn)
- İki panel üstten ve alttan **ortaya çekilir**, birleştikleri çizgide "3 · 2 · 1" büyük (Sora 800, eğik).
- Her sayıda kısa haptik + tık sesi. "1" bitince klavye otomatik açılır.

## 3. Tur (15 sn)
```
┌──────────────────────────┐
│ ████████████░░░░░ 11     │  ← zaman çubuğu, son 5 sn kırmızı
│ Galatasaray  ×  Inter    │  ← iki takım tek satır, mor/amber chip
│ ┌──────────────────────┐ │
│ │ Hak|                 │ │  ← tahmin kutusu (klavye hep açık)
│ └──────────────────────┘ │
│   Hakan Çalhanoğlu       │  ← öneriler (tüm oyuncular, kesişim DEĞİL)
│   Hakan Şükür            │
│   Hakan Balta            │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│ Rakip: yazıyor… / ⏳ 4   │  ← ince şerit, klavyenin hemen üstünde
├─ klavye ─────────────────┤
```
- **Gönder = öneriye dokunmak.** Ayrı "Bildi" butonu yok; 15 sn'de her dokunuş değerli. Yanlış dokunmanın bedeli zaten 5 sn ceza. Serbest metin kabul edilmez, sadece listeden seçim (yazım hatası tartışması biter).
- Yanlış: kutu kırmızı soft'a döner, içinde "Yanlış · 5" geri sayar, klavye kapanmaz ama giriş kilitli. Rakibe de "Rakip yanlış dedi ⏳5" gider (gerilim).
- Rakip bildiğinde: kendi klavyen kapanır, 4. ekrana geçilir.
- Zaman biterse: puan yok, 4. ekran "Kimse bilemedi" ile.

## 4. Tur sonu (4 sn)
- Paneller yine üstten/alttan gelir, ortada skor: `2 : 1`.
- Bilen tarafın panelinde cevap: "Hakan Çalhanoğlu ✓". Bilemeyen turda altta "Olası cevaplar: …" (ilk 5, varsa "+12").
- Sonra paneller kayar, 1. ekrana (takım seçimi) dönülür. 3 puan → 5. ekran.

## 5. Maç sonu
- Kazanan büyük, skor, tur özeti (hangi çiftte kim bildi).
- **Rövanş** (aynı odada), **Ayrıl**. Paylaş (sonra).

## Kenar durumlar
- Rakip koptu: 10 sn "Bağlantı bekleniyor…", dönmezse maç bitti, kalan kazanır.
- Arka plana alma (telefon): tur devam eder, sunucu saati otorite; geri dönünce kalan süre sunucudan.
- Bağlantı gecikmesi: iki oyuncu aynı anda doğru derse sunucu ilk geleni sayar.
- Yeniden eşleşmede takma ad ve seçim geçmişi cihazda kalır.

## Ses / haptik (öneri)
| An | Ses | Haptik |
|---|---|---|
| 3·2·1 | tık ×3, "1"de düdük | hafif ×3 |
| doğru | kısa yükselen | orta |
| yanlış | kısa kalın | güçlü |
| son 5 sn | her saniye tık | — |
| rakip bildi | düşen | hafif |
