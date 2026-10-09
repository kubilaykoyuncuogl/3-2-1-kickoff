# Online akış bileşenleri

Kullanıcının paylaştığı sekiz görsel koyu tema içerik/durum referansıdır. Ana kitin seçilmiş görsel dili ve tokenları korunur. Yeni durum yorumları öneridir; kaynak ekranların bütünü onaylanmış tasarım sayılmaz. Pano: COMPONENT-LIBRARY.html. Kaynaklar: selected-references/online-dark/.

| Bileşen | Veri / durum | Sözleşme |
|---|---|---|
| EloSummary | nickname, rating, explanation | Surface; ad bodyStrong, değer score; tek bilgi grubu, gereksiz dokunma hedefi yok |
| ScopeOption | id, title, description, selected, disabled | Field/ChoiceOption temeli; minimum 56; kalıcı selected işareti ve native selected state; kontrol sınırı/focus; ikon dekoratif |
| ChoiceGroup | label, options, value, onChange | Dönem/süre seçimleri; minimum 48 hedef; çok satıra sarma; tek seçim state; tek lig alt seçimi mevcut akıştan gelir |
| CriteriaChip | label | Arama kapsamının salt okunur özeti; basılabilir değilse button rolü verilmez; amber dönem anlamı için kullanılmaz |
| MatchmakingStatus | status, elapsedSeconds, ratingRange, searcherCount, expansionSeconds, criteria, onCancel | searching/cancelling/error; sayaç gerçek veriden biçimlenir, negatif/NaN gösterilmez; her saniye duyuru yok; iptal minimum 48; busy state; iptal sonrası mevcut online ayarlarına dönülür |
| TeamSelectionPanel | role, nickname, team, ready, onChange, onReady | Sen mor/rakip amber; editing/validating/selected/ready; Değiştir ve Hazırım büyük metinde alt alta; ready sonrası tekrar submit engellenir; devasa boş renk blokları oluşturulmaz |
| OpponentStatus | selecting, ready, disconnected + remainingSeconds | Rol etiketi ayrı, bağlantı mesajı warning; gerçek geri bağlantı süresi; oyun sonucu uydurulmaz |
| TeamUsedFeedback | teamName, message, locked | Inputa yakın açık mesaj; odak korunur; used state için erişilebilir hata duyurusu bir kez; mevcut geçici kilit kuralları değiştirilmez |
| VersusIntro | selfTeam, opponentTeam, nicknames | İki TeamBadge/rol yüzeyi; sözel karşılaşma bilgisi; geçiş reduced motion ile uyumlu; yeni süre kuralı yok |
| RoundOutcome | selfScored / opponentScored / noAnswer; playerName; scoreDelta | Sen puan aldın success; rakip puan aldı opponent; kimse bilemedi neutral. Rakibin doğru cevabı danger değildir. Yalnızca bir durum gösterilir |
| AnswerRevealList | answers, initialVisibleCount, expanded, onExpand | İç içe bağımsız kartlar yerine numaralı gruplu liste; kalanlar gerçek veriden açılır; +N tek başına değil N oyuncuyu daha göster; bu sonuç listesi SuggestionRow değildir |

## Ekran yerleşimi

OnlineSetup: ScreenHeader → EloSummary → ScopeOption grubu → dönem → tur süresi → Ara → oda eylemleri → Elo açıklaması. Dar ekranda scroll; eylemler örtülmez.
Matchmaking: ScreenHeader → MatchmakingStatus → CriteriaChip özeti → iptal. Merkezli bekleme alanı büyük metinde sayfa akışına döner.
TeamSelection: ortak üst Scoreboard → kalan süre → kendi seçim paneli → rakip durumu → gerekiyorsa bağlantı mesajı.
RoundResult: üst Scoreboard → RoundOutcome → ilgili takım bilgisi → AnswerRevealList → mevcut sonraki tur davranışı. Skor kaynaktaki orta/alt konumlara taşınmaz.

## Uygulama sınırı

Pano HTML ile bileşen görünüşünü örnekler; gerçek RN implementasyonu değildir. Tema değiştirme ve seçim grupları görsel inceleme için çalışır. Diğer eylemler statik örnektir. Sistem fontu kullanılır; native üretimde Sora yüzleri gerekir. Mevcut JSON/TS tokenları değiştirilmedi. Native VoiceOver/TalkBack, cihaz, klavye ve oyun protokolü testleri henüz yapılmadı.
