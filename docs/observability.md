# Clarity ve Sentry

Uygulama: Expo SDK 57, Expo'nun seçtiği `@sentry/react-native ~7.11.0`, native Clarity ve web Clarity. Sunucu: Sentry Python 2.x, FastAPI ve Starlette entegrasyonları.

## Ortam değişkenleri

Release yapılandırması `app/.env.production` içinde hazırdır: yalnız public DSN ve proje kimlikleri içerir, auth token içermez. Expo production export/build bunları yükler; ana checkout'ta ayrıca gizli bir `.env.local` dosyasının bulunmasına bağlı değildir. Yerel override için `app/.env.example` dosyasını **git dışında kalan** `app/.env.local` dosyasına kopyalayın. Boş DSN/Project ID ile ilgili servis açılmaz. Geliştirme ortamında ayrıca `EXPO_PUBLIC_TELEMETRY_IN_DEV=true` gerekir; normal geliştirme varsayılan olarak veri göndermez.

| Değişken | Kullanım |
| --- | --- |
| `EXPO_PUBLIC_SENTRY_DSN` | Sentry'deki React Native uygulama projesinin DSN'i; web de bu projeyi kullanır |
| `EXPO_PUBLIC_CLARITY_WEB_PROJECT_ID` | Clarity Website projesinin Project ID'si |
| `EXPO_PUBLIC_CLARITY_MOBILE_PROJECT_ID` | Clarity Mobile projesinin Project ID'si |
| `EXPO_PUBLIC_CLARITY_MOBILE_MASKING_READY` | Mobile projesinde **Strict masking** ayarlandıktan sonra `true` |
| `EXPO_PUBLIC_TELEMETRY_ENVIRONMENT` | `production`, `staging` veya `development` |
| `EXPO_PUBLIC_SENTRY_TRACES_SAMPLE_RATE` | 0–1; varsayılan `0`, yalnız hata raporları |
| `SENTRY_ORG`, `SENTRY_PROJECT` | Native build/source map yüklemesi için organizasyon ve uygulama projesi slug'ları |
| `SENTRY_AUTH_TOKEN` | Build/CI ortamında secret; **EXPO_PUBLIC_ önekiyle tanımlanmaz**, git'e eklenmez |

`EXPO_PUBLIC_` değerleri JS paketine derleme sırasında gömülür. Değişiklikten sonra web export veya yeni native build/update gerekir. Değerleri değiştirdikten sonra export'a `--clear` ekleyin; Metro'nun eski dönüşümleri boş/eski DSN taşıyabilir. `npm run export:web` bunu uygular. Sunucu ortamını değiştirmek mevcut web paketini değiştirmez.

Compose sunucu Sentry ayarlarını `server/.env.production` içinden otomatik yükler; sonraki `../.env` dosyası deployment secret'larını ve override'ları sağlar. Mevcut index anahtarı ve daily salt satırlarını koruyun. `SENTRY_DSN` ayrı FastAPI projesinin DSN'idir. `SENTRY_ENVIRONMENT`, isteğe bağlı `SENTRY_RELEASE` ve `SENTRY_TRACES_SAMPLE_RATE` sunucuda kullanılır. Compose dışında çalıştırıyorsanız `server/.env.example` satırlarını süreç ortamına ekleyin. Açık boş `SENTRY_DSN` override'ı raporlamayı kapatır.

6 Ekim 2026'da mevcut canlı deployment'ın `/home/kickoff/kickoff/.env` dosyasına sunucu DSN'i, `production` ortamı ve `0` trace örneklemesi eklendi. Diğer satırlar birebir korundu; index anahtarı ve daily salt'ın resolved Compose ortamında bulunduğu doğrulandı. Önceki dosya kullanıcıya özel izinlerle yedeklendi, `.env` izni `0600` yapıldı. Çalışan konteyner yeniden oluşturulmadı; ayarlar Sentry kodunu içeren sonraki Compose yayınıyla süreç ortamına alınır.

Clarity projeleri 6 Ekim 2026'da hazırlandı:

| Platform | Proje | Project ID | Maskeleme |
| --- | --- | --- | --- |
| Web | Kickoff (`kickoff.grandecorpo.com`) | `ytk0sewicz` | Strict / Katı |
| iOS + Android | Kickoff Mobile (`com.kickoff321.app`) | `ytk1yv92fh` | Strict / Katı |

Mobil panel ayarının cihazlara ulaşması bir saate kadar sürebilir. Web ve mobil ekranları aynı sabit olay adlarını kullanır; kayıtları ayrı projelerde inceleyin. Clarity davranış içgörüsü toplar; bu değişiklik doğrudan kullanıcı mesajı gönderen bir feedback formu eklemez.

