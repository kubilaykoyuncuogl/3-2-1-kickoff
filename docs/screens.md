# Ekran akışı (taslak: 2026-10-05, Kubilay'ın önerisi + notlar)

Önizleme (telefon çerçeveleri + geçiş demosu): `docs/screens-preview.html` · https://claude.ai/artifact/WMQ8tLym8b9hKbRi763T4B

İlke: **her oyuncu kendi ekranında üsttedir**, rakip alttadır. Sunucu için A/B; istemci kendini her zaman üste çizer. Sebep: klavye alttan açılır, kendi alanı ve yazı kutusu klavyenin üstünde kalmalı.

Portre kilitli. Masaüstü/web'de aynı düzen, sadece klavye yok.

## 0a. Ana menü
Dört madde, başka bir şey yok:
```
┌──────────────────────────┐
│ 3·2·1            (kubi) ●│  ← wordmark (tek eğik öğe) + profil chip
│ KICKOFF                  │
│ ┌──────────────────────┐ │
│ │ ONLINE OYNA     1240 │ │  ← birincil, mor fill; sağda Elo'n
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ TEK OYNA             │ │  ← amber fill; dokununca modlar açılır
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ NASIL OYNANIR        │ │  ← çerçeveli
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ AYARLAR              │ │  ← çerçeveli
│ └──────────────────────┘ │
└──────────────────────────┘
```
- Günlük kart menüden çıktı; Tek oyna sayfasına taşındı.
- Yazılar düz (eğim yalnızca wordmark ve geri sayım rakamlarında). Kenarlıklar 1.5 px, net; gölge yalnızca dolgulu butonlarda, 0 2px 0 koyu ton (basılı his), bulanık gölge yok.

## 0b. Online oyna
```
┌──────────────────────────┐
│ ‹            ONLINE OYNA │
│ ┌──────────────────────┐ │
│ │ kubi            1240 │ │  ← Elo kartı: puan, son 5 maç (● ● ○ ● ●), sıra
│ │ ●●○●●   #318         │ │
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ ARA              ▸   │ │  ← birincil: Elo'ya göre otomatik eşleşme
│ └──────────────────────┘ │
│ ┌──────────┐┌──────────┐ │
│ │ ODA KUR  ││ ODAYA    │ │  ← arkadaşla; Elo işlenmez (dostluk maçı)
│ │          ││ KATIL    │ │
│ └──────────┘└──────────┘ │
│ Skor tablosu ▸           │
└──────────────────────────┘
```
- **Elo** satranç gibi: başlangıç 1000, K = 32 (ilk 20 maçta 40). Yalnızca **Ara** ile eşleşen maçlar işlenir; oda maçları dostluk, Elo'ya dokunmaz.
- **Ara:** ±100 Elo bandı, her 10 sn'de ±100 genişler, 60 sn'de bulamazsa "Oda kur" önerir. Arama ekranı: nabız + "Rakip aranıyor · 1140–1340" + İptal.
- **Doğrulanmış (verified):** Ayarlar'dan hesap bağlayan oyuncu doğrulanmış sayılır ve **yalnızca doğrulanmışlarla eşleşir**. Doğrulanmış maçların Elo'su da tutulur ama tabloda doğrulanmış etiketi gösterilmez (tek tablo, tek Elo). Varsayım: Kubilay'ın cümlesi böyle okundu; alternatif okuma "tabloda yalnızca doğrulanmışlar görünür" ise tek satır değişiklik.
- **Oda kur:** 4 haneli kod büyük, Kopyala · Paylaş; altta "Rakip bekleniyor…". **Odaya katıl:** 4 kutu, otomatik ilerler, yanlış kodda kutular sallanır.

## 0c. Tek oyna
- Üstte günlük kart (bugünün koşusu, skorun, sıran, oynayan sayısı).
- İki büyük kart: **Klasik merdiven** (yaz) · **Blitz** (5 isim, dokun). Her kartta kendi en iyin ve bugünkü sıran.
- Altta "Pratik (tablosuz)" anahtarı.

## 0d. Nasıl oynanır
Tek tur oynatan tur: gerçek ekranlarla, sahte rakip ("Koç").
1. "İki takım seç" → Galatasaray ve Inter önceden seçili, Hazırım'a dokun.
2. Geri sayım gerçek.
3. Tur: ipucu balonu "İki takımda da oynamış birini yaz" → "Hak" yazınca öneriler, Çalhanoğlu'na dokun.
4. Tur sonu: "+1. Yanlış dersen 5 sn beklersin. 3 puan maçı alır."
5. "Hazırsın" → Online oyna'ya buton.
Ayarlar'dan tekrar açılabilir.

## 0e. Ayarlar
| Bölüm | Alanlar |
|---|---|
| Profil | Takma ad (düzenle), avatar rengi (mor/amber tonları) |
| Hesap | Hesap bağla (Google / Apple / e-posta) → "Doğrulanmış ✓" rozeti; bağlıysa Çıkış |
| Ses | Ana ses (anahtar) → açıkken: Oyun müziği (kaydırıcı), Oyun sesleri (kaydırıcı), Titreşim (anahtar) |
| Görünüm | Tema: Sistem / Açık / Koyu; Animasyonları azalt |
| Dil | Türkçe, English (v1), oyuncu/takım adları her dilde aynı |
| Diğer | Nasıl oynanır'ı tekrar aç, Gizlilik, Sürüm |

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
