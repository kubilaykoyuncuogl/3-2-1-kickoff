# Kodlama agentına verilecek görev

Kickoff istemcisi Expo / React Native kullanıyor ve mevcut route dizini `app/`. Ekli tasarım paketini mevcut uygulamaya uygula. Çalışan domain/oyun kuralları, ağ protokolü, puanlama, süre ve hesap davranışlarını koru. Paket v0.2 token standardını ve kullanıcının seçtiği dört görsel bileşeni içerir. Birleşik önizlemenin tamamı ayrıca değerlendirme bekliyor; dört parça seçimi SELECTED-DIRECTION.md içinde kayıtlıdır.

Hedef ürün **iOS ve Android native mobil uygulama**. Ortak tasarım tokenları ve bileşenler kullan; safe area, sistem barları, klavye, geri davranışı, modal ve erişilebilirlik uyarlamalarını platforma göre yap. Web veya tarayıcı önizlemesi native kabul testlerinin yerine geçmez.

## Önce oku

1. Depodaki AGENTS.md, package.json, Expo SDK/RN sürümü, `app/` rotaları, mevcut theme/fonts/components ve test düzeni.
2. `design/SELECTED-DIRECTION.md`: kullanıcı seçimleri, birleşik referans ve üst skor / ayrı öneri satırı yerleşimi. Ardından `design/DESIGN.md`: renk, font, spacing ve erişilebilirlik kararları.
3. `design/COMPONENTS.md`: bileşen ve durum sözleşmeleri.
4. `design/kickoff-theme.ts` ve `design/tokens.json`: tek değer kaynağı.
5. `design/REVIEW.md` ve `design/SCREEN-INVENTORY.md`: kaynak ekran kimlikleri ve kanıtın kapsamı.

## Uygulama sırası

1. Mevcut yapıya uyumlu bir theme katmanı oluştur. Tek bir token kaynağını kullan; iki dosyayı bağımsız güncelleme. TS dosyası JSON'dan üretilmiş aynadır. Theme/helper/component dosyalarını `app/` içine rota olarak koyma; mevcut `src/` veya ortak bileşen düzenini kullan.
2. Sistem/açık/koyu tema çözümlemesini mevcut ayara bağla. Mevcut kullanıcı tercihlerini ve persistence davranışını koru.
3. Sora 400/500/600/700/800 gerçek font yüzlerini aliaslara yükle. Mevcut Expo SDK'nin font yöntemini kullan. Paket yoksa bağımlılığı mevcut sürümle uyumlu şekilde ekle; keyfi SDK upgrade yapma. Logo için mevcut varlığı kullan.
4. AppText, Button, IconButton, Field, SuggestionRow, TeamBadge, Scoreboard, RoundTimer, FeedbackBanner, SettingsRow bileşenlerini önce kur/uyarla. Var olan benzer bileşenleri düzelt; aynı iş için ikinci sistem yaratma.
5. Beş pilot ekranı uygula: c01-01A, c04-04B, c14-04B, c02-01A, c04-04D. Pilotta açık/koyu tema, büyük metin ve native klavye davranışını doğrula.
6. Pilot sonuçlarını somut ekran görüntüleriyle sun; seçilen görsel yön doğrulandıktan sonra ortak şablonları kalan ekranlara yay. Kaynak onay sayfasındaki mühür/revize kayıtlarını değiştirme.

## Kesin uygulama kuralları

- Renkler semantic tokenlardan; koyu primary üzerindeki yazı `#131218`, beyaz değil.
- Amber rakip bilgisi için; “Tek oyna” ikincil mor yüzey kullanır.
- Body 16/24 regular; kritik caption en az 14/20; oyuncu adları 16/24 semibold. Input 18/26 regular; fieldLabel 14/20 semibold; navigationTitle 20/28 semibold; scoreCompact 20/28 bold; countdown 64/72 extrabold. Metin sığdırmak için font küçültme.
- `allowFontScaling` açık; ekran/düğme/input yükseklikleri minimum değer, fixed height değil.
- Touch target en az 48×48 mantıksal birim; hitSlop gerekirse yalnızca alanlar çakışmayacak şekilde. Görsel icon 24 olabilir.
- Büyük fontta tema seçimlerini ve takım adlarını sar; önemli adları veya CTA metnini kesme.
- TextInputların görünür labelı ve erişilebilir adı olsun. Web ARIA attribute'larını native prop yerine kullanma.
- Buttons: `accessibilityRole="button"`, gereken `accessibilityState` disabled/busy/selected. Switch state native kontrolle veya eşdeğer checked özelliğiyle okunabilsin.
- Status değişikliklerini platform desteklerine göre duyur: Android polite live region, iOS uygun AccessibilityInfo duyurusu. Aynı olayı iki yöntemle çift okutma. Her saniye countdown duyurusu yapma.
- Reduced motion sistem ve uygulama tercihinden türetilir. Ses ve haptic tercihlerine uy. Durum metin+ikonla da anlaşılır olsun.
- Öneri seçimi ilk dokunuşta çalışsın; native klavye gerçek viewport/keyboard olaylarına göre yönetilsin. Kaynak keyboard PNG'sini bileşen olarak koyma.
- Yanlış/kilit/ağ durumlarını tek açık status alanında göster; çelişen sayaç veya kopya mesajlar üretme.
- Gerçek oyunun süre kısıtı, online rekabet ve ekran okuyucu etkileşimini ayrıca değerlendir; mevcut kuralları sessizce değiştirme.

