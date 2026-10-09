# Kickoff bileşen ve durum sözleşmeleri

Bu sözleşmeler Expo / React Native kodlama agentı içindir. Kaynak ekran kimlikleri [SCREEN-INVENTORY.md](SCREEN-INVENTORY.md). Sayı, süre, skor ve kilit davranışı mevcut domain verisinden gelir.

## Ortak bileşenler

| Bileşen | Görsel / davranış | Erişilebilirlik |
|---|---|---|
| AppText | `typography` tokenından yüz/boyut/satır yüksekliği; tema rengi | Font scaling açık; önemli adlar ellipsis ile gizlenmez |
| Screen | Safe area, zemin, 20 gutter; dar ekranda 16 | Mantıksal okuma sırası; birden fazla alt kontrolü tek accessible container içine hapsetme |
| ScreenHeader | Geri düğmesi, ekran başlığı, gerekirse ikincil eylem | Başlık header rolü; geri button etiketi “Geri”; 48 hedef |
| Button | Primary / secondary / neutral / danger; minHeight 52; 16 label; yatay padding 16 | button rolü; disabled/busy state; görünen ad erişilebilir ada dahil |
| IconButton | 24 ikon, 48 dokunma alanı | button rolü ve açık ad; dekoratif ikon gizli |
| Field | Kalıcı label; minHeight 56; kontrol sınırı; helper/error altta | TextInput açık label; hata ve helper metinleri erişilebilir; placeholder tek etiket değil |
| SuggestionRow | Ayrı çerçeveli beyaz satır; ad solda 16/600, doğum yılı sağda 14/500; minHeight 56; aralık 8; wrap destekli | “Wesley Sneijder, 1984, seç” gibi tek anlaşılır seçim; seçili durum; ilk dokunuş çalışır |
| ChoiceOption | Üst üste veya yeterli alanda grid; birbiriyle eşit temel stil | button rolü; seçim state; sonuç yalnızca renk değil “Doğru cevap” metni |
| TeamBadge | Sen/Rakip etiketi + takım adı; semantik soluk yüzey | Renkten bağımsız oyuncu/rol bilgisi |
| Scoreboard | Sen ve rakip adlarıyla skor; normal büyük, klavye açık kompakt | Bir okunabilir özet: “Sen 1, rakip 0”; anlamlı skor değişikliği duyurulur |
| RoundTimer | Sayı + okunabilir kalan süre; progress ek gösterim | timer rolü / erişilebilir metin; grafik varsa dekoratif ya da progressbar olarak anlamlı değer |
| FeedbackBanner | İkon, başlık, açıklama; success/danger/warning/neutral | Anlamlı olay bir kez duyurulur; tüm saniyeleri canlı bölgeye akıtma |
| SettingsRow | Label + switch, giriş veya seçim; minHeight 56 | Native Switch varsa built-in durum; custom control varsa rol/checked; dış satır aynı eylem için ikinci odak yaratmaz |
| SegmentedChoice | Tema Sistem/Açık/Koyu; alan daralınca sarma veya dikey düzen | Her seçenek button ve selected state; grup başlığı görünür |
| ResultCard | Sonuç, skor, kısa özet; bir primary sonraki eylem | Kazandı/kaybetti/berabere başlığı yazılı; renk tek anlam taşımaz |
| EmptyState | Ne olduğu + yapılabilir sonraki eylem | Heading ve anlaşılır açıklama; boş spinner bırakma |
| ErrorState | Hata nedeni biliniyorsa kısa açıklama + tekrar dene | Ağ hatası/yanlış giriş ayrılır; tekrar dene busy durumu |
| ConfirmationSheet | Başlık, etkisi, iptal ve teyit; danger yalnızca yıkıcı işlemde | Modal odağı içeride; kapatınca tetikleyene dönüş; Android back ve iOS dismiss test edilir |

## Temel durum matrisi

| Durum | Görünüm | Davranış |
|---|---|---|
| Default | Token çiftleri ve gerekli kontrol sınırı | Aktif |
| Pressed | Primary: primaryPressed; secondary: secondaryPressed; neutral: surfaceSubtle | Yalnızca dokunma sırasında; bütün bileşeni opacity ile soldurma |
| Keyboard focus | 2 birim focus çerçevesi; gerekirse arada yüzey rengi boşluk | Harici klavye odağı ve görünür input odağı |
| Selected | İşaret + görünür seçili açıklaması + semantik yüzey | selected / checked state; primary ile selected rolleri karışmaz |
| Disabled | disabledSurface + disabledText; açık gerekçe | `disabled` native prop + erişilebilir disabled state; yalnızca renkle devre dışı bırakma |
| Loading | Aynı label/alan korunur; spinner eklenir | Tekrarlı submit engellenir; busy state |
| Error | danger çerçeve + yakın hata metni | Odak kaybolmaz; düzeltme yolu görünür |
| Success | success yüzey + ikon + metin | Sonraki eylem açık; bilgi sadece titreşim/ses değil |
| Reduced motion | Geçişler sade veya 0 ms | Alan yeniden akışı ani ama kararlı; ekran flaşı yok |

Disabled metnini kitte okunabilir tuttuk; kontrast standardında inactive UI istisnası olması onu gereksizce soluk yapmak için gerekçe değildir. İş kuralları bakımından gerekli kilit durumunda kilidin süresi ve nedeni açık yazılır.

## Kaynak bölümleri ortak şablonlara bağlama

