# Kickoff — AI slop kaynak incelemesi

9 Ekim 2026. İnceleme kapsamı: KIT.html ve COMPONENT-LIBRARY.html HTML/CSS kaynakları; seçilmiş ürün kararları ve paylaşılan referanslar. Tarayıcı yakalama aracı süreç hatası verdi; bu turda yeni rendered screenshot alınamadı. Bu rapor görsel/browser audit veya Impeccable detector çıktısı değildir. Native uygulama yok. Slop puanı üretilmedi.

## Kullanılan kaynaklar

- [Impeccable kataloğu](https://impeccable.style/slop/#catalog): iç içe yüzeyler, tekrar eden kartlar, gereksiz üst etiketler, okunabilirlik ve sistem dışına çıkan değerler için inceleme çerçevesi.
- [Developers Digest yazısı](https://www.developersdigest.tech/blog/ai-design-slop-and-how-to-spot-it): alışkanlık olarak tekrarlanan font/renk/yerleşim tercihleri. Yazının örneklemi landing page'lerdir; mobil oyun veya bileşen kütüphanesine eşik/puan aktarmadık.

## Kaynakta bulunanlar ve düzeltmeler

| Konum | Bulgu | Yapılan değişiklik |
|---|---|---|
| Kütüphane, 15 section | Her örnek aynı yuvarlak dış kutu içinde; ürün kontrolünün çevresinde ek sınır | Dış kutular kaldırıldı; örnekler 5 anlamlı aileye ayrıldı; içerik arasında boşluk ve bölüm ayracı |
| Kütüphane başlığı / section başlıkları | Tekrar eden üst etiket, sıralama ifade etmeyen görünür numaralar | Başlık sadeleşti; 01–15 referans numaraları kapalı uygulama notlarına taşındı |
| Bütün örnekler | Bileşen kod adları ve uzun uygulama açıklamaları örnek UI ile aynı akışta | Kod adları ve son açıklamalar açılabilir tasarım notlarına alındı; ürün içeriği önde |
| Solo mod menüsü | Her mod ayrı kart gibi; eşit görsel gürültü | Gruplu liste ve satır ayraçları; seçilmiş ana menü oyun düğmeleri korunur |
| ClubPairPrompt | Okuma alanına gereksiz kapalı kart | Başlık/boşluk/iki ince ayraç ile grup; input ve cevap kontrol sınırları korunur |
| Sonuç kartları | Liste ve futbol bilgisi kart içinde ayrı kart katmanları | Gruplu cevap listesi; bilgi alanında başlık ve ayraç; paylaşılacak ana yüzey korunur |
| HUD / arama | Her bilgi için rozet; dekoratif üç nokta | Salt okunur bilgiler inline; can sayısı metinle; arama noktaları çıkarıldı |
| Tema | Pano varsayılan olarak zorunlu dark açılıyordu | İlk tema sistem tercihinden, düğmeyle karşılaştırılabilir; referansların dark olduğu kaydı korunur |
| Seçili durum | Kalın çizgi, dolgu, işaret üst üste | 1 birim sınır ve seçim işareti; focus gerektiğinde ayrı 2 birim dış çizgi |
| Semantik renkli yüzeyler | İkincil metin sınıfı griyi devralabilir | Rol yüzeylerinde metin aynı semantik yazı rengini devralır |
| KIT.html genel pano | Doküman ve renk bilgisi de kutu katmanları oluşturuyor | Doküman yüzeyleri düzleştirildi; gerçek kontrol örnekleri sınırlı demo yüzeyinde kaldı |

## Bilinçli korunan ürün kararları

Mor kullanıcı seçimi ve mevcut marka kararımızdır; katalogda mor geçiyor diye değiştirilmedi. Sora tek aile olarak kalır; tipografi boyut/ağırlıkla hiyerarşi kurar. Sen/rakip semantik rozetleri, skorun büyük rakamı, gerçek can/ilerleme bilgisi mobil oyunda işlevlidir. Kullanıcının seçtiği ayrı çerçeveli öneri satırları ve haftanın maçı marka bandı korunur. Cevap kontrollerinin sınırları erişilebilirlik için gerekli olabilir; dekoratif kart karşıtı kural bunları kaldırmaz.

## Doğrulama ve kalanlar

HTML yapısı, 15 örnek ve 5 aile, benzersiz kimlikler, local bağlantılar, her iki temada kullanılan CSS token adları, kontrast token raporu ve ZIP bütünlüğü kontrol edilir. Bunlar rendered taşma, gerçek Sora, native dokunma hedefi veya ekran okuyucu kabulü değildir. Gerçek mobil uygulamada 320–430 genişlik, büyük metin, iki tema ve gerçek klavye kontrolü gereklidir. Saklanan önceki kaynaklar evidence/slop-review/ altında.
