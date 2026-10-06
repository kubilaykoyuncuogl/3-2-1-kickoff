# Expo'ya geçiş planı (uygulama öncelikli)

> Karar 2026-10-06 (Kubilay): ürün **mobil uygulama** (Android + iOS), web yan kapı. Godot istemcisi ve Godot oyun sunucusu kaldırılacak; istemci **Expo / React Native**, oyun sunucusu **Python**. Bu belge uygulayacak ajan için yazıldı: önce `CLAUDE.md`, `docs/data.md`, `docs/screens.md`, `docs/single-modes.md`, `docs/palette.md`'yi oku; kurallar orada, burada yalnızca geçiş.

## 0. Hedef ve sınırlar

Kararlar (2026-10-06, Kubilay):
- Süreler ve zorluk: geçiş sırasında dokunulmaz; geçişten sonra tüm modlar için ayrı bir **level design** çalışması yapılacak (tur süresi, basamak süreleri, tier geçişleri, can sayıları hep birlikte).
- Reklam (Faz 7): sonra, ayrı "başla" ile.
- Mağaza hesapları: Apple ve Google geliştirici hesapları var; EAS/mağaza bağlantılarını arkadaşı yapacak. Faz 6'da ajan `eas.json` ve komutları hazırlar, hesap işlemlerini yapmaz.

- Tek kod tabanı: `app/` (Expo). Çıktılar: Android (AAB/APK), iOS (EAS bulut derlemesi, Mac yok), web (Expo web; oda linki paylaşımı için yeterli, öncelik değil).
- Sunucu: tek Python süreci (FastAPI + WebSocket). Index servisi (`server/index_service.py`) ve hesaplar (`server/accounts.py`) **aynen kalır**; oda/maç/tek oyunculu mantık `game/scripts/game.gd`'den Python'a taşınır.
- Kurallar, süreler, puanlar, tier/kapsam/dönem, hesap akışları, dil anahtarları, palet **değişmez**. Bu bir yeniden yazım, yeniden tasarım değil. Godot'da bitmiş ekranlar birebir referans (`./shots.sh light|dark` ile `/tmp/kickoff-shots/` üretilir; başlamadan bir kez üretip sakla).
- Godot kodu geçiş bitene kadar silinmez; `game/` referans olarak durur. Geçiş sonunda `game/`, `build/`, `shots.sh`, `run_local.sh`'ın Godot kısımları kaldırılır.
- Deploy komutlarını (rsync, ssh, docker compose, git push, EAS submit) **kullanıcı çalıştırır**; ajan komutu yazar.

## 1. Mimari (hedef)

```
app/            Expo (React Native + TypeScript)        ── wss://kickoff.grandecorpo.com/ws
server/
  index_service.py   (aynen)  127.0.0.1:9081  veri, paketler, öneri, doğrulama
  accounts.py        (aynen)  /acct/*
  game/              YENİ: oda, maç durum makinesi, tek oyunculu oturumlar, eşleşme, Elo
  ws.py              YENİ: WebSocket uç (/ws), oturum, mesaj yönlendirme, oran sınırı
  main.py            YENİ: tek FastAPI uygulaması: index_service + accounts + ws
deploy/            Caddy :8080 → /ws ve /acct python'a, / web build'e
```

- Tek süreç, tek port: Caddy → `127.0.0.1:9081` (hem HTTP hem WS). Godot ikilisi ve `bin/` kalkar.
- Sunucu otorite kalır: zamanlayıcı, puan, ceza, doğrulama hep sunucuda; istemci yalnızca gösterir ve niyet gönderir.
- Oyuncu→kulüp ilişkisi istemciye yine inmez (`docs/data.md` kuralları).

## 2. Mesaj sözleşmesi (RPC → JSON)

Godot RPC'leri birebir JSON mesajına çevrilir. Her mesaj `{"t": "<tip>", ...}`. İstemci→sunucu (eski RPC adı parantezde):

