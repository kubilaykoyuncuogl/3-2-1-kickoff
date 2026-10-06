# Yapılacaklar

Güncelleme: 2026-10-06. Biten işler buradan silinir; ayrıntı ilgili dokümanda.

## Hesap ve giriş
- [ ] **Google ile giriş.** Akış: oyun bir bağlantı açar → kullanıcı tarayıcıda Google'da onaylar → sunucu geri çağrıyı alır → oyuna WebSocket'ten haber verir (web, Android, iOS için tek akış, eklenti gerekmez).
  - Gereken (Kubilay): Google Cloud'da OAuth istemcisi (Web application), yetkili yönlendirme adresi `https://kickoff.grandecorpo.com/auth/google/callback`. İstemci kimliği ve sırrı `.env`'e: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.
  - Kod: `server/accounts.py`'ye `/auth/google/start` ve `/auth/google/callback`; `identities` tablosuna `(google, sub)` yazılır, kullanıcının `verified` alanı 1 olur. Caddy'de `/auth/*` yolu Python servisine yönlenir. Oyunda Hesap ekranına "Google ile bağlan" düğmesi (şu an "yakında" yazıyor).
  - Google kimliği başka bir hesaba bağlıysa: o hesaba geçiş (cihaz ekleme gibi davranır).
- [ ] **Apple ile giriş.** iOS'a çıkarken zorunlu (başka sağlayıcı sunuluyorsa Apple da sunulmalı). Apple Developer hesabı, Services ID ve anahtar gerekir. Akış Google ile aynı; `identities`'e `(apple, sub)`.
- [ ] **Doğrulanmış havuz.** Eşleşmede `verified` ayrımı kodda var; Google/Apple gelince anlam kazanır.
- [ ] Takma ad için küfür / taklit filtresi.
- [ ] Gizlilik metni ve mağaza için "hesabımı sil" bağlantısı (silme işlevi oyunda var).
- [ ] Hesap veritabanı yedeği: sunucuda `kickoff-data` volume'ündeki `kickoff.sqlite` (günlük kopya).

## Skor tablosu
- [ ] Karar: tabloda kim görünsün (öneri: yalnızca hesaplı oyuncular; misafir kendi sırasını görür).
- [ ] Elo tablosu ve mod başına tek oyunculu tablolar (haftalık + tüm zamanlar), ilk 50 + kendi sıran. Veri hazır: `users.elo`, `bests`. Haftalık için skor geçmişi tablosu eklenecek.
- [ ] Online sayfasına ve Tek oyna kartlarına tablo girişi.

## Oyun
- [ ] Yeni üç modun çok oyunculusu (Kariyer yolu, Sıradaki kulüp, O mu bu mu): tek oyunculu test sonuçlarına göre.
- [ ] Panel geçiş animasyonları (paneller ortaya kayar, chip'e küçülür); `docs/screens.md` geçiş tablosu.
- [ ] Ses ve titreşim (geri sayım, düdük, doğru/yanlış). Ayarlar'da yalnızca aç/kapa duruyor; müzik ve efekt düzeyi kaydırıcıları ekrana sığdırmak için kaldırıldı (değerler `App.music_vol` / `App.sfx_vol`'da), ses gelince geri eklenecek.
- [ ] "Nasıl oynanır"ı oynanabilir tura çevirmek (şu an beş adımlık anlatım).
- [ ] Önerilerde aynı adlı kulüplere ülke etiketi (iki "Arsenal FC").
- [ ] Daha fazla mod: Hangisi pahalı, Kiralık mı satış mı, Kariyeri sırala.
- [ ] Günlük koşu ve görevler (bilerek kaldırıldı, tablo gelince yeniden).

## Mobil ve yayın
- [ ] Gerçek telefonda klavye testi (Android APK ve iPhone Safari): kutu klavyenin üstünde kalıyor mu.
- [ ] Android: kalıcı release anahtarı, AAB (gradle build), Play Console. Şu an debug imzalı APK.
- [ ] iOS: Mac + Xcode + Apple Developer hesabı gerekir.
- [ ] Ad ve logo: "MR GUESS" yönü konuşuldu, logo denemeleri beğenilmedi (`tools/logo/`). Ad kesinleşince uygulama adı, paket adı, ikon değişecek. Kaynak siluet bir basın fotoğrafından; yayında kullanılmamalı.
- [ ] Dil: varsayılanı cihaz diline göre seçmek; `en.json` çevirisinin gözden geçirilmesi.

## Veri
- [ ] Kulüp adlarını kendi yazımımıza çekmek (en az ilk birkaç yüz kulüp: "Fenerbahçe", "Başakşehir").
- [ ] Transfer bedellerinde kaynağın tahmini olanları ayıklamak ya da bedel ipucunu yuvarlamak.
- [ ] Ün sıralamasını piyasa değerinden bağımsız kurmak (maç/gol/kulüp tier'ı yeterli olabilir); sonra `mv_max` ve `stints.mv` sütunlarını index'ten tamamen silmek.
- [ ] Yayından önce: lisanslı ya da açık bir veri kaynağı ve hukuki görüş.
- [ ] İstatistiklerde tuhaf değerlerin taranması (ör. bazı oyuncularda sarı kart sayısı şüpheli).
- [ ] Sıradaki kulüp ipucundaki lig, kulübün bugünkü ligi; transfer yılındaki lig veride yok.