| Kaynak | Şablon / ortak parçalar | Varyantlar |
|---|---|---|
| c01, 4 ekran | HomeScreen, NicknameForm | Haftanın maçı var/yok; takma ad boş/dolu |
| c02, 10 ekran | SettingsScreen, AccountScreen, CodeForm, ConfirmationSheet | Misafir/bağlı; cihaz/kurtarma kodu; geçersiz giriş; hesap silme teyidi |
| c03, 8 ekran | OnlineSetup, MatchmakingStatus, RoomLobby, JoinRoomForm | Lig/dönem/kapsam; aranıyor; kuruldu; kod; oda bulunamadı |
| c04, 32 ekran | TeamSelection, Countdown, MatchRound, RoundResult, MatchResult | Öneri/hızlı seçim; hazır/bekliyor; takım doğrulama; yanlış/kilit; bağlantı; rövanş |
| c05, 7 ekran | SoloModeMenu, ScopeSelector, Loading/ErrorState | Skor var/yok; dönem/lig; yükleme/yanıt yok |
| c06, 6 ekran | LadderRound, SoloResult | Basamak, öneri, yanlış, süre doldu, rekor, uzun liste |
| c07, 4 ekran | MultipleChoiceRound, SoloResult | Soru, doğru, yanlış, sonuç |
| c08, 6 ekran | CareerRound, SoloResult | Kulüp ipuçları; öneriler; yanlış; sıradaki oyuncu |
| c09, 5 ekran | NextClubRound, SoloResult | İlk soru; sonraki ipuçları; öneriler; yanlış |
| c10, 6 ekran | ComparisonRound, SoloResult | Değer açık; kategori; doğru/yanlış |
| c11, 6 ekran | WeeklyMatchIntro, MultipleChoiceRound, WeeklyResult | Taraf seçilmedi/seçildi/kilitli; soru/yanlış/sonuç |
| c12, 23 ekran | HowToPlayPager | Mod bazında veriyle beslenen 7 öğretici; sayfa başlığı ve ilerleme |
| c13, 1 ekran | UpdateNotice | Yeni sürüm; gerçek zorunluluk durumuna göre action |
| c14, 19 ekran | Yukarıdaki formların klavye açık varyantı | Aynı state, uyarlanan layout; ayrı domain ekranı değil |

Her PNG için ayrı kopya komponent üretme. Gerçek route sınırlarını mevcut `app/` yapısından al. Yukarıdaki isimler bileşen/şablon önerisidir, zorunlu rota adı veya dosya şeması değildir.

## Maç alanı için tutarlılık

Normal ve klavye açık yerleşimde okuma sırası: roller/takımlar ve skor → kalan süre → alan etiketi/input → öneri listesi → geri bildirim. Görsel yerleşim bu sırayı destekler.

Tur durumlarını mevcut state makinesinden türet. Render düzeyinde önerilen açık durumlar: `ready`, `typing`, `submitting`, `locked`, `resolved`, `connectionLost`. Bunlar mevcut domain state'in yerine geçirilmez; örneğin `locked` süre bitince tekrar aynı turdaki `typing` durumuna dönebilir.

- Input/öneri doğrulama tek olay kaynağından yürür; yanlış cevap iki kez gösterilmez.
- `locked`: kalan süre ve neden görünür; input gerçekten editable=false olur, aynı zamanda durum okunur.
- `connectionLost`: kalıcı kısa açıklama; skor uydurma, otomatik kazanma/kaybetme kararı verme.
- `resolved`: sonuç metni, mevcut doğru cevap verisi ve mevcut next action; input odağını gereksizce yeniden açma.
- Rövanş eylemleri aynı primary/secondary kurallarını kullanır; waiting ve incoming request ayrı anlaşılır kopyaya sahiptir.
- Ekran okuyucu akışı için uygulamanın özel gameplay testi gerekir; form etiketleri eklemek tek başına süreli oyunu erişilebilir yapmaz.

## Önce örneklenmesi gereken ekranlar

1. `c01-01A` Ana menü: amberin eylem rolünden çıkması; Elo 1000 değerinin “Elo 1000” olarak açıklanması; küçük haftanın maçı metinlerinin büyümesi.
2. `c04-04B` Tur öneriler: görünür input etiketi; oyuncu adı/yıl tipografi hiyerarşisi; kontrol sınırı.
3. `c14-04B` Aynı turun klavye açık hali: liste alanı, kompakt skor ve büyük fontla taşma.
4. `c02-01A` Ayarlar: 48+ hedefler, switch durumları ve büyük metinde tema/dil seçenekleri.
5. `c04-04D` Yanlış/kilit, koyu tema: tek açık geri bildirim; kalan kilit süresi; yeni kontrast çiftleri.

Bu beş örnek kodda ve cihazda doğrulandıktan sonra aynı kurallar envantere uygulanır. Bütün 137 ekranı görsel incelemiş gibi işaretleme.

## Kullanıcı tarafından seçilen görünüm

[SELECTED-DIRECTION.md](SELECTED-DIRECTION.md) bu sözleşmelerin ana menü, Ayarlar girişi, haftanın maçı ve klavye açık maç yerleşimini somutlaştırır. Skor üsttedir; klavye üzerinde tekrarlanmaz. Öneriler ayrı çerçeveli satırlardır.

## Online bileşen genişlemesi

Kullanıcının eklediği koyu tema referanslarından türetilen 11 bileşen ve durumları [ONLINE-COMPONENTS.md](ONLINE-COMPONENTS.md) içinde; iki temalı inceleme panosu [COMPONENT-LIBRARY.html](COMPONENT-LIBRARY.html). Mevcut temel bileşenler yeniden kullanılır.

## Oyun ve sonuç genişlemesi

[GAME-COMPONENTS.md](GAME-COMPONENTS.md), 11 yeni koyu tema referansından türetilen mod, oyun, kariyer, transfer, sonuç, karşılaştırma ve haftalık bileşenlerini tanımlar. [COMPONENT-LIBRARY.html](COMPONENT-LIBRARY.html) 07–15 grupları açık/koyu tema örnekleridir.
