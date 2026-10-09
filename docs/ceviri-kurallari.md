# Çeviri kural seti

3-2-1 Kickoff'un yazılarını başka dillere taşırken uyulacak kurallar. Çeviriyi yapan (insan ya da yapay zekâ), okuyup onaylayan
ve koda dokunan herkes için tek kaynak. Durum: **kural seti hazır, altyapı (bölüm 9) henüz yazılmadı** (2026-10-09).

## 1. Neden çeviri değil yerelleştirme

Oyun bir futbol sohbeti gibi konuşuyor: kısa, samimi, taraftarın diliyle. Kelime kelime çevrilmiş bir metin doğru olsa bile
"yabancı uygulama" kokar; oyuncu ilk ekranda bunu sezer ve oyunun bilgisine de güvenmez. Hedef, her dilde o ülkenin spor
sayfasında, maç yorumunda, tribünde duyulan dille yazmak.

Bunun pratik karşılığı:

- **Anlam çevrilir, cümle baştan kurulur.** Türkçe cümlenin kelime sırası, eki, noktalaması hedef dile taşınmaz.
- **Terim o ülkenin futbol dilinden seçilir**, sözlükten değil (bölüm 6).
- **Biçimler yerele uyar:** sayı, para, tarih, tırnak, büyük harf (bölüm 7).
- **Kültüre özgü espri ve deyim çevrilmez, yerine o dilde aynı işi gören söz konur** ya da hiç konmaz (bölüm 5.6).

## 2. Kapsam: diller

Tek lig seçimindeki 20 ülkenin resmî dilleri. 14 dil, 15 dosya:

| Kod | Dil | Ülkeler (20 ligden) | Yazı | Not |
|---|---|---|---|---|
| `tr` | Türkçe | Türkiye | Latin | **Asıl kaynak.** Her yeni yazı önce buraya girer |
| `en` | İngilizce | İngiltere, ABD | Latin | Tek dosya; "football" denir, "soccer" denmez |
| `es` | İspanyolca | İspanya, Arjantin | Latin | Tek dosya, iki kıyıda da doğal duran sözlerle (bölüm 6.2) |
| `it` | İtalyanca | İtalya, İsviçre | Latin | |
| `de` | Almanca | Almanya, Avusturya, İsviçre, Belçika | Latin | Tek dosya (ß kullanılır) |
| `fr` | Fransızca | Fransa, Belçika, İsviçre | Latin | |
| `nl` | Felemenkçe | Hollanda, Belçika | Latin | |
| `pt-PT` | Portekizce (Portekiz) | Portekiz | Latin | `pt-BR`'den ayrı dosya: futbol sözlüğü farklı |
| `pt-BR` | Portekizce (Brezilya) | Brezilya | Latin | |
| `el` | Yunanca | Yunanistan | Yunan | Yazı tipi gerekir (bölüm 8.1) |
| `ru` | Rusça | Rusya | Kiril | Yazı tipi gerekir |
| `uk` | Ukraynaca | Ukrayna | Kiril | Yazı tipi gerekir |
| `sr` | Sırpça | Sırbistan | **Latin** | Latin alfabesiyle yazılır (latinica) |
| `ro` | Rumence | Romanya | Latin | |
| `pl` | Lehçe | Polonya | Latin | |

Kapsam dışı: sağdan sola yazılan diller (Arapça, İbranice). Ekranların aynalanması ayrı bir iştir.

Bölgesel ayrım yalnızca Portekizcede yapılır. Almanca, Fransızca ve Felemenkçe için ülke başına ayrı dosya açılmaz;
İspanyolcada ayrım gerekirse (oyuncu geri bildirimi gelirse) `es-AR` sonradan eklenir.

Cihaz dili listede yoksa: `pt` → `pt-PT`, bilinmeyen dil → `en`. Çevirisi eksik anahtar `en`'e, o da yoksa `tr`'ye düşer.

## 3. Dosya düzeni

```
app/lang/
  tr.json                asıl kaynak
  en.json, es.json, …    aynı anahtarlar, aynı sıra
  countries/<kod>.json   ülke adları (bölüm 7.6)
  langs.json             dil listesi: kod, dilin kendi adı (Türkçe, English, Español, Ελληνικά, Русский)
  notes.json             anahtar başına bağlam (bölüm 4.4)
```

