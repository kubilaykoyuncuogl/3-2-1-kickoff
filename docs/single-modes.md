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

## Üç yeni mod (uygulandı 2026-10-06)
Ortak: **ünlü oyuncu havuzu** (`index_service._build_famous`, 5000 oyuncu). Şart: üst liglerde ≥120 maç, lig maçlarının ≥%60'ı üst liglerde, doğum ≥1965. Ün puanı: 5 büyük lig maçı ×1 ve golü ×3, Süper Lig maçı ×0,6 ve golü ×1,8, diğer üst ligler ×0,4 / ×1,2, zirve piyasa değeri (M€) ×3, oynadığı T1-T3 kulüp sayısı ×80. Global odak; Türkler kendi sırasında girer (Burak Yılmaz #192, Çalhanoğlu #197, Şükür #232). Paketler ünlüden az ünlüye üç kovadan çekilir (0-300, 300-1200, 1200-5000).
İstatistikler `tools/build_stats.py` ile gelir (`player_stats` tablosu: maç, gol, asist, kart, penaltı, tek sezon en çok gol, 5 büyük lig ve Süper Lig kırılımı). Kaynak her oyuncuda tüm kariyeri kapsamayabilir.

- **Kariyer yolu** (`career`): kulüpler ilk kulüpten başlayıp 4 sn arayla tek tek açılır, oyuncu adı yazılır. Puan 100 + gizli kalan kulüp × 60. Yanlış = 1 can, kilit yok. Hepsi açıldıktan 12 sn sonra süre dolar (1 can, cevap gösterilir). 3 can. Kiralık dönüşleri yoldan atılır.
- **Sıradaki kulüp** (`chain`): oyuncu adı, doğum yılı ve mevkisi verilir. Önce ilk profesyonel kulübü, sonra her hamlenin hedefi tahmin edilir; ipucu yıl + tür (Satış / Kiralık / Bedelsiz-açıklanmadı) + varsa bedel. Adım başına 20 sn ve tek deneme: doğru 100 + kalan saniye × 5; yanlış ya da süre = 1 can, doğrusu gösterilir ve zincir devam eder. 3 can. Yalnızca tüm kulüpleri T10 ve üstü olan oyuncular (silik kulüp tahmin ettirilmez).
- **O mu bu mu** (`versus`): iki futbolcu, bir kategori; değeri büyük olana dokun. Doğruysa o kalır (değeri görünür), karşısına yenisi gelir. Yanlış ya da süre = koşu biter. Puan 100 + hız bonusu (kalan saniye × 10); süre 9 sn'den 4 sn'ye iner. Kalan oyuncu listenin ilk 3'üne girince ya da 5 tur üst üste kalınca **yeni kategori**. Rakip %75 yakın sıradan (±120) seçilir. Havuz ilk 2000 ünlü. Kategoriler (12): gol, maç, asist, sarı kart, kırmızı kart, tek sezon gol, 5 büyük lig golü, penaltı golü, zirve piyasa değeri, en pahalı transfer, toplam bonservis, kulüp sayısı. Yeni kategori = `CATS`'e bir satır + `cat.<anahtar>` çevirisi.

Sunucu: `game.gd` (`single_guess` kariyer, `single_team` zincir, `single_answer` o mu bu mu), paketler `/career/pack`, `/chain/pack`, `/versus/pack` (cevap alanları `_` ile başlar, istemciye gitmez). İstemci: `screens/single_base.gd` + `career_play.gd`, `chain_play.gd`, `versus_play.gd`. Bu modlarda kulüp kapsamı seçimi yok.

## Dönem seçimi
Her modda oyundan önce dönem sorulur: Tümü ya da bir / birkaç on yıl (80'ler … 20'ler). Tümü seçiliyken bir on yıla basınca yalnız o seçilir, sonraki basışlar aç/kapa; hiçbiri kalmazsa Tümü'ye döner. Oyuncu havuzu seçilen on yıllarda en az bir maça çıkmış oyunculardan kurulur: Klasik ve Beşte Bir'de kulüp çiftinin ortak oyuncuları o döneme göre sayılır ve öneriler yalnızca o dönemin oyuncularını gösterir; Kariyer yolu, Sıradaki kulüp ve O mu bu mu ünlü havuzunun o döneme süzülmüş halini kullanır (Tümü'de 1965 sonrası doğumlular, dönem seçilince doğum sınırı yok). Dar seçimlerde (ör. 5 büyük lig + 80'ler) merdiven kısalabilir.