| t | alanlar | eski |
|---|---|---|
| `hello` | `nick, device, proto` | `hello(nick, device)` |
| `create_room` | `scope, era` | aynı |
| `join_room` | `code` | aynı |
| `find_match` | `scope, era` | aynı |
| `cancel_find` | – | aynı |
| `leave_room` | – | aynı |
| `pick_team` | `team_id, team_name` (0 = seçimi kaldır) | aynı |
| `set_ready` | – | aynı |
| `guess` | `player_id, name` | aynı |
| `suggest` | `kind: "team"\|"player", q` | aynı |
| `rematch` | – | aynı |
| `single_start` | `mode, scope, era` | aynı |
| `single_guess` | `player_id, name` (ladder, career) | aynı |
| `single_answer` | `option` (blitz, versus) | aynı |
| `single_team` | `team_id, name` (chain) | aynı |
| `single_quit` | – | aynı |
| `acct` | `op, a, b` | aynı |

Zarf: istemci→sunucu `{"t": "<tip>", ...alanlar}`; sunucu→istemci `{"t": "room_state"|"single_state"|"profile_state"|"acct_result", "d": {...}}`, `{"t": "suggest_result", "kind", "q", "list"}`, `{"t": "err", "key"}`, bağlanınca `{"t": "welcome", "pid", "proto"}`. `room_state.d.me` izleyenin kendi pid'i (Godot'daki `multiplayer.get_unique_id()` karşılığı).

Sunucu→istemci: `room_state`, `suggest_result {kind, q, list}`, `single_state`, `profile_state` (içinde `proto`), `acct_result`, `err {key}` (istemci `err.*` anahtarını çevirir). Sözlük alanları `game.gd`'deki `_broadcast`, `_single_send`, `_send_profile`, `_send_queue` ile **aynı adlarla** kalsın; ekran kodu bu alanlara göre yazılacak.

- `proto`: `hello`'da istemci gönderir; tutmuyorsa sunucu `err {key:"err.proto"}` + `profile_state` yollar, istemci "Yeni sürüm var" kartını açar (Expo Updates varken bu kart "güncelleniyor" olur, bkz. 6.3).
- Yeniden bağlanma: `hello`'daki `device` ile 10 sn içinde odaya geri bağlanır (`RECONNECT_MS`, `pending_rc`). Aynı mantık.
- Oran sınırı: `_allow("%d:guess", 30/60 sn)`, `"%d:suggest"` 12/sn ayrı sayaçlar; `hello` ve `acct` için ek genel sınır (IP başına dakikada 20).

## 3. Sunucu: GDScript → Python taşıma (`server/game/`)

Kaynak: `game/scripts/game.gd` (~760 satır). Taşınacak parçalar ve hedef dosyalar:

