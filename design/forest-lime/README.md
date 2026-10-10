> Repodaki kopya (2026-10-10): Tolga'nın `forest-lime-mobile-v1` paketi; stadyum PNG'leri ve font dosyaları alınmadı (fontlar `@expo-google-fonts/*` paketlerinden, çizimler SVG olarak `assets/illustrations/`). Uygulamadaki kararlar ve kitten sapmalar: kökteki `CLAUDE.md` "Tasarım: Forest Lime" maddesi.

# 3·2·1 KICKOFF — Forest Lime mobile handoff v1

10 Ekim 2026 · Teknolojiden bağımsız tasarım paketi · Dil: Türkçe

**Geliştirmeye başlanacak görsel kaynak:** `references/approved-home.png` ve `references/approved-weekly.png`. Kullanıcının seçtiği iki ekran aynen korunmuştur. Ana sayfa / Maçlar / Ayarlar menüsündeki geniş yeşil aktif kapsül seçilidir. Diğer menü denemeleri bu pakete dahil değildir.

## Önce bunları aç

1. [Görsel UI kataloğu](catalog/index.html): tarayıcıda açılır; internet, kurulum veya framework gerektirmez. Renkler, butonlar, menü, kartlar, formlar, takım seçimi, oyun durumu ve geri bildirim örnekleri içerir.
2. [Ekran ölçüleri ve içerik](docs/02-screen-specs.md): iki seçili ekranın hiyerarşisi, kopyası ve mobil ölçüleri.
3. [Tasarım sistemi](docs/01-design-system.md) ve [JSON token dosyası](tokens/tokens.json).
4. [Bileşen sözleşmeleri](docs/03-components.md) ve [etkileşimler](docs/04-interactions.md).
5. [SVG ve font envanteri](docs/06-assets.md), [QA ve kabul listesi](docs/05-mobile-qa.md), [ürün tasarımı değerlendirmesi](docs/07-product-review.md).

## Paketin kapsamı

- **Kullanıcının seçtiği:** Forest Lime yönü, bu iki ekranın kompozisyonu ve içerikleri, ayrı Haftanın maçları sayfası, üç menü hedefi, ekrandaki menü stili.
- **Önerilen uygulama tanımları:** raster kaynaktan normalize edilen renk/ölçü/type tokenları, SVG exportları, ek UI bileşenlerinin görsel dili ve durumları. Bunlar kullanıcı onayı almış yeni ekranlar değildir.
- **Katalog:** geliştiriciye örnek davranış ve görünüm gösterir. Çalışan oyunun, backend'in veya mevcut mobil prototipin yeni sürümü değildir. CSS platform bağımsız ölçülerin okunabilir referansıdır; herhangi bir framework şartı yoktur.

Ana sayfadaki haftalık kart yalnızca sayfa yönlendirmesidir. Takım seçimi ilgili maç kartının `Tarafını seç` eylemiyle açılır. Puanlar örnek katkı puanlarıdır; Man. City–Liverpool için bilinmeyen değer `—` kalır. Demo değerler ve süreler canlı veri değildir.

## Developer'a teslim

Bu klasörü veya aynı isimli ZIP'i ver. Bağıl yollar korunmalıdır. Yerel bilgisayar yolu, API anahtarı, node_modules veya çalışma klasörü bağımlılığı yoktur. `manifest.json` dosyaların SHA-256 değerlerini; `qa/verification.md` gerçekten yapılan kontrolleri içerir.

İlk geliştirme tesliminde iki ana ekranı gerçek metin/etkileşim katmanlarıyla kur; ekran PNG'sini arayüz olarak kullanma. Önce 393×852 görünümünü eşleştir, sonra 320/360/427 genişlik ve büyütülmüş yazı kontrolünü yap. Native safe area, klavye ve geri davranışı gerçek cihazda ayrıca doğrulanmalı.
