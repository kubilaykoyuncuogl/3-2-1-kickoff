# Kickoff — Expo / React Native tasarım sistemi v0.2

Durum: dört bileşenin görsel yönü kullanıcı tarafından seçildi; birleşik önizleme ayrıca değerlendirme bekliyor. Seçimler ve güncel yerleşim [SELECTED-DIRECTION.md](SELECTED-DIRECTION.md) içinde.
Tarih: 9 Ekim 2026. İstemci: Expo / React Native, mevcut rota dizini `app/`. Hedef: iOS ve Android native mobil uygulama.

## Mobil platform kapsamı

Ürün iOS ve Android telefonlarda çalışacak. Ortak marka, renk tokenları, Sora tipografisi ve oyun bileşenleri iki platformda tutarlı kalır. Sistem davranışları platforma uygun uygulanır: safe area, status/navigation bar alanları, native klavye, geri navigasyonu, modal kapanışı ve erişilebilirlik.

48 birim dokunma hedefi kitin her iki platform için ortak ürün kararıdır. React Native ölçüleri mantıksal birimlerdir; kaynak PNG pikselleri fiziksel ekran pikseli veya sabit cihaz boyutu olarak kullanılmaz. Minimum yükseklikler sistem metin ölçeğiyle büyüyebilir.

Pilot ekranlar hem iOS hem Android üzerinde ayrı doğrulanır. Telefonun üst/alt sistem alanları, ekran kesikleri, klavye, platform geri davranışı, büyük metin ve VoiceOver/TalkBack testleri kabulün parçasıdır. Tarayıcıdaki tasarım görüntüsü native uygulama testinin yerine geçmez.

## Amaç ve kaynak

137 kaynak ekranı ortak renk, tipografi, bileşen ve durum kurallarıyla kodlanabilir hale getirmek. Oyun kuralları, puanlama ve süreleri bu çalışma değiştirmez.

