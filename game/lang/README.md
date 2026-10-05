# Dil paketleri

Her dil bir dosya: `tr.json`, `en.json`, … (anahtar → metin). Kodda `T.t("anahtar")` ile çağrılır (`game/scripts/t.gd`).

**Yeni dil eklemek:** `tr.json`'u kopyala (ör. `de.json`), değerleri çevir. Başka bir şey gerekmez; Ayarlar > Dil'de kendiliğinden çıkar.

Kurallar:
- Anahtarları değiştirme, sadece değerleri çevir. `%d`, `%s`, `%.1f` yer tutucuları aynı sayıda ve aynı sırada kalmalı.
- Baştaki/sondaki boşluklar ve `·` ayraçları bilerek var (metinler birleştiriliyor), koru.
- Eksik anahtar Türkçeye düşer; yarım çeviri oyunu bozmaz.
- Kulüp ve oyuncu adları çevrilmez, veriden gelir.
- `err.*` anahtarları sunucunun gönderdiği hata kodlarıdır.

Kontrol: `python3 tools/check_lang.py` eksik anahtarları ve yer tutucu uyuşmazlıklarını listeler.