## Kabul ölçütleri

- Beş pilot ekran hem iOS hem Android'de ayrı kontrol edilir. Sonuçta platform, cihaz/emülatör ve OS sürümü belirtilir; gerçek cihazda test edilmeyen klavye, ses veya haptic davranışları doğrulanmış sayılmaz.
- Ekran kesikleri, status bar, iOS home indicator ve Android sistem navigasyon alanları içerik/eylemleri örtmez. Android sistem geri davranışı ve iOS mevcut geri navigasyonu tutarlıdır.
- Uygulamanın mevcut typecheck/lint ve ilgili davranış testleri geçer. Görünüş değerlerini birebir tekrar eden gereksiz unit testler ekleme.
- Seçim, yanlış cevap kilidi, tekrar dene ve rövanş gibi davranışlar mevcut kurallara göre çalışır.
- İki temada kontrast çiftleri token raporuyla tutarlı. Gerçek screenshotta opacity/overlay/brand rengiyle değişen çiftler ayrıca ölçülür.
- 320/360/390/430 birim genişlikte ve OS metin ölçeği 100% / 150% / 200% civarında cihazın desteklediği ayarlarda kritik içerik kesilmez; bütün eylemlere erişilir. 200% üstü platform büyük metin ayarlarını da dene.
- iOS VoiceOver ve Android TalkBack ile pilot akış yapılabilir: alan adları, öneri seçimi, durum, geri, modal ve skor anlaşılır. Timed gameplay için kalan kısıtlar açık raporlanır.
- Native keyboard iki platformda açılır; input ve aktif öneri görünür; sonuçlara kaydırarak erişilir; skor/status klavye arkasında kalmaz.
- Sistem tema değişimi, reduced motion, ses/titreşim kapalı durumları denenir.
- Native route geçişleri, geri davranışı ve hesap silme teyidi bozulmaz. Hesap silme gibi yıkıcı işlemler testte gerçek kullanıcı verisiyle uygulanmaz.
- Teslimde hangi ekranların uygulandığını, kanıt screenshotlarını, kontrolleri ve kalan belirsizlikleri belirt. Yalnızca renk testleri geçti diye “tam erişilebilir” deme.

## Bu paketin sınırları

Bu klasörde gerçek Expo istemcisi yok; uygulama entegrasyonu yapılmadı. 137 ekranın ad/kimlik envanteri var; beş ekran görsel olarak incelendi. Görsellerin tamamı indirilemedi; kaynak screenshot kanıtları `design/evidence/` altında. Backend'e bağlı onay verisi oturum duvarı arkasında. Bu verileri kullanılmış ya da tüm ekranlar onaylanmış kabul etme.

## Ek online referansları

ONLINE-COMPONENTS.md ve COMPONENT-LIBRARY.html kapsam, arama, takım seçimi ve tur sonucu için önerilen bileşenleri gösterir. Ek sekiz kaynak koyu tema örneğidir. Rakibin puan alması opponent durumu; kimse bilemedi neutral durumdur. Bu genişleme native uygulama onayı veya bütün kaynak ekranların incelendiği anlamına gelmez.

## Tek oyun / haftalık / sonuç referansları

GAME-COMPONENTS.md dosyasını okuyun. Kütüphanenin 07–15 grupları örnek durumları gösterir; native uygulama onayı değildir. Kaynak ekranlardaki alan büyüklüklerini sabit yükseklik olarak taşımayın; domain verisi, oyun süresi ve kilit kurallarını koruyun. Solo modda iki kulübü sen/rakip olarak renklemeyin.

## Tasarım sadeliği: bu kitin kuralları

- Önce boşluk, yazı hiyerarşisi ve ayraç; kart sınırı yalnızca bağımsız nesne, gerçek kontrol veya paylaşım çıktısında.
- Ana menüde seçilen Online/Tek oyun düğmeleri ve ayrı öneri satırları korunur. ModeRow için gruplu satırlar kullanılır.
- Kulüp ipucu bir bilgi grubudur; ClubPairPrompt kapalı kart gerektirmez. FactCard nötr bilgi başlığı ve ayraçla uygulanabilir. Paylaşılacak sonuç yüzeyi içinde tekrar kart katmanları ekleme.
- Salt okunur HUD/kapsam bilgisini düğme gibi rozetlerle doldurma. Can, çarpan, skor, süre anlamlı metinlerle okunur.
- Mor, Sora ve rol renkleri kullanıcı kararıdır. Yalnızca bir anti-slop listesine uymak için palet/font değiştirme. Gradient, glow, dekoratif yan renk şeridi ekleme.
- Native ürün ekranlarında bileşen kod adları, ref numaraları ve geliştirici açıklamaları yer almaz; bunlar kit dokümanlarıdır.
- Tek tema zorunlu değil; mevcut Sistem/Açık/Koyu tercihini uygula. Seçili ile focus stillerini ayır.

İnceleme gerekçeleri ve kanıt sınırı [SLOP-REVIEW.md](SLOP-REVIEW.md) içinde.