- Dil başına tek dosya. Ekran ekran bölünmez; anahtar önekleri (`match.`, `learn.`, `weekly.`) zaten öbekler.
- Anahtar adı İngilizce ve değişmez; anahtar adından anlam çıkarılmaz, bağlam `notes.json`'dan okunur.
- Kodda görünen metin yazılmaz. Yeni yazı = önce `tr.json`'a anahtar, sonra bütün dillere.

## 4. Yazı biçimi

### 4.1 Adlı boşluklar

Değişkenler adla yazılır: `{name}`, `{club}`, `{apps}`. Sıra numaralı `%s` / `%d` kullanılmaz.

```
tr  {name}, {club} formasıyla {apps} maçta {goals} gol attı
en  {name} scored {goals} goals in {apps} games for {club}
de  {name} erzielte in {apps} Spielen für {club} {goals} Tore
```

- Boşluk adları her dilde **aynı** kalır; çevrilmez, süslü parantezin içine dokunulmaz.
- Sıra serbesttir: her dil kendi cümlesini kurar.
- Kaynakta olan her boşluk çeviride de bulunur. Bir boşluğu atmak ancak `notes.json`'da "isteğe bağlı" yazıyorsa olur.

### 4.2 Çoğul

Sayıya göre değişen yazı tek anahtar altında biçimlerle tutulur. Biçim adları standarttır (`one`, `few`, `many`, `other`):

```
"career.summary": { "one": "{n} player named", "other": "{n} players named" }
```

Dil başına gereken biçimler:

| Diller | Biçimler |
|---|---|
| tr | `other` (tek biçim) |
| en, es, it, de, nl, pt-PT, pt-BR, el | `one`, `other` |
| fr | `one` (0 ve 1), `other` |
| ro | `one`, `few`, `other` |
| sr | `one`, `few`, `other` |
| ru, uk, pl | `one`, `few`, `many`, `other` |

Kurallar:
- Sayı içeren her cümle çoğul anahtarı sayılır; "nasılsa hep çoğul gelir" diye tek biçim yazılmaz.
- Hangi sayının hangi biçime düştüğünü çevirmen hesaplamaz; cihaz hesaplar. Çevirmen yalnızca o dilin istediği bütün biçimleri yazar.
- "1" yerine "bir" yazmak gibi özel durumlar için `one` biçimi kullanılır, sayı cümleye elle gömülmez.

### 4.3 Parça birleştirme yasağı

Cümle kodda parçalardan dizilmez. Her cümle, bütün hâliyle tek anahtardır.

Bugün bu kuralı çiğneyen ve **yeniden yazılacak** yerler:

| Anahtar | Bugünkü hâli | Sorun | Olması gereken |
|---|---|---|---|
| `fact.two_spells`, `fact.year`, `fact.years`, `fact.since`, `fact.and` | "%d-%d yıllarında" + "forması giydi" + " ve " | Cümle beş parçadan diziliyor; sıra ve ekler başka dilde tutmaz | Dönem sayısına göre bütün cümleler (tek dönem, iki dönem, hâlâ orada) |
| `match.others`, `match.possible` | "Diğerleri: " (kod sondaki `:` işaretini siliyor) | Kod metni kırpıyor | Başlık olarak iki noktasız ayrı anahtar |
| `match.more` | " … +%d oyuncu daha" (kod baştaki `…` işaretini siliyor) | Aynı | Kırpılmadan kullanılacak ayrı anahtar |
| `ac.used`, `ac.out_of_scope`, `sp.best`, `sp.record`, `sp.speed_bonus`, `match.waiting_paren` | "  · kullanıldı" gibi başında boşluk ve ayraç olan ekler | Ayraç ve boşluk metnin içinde; ek öne mi arkaya mı gelecek dile göre değişir | Ayraç kodda, metin yalın ("kullanıldı") |
| `net.failed_at`, `room.share_text`, `set.version` | "Odama gel: " + bağlantı | Sonuna ekleme varsayılıyor | `{link}` boşluklu bütün cümle |

Genel kural: **metnin başında ya da sonunda boşluk olmaz**; kod çeviriyi kırpmaz, kesmez, değiştirmez.