Sentry projeleri 6 Ekim 2026'da `grande-corpo` organizasyonunda oluşturuldu: `kickoff-app` (React Native, web dahil) ve `kickoff-server` (FastAPI), takım `#grande-corpo`. Uygulama DSN'i `app/.env.production`, sunucu DSN'i `server/.env.production` içinde public yapılandırma olarak bulunur. Normal Compose yayınında sunucu ayarlarını elle kopyalamak gerekmez.

Sunucu entegrasyonu üzerinden bir test exception'ı ve uygulamanın raporlama/temizleme kodu üzerinden web SDK transport'u ile bir test exception'ı gönderildi. İki kayıt Sentry panelinde `KICKOFF-SERVER-1` ve `KICKOFF-APP-1` olarak doğrulandı; mesajlar `[redacted]`. Bu kontrol gerçek native cihaz veya tam web arayüzü testi değildir.

Sentry CLI kimlik doğrulaması tamamlandı. Token gerçek kullanıcı home'undaki `.sentryclirc` dosyasında yalnız kullanıcıya açık (`0600`) saklanır; repoda veya uygulama paketinde bulunmaz. `npm run export:web:sentry` ile DSN ve web Clarity ID'sinin JS içine gömüldüğü kontrol edilerek web export'u yeniden üretildi. 3 JS dosyası ve 3 source map `kickoff-app` projesine yüklendi; Sentry sunucusunda işleme tamamlandı (artifact bundle: `ee096cfb-4125-5709-90b8-1ec20bb0b65f`). Web map'leri dağıtım klasöründen `.expo/sentry-sourcemaps/` altında git dışı arşive taşındı; public `dist` içinde map kalmadı. Gerçek hata stack'inin source map ile çözülmesi ayrıca doğrulanmalıdır.

## Kaydedilen veriler

Clarity ekran adlarını ve aşağıdaki sabit olay adlarını alır. Hesap/device kimliği, kullanıcı adı, kurtarma/eşleme kodu veya oda kodu özel tag/event olarak gönderilmez. Web'de belge kökü SDK yüklenmeden önce `data-clarity-mask="true"` ile maskelenir. Mobile SDK yalnız Strict masking hazır bayrağıyla başlar; bu bayrak panel ayarını otomatik değiştirmez.

`room_create`, `room_join`, `match_search`, `rematch_request` ve `single_start` kullanıcı aksiyonlarını sayar; sunucunun isteği kabul ettiği anlamına gelmez. `match_start`, ilk takım seçimine veya rövanşa geçildiğinde; `match_complete`, maç bitişine geçildiğinde; `single_complete`, tek oyunculu oyun bittiğinde gönderilir. Yeni tur geri sayımı yeni maç sayılmaz. Yeniden bağlanan istemcinin gözlemlediği ilk durum tekrar sayılabilir; bu olaylar istemci davranışı analizi içindir, tekil maç sayısı için sunucu verileri kullanılmalıdır.

Sentry uygulamada yakalanmamış hataları, Router error boundary hatalarını ve WebSocket mesaj işleme hatalarını; sunucuda FastAPI/Starlette hatalarını, yakalanıp devam edilen engine/index/accounts hatalarını ve başarısız background task'ları alır. Normal WebSocket kopması ve iptal edilen görevler hata raporu üretmez.

Sentry Replay kapalıdır. PII gönderimi kapalıdır; request body/header/cookie/query, kullanıcı/extra alanları, otomatik breadcrumb'lar ve stack local değişkenleri temizlenir. Hata mesajları da hesap kodu içerebildiğinden `[redacted]` olur; exception tipi, dosya/fonksiyon/satır ve işlem tag'i korunur. Performans kaydı açılırsa span açıklaması/data temizlenir; işlem tipi ve süre korunur. Bu tercih hata mesajıyla ayrıntılı teşhis imkânını azaltır.

## Build ve source map

Native Clarity **Expo Go'da çalışmaz**; uygulama Expo Go'da Clarity'yi yüklemez. Yeni native bağımlılıklar için development/production build gerekir. `ios/` ve `android/` klasörlerini elle üretip commit etmeyin; Expo/EAS autolinking kullanır.

Dinamik Expo config Sentry build plugin'ini `grande-corpo` / `kickoff-app` varsayılanlarıyla ekler. Ortam değişkenleri başka organizasyon/proje seçebilir; açık boş `SENTRY_ORG` veya `SENTRY_PROJECT` plugin'i kapatır. Diğer Expo plugin'leri korunur. EAS native build sırasında source map yüklemesi için build ortamında `SENTRY_AUTH_TOKEN` gerekir; yerel CLI tokenı EAS'e otomatik taşınmaz. SDK 7'de Router hataları `_layout.tsx` üzerinden açıkça raporlanır.

