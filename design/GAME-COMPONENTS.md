# Tek oyun, karşılaştırma ve sonuç bileşenleri

Kullanıcının eklediği 11 koyu tema referansı: selected-references/solo-weekly-dark/. Önceki 8 online referansıyla toplam 19 kaynak görüntü saklandı. Görüntüler ihtiyaç ve içerik kanıtıdır; hepsinin yerleşimi onaylanmış değildir. Seçilen ana kit korunur. Kütüphanedeki 07–15 numaralı gruplar bu genişlemeyi örnekler.

| Bileşen | Props / durumlar | Görsel ve davranış sözleşmesi |
|---|---|---|
| ModeRow | modeId, title, bestScore?, onPress | Gruplu nötr liste, satır ayraçları; title bodyStrong; opsiyonel rekor caption; chevron dekoratif; tek eylem; en az 56; büyük metinde alt satır |
| BestScoreBadge | score, unit | Skor yoksa gizli; sıfır gerçek skor ise gösterilir; oyun modunun puan birimi korunur |
| RunHUD | stageLabel, stageValue, score, multiplier?, seconds, initialSeconds | Wrap; sayı ve zaman görünür; progress dekoratif/aynı süreyi özetler; yeni süre veya puan hesabı yok |
| LivesIndicator | remaining, total | Noktalara ek “2 can kaldı” metni; kayıp can sadece renk değil boş işaret; her tick duyurulmaz |
| ClubPairPrompt | clubA, clubB, prompt | Nötr bilgi grubu, başlık/boşluk/ayraç; iki kulüp adı sarabilir; solo kulüpler sen/rakip değildir |
| ChoiceOption / ChoiceGroup | id, label, selected, result?, disabled, onSelect | 5 seçenek gerçek veriden; default eşit; selected secondary+işaret; correct success+Doğru cevap; incorrect danger+Yanlış cevap; submitting tekrar seçimi engeller |
| PlayerSummary | name, birthYear?, position?, step?, totalSteps? | Hiyerarşi: isim sectionTitle, kalanlar caption; kaynak değerler doğrulanmış güncel futbol bilgisi kabul edilmez |
| CareerClueRow | index, club, country?, year?, newlyRevealed | Yeni ipucu secondary + metinle belirtilir; liste domain sırasını korur; ana bilgi bodyStrong, yıl caption |
| HiddenClueSummary | remainingCount, revealRuleLabel? | “3 kulüp daha açılacak”; bilgi satırı. Manuel açma mevcut kurallarda yoksa düğmeye dönüşmez |
| TransferClueGrid | year?, type?, fee?, country?, league? | Etiket/değer grid; büyük metinde 1 sütuna iner; bilinmeyen alan “Bilinmiyor”; fee=0 ise ücretsiz/bedelsiz domain anlamına göre gösterilir |
| CareerHistory | steps[], activeStep | CareerClueRow yeniden kullanılır; input/öneri/geçmiş kaydırılabilir; mevcut seçimi değiştirmez |
| RunResultSummary | score, bestScore?, isNewRecord, completedCount, endReason | Rekor yalnızca gerçek state ile; sonuç yazılı; Tekrar oyna primary, paylaş secondary/neutral; internet hatası oyun bitiş nedeni ile karıştırılmaz |
| LastQuestionReview | question, submittedAnswer?, correctAnswer?, failureReason | Nötr bilgi; yanlış cevap varsa danger; süre bitti ise “Süre doldu”; gönderilmemiş cevap uydurulmaz |
| MatchResultSummary | outcome, selfScore, opponentScore, names, elo?, delta?, mode | won/lost/draw/abandoned ayrı açık metinler; Elo sadece mevcut kuralların uygulandığı maçta; rövanş eylemleri gönderiliyor/bekliyor/gelen/reddedildi durumları |
| RoundHistoryList | rounds[], expanded? | Numara + kulüp çifti + puanı alan rol + doğru oyuncu; noAnswer açık; bütün turlara erişim; önemli adlar kesilmez |
| FactCard | title, content, sourceData? | Nötr bilgilendirme; amber uyarı gibi kullanılmaz; dışarıdan futbol gerçeği uydurulmaz; uzun metin sarar |
| ShareResultCard | mode, outcome, score, summaries, handle?, brandAsset | ResultCard görünümünün eylemsiz sunumu; gerçek logo; kişinin paylaşım tercihlerine göre nickname/handle; hesap/kurtarma kodları yok; native share iptali hata değildir |
| ComparisonOption | id, player, club?, birthYear?, value?, selected, revealed, outcome | İki eşit temel yüzey; gizli değer metinle açıklanır; reveal sonrası ölçüt ve birim görünür; correct success yazı+zemin çifti; green zemin üstünde purple text yok |
| WeeklyScoreSummary | teams[], totals[], runCounts[], lead | Toplamlar görünür; pay çubuğu yalnızca ek gösterim; toplam=0 ise 0/0 bölünmez; veri bekleme/hata durumu ayrı; marka rengi gerçek asset kaynaklı |
| SideSelector | teams, selectedTeamId?, locked, onSelect | Tek seçim; isim ve selected state; seçim olmadığında devamın neden beklediği açıklanır; lock haftalık domain kuralından gelir |

## Ekran eşlemesi

c05 → ModeRow / ScopeOption.
c06 → RunHUD + LivesIndicator + ClubPairPrompt + Field/SuggestionRow.
c07 → RunHUD + ClubPairPrompt + ChoiceGroup.
c08 → Player/Question başlığı + Field/SuggestionRow + HiddenClueSummary + CareerClueRow.
c09 → PlayerSummary + TransferClueGrid + Field/SuggestionRow + CareerHistory.
c10 → RunHUD + ComparisonOption ×2 + tek FeedbackBanner.
c11 → WeeklyScoreSummary + SideSelector; soru ekranında RunHUD + ComparisonOption ×2, club bilgisiyle.
c04 sonuç → MatchResultSummary + RoundHistoryList + isteğe bağlı FactCard + rövanş/ayrıl.
Tek oyun sonuçları → RunResultSummary + LastQuestionReview + FactCard + tekrar/paylaş.

## Ortak kurallar ve kanıt

Ana palet, Sora, radius ve spacing tokenları aynıdır. Solo eylemler rakip amberini devralmaz. Bağımsız oyuncu/takım seçimleri ve öneriler çerçeveli; sonuç ve kariyer listeleri gruplu okunur. Sonuç ekranındaki paylaşım kartı ekranın tamamı değildir; eylemler kart dışında kalır. Kaynakta büyük boş bloklar üretimde fixed height ile kopyalanmaz.

Pano örnek veriler içerir; örnek futbolcu/transfer istatistikleri yeniden doğrulanmadı. Gerçek içerik domain verisidir. HTML görsel örnek, RN uygulaması değildir. Native ekran okuyucu, büyük metin, klavye ve gerçek oyun akışı ayrıca test edilir. Kaynak armaları yeniden üretilmez. Sonuç/soru panoları birbirinden bağımsız durumları aynı inceleme grubunda gösterebilir; gerçek ekranda yalnızca aktif state render edilir.

## Kaynak incelemesi sonrası sadeleştirme

HUD salt okunur bilgileri inline; ModeRow gruplu satır; ClubPairPrompt bilgi grubu; FactCard başlık ve ayraçtır. Cevap/öneri kontrolleri ile paylaşım kartı ayrı yüzey olabilir. Ayrıntılar SLOP-REVIEW.md içinde.