- `state.py`: `State` enum `{LOBBY, PICK_TEAMS, COUNTDOWN, REVEAL, ROUND, ROUND_END, GAME_OVER}` ve sabitler: `ROUND_MS 15000, COUNTDOWN_MS 3000, REVEAL_MS 1800, PICK_MS 45000, QUICK_AT_MS 20000, PENALTY_MS 5000, ROUND_END_MS 4000, NO_COMMON_MS 3000, WIN_SCORE 3, MAX_INVALID_PAIRS 3, RECONNECT_MS 10000, CROSS_SCOPE_MS 45000, BAND_START 75, BAND_STEP 50, BAND_STEP_MS 20000, BAND_MAX 500, ELO_K 32, ELO_K_NEW 40, SINGLE_LIVES, CAREER_REVEAL_MS 8000, CAREER_LAST_MS 15000, CHAIN_STEP_MS 20000, PROTO`.
- `rooms.py`: `Room` (code, ranked, scope, era, players, teams, team_names, ready, score, penalty_until, used_teams, invalid_streak, last, answers, answers_total, winner, rematch, elo_delta, away, quick_picks, gen, phase_end). Akış: `_start_pick → (hızlı seçenekler QUICK_AT_MS'te) → set_ready ×2 → ortak oyuncu ön kontrolü (yoksa _no_common) → COUNTDOWN → REVEAL → ROUND → _end_round → ROUND_END → _start_pick`. Rakibin takımı PICK'te gizli (`_broadcast` izleyene göre). Oda kodları `server/words.txt`'ten (`game/assets/room_words.txt` ile aynı liste; tek kopya `server/`de kalsın).
- `matchmaking.py`: kuyruk, `_band`, aynı kapsam + aynı dönem, 45 sn sonra genişleme (dönem birleşimi kuralı `_tick_queue`'daki gibi), verified eşleşmesi, az önceki rakibe 20 sn bekleme.
- `singles.py`: ladder, blitz, career, chain, versus oturumları (`single_start`, `_single_next`, `_single_send`, puanlama, kombo, can, süreler). Paketler index servisinden (`/ladder`, `/blitz/pack`, `/career/pack`, `/chain/pack`, `/versus/pack`), `_`'lı cevap alanları istemciye gitmez.
- `elo.py`: `_apply_elo`.
- `profiles.py`: `hello` → `/acct/hello`, `_send_profile`, `_apply_profile`, en iyi skor kaydı (`/acct/best`), Elo kaydı (`/acct/save`).
- `ws.py`: bağlantı başına görev, mesaj doğrulama (pydantic), zamanlayıcılar `asyncio` ile; Godot'daki `gen` sayaç deseni korunur (geç gelen zamanlayıcı eski turu bozmasın).
- Index servisi aynı süreçte olduğu için HTTP yerine doğrudan fonksiyon çağrısı yapılabilir; ama `LockedDB` kilidi ve `lru_cache` davranışı aynı kalmalı. İlk sürümde HTTP ile (localhost) kalmak da kabul; iş bitince optimize et.

Doğrulama: `tools/wsbot.py` (Python) — eski `test_bot.gd`'nin karşılığı: `--bot ad --team x --guess y [--era n] [--single mod]`; iki botla maç, ortak oyuncusuz çift, kopma/yeniden bağlanma, her tek oyunculu mod. Bu bot geçiş boyunca sunucunun kabul testi.

## 4. İstemci: Expo uygulaması (`app/`)

### 4.1 Kurulum
- `npx create-expo-app app --template blank-typescript`, Expo SDK güncel kararlı. Expo Router (dosya tabanlı yönlendirme). Paketler: `expo-router`, `expo-font` (Sora: `game/assets/fonts/Sora[wght].ttf`, OFL), `expo-haptics`, `expo-clipboard`, `expo-sharing`/`Share`, `expo-updates`, `expo-secure-store` (cihaz kimliği), `@react-native-async-storage/async-storage` (ayarlar), `react-native-reanimated` (geçişler), `react-native-safe-area-context`, `react-native-google-mobile-ads` (reklam, faz 7), `zustand` (durum; küçük ve okunur).
- Dil: `game/lang/*.json` dosyaları **taşınmaz, paylaşılır** → `app/lang/` içine sembolik değil kopya; `tools/check_lang.py` iki konumu da kontrol etsin. `t("anahtar")` + `%s/%d` biçimi aynı.
- Palet: `docs/palette.md` → `app/theme/palette.ts` (LIGHT/DARK token sözlükleri, `game/scripts/palette.gd` ile aynı hex'ler). Sistem/açık/koyu seçimi.
- Ölçek: tasarım genişliği 400; `useWindowDimensions` ile 400→ekran genişliği oranı, en fazla 1.35 (Godot `MAX_SCALE`). Tabletlerde içerik ortalanır, en fazla `MAX_COL` (ui.gd'deki değer) genişlik.

### 4.2 Ağ katmanı (`app/net/`)
- `socket.ts`: tek WebSocket, otomatik yeniden bağlanma (1, 2, 4 sn… en fazla 10 sn), bağlanınca `hello`. Uygulama arka plana gidince bağlantı kopabilir; öne gelince hemen yeniden bağlan (`AppState`).
- `store.ts` (zustand): `room`, `single`, `profile`, `suggestions`, `error`, `connected`. Sunucu mesajları doğrudan store'a yazılır; ekranlar store'u okur. Godot'daki sinyallerin karşılığı.
- `proto.ts`: mesaj tipleri (TypeScript), `PROTO` sabiti sunucuyla aynı.

### 4.3 Ekranlar (`app/app/` Expo Router)
Godot `game/scripts/screens/` birebir; her biri için referans ekran görüntüsü var.

| Rota | Godot | Not |
|---|---|---|
| `/` | `menu.gd` | logo/wordmark, Online, Tek oyna, Nasıl oynanır, Ayarlar, Elo |
| `/nickname` | `nickname.gd` | ilk açılış |
| `/online` | `online.gd` | Elo kartı, kapsam seçici, dönem çipleri, Ara / Oda kur / Odaya katıl; arama ve oda bekleme aynı ekranda |
| `/match` | `match.gd` | PICK / COUNTDOWN / REVEAL / ROUND / ROUND_END (+ no_common) / GAME_OVER; durumlar arası geçiş yumuşak (opacity); uyarılar ortada kart; kopma geri sayımı; rakip ayrılınca 5 sn sonra çık |
| `/single` | `single.gd` | 5 mod kartı, en iyi skor çipi |
| `/single/scope` | `single_scope.gd` | ladder, blitz |
| `/single/era` | `single_era.gd` | hepsi |
| `/single/play` | `single_play.gd` | ladder + blitz |
| `/single/career`, `/single/chain`, `/single/versus` | `*_play.gd` + `single_base.gd` | |
| `/settings` | `settings.gd` | tek ekran, kaydırmasız |
| `/account` | `account.gd` | oluştur / bağla / kurtar / çıkış / sil |
| `/howto` | `howto.gd` | 10 adım |

Bileşenler (`app/ui/`): `ui.gd` karşılığı: `Button, Toast, Badge, Chip, Row, ListCard, Kv, TimerBox, Progress, OptionCard, ScopeButton/ScopePicker, EraPicker, Segment, Chevron, DefunctIcon, Nav, Page, Autocomplete` (debounce 120 ms, 6 öneri, kullanıldı/kapsam dışı/kapanmış durumları), `UpdateCard`.

Klavye: `KeyboardAvoidingView` + `autoFocus`, Godot'daki "onay düğmesi klavyenin arkasında kalıyor" sorunu burada yerel klavye olduğu için kendiliğinden çözülür; yine de maç ve tek oyunculu ekranlarda yazı kutusu üstte kalır (docs/screens.md).

Oda linki: `kickoff://oda/<kod>` (uygulama şeması) + `https://kickoff.grandecorpo.com/?oda=<kod>` (web). Expo Router linking ile ikisi de `/online?oda=` açar.

### 4.4 Web çıktısı
`npx expo export --platform web` → `dist/` → Caddy `root`. COOP/COEP başlıkları artık gerekmez (SharedArrayBuffer yok), `Cache-Control: no-cache` (no-store değil). Web'de reklam yok.

## 5. Deploy

- `deploy/Dockerfile`: python + `server/` + `dist/` (web). Godot ikilisi, `caddybin` aşaması kalır (Caddy), `bin/` kalkar.
- `deploy/entrypoint.sh`: tek `uvicorn server.main:app --port 9081` + Caddy.
- `deploy/Caddyfile.container`: `/ws` ve `/acct/*` → 9081, geri kalan `dist/`.
- `kickoff-bridge.service` ve compose portu aynı (8080). `data/state` volume aynı (`kickoff-data`).
- Yerel: `run_local.sh` → uvicorn + `npx expo start`. Web için `npx expo start --web`.

## 6. Fazlar ve kabul ölçütleri

Her faz sonunda commit; mesajlar Türkçe, `Co-Authored-By` satırı.

### Faz 1 — Python oyun sunucusu (Godot istemciyle uyumlu değil, bağımsız test) — **tamamlandı 2026-10-06**
Dosyalar: `server/game/{consts,engine,singles}.py`, `server/ws.py`, `server/main.py`, `tools/wsbot.py`. Çalıştırma: `set -a; . ./.env; set +a; .venv/bin/uvicorn server.main:app --host 127.0.0.1 --port 9081`. Kabul testleri botla geçti (maç, ortak oyuncusuz çift, pick zaman aşımı, kopma/geri bağlanma, Elo, dönem, 5 mod, hesap akışı, 10 eşzamanlı maç). Not: eski Godot istemcisi bu sunucuyla konuşamaz; test sürümü Faz 5'e kadar Godot sunucusuyla yayında kalır.
1. `server/game/*`, `server/ws.py`, `server/main.py`.
2. `tools/wsbot.py`.
3. Kabul: iki botla tam maç (3 puan), ortak oyuncusuz çift (uyarı, 3 sn, seçime dönüş, 3 kez → berabere), 45 sn seçim zaman aşımı, yanlış tahminde 5 sn kilit, kopma → 10 sn içinde geri bağlanma, Elo değişimi, oda kodu ile katılma, aynı takım tekrar seçilemez, rakip takımı PICK'te gizli, kapsam dışı takım reddi, dönem süzmesi (GS–Inter 80'ler → yalnız Şükür). Beş tek oyunculu mod başlar, yanar, en iyi skor hesaba yazılır. 20 eşzamanlı bot maçı (eski `load_*.log` senaryosu) hatasız.

### Faz 2 — Expo iskeleti + ağ + menü/ayarlar/hesap — **tamamlandı 2026-10-06**
1. Proje, font, palet, tema, dil, ölçek, store, socket.
2. `/`, `/nickname`, `/settings`, `/account`, `/howto`.
3. Kabul: Android emülatör ve Expo Go'da açılır; dil ve tema anında değişir; hesap akışları (oluştur, bağlama kodu, kurtarma, çıkış, sil) Faz 1 sunucusuyla çalışır; `check_lang.py` temiz.

### Faz 3 — Online maç — **tamamlandı 2026-10-06** (tarayıcıda bot rakibe karşı oynandı; iki gerçek telefonla deneme bekliyor)
1. `/online`, `/match`, Autocomplete, hızlı seçenekler, uyarı kartı, geçişler, kopma/ayrılma davranışları.
2. Kabul: iki telefon (ya da telefon + bot) ile tam maç; Godot ekran görüntüleriyle yan yana karşılaştırma; her durum ekranı referansa uygun; klavye hiçbir düğmeyi kapatmıyor.

### Faz 4 — Tek oyunculu beş mod — **tamamlandı 2026-10-06**
1. `/single/*`.
2. Kabul: her mod başlar, oynanır, biter; en iyi skor görünür; dönem ve kapsam seçimi paketlere yansır.

### Faz 5 — Deploy ve web — **dosyalar hazır 2026-10-06**, canlıya alma kullanıcıda (konteyner yerelde derlenip denendi: sayfalar, /ws, önbellek başlıkları, bot maçı)
1. Dockerfile/entrypoint/Caddyfile, `run_local.sh`, `README`/`CLAUDE.md` güncellemesi.
2. Web export; oda linki web'den açılıyor.
3. Kabul: canlıda web + Android APK (EAS ya da yerel `expo run:android`) aynı sunucuyla oynuyor.

### Faz 6 — Mağaza hazırlığı — `app/eas.json` ve `app.json` hazır; EAS projesi, hesap bağlantıları ve derlemeler bekliyor
1. `eas.json` (development / preview / production profilleri), `app.json` (paket adı `com.kickoff321.app` benzeri, ikon, splash, şema `kickoff`).
2. Expo Updates: üretim kanalı; `proto` uyuşmazlığında istemci önce `Updates.fetchUpdateAsync` dener, başarısızsa "mağazadan güncelle" kartı.
3. iOS: EAS bulut derlemesi (Apple geliştirici hesabı kullanıcıda), TestFlight. Android: AAB, iç test kanalı.
4. Kabul: TestFlight ve Play iç testte kurulup oynanıyor.

### Faz 7 — Reklam (ürün kararı sonrası)
- `react-native-google-mobile-ads`: tek oyunculuda "reklam izle, 1 can" (ödüllü), 3 maçta bir geçiş reklamı; maç sırasında reklam yok. Test kimlikleriyle geliştir, gerçek kimlikler `.env`/EAS secret.
- Bu faz ayrı onay ister; plana yalnızca yer ayrıldı.

### Faz 8 — Godot'un kaldırılması
- `game/`, `build/`, `shots.sh`, `test_bot.gd`, Godot export preset'leri, `deploy`'daki Godot izleri silinir; `CLAUDE.md` ve `docs/*` güncellenir; bellek notları (`~/.claude/.../memory/kickoff-*.md`) güncellenir.

## 7. Değişmeyecekler (dokunma)

- `tools/build_index.py, build_stats.py, build_geo.py, finalize_index.py, encrypt_index.py, normalize.py` ve `data/index/index.enc`.
- `server/index_service.py` uçları ve `LockedDB` kuralı; `server/accounts.py`; `server/tiers_curated.txt`; `server/words.txt`.
- Kurallar: süreler, puanlar, can sayıları, tier/kapsam/dönem mantığı, Elo K değerleri.
- Dil anahtarları (yeni ekleme serbest, var olanı yeniden adlandırma yok).
- Palet hex değerleri ve Sora fontu.

## 8. Riskler ve kararlar

- **Zamanlayıcı doğruluğu**: Python'da `asyncio` zamanlayıcıları Godot'daki `create_timer` ile aynı `gen` deseniyle korunmalı; aksi halde geç gelen tur sonu yeni turu bozar. Faz 1 botlarında özellikle "rematch sırasında eski zamanlayıcı" senaryosu denensin.
- **Tek süreçte index + oyun**: index servisi CPU'yu uzun tutan sorgularda (hazır havuz işçisi) WebSocket gecikebilir. Havuz işçisi zaten ayrı iş parçacığında; sorun olursa oyun sunucusunu ayrı uvicorn sürecine böl (aynı Caddy arkasında).
- **Expo web**: ikincil; web'de görsel kusur kabul, oyun akışı çalışmalı.
- **Expo Go sınırı**: reklam ve bazı yerel modüller Expo Go'da çalışmaz; Faz 6'dan itibaren development build kullan.
- **iOS yayın**: Apple hesabı ve EAS kotası kullanıcıda; ajan `eas build` komutunu yazar, çalıştırmaz.
- **Dönem/kapsam gibi yeni kurallar** geçiş sırasında Godot sürümüne eklenmeyecek; test geri bildirimleri `docs/TODO.md`'ye yazılıp Expo sürümünde yapılır.

## 9. Sıra ve süre tahmini

Faz 1 (sunucu) → Faz 2 → Faz 3 → Faz 4 → Faz 5 arka arkaya; Faz 6 kullanıcı hesapları hazır olunca; Faz 7 ayrı karar; Faz 8 en son. Kaba tahmin: Faz 1 bir gün, Faz 2–4 iki-üç gün, Faz 5–6 bir gün; toplam yaklaşık bir hafta yoğun iş.

## 10. Uygulama notları (geçiş sırasında öğrenilenler)

- **Metro önbelleği**: kod değişince `expo start` eski paketi sunabiliyor (yeni dosya/ekran görünmüyor). Çözüm: sunucuyu `--clear` ile yeniden başlat (`run_local.sh` hep öyle başlatır).
- **Ekran görüntüsü**: `tools/expo_shots.sh [light|dark] [tr|en]` başsız Chrome ile `/tmp/kickoff-shots/expo/` üretir; sayfalar geliştirme modunda `?nick=&theme=&lang=` alır (`app/src/store.ts`). Sanal zaman ileri sarıldığı için sayaçlar 0-1 görünür, normal.
- **Sunucu adresi** (`app/src/net/socket.ts`): web'de sayfayı sunan adresin `/ws`'si, uygulamada `PROD_URL`, geliştirmede Expo sunucusunun makinesi `:9081`.
- **Caddy**: `/ws` ayrı `handle` bloğunda olmalı; yoksa `try_files` isteği `index.html`'e çevirir.
- **Eşzamanlılık**: turu bitiren her yol `Engine._finish_round` üzerinden geçer (gen eşzamanlı artar); `set_ready` tekrar gelirse yok sayılır. Godot sürümünde bu iki yarış vardı, Python'da kapatıldı.
- **Sözleşme sürümü**: `PROTO = 3` (`server/game/consts.py` ve `app/src/net/socket.ts` aynı olmalı).
- Godot istemcisi yeni sunucuyla konuşamaz: Faz 5 canlıya alınınca eski APK ve açık sekmeler çalışmaz (web'de sayfa yenilenince yeni istemci gelir).