### 4.4 Bağlam notları

Çevirmen cümleyi nerede göründüğünü bilmeden çeviremez. `notes.json` her anahtar (ya da önek) için şunları taşır:

- **Nerede:** hangi ekran, hangi parça (düğme, başlık, bildirim, kart satırı). Ekran onay sayfasındaki numarayla (ör. "04 · 05A").
- **Uzunluk sınırı:** karakter olarak (bölüm 7.1).
- **Boşluklar:** her birinin ne olduğu ve örnek değeri (`{club}` = kulübün kısa adı, "Beşiktaş").
- **Ton notu:** gerekiyorsa ("sevinç", "kuru bilgi", "uyarı").

Notu olmayan anahtar çeviriye gönderilmez.

## 5. Cümle kurma kuralları

### 5.1 Değişkene ek ya da çekim yapıştırılmaz

Değişkenin (oyuncu, kulüp, ülke adı) yanına dilbilgisi eki gelmeyecek şekilde cümle kurulur.

- Türkçe: "{club}'lu oyuncu", "{name}'in" yazılmaz (ünlü uyumu ve kesme işareti tutmaz). → "{club} oyuncusu", "Cevap: {name}".
- Rusça, Ukraynaca, Lehçe, Sırpça, Yunanca, Rumence, Almanca: isimler hâle göre çekilir; değişken çekilemez. Cümle, değişken
  **yalın hâlde** kalacak biçimde kurulur. "за {club}" (kulüp adı çekilmeden okunabiliyorsa) ya da etiket biçimi: "Клуб: {club}".
- Tanımlık isteyen dillerde (it, fr, es, pt, de, el) kulüp adının önüne cinsiyete göre tanımlık koymak gerekiyorsa cümle
  tanımlık gerektirmeyecek biçimde yeniden kurulur ("al Milan / alla Roma" ikilemi yerine "Club: {club}" ya da "con {club}").

Yalın hâlde kurulamıyorsa etiket biçimine geçilir. Çirkin ama doğru, yanlış çekimden iyidir.

### 5.2 Oyuncuya hitap

Samimi tekil hitap, her dilde:

| Dil | Hitap | Dil | Hitap |
|---|---|---|---|
| tr | sen | pt-BR | você |
| en | you | el | εσύ |
| es | tú | ru | ты |
| it | tu | uk | ти |
| de | du | sr | ti |
| fr | tu | ro | tu |
| nl | je | pl | 2. tekil kişi (ty), "Pan/Pani" yok |
| pt-PT | tu | | |

Resmî hitap (Sie, vous, usted, Вы) hiçbir yerde kullanılmaz; hesap silme gibi ciddi ekranlar dâhil.

### 5.3 Cinsiyet

Oyuncunun cinsiyeti bilinmez. Oyuncuya dönük cümlelerde cinsiyet belli eden biçim kullanılmaz.

- Slav dillerinde geçmiş zaman fiili cinsiyet taşır ("ты выиграл / выиграла"). → İsim cümlesi: "Победа!", "Правильно", "Время вышло".
- Roman dillerinde sıfat uyumu ("¿Estás listo/lista?"). → "¿Todo listo?", "Prêt ?" yerine "C'est parti ?".
- Almanca: "Gewinner" yerine "Sieg!".
- Parantezli ya da eğik çizgili çift biçim ("listo/a", "gotowy(-a)") yazılmaz.

Futbolcular için cinsiyet sorunu yok: veri erkek futbolu. Futbolcu hakkındaki cümleler eril kurulur.

### 5.4 Uzunluk ve ritim

- Düğme ve başlık: fiil ya da isim, cümle değil. "Ara", "Tekrar", "Hazırım" gibi.
- Bildirim: tek bilgi, tek satır.
- "Biliyor muydun?" ve "Seni yakan soru": tam, doğal cümle; telgraf üslubu yok ("Hami Mandıralı, for Trabzonspor: 557 games" **yanlış**).
- Sığmayan metin üç noktayla kesilmez, kısaltma uydurulmaz; daha kısa söylenir. Kısa söylenemiyorsa sınır `notes.json`'da tartışılır.

### 5.5 Noktalama

