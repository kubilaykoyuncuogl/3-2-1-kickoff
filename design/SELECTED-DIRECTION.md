# Kickoff seçilen tasarım yönü

9 Ekim 2026. Kullanıcı dört görsel parçasını açıkça seçti. Birleşik referans [combined-v1.png](concepts/combined-v1.png). Bu birleşik görüntü yeni bir görsel önizlemedir; henüz kullanıcı tarafından ayrıca değerlendirilmedi. Aşağıdaki dört bileşen tercihi doğrudan kullanıcı seçimidir.

| Parça | Seçilen düzen | Kullanıcı referansı |
|---|---|---|
| Oyun seçenekleri | Mor Online oyna; sağında ayraç, Elo değeri ve chevron. Altında soluk mor Tek oyna. | [play-actions.png](selected-references/play-actions.png) |
| Ayarlar girişi | Beyaz yuvarlatılmış satır; solda dişli ve Ayarlar, sağda chevron. | [settings-row.png](selected-references/settings-row.png) |
| Haftanın maçı | Üstte bölüm/mod başlığı; çapraz takım marka renkleri; iki takım, arma ve puan; altta açıklama ve Tarafını seç. | [weekly-match.png](selected-references/weekly-match.png) |
| Maç / klavye açık | Üstte kullanıcılar, skor ve takım rozetleri; süre; kalıcı alan etiketi; input; ayrı çerçeveli öneri satırları, ad solda yıl sağda. | [match-keyboard.png](selected-references/match-keyboard.png) |

## Uygulama kararları

- Sen mor, rakip amber semantik renklerini kullanır. Kullanıcının seçtiği maç referansındaki ters renk eşleşmesi birleşik önizlemede düzeltildi. Takım adları bu rol rengini değiştirmez.
- Skor üstte kalır; klavye üzerinde ikinci bir skor oluşturulmaz. Klavye açılınca gerekirse scoreCompact uygulanır. Önceki alt skor yerleşimi bu seçimle değiştirildi.
- Öneriler birleşik bir liste kartı yerine ayrı beyaz, yuvarlatılmış, çerçeveli satırlardır. Satırlar arasında 8 birim boşluk; minimum yükseklik 56. Dört satır görsel örneğidir, sonuç sayısı sınırı değildir. Liste kaydırılabilir.
- Online oyna erişilebilir adı Elo bilgisini de anlaşılır biçimde içerir. Elo ve chevron aynı eylemin dekoratif/yardımcı parçalarıdır; ayrı dokunma hedefleri oluşturulmaz. Uzun değer ve büyük metinde sağ blok yeniden akar.
- Ana oyun seçeneklerinin minimum yüksekliği mevcut buttonMin=52; içerik ve padding ile daha yüksek olabilir. Fotoğraftan sabit yükseklik veya font boyutu çıkarılmaz.
- Ayarlar giriş satırı tek navigasyon eylemidir. Dişli ve chevron dekoratiftir; metin 16/22 semibold, hedef en az 48, satır minimum 56.
- Haftanın maçı açıklaması: “İki kulübün oyuncuları karşı karşıya. Tarafını seç, puanın takımına yazılsın.” Dar ekranda ve büyük metinde CTA açıklamanın altına geçer. Takım adları sarabilir; küçültülmez.
- Haftanın maçı tek navigasyon hedefi olarak uygulanır; başlık chevronu ve Tarafını seç aynı hedefe gider, ayrı ekran okuyucu odakları yaratılmaz. Kartın erişilebilir adı takım adlarını, puanları ve eylemi içerir.
- Haftanın maçı bant renkleri takım marka varlıklarından gelir. Metin/zemin kontrastı gerçek renklerle ayrıca ölçülür. Yapay zekanın ürettiği armalar ve logo üretim varlığı değildir; onaylı gerçek assetler kullanılır.
- Açık/koyu renkler, Sora font yüzleri ve ölçülerin kaynağı tokens.json ve ondan üretilen kickoff-theme.ts. Görseldeki yaklaşık renk, kalınlık, gölge veya gradyan kopyalanmaz. Düz renkler kullanılır.
- Native Türkçe klavye sistem tarafından çizilir; görseldeki klavye uygulama bileşeni değildir. iOS/Android sistem alanları platforma göre uygulanır.

## Kanıt sınırı

Birleşik referans yapay zeka görselidir; gerçek Expo ekranı, tam cihaz ölçüsü veya erişilebilirlik testi değildir. Ana ekran ve klavye açık maç için görsel hedef sunar. Diğer oyun durumları COMPONENTS.md sözleşmeleriyle sürdürülür. Native uygulama henüz bu çalışma alanında bulunmuyor.