Web export ve map yüklemesi (repo kökünden):

```sh
cd app
# Token için sentry-cli login veya CI secret kullanın.
npm run export:web:sentry
```

Bu komut export cache'ini temizler, map'leri doğrulayarak yükler ve Sentry processing sonucunu bekler. Yalnız başarılı yüklemeden sonra map'leri public `dist` dışına arşivler. Export/upload başarısızsa nonzero döner; map'ler teşhis için yerinde kalır, o çıktıyı yayınlamayın. Repo kendi `@sentry/cli` bağımlılığını kullanır; global CLI kurulumu gerekmez.

Metro Sentry yapılandırması Debug ID'leri ekler. Source map'leri, dağıtılacak JS dosyalarıyla aynı export'tan yükleyin; başka bir export'un map'lerini kullanmayın. Map dosyalarını halka açık web dağıtımına dahil etmeyin. Normal `npm run export:web` map üretmez. Web release için `export:web:sentry` çıktısını `deploy/Dockerfile` ile paketleyin. EAS Update kullanıma alınırsa update'in map'leri ayrıca `npx sentry-expo-upload-sourcemaps dist` ile yüklenmelidir.

## Doğrulama

```sh
cd app
npm run typecheck
npm run lint
npm run test:telemetry
npx expo export --platform all --source-maps --clear
cd ..
.venv/bin/python -m unittest discover -s server/tests -v
```

DSN'leri girdikten sonra test ortamında `EXPO_PUBLIC_TELEMETRY_IN_DEV=true` ile bir test hatası üretip Sentry'de tip/stack/operation alanlarını ve source map çözümlemesini doğrulayın. Hesap ekranında nickname/recovery/link metinlerinin Clarity kaydında maskeli olduğunu web ve gerçek native build üzerinde kontrol edin. ID/DSN olmadan derleme ve testlerin geçmesi, vendor'a teslimatın veya gerçek cihazda native kaydın doğrulandığı anlamına gelmez.

6 Ekim 2026 doğrulaması:

- Son `origin/main` (`c61d246`) branch'e alındı. Yeni round alanları ve weekly mesajları korunuyor; socket testi bunları da doğruluyor. Yukarıdaki web artifact bundle önceki main sync'inde üretildi; yeni release için `export:web:sentry` yeniden çalıştırılır.
- Chrome'da `http://127.0.0.1:18084` production export'u açıldı. Takma ad → ana ekran → ayarlar → dil değişikliği çalıştı; framework hata overlay'i yok. Console'da yalnız üçüncü taraf Acrobat extension hataları görüldü.
- Web DOM kökünde `data-clarity-mask="true"` ve doğru `https://www.clarity.ms/tag/ytk0sewicz?ref=npm` script adresi doğrulandı. Kontrol anında Clarity tag endpoint'i `204 No Content` döndü ve panel hâlâ Başlarken ekranındaydı. SDK script eklenmesi doğrulandı; gerçek collect isteği, kayıt teslimatı ve maskeli replay henüz doğrulanmadı. Microsoft FAQ, dashboard verilerinin görünmesinin birkaç saat sürebileceğini belirtiyor. Sonraki kontrol: tag'in JavaScript döndürmesi, web'de yeniden bir session açılması, ardından Kayıtlar ekranında maskeli metinlerin incelenmesi.
- iOS Expo prebuild ve `pod install --repo-update` başarılı; Clarity 4.1.2 ve Sentry 8.58.0 native pod'ları kuruldu. Mevcut Xcode'da kullanılabilir iOS 26.5 platform/destination bulunmadığından native binary derlemesi ve gerçek cihaz kaydı doğrulanamadı. Expo Go kaydı test etmek için yeterli değildir.
- Typecheck, 7 client testi ve 5 server testi geçti. Full lint, aynı config ile ölçülen güncel main baseline'ıyla aynı 27 error / 31 warning veriyor; değişen dosyalarda ek lint hatası yok.
- Tam oyun akışı bu worktree'de eksik encrypted index/backend yapılandırması nedeniyle test edilmedi. Merge ve deployment yapılmadı.

Resmî kaynaklar:

- https://docs.expo.dev/versions/v57.0.0/
- https://docs.expo.dev/guides/using-sentry/
- https://docs.expo.dev/guides/environment-variables/
- https://docs.sentry.io/platforms/react-native/manual-setup/
- https://docs.sentry.io/platforms/python/integrations/fastapi/
- https://learn.microsoft.com/en-us/clarity/mobile-sdk/react-native-sdk
- https://learn.microsoft.com/en-us/clarity/mobile-sdk/clarity-sdk-masking
- https://learn.microsoft.com/en-us/clarity/faq
