# Temsilî tasarım incelemesi

9 Ekim 2026. Kaynak: [Claude artifact](https://claude.ai/artifact/QCatPimAFP4BB4RPFmfanc). Amaç: kit kararlarını kaynak örnekleriyle temellendirmek. Çalışan native akış testi yapılmadı.

![İncelenen beş kaynak ekran](evidence/review-strip.jpg)

Şeritteki görüntüler bu oturumda alınan tam tarayıcı ekran görüntülerinin kırpılmış kaynak alıntılarıdır. Yeniden tasarım değildir. Tam kayıtlar aynı klasörde korunur.

## 1. Ana menü — c01-01A

Genel durum: ana seçenekler anlaşılır; renk rolleri ve küçük açıklamalar iyileştirilmeli.

Mor online eylemi baskın, beyaz ayarlar daha sakin: iyi hiyerarşi. Ancak amber “Tek oyna” eyleminde de kullanılıyor; oyuncu/rakip renk ayrımını zayıflatıyor. Kitte bu buton ikincil mor yüzeye geçer. “1000” değeri ne olduğunu kendi başına anlatmıyor: görünür “Elo 1000” ve erişilebilir ad önerilir. Haftanın maçı üst etiketleri diğer içeriğe göre çok küçük görünüyor; exact font ölçüsü PNG'den çıkarılmadı. Öneri 14/20 minimum ikincil metin.

![Ana menü kaynak alıntısı](evidence/02-home-light-excerpt.jpg)

[Tam kayıt](evidence/02-home-light.jpg).

## 2. Tur öneriler — c04-04B

Genel durum: input ve seçenekler açık; etiket ve bilgi hiyerarşisi iyileştirilmeli.

Takım renkleri, süre, input ve listede tutarlı hizalama var. Oyuncu adı ve yıl aynı satırda aynı ağırlıkla okunuyor; ad semibold, yıl caption olarak ayrılabilir. Inputta görünen kalıcı etiket yok: “Oyuncu adı” eklenmeli. Kontrol sınırları paletin zayıf çizgisini kullanırsa gerekli non-text kontrastı karşılamayabilir; PNG piksel stili kesinleştirilmedi. `controlBorder` tokenı bu rol için ayrı tanımlandı.

![Tur öneriler kaynak alıntısı](evidence/03-round-light-excerpt.jpg)

[Tam kayıt](evidence/03-round-light.jpg).

## 3. Klavye açık tur — c14-04B

Genel durum: input ve öneriler görünür; dinamik yerleşim mutlaka cihazda test edilmeli.

Klavye açık örnekte skor daha küçük bir satıra dönüşüyor ve altıncı öneri görünmüyor. Bunun kaydırma veya veri sınırı olup olmadığı screenshotla anlaşılamaz. Kit önerisi: bütün öneriler kaydırılabilir bölgede, skor aynı rolün kompakt varyantı; süre/input sabit koordinatlara bağlanmaz. PNG klavyesi gerçek Android/iOS klavye boyutlarını veya font ölçeğini kanıtlamaz.

![Klavye açık kaynak alıntısı](evidence/04-keyboard-light-excerpt.jpg)

[Tam kayıt](evidence/04-keyboard-light.jpg).

## 4. Ayarlar — c02-01A

Genel durum: ayarlar sırası anlaşılır; küçük seçimler ve erişilebilir state doğrulanmalı.

Ses, titreşim, tema ve hareket tercihleri zaten mevcut: bunları korumak iyi temel. Tema ve dil seçenekleri dar, geri ikonunun görünen kutusu da küçük görünüyor. Gerçek hit alanı bilinmiyor. Minimum 48 hedef, büyük fontta seçeneklerin sarılması ve native Switch durumlarının okunması kit sözleşmesine eklendi. Satırdaki switch ve bütün satırın ayrı ayrı aynı eylemi okutmaması gerekir.

![Ayarlar kaynak alıntısı](evidence/05-settings-light-excerpt.jpg)

[Tam kayıt](evidence/05-settings-light.jpg).

## 5. Yanlış / kilit, koyu — c04-04D

Genel durum: hata metinle de işaretlenmiş; açıklığı ve konumu iyileştirilmeli.

Pembe çerçeveye ek olarak “Yanlış” yazısı olması renk dışı bir ipucu. Fakat üstte “Yanlış · 3”, altta “... 5 sn kilit” birlikte görünüyor; 3'ün ne olduğu anlaşılmıyor ve iki mesajın farklı zaman noktalarını mı anlattığı belli değil. Mevcut domain state'ten tek açık geri bildirim üret; kalan kilit süresini ayrı anlaşılır metinle göster. Screenshotta gri üst yazının hangi token/opacity ile üretildiği bilinmiyor. Bu nedenle pixel-level kontrast ihlali iddiası yok; önerilen danger çiftleri hesapla doğrulandı.

![Koyu yanlış/kilit kaynak alıntısı](evidence/06-error-dark-excerpt.jpg)

[Tam kayıt](evidence/06-error-dark.jpg).

## Kapsam ve doğrulama sınırları

- Beş temsilî ekran, genel palet/font görünümü ve 137 ad/kimlik kaydı bu oturumda okundu.
- 137 ekranın tamamının yerleşimi incelenmedi. Görsel içindeki bütün metinler OCR ile çıkarılmadı.
- Kaynak app ekranları PNG; mobil erişilebilirlik ağacı, hitSlop, gerçek font boyutu, animasyon ve ağ davranışı görünmüyor.
- Kaynak ortak onay/veri için oturum açılmasını istiyor. Mühür/revize sayıları gerçek kullanıcı onayı sayılmadı.
- [Kontrast raporu](contrast-report.json) yalnızca kitte tanımlanan opak çiftlerin matematiksel ölçümüdür.
- Native büyük metin, VoiceOver/TalkBack, keyboard, orientation ve timed gameplay uygulanmış istemcide test edilmelidir.

Tasarıma aktarılacak kararlar [DESIGN.md](DESIGN.md), agent görevi [AGENT-BRIEF.md](AGENT-BRIEF.md).