- Uzun tire (—) kullanılmaz. Ayraç olarak orta nokta (" · ") kodda durur, metne yazılmaz.
- Ünlem yalnızca gerçek sevinçte, en çok bir tane. İspanyolcada açılış işaretleri de yazılır (¡ ¿).
- Başlık ve düğme sonunda nokta olmaz; tam cümleli açıklamalarda olur.
- Tırnak o dilin tırnağıdır: tr/en “ ”, de „ “, fr « » (içinde dar boşlukla), pl „ ”, ru/uk « », el « », ro „ ”, es/it/pt « » ya da “ ”.
- Yunancada soru işareti `;` karakteridir.
- Fransızcada `? ! : ;` öncesine dar bölünmez boşluk konur.

### 5.6 Kültüre özgü söz

- Deyim, tekerleme, dinî ya da yerel gönderme çevrilmez. Örnek: ana menünün altındaki "mükemmellik Allah'a mahsus". Her dilde
  ya o dilde aynı tevazu esprisini yapan yerleşik bir söz konur ya da satır yalnızca sürüm numarası olur. Hangi dilde ne
  konacağına o dili konuşan onaylayıcı karar verir; yapay zekâ taslağında bu satır **boş bırakılır ve işaretlenir**.
- "Nasıl oynanır" örneklerindeki isimler (Hami Mandıralı, Feyyaz Uçar, Hakan Şükür) o dilin oyuncusuna tanıdık isimlerle
  değişebilir. İsimler çeviri dosyasında değil, dile göre örnek listesinde tutulur; örnek doğru olmalıdır (gerçekten o iki
  kulüpte oynamış, gerçekten daha çok gol atmış).
- Argo ve küfür yok. Takım tutan dil yok: hiçbir kulüp, ülke ya da oyuncu hakkında yargı cümlesi kurulmaz.

## 6. Futbol sözlüğü

### 6.1 Oyunun kendi terimleri

Bu terimler bir dilde bir kez seçilir ve her yerde aynı kullanılır. Seçim `notes.json`'daki sözlüğe yazılır.

| Türkçe | Ne demek | Not |
|---|---|---|
| 3-2-1 Kickoff | Oyunun adı | **Çevrilmez**, hiçbir dilde |
| Klasik merdiven, Beşte Bir, Kariyer yolu, Sıradaki kulüp, O mu bu mu | Mod adları | Çevrilir; kısa, akılda kalır, o dilde oyun adı gibi durmalı. Kelime kelime çeviri aranmaz |
| Haftanın maçı | Haftalık etkinlik | Çevrilir |
| Tur | Online maçta tek soru | "Round" karşılığı |
| Koşu | Tek oyunculu bir deneme (başla → yan) | "Run" karşılığı; "oyun" ya da "maç" denmez, onlar başka şey |
| Can | Yanlış yapma hakkı | |
| Basamak | Merdivende soru sırası | |
| Elendi | Yanlış denenen isim bir daha denenemez | |
| Tolga mührü | Ekran onay sayfasındaki düğme | Oyunun içinde yok, çevrilmez |
| Kapsam | Hangi kulüplerden soru geleceği | |
| Dönem | Hangi on yıllar | |
| Taraf | Haftanın maçında tutulan kulüp | |

### 6.2 Futbol terimleri: başlangıç sözlüğü

Aşağıdaki karşılıklar başlangıç taslağıdır; her dilde o dili konuşan onaylayıcı doğrulamadan kesinleşmez.

| tr | en | es | it | de | fr | nl |
|---|---|---|---|---|---|---|
| maç | game / match | partido | partita | Spiel | match | wedstrijd |
| gol | goal | gol | gol | Tor | but | doelpunt |
| asist | assist | asistencia | assist | Vorlage | passe décisive | assist |
| kiralık | loan | cesión | prestito | Leihe | prêt | huur |
| bedelsiz | free transfer | libre | a parametro zero | ablösefrei | libre | transfervrij |
| kulüp | club | club | club | Verein | club | club |
| sezon | season | temporada | stagione | Saison | saison | seizoen |
| sarı kart | yellow card | tarjeta amarilla | cartellino giallo | Gelbe Karte | carton jaune | gele kaart |

