# Clarity ve Sentry

Uygulama: Expo SDK 57, Expo'nun seçtiği `@sentry/react-native ~7.11.0`, native Clarity ve web Clarity. Sunucu: Sentry Python 2.x, FastAPI ve Starlette entegrasyonları.

## Ortam değişkenleri

Uygulama için `app/.env.example` dosyasını **git dışında kalan** `app/.env.local` dosyasına kopyalayın. Boş DSN/Project ID ile ilgili servis açılmaz. Geliştirme ortamında ayrıca `EXPO_PUBLIC_TELEMETRY_IN_DEV=true` gerekir; normal geliştirme varsayılan olarak veri göndermez.

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

`EXPO_PUBLIC_` değerleri JS paketine derleme sırasında gömülür. Değişiklikten sonra web export veya yeni native build/update gerekir. Sunucu ortamını değiştirmek mevcut web paketini değiştirmez.

Sunucu için `server/.env.example` içindeki satırları mevcut kök `.env` dosyasına ekleyin; index anahtarı ve daily salt satırlarını koruyun. `SENTRY_DSN` ayrı FastAPI projesinin DSN'idir. `SENTRY_ENVIRONMENT`, isteğe bağlı `SENTRY_RELEASE` ve `SENTRY_TRACES_SAMPLE_RATE` sunucuda kullanılır. Compose mevcut `env_file` üzerinden bunları okur.

Clarity projeleri şimdilik oluşturulmadı; ID'ler sonradan girilebilir.

## Kaydedilen veriler

Clarity ekran adlarını ve aşağıdaki sabit olay adlarını alır. Hesap/device kimliği, kullanıcı adı, kurtarma/eşleme kodu veya oda kodu özel tag/event olarak gönderilmez. Web'de belge kökü SDK yüklenmeden önce `data-clarity-mask="true"` ile maskelenir. Mobile SDK yalnız Strict masking hazır bayrağıyla başlar; bu bayrak panel ayarını otomatik değiştirmez.

`room_create`, `room_join`, `match_search`, `rematch_request` ve `single_start` kullanıcı aksiyonlarını sayar; sunucunun isteği kabul ettiği anlamına gelmez. `match_start`, ilk takım seçimine veya rövanşa geçildiğinde; `match_complete`, maç bitişine geçildiğinde; `single_complete`, tek oyunculu oyun bittiğinde gönderilir. Yeni tur geri sayımı yeni maç sayılmaz. Yeniden bağlanan istemcinin gözlemlediği ilk durum tekrar sayılabilir; bu olaylar istemci davranışı analizi içindir, tekil maç sayısı için sunucu verileri kullanılmalıdır.

Sentry uygulamada yakalanmamış hataları, Router error boundary hatalarını ve WebSocket mesaj işleme hatalarını; sunucuda FastAPI/Starlette hatalarını, yakalanıp devam edilen engine/index/accounts hatalarını ve başarısız background task'ları alır. Normal WebSocket kopması ve iptal edilen görevler hata raporu üretmez.

Sentry Replay kapalıdır. PII gönderimi kapalıdır; request body/header/cookie/query, kullanıcı/extra alanları, otomatik breadcrumb'lar ve stack local değişkenleri temizlenir. Hata mesajları da hesap kodu içerebildiğinden `[redacted]` olur; exception tipi, dosya/fonksiyon/satır ve işlem tag'i korunur. Performans kaydı açılırsa span açıklaması/data temizlenir; işlem tipi ve süre korunur. Bu tercih hata mesajıyla ayrıntılı teşhis imkânını azaltır.

## Build ve source map

Native Clarity **Expo Go'da çalışmaz**; uygulama Expo Go'da Clarity'yi yüklemez. Yeni native bağımlılıklar için development/production build gerekir. `ios/` ve `android/` klasörlerini elle üretip commit etmeyin; Expo/EAS autolinking kullanır.

`SENTRY_ORG` ve `SENTRY_PROJECT` birlikte tanımlandığında dinamik Expo config Sentry build plugin'ini ekler. Diğer Expo plugin'leri korunur. EAS native build sırasında source map yüklemesi için build ortamında `SENTRY_AUTH_TOKEN` gerekir. SDK 7'de Router hataları `_layout.tsx` üzerinden açıkça raporlanır.

Web export ve map yüklemesi (repo kökünden):

```sh
cd app
npx expo export --platform web --source-maps
cd ..
# SENTRY_ORG ve SENTRY_PROJECT uygulama projesini göstermelidir.
# Token için sentry-cli login veya CI secret kullanın.
sentry-cli sourcemaps upload app/dist
# Yükleme başarıyla tamamlandıktan sonra, dağıtımdan önce:
find app/dist -type f -name '*.map' -delete
```

Metro Sentry yapılandırması Debug ID'leri ekler. Source map'leri, dağıtılacak JS dosyalarıyla aynı export'tan yükleyin; başka bir export'un map'lerini kullanmayın. Map dosyalarını halka açık web dağıtımına dahil etmeyin. Normal `npm run export:web` map üretmez. EAS Update kullanıma alınırsa update'in map'leri ayrıca `npx sentry-expo-upload-sourcemaps dist` ile yüklenmelidir.

## Doğrulama

```sh
cd app
npm run typecheck
npm run lint
npm run test:telemetry
npx expo export --platform all --source-maps
cd ..
.venv/bin/python -m unittest discover -s server/tests -v
```

DSN'leri girdikten sonra test ortamında `EXPO_PUBLIC_TELEMETRY_IN_DEV=true` ile bir test hatası üretip Sentry'de tip/stack/operation alanlarını ve source map çözümlemesini doğrulayın. Hesap ekranında nickname/recovery/link metinlerinin Clarity kaydında maskeli olduğunu web ve gerçek native build üzerinde kontrol edin. ID/DSN olmadan derleme ve testlerin geçmesi, vendor'a teslimatın veya gerçek cihazda native kaydın doğrulandığı anlamına gelmez.

Resmî kaynaklar:

- https://docs.expo.dev/versions/v57.0.0/
- https://docs.expo.dev/guides/using-sentry/
- https://docs.expo.dev/guides/environment-variables/
- https://docs.sentry.io/platforms/react-native/manual-setup/
- https://docs.sentry.io/platforms/python/integrations/fastapi/
- https://learn.microsoft.com/en-us/clarity/mobile-sdk/react-native-sdk
- https://learn.microsoft.com/en-us/clarity/mobile-sdk/clarity-sdk-masking
