# Görsel sistem

## Kaynak ve ölçü birimi

Seçili kaynaklar 852×1846 raster görüntülerdir. Yaklaşık 2,168× oranıyla 393×852 mantıksal mobil alana okunur. Dosyadaki px sayıları CSS px / native pt-dp ölçeğine aktarılacak **mantıksal tasarım değerleri**dir; 852px genişliğinde bir native layout kurulmaz. Ekran görüntüsündeki ince doku ve geçişler değişken değildir; aşağıdaki sistem tutarlı uygulama için normalize edilmiştir.

## Renkler

| Token | Değer | Kullanım |
|---|---|---|
| canvas | #013026 | Ana ekran zemini |
| surface | #043A2F | Kart ve ikincil eylem |
| raised | #124B38 | Önerilen yükseltilmiş yüzeyler |
| primary | #DAEC5A | Online oyna, seçili ikon ve vurgu |
| primaryPressed | #C3DB46 | Basılı ana eylem |
| text | #FFFBEA | Başlık, takım ve ana metin |
| textMuted | #B6C6B9 | Açıklama ve metadata |
| borderQuiet | #3E7862 | Dekoratif kart çerçevesi / ayırıcı |
| borderControl | #78A38A | Form sınırı, etkileşim algısı |
| activeSurface / activeBorder | #235C3C / #6C9A5B | Aktif menü ve seçili takım |
| error / warning | #FFB3AD / #F7D680 | Önerilen hata ve uyarı |

Normal yazıdaki koyu/aydınlık ayrımı için metin renkleri bu opak yüzeylerde kullanılır. Stadyum üstüne destek metni doğrudan yazılmaz; altına opak yeşil okuma bölgesi konur. Pembe ve kırmızı yalnızca illüstrasyon içindedir; uygulamanın ikinci ana aksan rengi değildir.

## Tipografi

Kaynak font bilgisi rasterdan geri alınamaz. En yakın geliştirilebilir eşleme **Barlow Condensed** (aksiyon, başlık, takım, puan) + **Inter** (gövde, metadata, nav) olarak önerilmiştir. Font dosyaları ve Türkçe desteği paketlidir. Logo bağımsız SVG'dir; fontla yeniden yazılmaz.

| Rol | Family / weight | Boyut / satır |
|---|---|---|
| Ana eylem | Barlow Condensed 800 | 32 / 36 |
| Sayfa başlığı | Barlow Condensed 700 | 30 / 34 |
| Kart başlığı | Barlow Condensed 700 | 28 / 32 |
| Takım etiketi | Barlow Condensed 700 | 20 / 24 |
| Puan | Barlow Condensed 700 | 34 / 38 |
| Gövde | Inter 400 | 16 / 24 |
| Küçük etiket | Inter 600 | 14 / 20 |
| Alt menü etiketi | Inter 600 | 12 / 16 |

Harfler: `ğ ü ş ı İ ö ç` doğru gösterilmeli. Puan ve sayaçlarda tabular rakamlar kullanılmalı. Dinamik metin boyutunu destekle; kritik etiketleri tek satıra zorlayıp kesme. Ekran büyütmelerinde kart ve satır yüksekliği içerikle büyür.

## Geometri ve malzeme

4px adımlı spacing: 4, 8, 12, 16, 20, 24, 32, 40, 48. Ana gutter 20. Aksiyon radius 10, kart 12, sheet üst köşeleri 24; rozet/menü tam kapsül.

Menü: 72 yüksekliğinde, 1px yeşil kenarlı, koyu yeşil yarı saydam kapsül. Blur yaklaşık 20px; iç aktif kapsül 56 yüksekliğinde. Blur desteklenmiyorsa `navSolid` kullan. Blur tek başına okunabilirlik sağlamaz; opaklık yeterli kalır. İç aktif kapsülü beyaz daireye dönüştürme.

## Hareket

Basılma 100ms, seçim 180ms, sheet yaklaşık 240ms. Uzun bounce, sürekli parlayan CTA, saat üzerine sallanma kullanılmaz. Reduce motion durumunda uzamsal geçiş kapatılır. Haptik ve ses varsa mevcut kullanıcı ses tercihi gözetilir; yeni tercih türleri eklenmez.
