# Yönlendirme ve durum davranışları

## Temel akış

Ana sayfa → Haftanın maçları giriş kartı **veya** Maçlar tabı → Haftanın maçları → ilgili kartın Tarafını seç footer'ı → takım seçimi sheet → takım seç → onay → aynı kartta seçili takım / Değiştir.

`Ana sayfa` ve `Maçlar` top-level sayfalardır. İki giriş aynı haftalık sayfayı açar. Tab değişiminde ilgili scroll konumu ve mevcut oturum seçimi korunur. Sheet açıksa önce kapatılır; sistem geri sheet'i kapatır, root sayfada platform konvansiyonu uygulanır. Uygulama geri davranışını katalog tarayıcısındaki history ile karıştırma.

## Takım seçimi

1. Sheet fixture adını gösterir, iki seçenek görünür. Önceden seçim varsa check ile gösterilir.
2. Kullanıcı tercih değiştirir; `Seçimi onayla` ancak seçenek seçildiğinde kullanılabilir.
3. Onay sırasında busy; tekrar gönderim yok. Başarılı yanıt gelince sheet kapanır, footer ve başarı bildirimi güncellenir.
4. Hata: sheet açık kalır, önceki sunucu seçimi korunur, mesaj + tekrar dene.
5. Kapat/geri/scrim: yeni seçim kaydedilmez. Focus açan footer'a döner. Native uygulamada ekran okuyucu sheet dışına çıkamaz.

Seçim değiştirmenin deadline sonrası ürün kuralı henüz tanımlanmadı. Kilitleme/güncelleyebilme backend'den gelmeli; tasarım yeni bir kural uydurmaz. Bitiş state'i için metin `Katılım sona erdi` önerisi vardır.

## Online / solo

Mevcut oyunun ilgili girişine bağlanır. Katalog start düğmeleri yalnız etkileşim örneği gösterir. Matching, rakip bulma, oturum kesilmesi veya Elo hesaplama backend işidir. Yeni solo mod kuralı bu pakete dahil değil.

## Oyun primitive'leri

Sayaç yalnız otoriter deadline/state üzerinden güncellenir. Yanlış cevapta 5sn lock, sadece input/sending'i durdurur; ana 15sn round timer ayrı kalır. Kabul edilmiş cevap +1 skor bildirir. 3 puan game-over sonucuna gider. UI autoplay/timer sonunda kendi kazanan kararını vermez. Oyun sonrası ekran ve tam oyuncu seçme akışı seçili ekran sayılmaz.

## Katalog davranışı ve üretim farkı

Katalog nav seçimi, ses switch'i, takım sheet'i, onay toast'u, yerel form error state'i, dialog kapatma ve örnek timer gösterir. Veriler yalnız bellekte tutulur. Refresh sonrası sıfırlanır. Auth, matchmaking, kalıcı ayarlar, gerçek takımlara katkı, cevap doğrulama ve network retry uygulanmadı.