Kaynak: [Kickoff Ekran Onayı](https://claude.ai/artifact/QCatPimAFP4BB4RPFmfanc). Ekran envanteri [SCREEN-INVENTORY.md](SCREEN-INVENTORY.md), yakalanan metin [source-content.txt](source-content.txt), inceleme [REVIEW.md](REVIEW.md).

Görsel değerlendirme beş temsilî ekranla sınırlıdır. Kaynak gerçek çalışan mobil uygulama yerine PNG ekranları gösteriyor. Bu nedenle erişilebilirlik rolleri, gerçek dokunma alanları, metin ölçekleme ve klavye davranışı burada doğrulanmış değildir.

## Görsel yön

Sade, okunabilir, hızlı futbol bilgi oyunu. Mevcut mor–amber kimliği ve Sora korunur. Nötr zeminler geniş alanları taşır; vurgu renkleri eylem, oyuncu kimliği ve durum anlatır. Küçük metinler ve ağır yazı ağırlıklarının aynı anda yarattığı yoğunluk azaltılır.

Kartlarda varsayılan gölge yok. Yüzey ayrımı gerektiğinde 1 birim dekoratif çizgi kullan. Çerçeve bir form alanını veya etkileşimli alanı ayırt etmek için gerekliyse daha güçlü `controlBorder` kullan. Kaynaktaki mor/amber gölge tonları kitin ilk sürümünde kullanılmaz.

## Renk kararları

Tam ve makinece okunabilir değerler [tokens.json](tokens.json); Expo için bağımsız TypeScript modülü [kickoff-theme.ts](kickoff-theme.ts).

| Rol | Açık | Koyu | Kullanım |
|---|---|---|---|
| Zemin | #F2F2F5 | #131218 | Ekranın ana zemini |
| Yüzey | #FFFFFF | #1C1B23 | Kart, input, liste satırı |
| Ana yazı | #1B1A21 | #ECEBF2 | Başlık ve gövde |
| İkincil yazı | #5F5D6B | #A09EAD | Açıklama, yardımcı bilgi |
| Dekoratif çizgi | #C9C8D3 | #3A3946 | Ayraç, zorunlu olmayan kart sınırı |
| Kontrol sınırı | #858292 | #747184 | Input ve gerekli etkileşim sınırı |
| Ana eylem | #5E4BC9 | #8C7CF0 | Bir ekranda baskın devam/başlat eylemi |
| Ana eylem yazısı | #FFFFFF | #131218 | Açık temada beyaz, koyu temada koyu yazı |
| Senin yazın / zeminin | #4A3AAE / #E9E5FA | #B3A7FF / #272443 | Sen etiketi ve takımın |
| Rakip yazısı / zemini | #895706 / #FBEFD8 | #F4C77A / #3A2D14 | Rakip etiketi ve takımı |
| Doğru yazısı / zemini | #167A52 / #DCF3E8 | #4FCF93 / #163528 | Doğru cevap ve başarı |
| Yanlış yazısı / zemini | #B72E48 / #FBE1E7 | #FF7D96 / #3C1B25 | Hata, yanlış cevap, yıkıcı eylem |

Kaynaktan anlamlı değişiklikler:

- `controlBorder` eklendi. Eski açık/koyu güçlü çizgiler yüzey üzerinde sırasıyla 2.66:1 ve 2.54:1; yeni değerler 3.75:1 ve 3.61:1.
- Açık tema yanlış yazısı #C2334F → #B72E48: pembe durum zemini üzerindeki kontrast 4.39:1 → 4.87:1.
- Açık tema amber yazısı #9A6207 → #895706: küçük rakip bilgileri için daha fazla kontrast payı.
- Ana menüde “Tek oyna” için amber dolgu yerine morun soluk ikincil eylem yüzeyi. Amberin rakip anlamı korunur. Uyarı ambere ihtiyaç duyarsa ikon ve açık “Uyarı” metniyle ayrılır.
- Koyu temada mor dolgu üzerine beyaz yazı kullanma: oran 3.36:1. `primaryText` ile 5.55:1 elde edilir.
- Amber dolgu üzerine beyaz yazı kullanma. Rakip etiketleri `opponentText` + `opponentSubtle` çiftini kullanır.

Renk tek başına bilgi taşımaz: “Sen”, “Rakip”, “Doğru”, “Yanlış” metinleri görünür kalır. Takım marka renkleri yalnızca takım kimliğinde kullanılabilir; genel eylem rengini değiştirmez. Marka zeminindeki her yazı çifti ayrıca ölçülür.

## Tipografi kararları

Tek font ailesi: **Sora**. Font çeşitliliği yerine boyut, ağırlık ve boşluk ile hiyerarşi oluştur.

| Token | Boyut / satır yüksekliği | Ağırlık | Kullanım |
|---|---|---|---|
| display | 40 / 48 | 800 | Büyük vurgu; logo kaynağının yerine geçmez |
| countdown | 64 / 72 | 800 | Tek rakamlı 3–2–1 geri sayım |
| navigationTitle | 20 / 28 | 600 | Ayarlar / Hesap gibi navigasyon başlıkları |
| screenTitle | 28 / 36 | 700 | Ekranın başlığı |
| sectionTitle | 20 / 28 | 700 | Mod / takım başlığı |
| score | 32 / 40 | 700 | Skor; eş aralıklı rakamlar desteklenirse etkinleştir |
| scoreCompact | 20 / 28 | 700 | Klavye açıkken skor |
| timer | 24 / 32 | 700 | Kalan süre |
| body | 16 / 24 | 400 | Açıklamalar |
| bodyStrong | 16 / 24 | 600 | Oyuncu adı, liste satırının ana bilgisi |
| label | 16 / 22 | 600 | Düğme ve seçim eylemi |
| fieldLabel | 14 / 20 | 600 | Input üstündeki kalıcı alan etiketi |
| input | 18 / 26 | 400 | Yazılan metin |
| caption | 14 / 20 | 500 | Doğum yılı, yardımcı metin, ikincil bilgi |

Kritik bilgi 14'ten küçük olmaz. Tamamı büyük harf etiketleri zorunlu değil; “Takım seçimi”, “Ayarlar” gibi normal yazımı tercih et. 800 ağırlık tüm başlıklara yayılmaz. Uzun oyuncu ve takım adları satır kırabilir; küçülterek sığdırma yapılmaz.

Logo için kaynak marka varlığını kullan. Font ailesinde doğrulanmış italik dosya yoksa sahte italik yüz oluşturma. Geri sayım 800 düz Sora ile de kullanılabilir; kaynak logoyu yeniden çizmek bu paketin kapsamı değildir.

Expo font aliasları `Sora-Regular`, `Sora-Medium`, `Sora-SemiBold`, `Sora-Bold`, `Sora-ExtraBold`. Gerçek font dosyalarını bu aliaslara bağla. Ağırlık için yüklenen font yüzünü seç; aynı bileşende ek `fontWeight` ile yapay ağırlık üretme. Ayrıntılar ve Expo'nun platform farkları için [Expo font belgeleri](https://docs.expo.dev/develop/user-interface/fonts/).

## Ölçü ve yerleşim

- 4 birimlik boşluk ölçeği: 4, 8, 12, 16, 20, 24, 32, 40, 48.
- Ekran yatay boşluğu 20. Çok dar ekranda 16'ya inebilir. Safe area boşlukları ayrıca uygulanır.
- Etkileşimli alan hedefi en az 48 × 48 mantıksal birim. Düğme minimum 52, input ve öneri satırı minimum 56 yüksekliğinde. Bunlar sabit yükseklik değildir; büyük metinle büyür.
- Kontrol radius 12, kart 16, sheet üst köşeleri 24. Pill sadece rozetlerde.
- Bölümler arası 24; ilişkili öğeler arası 8–12; kart içi boşluk 16.
- Tablet ve geniş ekranda içerik 560 birime kadar ortalanır. Telefon ekranını sabit 400 × 880 olarak kodlama; bu sadece kaynak PNG boyutudur.
- Mevcut oyun alanındaki boşluğu dekoratif içerikle doldurma. Skor, süre, input ve sonuçların takip edilebilirliğini düzelt.

## Erişilebilirlik hedefi

WCAG 2.2 AA'nın ilgili kontrast ve etkileşim ilkeleri ile native VoiceOver/TalkBack davranışlarını hedefle. Bu paket bir uygunluk sertifikası değildir.

Normal metin çiftlerinde en az 4.5:1, gerekli kontrol sınırları/ikonlarında en az 3:1 ölç. [W3C kontrast açıklaması](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Native kitte 48 birim dokunma hedefi ürün kararıdır; WCAG'nin web için 24 CSS piksel alt sınırıyla aynı ölçü veya iddia değildir. [W3C hedef boyutu açıklaması](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

60 tanımlı, opak renk çifti hesaplandı ve eşiklerini geçti; [contrast-report.json](contrast-report.json). Bu sonuç font, alfa/opaklık, gerçek rendered piksel, marka kartları veya bütün ekranların erişilebilirliğini kapsamaz. Renk çiftlerine sonradan opacity eklemek raporu geçersiz kılar.

- `allowFontScaling` açık. Genel bir `maxFontSizeMultiplier` sınırlaması koyma. Büyük metinde yükseklikleri ve satırları esnet. [React Native Text](https://reactnative.dev/docs/text).
- Buton, input, switch ve seçim durumları gerçek native erişilebilirlik özellikleri taşır; kit [COMPONENTS.md](COMPONENTS.md) içinde tanımlıdır. [React Native accessibility](https://reactnative.dev/docs/accessibility).
- İkonun adı görünür metni destekler; yalnızca dekoratif ikonlar ekran okuyucudan gizlenir.
- Placeholder görünür alan etiketi yerine geçmez. Inputun üstünde “Oyuncu adı” veya “Takım adı” yazısı bulunur.
- Hata alanın yakınında metinle belirtilir. “Yanlış · 3” yerine kuralların verdiği mevcut süreyle “Yanlış tahmin. 3 saniye sonra yeniden deneyebilirsin.”
- Süre ve skor erişilebilir değere sahiptir. Her saniye duyuru yapma; tur başlangıcı, kritik eşik ve tur sonucu gibi anlamlı değişiklikleri bir kez duyur. Kritik eşik mevcut oyun kurallarından alınır.
- Canlı rekabette süreyi tek taraflı uzatma. Süreli oyunların erişilebilirliği ürün kararı gerektirir; süre kısıtı zorunlu değilse süre ayarı veya süresiz antrenman yolu tasarla. Zorunlu rekabet süresinin gerekçesini belgeleyip uyum iddiasından önce incele.
- Azaltılmış hareket tercihini sistemden oku, uygulama tercihi varsa sistem tercihiyle birlikte uygula. Yanıp sönme, sürekli titreşim ve bütün ekranın renk patlaması yok. Ses/titreşim kapalıyken durum hâlâ anlaşılır.

## Klavye açıkken

Klavye 19 ayrı rota değil, ekranın bir yerleşim durumudur. Native klavye kullanılır; kaynak klavye resmi UI olarak taşınmaz.

Üstte kullanıcılar, skor ve takım rozetleri; ardından süre, görünür label + input ve kalan yüksekliği kullanan kaydırılabilir öneri listesi bulunur. Öneriler ayrı çerçeveli satırlardır. Skor klavye açıkken gerektiğinde kompaktlaşır; altta tekrarlanmaz. Geri bildirim input/liste yakınında tek alanda gösterilir. Bu alanlar büyük fontta sığmazsa kontrollü dikey kaydırma sağla, input ve aktif öneri görünür kalsın. Öneri sayısını sabit beşe düşürme; bütün sonuçlara kaydırarak erişilebilsin. Skoru rastgele float koordinatlarla konumlandırma.

`KeyboardAvoidingView` veya projedeki mevcut keyboard çözümünü kullan; Android resize/pan davranışını mevcut Expo yapılandırması ve gerçek cihazda doğrula. Öneriye basınca ilk dokunuşla seçim çalışmalı; odak/klavye davranışı tur akışına göre korunmalı. Klavye kapanınca aynı seçili state devam eder.

## Kodlama agentına aktarım

Önce [AGENT-BRIEF.md](AGENT-BRIEF.md), sonra bu dosya ve [COMPONENTS.md](COMPONENTS.md) okunur. `kickoff-theme.ts`, örneğin `src/theme/kickoff.ts` içine taşınabilir. `app/` mevcut Expo Router rotalarını taşır; tema, yardımcı fonksiyon ve bileşen dosyalarını rota dizinine koyma. Gerçek depo yapısı varsa onun mevcut düzeni önceliklidir.

Bu çalışma mevcut proje klasöründe çalışan Expo uygulaması bulunmadığı için yalnızca tasarım teslim paketidir. Native uygulama çalıştırılmadı; beş kaynak ekran incelendi. Renk ve font kararları ilk öneridir; nihai onay ve uygulama sonrasında yeniden doğrulama gerekir.


## v0.2 Product Design kontrolü

Renk paleti sabit tutuldu. `textPlaceholder` ve `iconSecondary`, doğrulanmış `textSecondary` değerine bağlandı; yeni bağımsız gri ton eklenmedi. İki rol ayrı isimlerle kullanılır. Placeholder görünür form etiketinin yerine geçmez.

Navigasyon başlığı 20/28 600, sayfa başlığı 28/36 700 olarak ayrıldı. Klavye açık skor 20/28 700; tek rakamlı geri sayım 64/72 800. Alan etiketi 14/20 600; düğme yazısı 16/22 600. Yeni rol değerleri görsel seçeneklerde değerlendirilecek öneridir, henüz onaylanmış ekran tasarımı değildir.

Öncelik: maç sırasında süre, tahmin alanı ve öneriler; skor ikincil. Klavye açıldığında skor kompaktlaşır, sonuç listesinin erişimi korunur. Aynı olay için iki konumda çelişen status mesajları üretme.

## Tasarım sadeliği: bu kitin kuralları

- Önce boşluk, yazı hiyerarşisi ve ayraç; kart sınırı yalnızca bağımsız nesne, gerçek kontrol veya paylaşım çıktısında.
- Ana menüde seçilen Online/Tek oyun düğmeleri ve ayrı öneri satırları korunur. ModeRow için gruplu satırlar kullanılır.
- Kulüp ipucu bir bilgi grubudur; ClubPairPrompt kapalı kart gerektirmez. FactCard nötr bilgi başlığı ve ayraçla uygulanabilir. Paylaşılacak sonuç yüzeyi içinde tekrar kart katmanları ekleme.
- Salt okunur HUD/kapsam bilgisini düğme gibi rozetlerle doldurma. Can, çarpan, skor, süre anlamlı metinlerle okunur.
- Mor, Sora ve rol renkleri kullanıcı kararıdır. Yalnızca bir anti-slop listesine uymak için palet/font değiştirme. Gradient, glow, dekoratif yan renk şeridi ekleme.
- Native ürün ekranlarında bileşen kod adları, ref numaraları ve geliştirici açıklamaları yer almaz; bunlar kit dokümanlarıdır.
- Tek tema zorunlu değil; mevcut Sistem/Açık/Koyu tercihini uygula. Seçili ile focus stillerini ayır.

İnceleme gerekçeleri ve kanıt sınırı [SLOP-REVIEW.md](SLOP-REVIEW.md) içinde.
