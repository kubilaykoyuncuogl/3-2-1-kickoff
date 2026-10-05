# Ekran akışı (taslak: 2026-10-05, Kubilay'ın önerisi + notlar)

Önizleme (telefon çerçeveleri + geçiş demosu): `docs/screens-preview.html` · https://claude.ai/artifact/WMQ8tLym8b9hKbRi763T4B

İlke: **her oyuncu kendi ekranında üsttedir**, rakip alttadır. Sunucu için A/B; istemci kendini her zaman üste çizer. Sebep: klavye alttan açılır, kendi alanı ve yazı kutusu klavyenin üstünde kalmalı.

Portre kilitli. Masaüstü/web'de aynı düzen, sadece klavye yok.

## 0. Ana menü / Lobi
- Ana menü: **Çok oyunculu** (Oda kur · Koda katıl · sonra Rastgele eşleş), **Tek oyunculu** modlar (ayrı doküman, gelecek), Ayarlar.
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
- **Bir maçta bir takım bir kez söylenir** (iki oyuncu için ortak liste). Kullanılmış takım listede soluk görünür, seçilemez. Oyuncular (futbolcular) tekrar tekrar söylenebilir.
- Ortak oyuncusu olmayan çift **reddedilmez**; tur normal oynanır, kimse bilemez, tur sonunda "Bu iki takımın ortak oyuncusu yok" gösterilir. Art arda 3 geçersiz çift → maç bozulur, **berabere** (kasıtlı kilitleme önlemi; sayaç geçerli çiftte sıfırlanır).
- Takım seçiminde süre yok. Videoda da düşünme payı var, takım hemen akla gelmiyor.
- Kolaylaştırıcılar: panelin üstünde **Favoriler** (oyuncunun en çok seçtiği takımlar, cihazda tutulur), **Rastgele takım**.

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
- Yanlış: kutu kırmızı soft'a döner, içinde "Yanlış · 5" geri sayar, klavye kapanmaz ama giriş kilitli. Rakibe de **isimle** gider: "Rakip: Podolski ✗ ⏳5". Rakibin elediği ismi görmek bilgi de verir, gerilim de.
- Rakip bildiğinde: kendi klavyen kapanır, 4. ekrana geçilir.
- Zaman biterse: puan yok, 4. ekran "Kimse bilemedi" ile.

## 4. Tur sonu (4 sn)
- Paneller yine üstten/alttan gelir, ortada skor: `2 : 1`.
- Bilen tarafın panelinde cevap: "Hakan Çalhanoğlu ✓". Bilemeyen turda altta "Olası cevaplar: …" (ilk 5, varsa "+12").
- Sonra paneller kayar, 1. ekrana (takım seçimi) dönülür. 3 puan → 5. ekran.

## 5. Maç sonu
- Kazanan büyük, skor, tur özeti (hangi çiftte kim bildi).
- **Rövanş** (aynı odada), **Ayrıl**. Paylaş (sonra).

## Geçişler (hareket dili)
Tek metafor: **iki panel**. Senin panelin üstten, rakibinki alttan gelir; buluştukları yerde olan biten (geri sayım, skor) yazılır. Her geçiş bu iki panelin hareketidir, başka geçiş efekti yok.

| Geçiş | Hareket | Süre |
|---|---|---|
| Menü → Lobi → Takım seçimi | sayfa sağdan kayar (push) | 220 ms ease-out |
| Rakip odaya girdi | alt panel ekran dışından yukarı kayar | 300 ms ease-out |
| İkisi hazır → Geri sayım | iki panel ortaya kayar, birleşme çizgisinde 3·2·1; her rakam 1 sn, scale 1.2→1 pop | 320 ms kayma + 3 × 1000 ms |
| "1" bitti → Tur | paneller küçülüp üstte tek satır chip olur, tahmin kutusu yukarı çıkar, klavye açılır | 260 ms |
| Bilindi / süre bitti → Tur sonu | klavye kapanır, chip'ler açılıp panele döner, ortada skor sayarak güncellenir | 300 ms + skor 400 ms |
| Tur sonu → Takım seçimi | paneller tam konumuna kayar, içerik değişir | 300 ms |
| 3 puan → Maç sonu | kazanan panel büyür (%60), kaybeden küçülür, konfeti yok, tek düdük | 400 ms |
| Yanlış tahmin | tahmin kutusu 2 kez yatay sallanır (8 px), kırmızıya döner | 240 ms |
| Son 5 sn | zaman çubuğu kırmızı, her saniye hafif nabız | — |

`prefers_reduced_motion` / Ayarlar > Animasyonları azalt: tüm kaymalar 120 ms çapraz geçişe iner, sallanma kapanır.

## Tek oyunculu ekranlar
- **Klasik basamak:** üstte "BASAMAK 7" + 3 can (top ikonu), zaman çubuğu, iki kulüp chip, tahmin kutusu + öneriler. Multi tur ekranıyla aynı iskelet, rakip şeridi yerine can/basamak satırı.
- **Blitz sorusu:** üstte soru sayısı + kombo çarpanı, hızlı zaman çubuğu, iki kulüp chip, altta 5 isim büyük dokunma hedefi (min 56 px yükseklik). Doğru: yeşil flaş, sonraki soru 150 ms'de gelir. Yanlış: kırmızı flaş, doğru olan yeşil işaretlenir, 1 sn sonra koşu sonu.
- **Koşu sonu:** büyük skor, basamak/soru sayısı, günlük sıralama, "Tekrar" + "Paylaş" (emoji dizisi), altta ilk 10 tablo.

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