| tr | pt-PT | pt-BR | el | ru | uk | sr | ro | pl |
|---|---|---|---|---|---|---|---|---|
| maç | jogo | jogo | αγώνας | матч | матч | utakmica | meci | mecz |
| gol | golo | gol | γκολ | гол | гол | gol | gol | gol |
| asist | assistência | assistência | ασίστ | голевая передача | гольова передача | asistencija | pasă decisivă | asysta |
| kiralık | empréstimo | empréstimo | δανεισμός | аренда | оренда | pozajmica | împrumut | wypożyczenie |
| bedelsiz | custo zero | sem custos | ελεύθερος | свободный агент | вільний агент | slobodan igrač | liber de contract | wolny transfer |
| kulüp | clube | clube | σύλλογος | клуб | клуб | klub | club | klub |
| sezon | época | temporada | σεζόν | сезон | сезон | sezona | sezon | sezon |
| sarı kart | cartão amarelo | cartão amarelo | κίτρινη κάρτα | жёлтая карточка | жовта картка | žuti karton | cartonaș galben | żółta kartka |

Dikkat edilecek ayrımlar:
- **es:** "cesión" İspanya'da, "préstamo" Latin Amerika'da yaygın. Tek dosyada "cedido" yerine iki tarafta da anlaşılan
  "a préstamo" tercih edilir; onaylayıcı karar verir.
- **pt-PT / pt-BR:** golo / gol, equipa / time, época / temporada, guarda-redes / goleiro, relvado / gramado. Bu yüzden iki dosya.
- **en:** "match" ve "game" ikisi de doğru; istatistikte "games" ("557 games"), etkinlikte "match" ("Match of the week").
- **"Forma giydi"** deyimi çevrilmez; "played for", "jugó en", "spielte für" gibi düz fiil kullanılır.

### 6.3 Çevrilmeyenler

- **Kulüp adları** veride nasılsa öyle kalır ("Bayern Munich", "Inter Milan"). Dile göre değiştirilmez.
- **Oyuncu adları** veride nasılsa öyle; Kiril ya da Yunan harfine çevrilmez.
- **Lig adları** özel isimdir (Premier League, La Liga, Süper Lig); çevrilmez.
- **Mevki kısaltmaları** (AM, RW, CF) veriden geldiği gibi gösterilir.
- **Ad araması Latin harfle yapılır.** Kiril ve Yunan klavyeli oyuncu için yazı kutusundaki ipucu bunu söylemelidir
  ("Latin harflerle yaz" karşılığı). Bu ipucu yalnızca `el`, `ru`, `uk` dosyalarında dolu olur.

## 7. Biçimler

### 7.1 Uzunluk sınırları

Türkçe kısa bir dildir. Almanca, Rusça, Yunanca, Lehçe ve Felemenkçe aynı şeyi yüzde 20-40 daha uzun söyler. Sınırlar
400 piksel genişlikte telefona göredir:

| Parça | Sınır | Örnek |
|---|---|---|
| Ana düğme | 18 karakter | "Online oyna" |
| Yarım genişlik düğme | 12 | "Oda kur" |
| Seçenek kutusu başlığı | 16 | "5 büyük lig" |
| Seçenek kutusu alt yazısı | 44, tek satır | "Yalnızca ülkelerin en üst ligleri" |
| Çip / rozet | 12 | "Puan 345" |
| Üst etiket (büyük harf) | 22 | "KULÜP KAPSAMI" |
| Bildirim | 40, en çok iki satır | "Luís Figo değil · elendi" |
| Mod adı | 18 | "Sıradaki kulüp" |
| Izgara altı ülke adı | 11 | "Yunanistan" |
| Nasıl oynanır paragrafı | 190 | |
| Sonuç kartı cümlesi | 120 | |

Sınır aşılırsa önce daha kısa söylenir; söylenemiyorsa ekran o dilde görüntülenip (bölüm 10) sığıp sığmadığına bakılır.

### 7.2 Sayılar

Binlik ve ondalık ayraç cihazın yerel kuralıyla yazılır; metnin içine elle sayı biçimi gömülmez.
`12.480` (tr, de, es, it, nl, pt, el, ro), `12,480` (en), `12 480` (fr, ru, uk, pl, sr).

