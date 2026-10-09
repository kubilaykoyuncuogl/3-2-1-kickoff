#!/usr/bin/env python3
"""Kite geçen ekranların önce / sonra karşılaştırması: tek, kendi başına açılan HTML dosyası (görüntüler içine gömülü).
Dosya e-posta / mesajla gönderilir; bakan kişi yorumlarını sayfada yazar, "Yorumları indir" ile metin dosyası olarak geri yollar.
(claude.ai sayfasında paylaşım yetkisi yüzünden notlar kaydolmuyordu; bu dosya hiçbir hesaba ya da sunucuya bağlı değil.)

  python3 tools/review_page/build_local.py [--out ~/Downloads/Kickoff-Kit-Onay.html]
Önce: screenshots/<tema>/…  (canlıdaki hal)   Sonra: screenshots/kit/<tema>/…  (tools/all_shots.py --out screenshots/kit)"""
import argparse, base64, io, json, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(pathlib.Path.home() / "Downloads" / "Kickoff-Kit-Onay.html")); A = ap.parse_args()

# (bölüm, kimlik, başlık, dosya, değişenler, aynı kalan)
ITEMS = [
 ("Ana sayfa", "home", "Ana menü", "01-acilis-menu/01A-ana-menu.png",
  ["“Tek oyna” amberden soluk mora geçti.", "“Online oyna”da çıplak 1000 yerine ayraç, “Elo 1000” ve ok.",
   "Haftanın maçı kartı üç katlı: üstte başlık, mod ve kim önde; ortada kulüp renkli bant; altta açıklama ve “Tarafını seç”.",
   "Ayarlar düğmesi dişlili ve oklu satır oldu.", "Sağ üstte BETA rozeti gitti; baş harfli yuvarlak ve takma ad geldi."], "Logo ve alt satır aynı."),
 ("Ana sayfa", "home-none", "Ana menü: haftanın maçı yok", "01-acilis-menu/01B-ana-menu-haftanin-maci-yok.png",
  ["Aynı düğmeler; haftanın maçı olmayınca Ayarlar satırı hemen altta."], ""),
 ("Ana sayfa", "home-two", "Ana menü: iki haftanın maçı", "01-acilis-menu/01C-ana-menu-iki-mac.png",
  ["İki maç alt alta iki kart; her biri kendi modunu yazıyor (o mu bu mu, kariyer yolu)."], "Eski görüntüsü yok: bu ekran eski görüntüler çekildikten sonra eklendi."),
 ("Giriş", "nick", "Takma ad: boş", "01-acilis-menu/02A-takma-ad-bos.png",
  ["Yazı kutusunun üstünde kalıcı “Takma ad” etiketi.", "Başlık ve açıklama büyüdü.", "Boşken “Devam” düğmesi soluk mor yerine gri (basılamaz olduğu belli).", "Kutudaki yazı kalından normale indi."], ""),
 ("Giriş", "nick-filled", "Takma ad: yazılı", "01-acilis-menu/02B-takma-ad-yazili.png",
  ["Aynı düzen; ad yazılınca “Devam” mor olur."], ""),
 ("Giriş", "nick-kb", "Takma ad: klavye açık", "14-klavye-acik/01-takma-ad.png",
  ["Etiket, kutu ve düğme klavyenin üstünde sığıyor."], ""),
 ("Ayarlar", "settings", "Ayarlar", "02-ayarlar-hesap/01A-ayarlar.png",
  ["Satırlar yükseldi (dokunması kolay), yazılar büyüdü.", "Anahtarlar büyüdü; açıkken mor.", "Tema ve dil seçiminde seçili olan siyah dolgu yerine mor çerçeveli.", "Üstteki başlık normal yazımla ve daha büyük."],
  "Satırların sırası ve içeriği aynı; hâlâ tek ekrana sığıyor."),
 ("Ayarlar", "settings-linked", "Ayarlar: hesap bağlı", "02-ayarlar-hesap/01B-ayarlar-hesap-bagli.png",
  ["Üstteki hesap kartı aynı kalıpta; bağlıyken mor."], ""),
 ("Hesap", "acct-guest", "Hesap: misafir", "02-ayarlar-hesap/02A-hesap-misafir.png",
  ["“Hesabım var” beyaz çerçeveli düğmeden soluk mor ikincil düğmeye geçti.", "Açıklama yazıları büyüdü."], "“Hesap oluştur” ana eylem olarak mor kaldı."),
 ("Hesap", "acct-linked", "Hesap: bağlı", "02-ayarlar-hesap/02B-hesap-bagli.png",
  ["Takma ad başlığı küçüldü (kit ölçüsü); rozetler ve Elo aynı yerde."], "Çıkış ve silme düğmeleri altta."),
 ("Hesap", "acct-recovery", "Hesap: kurtarma kodu", "02-ayarlar-hesap/02C-hesap-kurtarma-kodu.png",
  ["Kod kutusu amberden nötr (beyaz) yüzeye geçti: amber artık yalnızca rakibin rengi."], "“Kopyala” ve “Kaydettim” aynı."),
 ("Hesap", "acct-code", "Hesap: cihaz kodu", "02-ayarlar-hesap/02D-hesap-cihaz-kodu.png",
  ["Kod ve süre aynı yerde; başlık ve açıklama kit ölçüsünde."], ""),
 ("Hesap", "have-code", "Hesabım var: kod", "02-ayarlar-hesap/02E-hesabim-var-kod.png",
  ["Sekmelerde seçili olan siyah dolgu yerine mor çerçeveli.", "Kutunun üstünde etiket."], ""),
 ("Hesap", "have-recovery", "Hesabım var: kurtarma", "02-ayarlar-hesap/02F-hesabim-var-kurtarma.png",
  ["Kutuların içindeki soluk yazı (“Takma adın”, “Kurtarma kodun”) kutunun üstüne kalıcı etiket olarak çıktı."], ""),
 ("Hesap", "have-error", "Hesabım var: hatalı kod", "02-ayarlar-hesap/02G-hesabim-var-hatali-kod.png",
  ["Hata bildirimi çerçevesiz, sola yaslı, pembe zeminde."], ""),
 ("Hesap", "acct-delete", "Hesap silme onayı", "02-ayarlar-hesap/02H-hesap-silme-onayi.png",
  ["Uyarı aynı bildirim kalıbında, sola yaslı."], "“Evet, sil” ve “Vazgeç” aynı."),
 ("Hesap", "have-code-kb", "Hesabım var: kod, klavye açık", "14-klavye-acik/02A-hesabim-var-kod.png", ["Klavye açıkken üst başlık gizli; sekmeler, kutu ve düğme sığıyor."], ""),
 ("Hesap", "have-recovery-kb", "Hesabım var: kurtarma, klavye açık", "14-klavye-acik/02B-hesabim-var-kurtarma.png", ["İki etiketli kutu ve düğme klavyenin üstünde sığıyor."], ""),
]

def img(path: pathlib.Path) -> str:
    if not path.exists(): return ""
    buf = io.BytesIO(); Image.open(path).convert("RGB").save(buf, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

data = []
for sec, id_, title, f, changes, kept in ITEMS:
    data.append({"sec": sec, "id": id_, "title": title, "changes": changes, "kept": kept,
                 "old": {t: img(ROOT / "screenshots" / t / f) for t in ("acik", "koyu")},
                 "neu": {t: img(ROOT / "screenshots" / "kit" / t / f) for t in ("acik", "koyu")}})
    assert data[-1]["neu"]["acik"], f
tpl = (pathlib.Path(__file__).parent / "local_template.html").read_text()
out = pathlib.Path(A.out).expanduser()
out.write_text(tpl.replace("__ITEMS__", json.dumps(data, ensure_ascii=False)))
print(f"yazıldı: {out}  ({out.stat().st_size / 1e6:.1f} MB, {len(data)} ekran)")
