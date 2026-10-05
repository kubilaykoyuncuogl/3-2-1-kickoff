# Tasarım notları

## Akış (state machine, sunucu otorite)
```
LOBBY  → (2 oyuncu) → PICK_TEAMS → (ikisi ready) → COUNTDOWN(3s)
      → ROUND(15s) → ROUND_END(skor/cevap) → PICK_TEAMS | GAME_OVER(3 puan)
```
- ROUND içinde her tahmin sunucuya `guess(name)` olarak gider.
- Sunucu: normalize → oyuncu bul → iki takım setinde de var mı?
  - evet → +1, ROUND_END, doğru cevap ve diğer olası cevaplar gösterilir.
  - hayır → o oyuncuya `penalty_until = now+5s`; bu süre içinde gelen guess'ler reddedilir.
- 15 sn dolarsa puan yok, mümkün cevaplar gösterilir, yeni tur.

## Takım seçimi
- İki oyuncu da birer takım seçer. İkisi aynı takımı seçerse sunucu ikinciyi reddeder.
- Opsiyon: "rastgele takım" butonu; kesişimi boş olan takım çiftlerini sunucu engeller (en az 1 ortak oyuncu şartı).

## Açık sorular
- Oyuncu autocomplete: milyonlarca isim istemciye sığmaz. Seçenekler: (a) sunucu tarafı prefix arama (RPC), (b) sadece belli lig/seviye oyuncuları istemciye gömmek. Başlangıç: (a).
- Aynı isimli oyuncular (Mehmet Yılmaz x50): isim eşleşmesinde **herhangi biri** iki takımda da oynadıysa doğru say.
- "Oynamış" tanımı: datasetteki kayıt sayısı/kiralık dahil mi? Dataset incelenince karar.