### 7.3 Para

Tutar avro olarak ve kısaltılmış gösterilir. Simgenin yeri ve kısaltma dile göre:
`€23,3M` (tr), `€23.3m` (en), `23,3 Mio. €` (de), `23,3 M€` (fr, es, it, pt), `23,3 млн €` (ru, uk), `23,3 mln €` (pl, nl), `23,3 mil. €` (ro, sr), `23,3 εκατ. €` (el).

### 7.4 Yıl, dönem, süre

- Yıl aralığı: `2001-2005`; "yıllarında" gibi ekler cümlenin içinde çözülür (bölüm 4.3).
- On yıl etiketleri: `80'ler` (tr), `'80s` (en), `años 80` (es), `anni '80` (it), `80er` (de), `années 80` (fr), `jaren 80` (nl),
  `anos 80` (pt), `δεκαετία του '80` uzun olduğu için `'80` (el), `80-е` (ru), `80-ті` (uk), `80-e` (sr), `anii '80` (ro), `lata 80.` (pl).
- Saniye kısaltması: `sn` (tr), `s` (en, es, it, fr, nl, pt, ro, pl, sr), `Sek.` (de), `δ.` (el), `с` (ru, uk).
- Doğum yılı kısaltması `d. 1987`: her dilde o dilin kısaltması (`b. 1987`, `n. 1987`, `geb. 1987`, `né en 1987`, `р. 1987`, `ur. 1987`).

### 7.5 Büyük harf

Üst etiketler ve bazı başlıklar kodda büyük harfe çevrilir; çeviri dosyasına **normal yazılır**.

- Türkçe: i → İ, ı → I. Başka dilde Türkçe kuralı uygulanırsa "premier" → "PREMİER" olur (bölüm 8.2).
- Almanca: ß büyük harfte SS olur; kelime uzar.
- Yunanca: büyük harfte vurgu işareti düşer (ΑΓΩΝΑΣ, ΑΓΏΝΑΣ değil).
- Almancada isimlerin baş harfi cümle içinde de büyüktür; başka dilde başlık her kelimesi büyük yazılmaz (İngilizce dâhil:
  "Match of the week", "Match Of The Week" değil).

### 7.6 Ülke adları

