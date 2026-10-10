# UI bileşen envanteri ve sözleşmeleri

`Seçili` aşağıda yalnız iki kaynak ekranda görünen anatomiyi belirtir. Tam uygulama veya tüm state'ler kullanıcı tarafından test/onaylanmış değildir. `Öneri` ek UI kitini belirtir.

| ID / bileşen | Statü | Variant / state | Veri ve davranış |
|---|---|---|---|
| C01 IdentityHeader | Seçili | normal, uzun ad | logo, avatar initial, nickname; avatar min48 hit |
| C02 PlayAction | Seçili anatomi | primary, secondary; normal, pressed, focus, disabled, busy öneri | label, optional helper, caret; tek action; busy çift gönderimi engeller |
| C03 WeeklyEntry | Seçili | normal, focus | artwork, title, count, helper; tek navigation action |
| C04 MatchCard | Seçili | unselected; selected, ended, unavailable öneri | fixtureID, teams, contribution totals nullable, deadline, participation action |
| C05 FloatingNav | Seçili | home/matches/settings active | selectedDestination; item label+icon; kendi seçili state'i |
| C06 Button | Öneri | primary, secondary, quiet, destructive; busy, disabled, focus | min48; busy adı korunur; destructive lime olmaz |
| C07 IconButton | Öneri | back, close, sound; normal/pressed | 24 ikon içinde min48 hedef; erişilebilir tam adı |
| C08 Badge | Seçili anatomi | time, neutral, selected, error öneri | label; color tek state göstergesi değildir |
| C09 Avatar | Seçili | initial | K/kubi örneği; profil fotoğrafı gerektirmez |
| C10 SectionHeading | Seçili | title/count, helper | 2 satırlık responsive başlık; count bağımsız |
| C11 TextField | Öneri | empty, filled, focus, error, disabled | görünür label, helper, error, value; placeholder label yerine geçmez |
| C12 PlayerAutocomplete | Öneri | idle, typing, loading, results, empty, error | query, result list; seçilen id answer submission'a gider; roster/back-end ayrı |
| C13 ChoiceRow | Öneri | normal, selected, disabled | teamID+teamName; yalnız bir seçim; check ve state label |
| C14 TeamChoiceSheet | Öneri | open, selected, saving, error | fixture adı, 2 choice row, onay; kapatınca kayıt yapılmaz |
| C15 SettingsRow / Switch | Öneri | on/off, disabled | Ses efektleri; label satırına da dokunulabilir |
| C16 Toast | Öneri | success, error, neutral | kısa durum; eylem gerekirse inline alert/dialog kullan |
| C17 InlineAlert | Öneri | error, warning, info | açıklayıcı title+message, gerekirse retry |
| C18 EmptyState | Öneri | no matches, no search result | next step anlaşılır; var olmayan maç/roster uydurulmaz |
| C19 Skeleton / Loader | Öneri | pending | sonuç/loading eşlemesi; timeout/error ayrılır |
| C20 ConfirmDialog | Öneri | exit prompt | mevcut oyundan çıkmak gibi kesintiyi onaylar; iki açık eylem |
| C21 Countdown | Öneri | 3 / 2 / 1 | mevcut COUNTDOWN_MS=3000 süresine bağlı, dekoratif sayaç değildir |
| C22 RoundTimer | Öneri | normal, <=5s urgent, elapsed | ROUND_MS=15000 için remainingMs; tek zaman kaynağı |
| C23 Scoreboard | Öneri | 0–3, won | iki oyuncu, WIN_SCORE=3; katkı puanıyla karıştırılmaz |
| C24 AnswerFeedback | Öneri | accepted, incorrect, locked | doğru +1; yanlışta PENALTY_MS=5000; metin+ikon+timer |
| C25 RoundResult | Öneri | win/loss/tie | doğrulanmış backend/state sonucunu gösterir; kazananı UI hesaplamaz |
| C26 SegmentedChoice | Öneri | 2–3 option | dar seçim modülleri için; alt menü yerine kullanılmaz |
| C27 ConnectionState | Öneri | reconnecting/offline | mesaj+yeniden dene; gerçek bağlantı durumu servisten gelir |

## Ortak kurallar

48 mantıksal birim hedef minimumu; native iOS44pt / Android48dp altına inme. Spacing, kenar ve metin duruma göre kaymamalı. Focus halkası lime2px +3px offset. Disabled kontrol etkileşmez; neden gerekli ise helper ile açıklanır. Hover yalnız pointer ortamına yönelik opsiyonel önizlemedir, mobil için zorunlu state değildir.

Form hata mesajı inputun altında metinle gösterilir. Renk tek sinyal değildir. Loader alanı aynı yerde tutulur; ekrandaki içerik sıçramaz. Sheet ve dialog aynı anda açık kalmaz; klavye önce kapatılır. Toast bottom nav/safe area üstünde görünür.

C21–25 süre/kural referansı: 10 Ekim 2026 tarihinde okunan mevcut Godot `game/scripts/game.gd` sabitleri (COUNTDOWN_MS3000, ROUND_MS15000, PENALTY_MS5000, WIN_SCORE3). Bunlar mevcut çekirdek oyun için; solo alt modlara otomatik uygulanmaz. Katalog gerçek cevap doğrulamaz.
