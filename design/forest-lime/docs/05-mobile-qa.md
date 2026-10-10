# Mobil QA ve developer kabul listesi

## Bu paket için ölçülenler

Fiilî kontrol kaydı: `../qa/verification.md`. Görsel katalog kontrolü gerçek native cihaz testi yerine geçmez.

## Uygulama tesliminde kabul kriterleri

- [ ] İki seçili kaynakla 393×852 aynı viewport/state karşılaştırması yapılır; header, CTA sırası, kartların ayrılması ve aynı aktif kapsül korunur.
- [ ] 320/360/393/427 genişlikte yatay taşma yok; uzun nickname, takım adı, büyük puan ve count wrap kontrol edilir.
- [ ] 200% metin/dinamik type: satırlar/kartlar büyür, seçim ve CTA metni kaybolmaz.
- [ ] iOS ve Android safe area, status bar ve navigation bölgesi ölçülür. Son footer nav üstüne scroll edebilir.
- [ ] Klavye görünürken input ve hata mesajı görünür; sheet açılmadan klavye kapatılır.
- [ ] Tüm eylemler en az native44pt/48dp; tasarım hedefi48. Drag sonunda yanlış tap tetiklenmez.
- [ ] Screen reader nav'ın seçili hedefini, input label/error'u ve sheet başlığını okur; dekoratif stadyum gizlenir.
- [ ] Metin kontrastı gerçek composited surface'te ölçülür; normal yazı4.5:1, büyük yazı3:1, gerekli kontrol sınırı3:1 hedeflenir. Sessiz dekoratif border kontrol göstergesi sayılmaz.
- [ ] Focus modal içinde kalır; kapatınca açan elemana döner. Sistem geri ilk modalı kapatır.
- [ ] Loading/empty/error/timeout ayrıdır; double submit engellenir. Bilinmeyen toplam0 olmaz.
- [ ] Maçlar tabı ve home entry aynı sayfayı açar; sheet yalnız fixture CTA'dan açılır.
- [ ] Süre/puan sunucu veya otoriter oyun state'ine bağlıdır; arka plana girip dönüşte senkron kontrol edilir.
- [ ] SVG'ler native renderer'da açılır; path transform ve transparan logo görünümü test edilir.
- [ ] Reduce motion, offline başlangıç, bağlantı kaybı, ses on/off ve geri dönüş kontrol edilir.

## Açık ürün kararları

Deadline sonrası takım değişimi, katkı yazım anı, backend hata kodları ve oyun sırasında root menü görünürlüğü için mevcut ürün sahipliği/uygulama akışı doğrulanmalı. Bunlar tasarımın stilini seçmek için yeniden onay gerektirmez; geliştirme entegrasyonunda çözülmesi gereken davranışlardır.