Ülke adları elle çevrilmez; standart yerel ad listesinden (cihazın ve Unicode'un kullandığı liste) alınır.
Tartışmalı adlarda aynı liste izlenir, yorum katılmaz:

- Türkiye: İngilizcede "Türkiye".
- Kosova, Kuzey Makedonya, Çekya, Fildişi Sahili, Kongo DC: listedeki ad.
- Tarihî ülkeler (Yugoslavya, Sovyetler Birliği, Çekoslovakya, Zaire, Sırbistan-Karadağ) listede yoktur; elle yazılır ve onaylayıcı doğrular.
- Ukraynaca ve Rusça dosyalarda şehir ve kulüp adı çevrilmediği için "Kyiv / Kiev" tartışması doğmaz; veri "Dynamo Kyiv" der, öyle kalır.

## 8. Teknik kısıtlar

### 8.1 Yazı tipi

Oyunun yazı tipi Sora, Latin alfabesinin tamamını (Türkçe, Lehçe, Rumence, Sırpça Latin, Almanca dâhil) taşır;
**Kiril ve Yunan harflerini taşımaz** (dosyada denetlendi). `ru`, `uk` ve `el` için bu alfabeleri taşıyan, Sora'ya yakın
duruşlu ikinci bir yazı tipi gerekir. Seçilmeden bu üç dil yayına çıkamaz; harfler cihazın varsayılan yazı tipine düşer ve
tasarım bozulur.

### 8.2 Kodda düzeltilecekler

Çeviriden bağımsız, kodun yerele duyarsız olduğu yerler:

- Büyük harfe çevirme her yerde Türkçe kuralıyla yapılıyor (`toLocaleUpperCase("tr")`); etkin dile göre yapılmalı.
- Sayı biçimi yalnızca Türkçe ve İngilizceyi tanıyor (`tr-TR` / `en-US`); etkin dile göre olmalı.
- Para biçimi (`€23,3M`) tek kalıp; bölüm 7.3'e göre dil başına olmalı.
- Çeviriyi kırpan satırlar (`.trim().replace(...)`) kaldırılmalı (bölüm 4.3).
- Eksik anahtar Türkçeye düşüyor; önce İngilizceye düşmeli.

### 8.3 Sunucu

Sunucu yazı göndermez; hata için anahtar (`err.*`), bilgi kartı için yapılandırılmış veri gönderir, cümleyi istemci kurar.
Bu böyle kalır. Sunucudan gelen ülke adı İngilizce kaynak addır; istemci yerel ada çevirir.

## 9. Altyapıda yapılacaklar (sırayla)

1. Çeviri işlevine adlı boşluk ve çoğul desteği; `tr.json` ve `en.json`'un yeni biçime taşınması.
2. Bölüm 4.3'teki parçalı anahtarların bütün cümlelere çevrilmesi.
3. Ülke adlarının `countries/` altına ayrılması.
4. `notes.json`: bütün anahtarlar için bağlam ve sınır.
5. Denetim aracı (`tools/check_lang.py`): bölüm 10'daki bütün otomatik kurallar.
6. Bölüm 8.2'deki kod düzeltmeleri.
7. İngilizcenin baştan, doğal cümlelerle yazılması.
8. Cihaz dilini algılama; Ayarlar'da dil listesi.
9. Kiril ve Yunan için yazı tipi seçimi.
10. Diller: önce Latin alfabeli olanlar, sonra `ru`, `uk`, `el`.

## 10. Kalite süreci

Bir dil şu dört kapıdan geçmeden yayına çıkmaz:

**1. Otomatik denetim** (her değişiklikte, araç hata verirse yayın durur)
- Bütün anahtarlar var, fazla anahtar yok.
- Boşluk adları kaynakla aynı.
- Çoğul anahtarında o dilin istediği bütün biçimler dolu.
- Baş ve son boşluk yok; uzun tire yok; kaynakta olmayan satır sonu yok.
- Uzunluk sınırı aşılmamış (`notes.json`).
- Kaynakla birebir aynı kalan (çevrilmemiş) satır yok; özel isim olanlar notta işaretli.

**2. Taslak**
Taslağı yapay zekâ yazar: bu belge, `notes.json` ve Türkçe ile İngilizce kaynak birlikte verilir. Emin olunmayan her satır
işaretlenir; tahmin yürütülüp geçilmez.

**3. Ana dili konuşan onaylayıcı**
Her dilde, futbol izleyen ve o dili ana dili olarak konuşan bir kişi bütün satırları okur. Araç: ekran onay sayfasının benzeri
(satır satır kaynak, çeviri, düzeltme kutusu). Onaylayıcının işi doğruluk değil **doğallık**: "bunu bir spor sitesinde okusam
garip gelir mi?"

**4. Ekran taraması**
Bütün ekranların o dilde görüntüsü alınır (`tools/all_shots.py --lang <kod>`); taşan, kesilen, iki satıra düşen yazı aranır.
Klavye açık ekranlar (kategori 14) özellikle: en dar alan orası.

Sonrası: yayındaki bir dilde yeni anahtar eklendiğinde aynı dört kapı yalnızca o anahtar için işler. Çevirisi gelmemiş
anahtar İngilizce görünür; yayını durdurmaz ama denetim aracı listeler.

## 11. Kısa kontrol listesi (çevirmen için)

- [ ] Cümleyi çevirmedim, o dilde yeniden kurdum.
- [ ] Süslü parantez içlerine dokunmadım; hepsi yerinde.
- [ ] Değişkenin yanına ek, tanımlık ya da çekim gelmiyor.
- [ ] Oyuncuya samimi tekil hitap ettim; cinsiyet belli eden biçim yok.
- [ ] Sayı içeren cümlede dilin bütün çoğul biçimlerini yazdım.
- [ ] Terimleri sözlükten aldım; aynı şeye iki ayrı kelime kullanmadım.
- [ ] Kulüp, oyuncu, lig adlarına ve oyunun adına dokunmadım.
- [ ] Uzunluk sınırının içindeyim; üç noktayla kesmedim.
- [ ] Tırnak, soru işareti ve boşluklar o dilin kuralında.
- [ ] Emin olmadığım satırı işaretledim.
