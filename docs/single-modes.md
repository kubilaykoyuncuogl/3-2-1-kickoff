# Tek oyunculu modlar

> Güncelleme 2026-10-05: günlük koşu, tablo ve kilit kaldırıldı. Her başlatma rastgele tohumlu yeni merdiven/soru seti; en iyi skor cihazda (`App.best`). Aşağısı ilk taslak.


İki mod da **merdiven**: basamaklar bilinen kulüplerle başlar, nadirleşir. Yanınca koşu biter, skor tabloya yazılır. Günlük koşu (herkese aynı merdiven, tarih tohumlu) + sınırsız pratik (tablosuz).

## Zorluk nasıl ölçülür (ikisi için ortak)
Basamak zorluğu = kulüp bilinirliği **+ kesişim büyüklüğü**. İki ünlü kulübün 1 ortak oyuncusu olabilir, bu nadir kulüp çiftinden daha zordur. Sıralama ölçütü:
- `fame(A)`, `fame(B)`: datasetten türetilir (oyuncu sayısı, lig seviyesi, kayıt yoğunluğu; `tools/build_index.py` üretir).
- `|A ∩ B|`: ortak oyuncu sayısı. Erken basamaklar ≥ 15, orta 5–14, geç 1–4.
- Bir koşuda bir kulüp en fazla bir kez (multi kuralıyla aynı).

## Mod 1 · Klasik merdiven
- İki kulüp çıkar, oyuncu adı yazılır (autocomplete, multi ile aynı kutu).
- Basamak süresi 20 sn'den başlar, her 5 basamakta 2 sn kısalır, 10 sn'de durur.
- 3 can. Yanlış tahmin = 1 can + 3 sn ceza. Süre bitmesi = 1 can. Can bitince koşu biter.
- Puan: basamak × 100 + kalan saniye × 5. Tablo: günlük ve tüm zamanlar.
- Doğrulama **sunucuda** (oyuncu→takım ilişkisi istemciye inmez). Çevrimdışı oynanamaz.

## Mod 2 · Blitz (5 isim)
- Ekranda A ve B kulübü + 5 isim: 2'si yalnız A'da, 2'si yalnız B'de, 1'i ikisinde. Doğru olana dokun.
- Klavye yok, sadece dokunma. Hız modu: soru süresi 8 sn'den başlar, her 5 soruda 1 sn kısalır, 3 sn'de durur.
- Yanlış = koşu biter (tek can) **veya** 3 can; karar: tek can, Blitz'in gerilimi bu. Kombo: art arda doğru ×1.1, ×1.2 … ×2.0 (yanlışta sıfırlanır).
- Çeldirici kuralı: 4 çeldirici gerçekten A'da ya da B'de oynamış olmalı, **ikisinde birden oynamamış** olmalı (set kontrolü). Ünlülük karışık: doğru cevap bazen en ünlü, bazen en silik.
- Dataset eksikliği riski: "yalnız A'da" dediğimiz oyuncu gerçekte B'de de oynamışsa oyun haksız olur. Çeldiriciler için yalnızca kayıt sayısı yüksek oyuncular kullanılır (eksik kayıt ihtimali düşük).
- Günlük paket: sunucu her gün N soruyu üretir, cevabı istemciye **hash** olarak gönderir (SHA-256(soru_id + oyuncu_id)); istemci çevrimdışı oynayabilir, skor gönderiminde sunucu yeniden doğrular. Tablo yalnızca sunucu onaylı skorları gösterir.

## Günlük görevler (v2)
Örnek: "Blitz'te 20 soru", "Klasik'te 8. basamak", "Süper Lig çiftinde 3 doğru". Ödül: kozmetik (tema, rozet). v1'de yalnızca tablo + paylaşılabilir sonuç kartı (Wordle tarzı: basamak sayısı ve emoji dizisi).

## Açık sorular
- Blitz'te can: tek mi, üç mü? (öneri: tek)
- Tablo kimliği: takma ad yeter mi, hesap gerekir mi? (öneri v1 takma ad + cihaz id, v2 hesap)
- Klasik'te "pas geç" hakkı: 1 pas, can harcamaz ama basamak puanı yok? (öneri: var, koşu başına 1)

## Kulüp tier'ları ve merdiven ilerleyişi (plan, 2026-10-05 akşam, Kubilay)
Kulüpler popülerliğe göre sıralanır (`clubs.fame`: oyuncu piyasa değeri toplamı + oyuncu sayısı; ileride lig katsayısı eklenebilir) ve tier'lara bölünür:
- **T1** ilk ~40 kulüp (Real, Barça, City, GS, FB, BJK…), **T2** sonraki ~120, **T3** sonraki ~400, **T4** gerisi (kesişimi olan).
Merdiven basamakları çift tipine göre ilerler, her tipten 2-3 basamak:
```
T1×T1 → T1×T2 → T2×T2 → T2×T3 → T3×T3 → T3×T4 → T4×T4
```
Her basamakta çift, o tier çiftinden rastgele; ortak oyuncu sayısı ≥ 2 (son tier'larda ≥ 1). Aynı kulüp koşuda bir kez.
Blitz aynı şemayla, soru başına ilerleme daha hızlı (her 4 soruda bir tip).
Uygulama: `index_service.py` `/ladder` ve `/blitz/pack` içinde `tier(club)` eşiği ve `pairs_for(tierA, tierB)` sorgusu; `pair_counts` + `clubs.fame` yeter, yeni index gerekmez.

## 14 tier (uygulandı 2026-10-06)
- Popülerlik puanı servis açılışında hesaplanır (`index_service._compute_tiers`): ücret 0,35 + gelen piyasa değeri 0,30 + yıldız (≥20 M€) 0,20 + oyuncu sayısı 0,10 + yıl aralığı 0,05 (hepsi log10) + lig katsayısı (5 büyük 1,0 · güçlü üst ligler 0,8 · diğer üst 0,6 · alt 0,4 · bilinmeyen 0,2).
- İlk üç tier kürate: `server/tiers_curated.txt` (tier|club_id|ad). T1 10 kulüp (Real, Barça, United, Liverpool, Bayern, Juve, PSG, Chelsea, City, Arsenal). Süper Lig kulüpleri bir tier yukarı (`BOOST_COMP`).
- Tier büyüklükleri: 10, 14, 30, 45, 65, 90, 130, 180, 250, 350, 480, 650, 900; T14 gerisi (4000. kulübe kadar). Amatörler merdivene girmez.
- İlerleyiş: 27 tip (1-1, 1-2, 2-2 … 14-14). Klasik: tip başına 1 basamak, %25 ihtimalle bir önceki tip (yumuşatma). Blitz: tip başına 2 soru. Ortak oyuncu alt sınırı: T1-5 ≥3, T6-9 ≥2, T10-14 ≥1. Dar kapsamda (5 büyük lig) boş tier'lar atlanır.
- `/tiers?tier=N` uç noktası tier içeriğini listeler (ayıklama için).
