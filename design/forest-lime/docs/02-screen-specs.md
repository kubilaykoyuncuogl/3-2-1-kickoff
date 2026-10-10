# Seçili ekranlar ve responsive ölçüler

Bu dokümandaki ölçüler seçili 852×1846 kaynaklardan 393 genişliğe indirgenmiştir; pixel-perfect editable Figma ölçümü değildir. Görsel otorite `references/` içindeki iki kaynaktır.

## Ana sayfa

| Sıra | Bölüm | 393 genişlikte hedef |
|---|---|---|
| 1 | Logo + K / kubi | 20px gutter; logo yaklaşık 108×60; avatar 38; içerik status bar'ın altında |
| 2 | Online oyna / Elo 1000 | 353 genişlik; min 84 yükseklik; sağ caret |
| 3 | Tek oyna | 353 genişlik; min 60 yükseklik; önceki eylemle 10–12 aralık |
| 4 | Haftanın maçları giriş kartı | 353 genişlik; kaynakta yaklaşık 179 yükseklik; üstte art, altta opak metin |
| 5 | Alt menü | 353 genişlik; 72 yükseklik; Ana sayfa aktif |

Tam kopya: `Online oyna`, `Elo 1000`, `Tek oyna`, `Haftanın maçları`, `2 karşılaşma`, `Tarafını seç, puanın takımına yazılsın.`. Giriş kartının tamamı bir navigation eylemidir. O kartın içine maç isimleri ve puan tabloları geri eklenmez.

Giriş kartındaki başlık 28, açıklama 16, karşılaşma sayısı 14 başlangıç ölçüsüdür. Başlık/count 320 genişlikte sığmazsa count ayrı satıra geçer; metin üst üste bindirilmez. Kartın art kısmı yaklaşık 110 yüksekliğinde başlar ve metin uzadığında okuma bölgesi büyür. Boş alt alan başka modüllerle doldurulmaz.

## Haftanın maçları

Ortak kimlik başlığı korunur. Başlık + count + helper'dan sonra iki kart gelir. 353 genişlikte her kart kaynakta yaklaşık 216 yüksekliğinde; kart aralığı 12. Sabit 216 bir üst limit değildir.

| Kart | Başlık / süre | Sol | Sağ |
|---|---|---|---|
| 1 | O mu bu mu / 1 gün kaldı | Trabzonspor / 12.480 puan | Beşiktaş / 13.920 puan |
| 2 | O mu bu mu / Bu hafta | Man. City / — puan | Liverpool / — puan |

Merkez `VS`; alt footer `Tarafını seç` + arrow. Bu footer takım seçim sheet'ini açar. Seçim sonrası önerilen footer: check + `Trabzonspor seçildi` + `Değiştir`. Kartı dıştan tıklama aynı footer hedefini tetikleyecekse tek erişilebilir eylem tanımlanır; iç içe button kurulmaz.

Takım başlıkları solda/sağda iki esnek kolonda, `VS` ayrı dar orta alanda olmalı. Uzun isim 2 satır olabilir. Rakamlar dar genişlikte küçültülmeden önce puan birimi yeni satıra alınır. Dashes veri yok demektir; `0` ile değiştirilmez. Sayı örnekleri tr-TR binlik ayırıcıyla gösterilir.

## Alt menü

Sıra: `Ana sayfa` / `Maçlar` / `Ayarlar`. İkonlar: house / soccer-ball / gear. Her item kapsül genişliğinin üçte biri; ikon 24, metin 12, aralık 4. Aktif iç kapsül yeşil; ikon + yazı lime. Diğer ikon/yazılar cream. Hepsi etiketli kalır.

Konum: `bottom = safeAreaBottom + 12`, side 20. Scroll içerik son boşluğu en az `72 + safeAreaBottom + 36`. OS navigasyon bölgesi ve home indicator üstüne oturmaz. Status bar/app content hizası platform safe area ile belirlenir; raster üst boşluğu ayrıca eklenip iki kere sayılmaz.

## Ayarlar — önerilen tamamlayıcı ekran

Üçüncü hedef kullanıcı tarafından doğrulandı. Görsel ekran henüz seçilmedi. Ortak header, `Ayarlar` başlığı ve tek `Ses efektleri` switch satırı yeterli. K / kubi mevcut ayarlar kısayolunu korur. Hesap, abonelik, bildirim veya sıralama modülleri bu paketle eklenmez.

## Küçük ekran ve yazı büyümesi

320, 360, 393 ve 427 mantıksal genişlikte kontrol et. Native 200% yazı/erişilebilirlik boyutunda başlık/count stack olur, kartlar büyür, menu minimum yüksekliği artırılabilir. Gerekirse yalnız dikey scroll olur. Yatay sayfa scroll, gövde ölçekleme veya metnin rastera dönüşmesi kabul edilmez. Tam ekran oyun sırasında menünün görünürlüğü mevcut ürün akışına göre geliştiricide doğrulanmalı; bu paket yeni gameplay navigasyonu tanımlamaz.
