# Asset teslimi

## Dosyalar

| Dosya | Tür | Kaynak / statü | Kullanım |
|---|---|---|---|
| assets/brand/kickoff-logo.svg | Gerçek path SVG, transparan | Seçili home rasterından doğrudan renk ayrımı ve vektör trace; yeni fontla yazılmadı | Header; yaklaşık108×60; image/text-editable değil outlined brand |
| assets/illustrations/stadium-trabzon.svg | Gerçek path SVG | Seçili art'tan üretilmiş bağımsız illüstrasyonun renkli trace export'u; source kompozisyonunun yakın eşlemesi | Home entry + ilk maç |
| assets/illustrations/stadium-city.svg | Gerçek path SVG | İkinci maç art'ının aynı yöntemle export'u | İkinci maç |
| Aynı isimli PNG dosyaları | Fallback / raster kaynak | SVG üretiminin raster karşılığı | SVG desteği olmayan renderer / karşılaştırma |
| assets/icons/*.svg | 19 kütüphane SVG | Phosphor regular; MIT | UI ikonları |
| assets/fonts/*.ttf | 4 native font | Barlow Condensed600/700/800 + Inter variable; OFL | Native uygulama |
| assets/fonts/*.woff2 | 12 subset font | Fontsource5.3.0 latin + latin-ext | Offline browser katalog |
| references/*.png | Seçili ekran görüntüleri | Kullanıcının iki seçili eki, değiştirilmedi | Görsel hedef, UI olarak kullanılmaz |

SVG'ler PNG gömmesi değildir: `<path>` içerir, `<image>` veya data:image yoktur. viewBox'ları vardır. Stadyumlarda 3:1 oran korunur; üst art bölgesinde `cover` kullanılabilir, güneş/floodlight/goal güvenli bölgede tutulmalı. Logo `contain`; en-boy bozulmaz. İkonlar currentColor kullanır; 24x24 ve source viewBox256 ölçeğine göre renderer normalize eder.

## Sadakat sınırı

Kaynaklar raster olduğu için orijinal düzenlenebilir çizim/font bilgisi alınamadı. Stadyum exportları aynı dilde bağımsız asset üretimi ve vektörleştirme ile hazırlandı; **kaynak görselle matematiksel olarak aynı master vektör oldukları iddia edilmez**. Doku sadeleşir, çok ince saha/tribün detayları trace'te azalabilir. Üretimde önce kart boyutunda, sonra büyük ölçekte kontrol et. Logo kaynak rasterdan direkt trace olduğu için mevcut işaretin kompozisyonunu korur; 4K orijinal logo master'ının yerine tescil kaynağı olarak kullanılmaz.

## Kaynak ve lisans

- [Phosphor core resmî deposu](https://github.com/phosphor-icons/core): MIT; lisans pakette. İkon dosyaları dosya içindeki copyright/license bilgisiyle korunur.
- [Google Fonts Barlow Condensed](https://github.com/google/fonts/tree/main/ofl/barlowcondensed) ve [Inter](https://github.com/google/fonts/tree/main/ofl/inter): OFL metinleri pakette.
- [Fontsource](https://github.com/fontsource/fontsource): yereldeki5.3.0 WOFF2 subsetleri; fontların OFL metinleri korunur.
- [VTracer](https://github.com/visioncortex/vtracer):0.6.15 Python binding ile trace yapıldı; çıktı dosyaları kendi asset exportlarıdır. Export yorumundaki embedded generator version farklı olabilir.

İndirilen Google Fonts / Phosphor commitleri `assets/source-records.json` içinde sabitlenmiştir. Gereken lisansları dağıtımda sakla. Görsel üretim dosyalarının kullanımı verilen referansların ve proje brand'inin haklarına bağlıdır; üçüncü taraf takım logoları/kişiler eklenmedi.
