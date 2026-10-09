# Gerçek cihazda yapılacak testler

Durum (2026-10-09): **hiçbiri yapılmadı.** Bu makineden telefon build'i çıkmıyor (iOS için Mac + Xcode ve onaylı Apple hesabı gerekir;
Android için mağaza build'i henüz alınmadı). Bugüne kadarki bütün doğrulama web görüntüsüyle ve klavyeyi taklit eden geliştirme
kipiyle (`?kb=1`) yapıldı. Aşağıdakiler mağaza / EAS build'i çıkınca **ekipte telefonu olan kişilerce** yapılır; kod yazan taraf
(Claude) bunları yapamaz ve yapılmış sayamaz.

Kaynak: tasarım kitinin kabul ölçütleri (Kickoff-Design-Kit, `AGENT-BRIEF.md`) ve klavye düzeni çalışması (`CLAUDE.md`, "Klavye açıkken düzen").

## Kural

- iPhone ve Android **ayrı ayrı** denenir; biri öbürünün yerine geçmez.
- Sonuç yazılırken platform, cihaz ya da emülatör ve işletim sistemi sürümü belirtilir.
- Gerçek cihazda denenmeyen klavye, ses ve titreşim davranışı "doğrulandı" sayılmaz. Tarayıcı görüntüsü kanıt değildir.
- Hesap silme gibi geri alınamayan işlemler gerçek kullanıcı verisiyle denenmez.

## Liste

**Klavye** (en öncelikli; bugüne kadarki en büyük şikâyet buradan geldi)
- [ ] Yazı kutulu ekranlarda klavye açılınca kutu ve etkin öneri görünür kalıyor; hiçbir parça başka parçanın üstüne binmiyor.
      Ekranlar: takma ad, odaya katıl, hesap kodu, takım seçimi, tur, klasik merdiven, kariyer yolu, sıradaki kulüp.
- [ ] Öneriye ilk dokunuşta seçim çalışıyor (klavye kapanıp ikinci dokunuş istemiyor).
- [ ] Öneri listesi kaydırılarak sonuna kadar görülebiliyor.
- [ ] Skor ve durum bildirimi klavyenin arkasında kalmıyor.
- [ ] iPhone Safari (web sürümü): klavye açılınca sayfa yukarı kaymıyor, altta beyaz şerit çıkmıyor.

**Ekran alanları**
- [ ] Çentik, durum çubuğu, iPhone alt çizgisi ve Android gezinme çubuğu içeriği ya da düğmeleri örtmüyor.
- [ ] Android geri tuşu ve iPhone geri kaydırması her ekranda tutarlı; maçtan çıkış beklenen yere dönüyor.
- [ ] 320 / 360 / 390 / 430 genişlikte kritik içerik kesilmiyor, bütün düğmelere ulaşılıyor.

**Yazı boyutu**
- [ ] Telefonun yazı boyutu ayarı %100, %150 ve %200 iken: takım ve oyuncu adları kesilmiyor, düğmeler taşmıyor.

**Ekran okuyucu** (iPhone VoiceOver, Android TalkBack)
- [ ] Beş pilot ekran baştan sona yapılabiliyor: alan adları, öneri seçimi, durum, geri, pencere, skor anlaşılır okunuyor.
- [ ] Süre her saniye okunmuyor; tur başlangıcı, sonuç gibi anlamlı değişiklikler bir kez okunuyor.
- [ ] Süreli oyunda ekran okuyucuyla kalan kısıtlar ayrıca not ediliyor.

**Sistem tercihleri**
- [ ] Sistem teması değişince (açık / koyu) uygulama uyuyor.
- [ ] "Hareketi azalt" açıkken geçişler sade.
- [ ] Ses ve titreşim kapalıyken doğru / yanlış hâlâ anlaşılıyor.

**Akış**
- [ ] Takım seçimi, yanlış cevap kilidi, tekrar dene ve rövanş mevcut kurallarla çalışıyor.
- [ ] Hesap silme onayı ve ekran geçişleri bozulmamış.

## Sonuçlar

Denendikçe buraya yazılır: tarih · kim · platform, cihaz, sürüm · bulunanlar.

(henüz kayıt yok)
