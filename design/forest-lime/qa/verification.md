# Paket doğrulaması — 10 Ekim 2026

Sonuç: **handoff paket kontrolleri geçti**. Bu sonuç native uygulamanın veya tam oyunun onaylandığı anlamına gelmez.

## Gerçekten yapılan kontroller

- Kullanıcının seçtiği iki referansla paket kopyaları byte düzeyinde aynı.
- Katalog HTML dosyasındaki tüm yerel link ve asset yolları bulundu.
- 22 SVG XML olarak parse edildi; hepsinde viewBox var; gömülü image/data:image yok.
- Katalog JavaScript syntax kontrolü geçti.
- Browser'da 320 / 360 / 393 / 427 ve1200 genişlik: documentWidth=viewportWidth; yatay sayfa taşması yok. Yüklü img öğelerinde broken image yok.
- Inter ve Barlow Condensed font yükleme kontrolü geçti. Browser error/warn kaydı boş.
- Takım sheet'i açıldı, Trabzonspor seçildi, onaylandı; footer gerçekten `Trabzonspor seçildi · Değiştir` oldu.
- Menü Maçlar state'i doğrulandı; ses switch'i kapalı oldu; boş input hata gösterdi ve dolu input state'i temizlendi.
- Dialog açıldı ve Oyuna dön ile kapandı. Raster/SVG asset switch'i çalıştı.
- Görsel katalog ve sheet render'ları incelendi; kanıtlar `../previews/` içinde.
- Mevcut kickoff-mobile runtime integrity kontrolü geçti (28 protected file). Uygulama UI kodu bu görevde değiştirilmedi.

## Opak token çiftlerinin hesaplanan kontrastı

| Ön plan | Arka plan | Oran |
|---|---|---|
| text | canvas | 13.94:1 |
| textMuted | surface | 7.13:1 |
| onPrimary | primary | 11.11:1 |
| primary | activeSurface | 6.05:1 |
| error | surface | 7.45:1 |
| borderControl | surface | 4.48:1 |

Bu tablo opak token çiftlerini ölçer; blur, transparan katman ve görsel üstündeki gerçek composited contrast ayrıca uygulamada kontrol edilir. Quiet dekoratif border için erişilebilir kontrol sınırı iddiası yoktur.

## Yapılmayan kontroller

Native iOS/Android cihaz, gerçek OS safe area / keyboard, screen reader ile uçtan uca kullanım, 200% type, network / roster / matchmaking / contribution persistence, tam gameplay ve ekran PNG'leriyle üretim uygulamasının pixel karşılaştırması yapılmadı. 15sn timer primitive'i katalog örneğidir; gerçek oyun zamanlaması doğrulanmadı.
