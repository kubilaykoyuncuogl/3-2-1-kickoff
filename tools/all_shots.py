#!/usr/bin/env python3
"""Oyundaki bütün ekranların görüntüsünü kategori klasörlerine, sıra numarasıyla çeker. Aynı ekranın halleri 1, 1B, 1C… diye adlanır.

  .venv/bin/python tools/all_shots.py [--theme acik|koyu|ikisi] [--lang tr] [--only 04] [--out screenshots] [--jobs 4]
  → <out>/<tema>/<NN-kategori>/<numara>-<ad>.png   (ör. screenshots/acik/04-mac/1G-uyari-ayni-takim.png)

Önce yerel sunucular çalışıyor olmalı: ./run_local.sh  (Expo web 8081 + oyun sunucusu 9081).
Ekran durumları geliştirme modundaki hazır durumlardan gelir (app/src/dev/mocks.ts, ?mock=…); öneri listeleri gerçek sunucudan.
Yeni ekran / durum eklenince aşağıdaki SHOTS listesine ve gerekiyorsa mocks.ts'e ekle."""
import argparse, asyncio, json, pathlib, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--theme", default="ikisi"); ap.add_argument("--lang", default="tr"); ap.add_argument("--only", default="")
ap.add_argument("--out", default=str(ROOT / "screenshots")); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--size", default="400x880")
A = ap.parse_args()
L = json.loads((ROOT / "app" / "lang" / f"{A.lang}.json").read_text())
T = lambda k: L[k]

# (kategori, numara, ad, yol, parametreler, eylemler, bekleme sn). Eylem: ("tap", metin, sn) | ("type", metin, sn)
SHOTS = [
    # 01 açılış ve menü
    ("01-acilis-menu", "1", "ana-menu", "/", {"mock": "weekly_fresh"}, [], 4),
    ("01-acilis-menu", "1B", "ana-menu-haftanin-maci-yok", "/", {"mock": "weekly_none"}, [], 4),
    ("01-acilis-menu", "2", "takma-ad-bos", "/nickname", {"nick": ""}, [], 3),
    ("01-acilis-menu", "2B", "takma-ad-yazili", "/nickname", {"nick": ""}, [("type", "kubilay", 2)], 3.5),
    # 02 ayarlar ve hesap
    ("02-ayarlar-hesap", "1", "ayarlar", "/settings", {}, [], 3),
    ("02-ayarlar-hesap", "1B", "ayarlar-hesap-bagli", "/settings", {"mock": "linked"}, [], 4),
    ("02-ayarlar-hesap", "2", "hesap-misafir", "/account", {}, [], 3),
    ("02-ayarlar-hesap", "2B", "hesap-bagli", "/account", {"mock": "linked"}, [], 4),
    ("02-ayarlar-hesap", "2C", "hesap-kurtarma-kodu", "/account", {"mock": "acct_recovery"}, [], 4),
    ("02-ayarlar-hesap", "2D", "hesap-cihaz-kodu", "/account", {"mock": "linked,acct_code"}, [], 4),
    ("02-ayarlar-hesap", "2E", "hesabim-var-kod", "/account", {}, [("tap", T("acct.have"), 2)], 3.5),
    ("02-ayarlar-hesap", "2F", "hesabim-var-kurtarma", "/account", {}, [("tap", T("acct.have"), 2), ("tap", T("acct.tab_recovery"), 2.8)], 4),
    ("02-ayarlar-hesap", "2G", "hesabim-var-hatali-kod", "/account", {"mock": "acct_error"}, [("tap", T("acct.have"), 2)], 4),
    ("02-ayarlar-hesap", "2H", "hesap-silme-onayi", "/account", {"mock": "linked"}, [("tap", T("acct.delete"), 3.2)], 4.5),
    # 03 online giriş
    ("03-online", "1", "online-menu", "/online", {}, [], 3.5),
    ("03-online", "1B", "online-menu-lig-donem-sure", "/online", {"scope": "TR1", "era": "6", "round": "30"}, [], 3.5),
    ("03-online", "1C", "online-menu-5-buyuk-lig", "/online", {"scope": "big5", "era": "16", "round": "10"}, [], 3.5),
    ("03-online", "2", "rakip-araniyor", "/online", {"mock": "online_search", "scope": "TR1", "era": "6"}, [], 3.5),
    ("03-online", "3", "oda-kuruldu-bekleniyor", "/online", {"mock": "online_room"}, [], 3.5),
    ("03-online", "4", "odaya-katil", "/online", {}, [("tap", T("online.join"), 2)], 3.5),
    ("03-online", "4B", "odaya-katil-kod-yazili", "/online", {}, [("tap", T("online.join"), 2), ("type", "zidane", 2.8)], 4),
    ("03-online", "4C", "odaya-katil-oda-bulunamadi", "/online", {"mock": "join_error"}, [("tap", T("online.join"), 2), ("type", "xyz", 2.4)], 4),
    # 04 maç
    ("04-mac", "1", "takim-secimi-bos", "/match", {"mock": "pick_empty"}, [], 3),
    ("04-mac", "1B", "takim-secimi-oneriler", "/match", {"mock": "pick_empty"}, [("type", "gala", 2)], 4),
    ("04-mac", "1C", "takim-secimi-hizli-secenekler", "/match", {"mock": "pick_quick"}, [], 3),
    ("04-mac", "1D", "takim-secildi-degistir-hazirim", "/match", {"mock": "pick_chosen"}, [], 3),
    ("04-mac", "1E", "hazir-rakip-bekleniyor", "/match", {"mock": "pick_ready"}, [], 3),
    ("04-mac", "1F", "rakip-hazir-seni-bekliyor", "/match", {"mock": "pick_oppready"}, [], 3),
    ("04-mac", "1G", "sure-azaldi", "/match", {"mock": "pick_late"}, [], 3),
    ("04-mac", "1H", "uyari-ayni-takim", "/match", {"mock": "pick_clash"}, [], 2.4),
    ("04-mac", "1I", "uyari-takim-kullanildi", "/match", {"mock": "pick_used"}, [], 2.4),
    ("04-mac", "1J", "uyari-kapsam-disi", "/match", {"mock": "pick_scope"}, [], 2.4),
    ("04-mac", "1K", "rakibin-baglantisi-koptu", "/match", {"mock": "pick_away"}, [], 3),
    ("04-mac", "2", "geri-sayim", "/match", {"mock": "countdown"}, [], 1.6),
    ("04-mac", "3", "takimlar-aciklandi", "/match", {"mock": "reveal"}, [], 1.6),
    ("04-mac", "4", "tur-bos", "/match", {"mock": "round"}, [], 3),
    ("04-mac", "4B", "tur-oneriler", "/match", {"mock": "round"}, [("type", "snei", 2)], 4),
    ("04-mac", "4C", "tur-son-saniyeler", "/match", {"mock": "round_hot"}, [], 2.2),
    ("04-mac", "4D", "tur-yanlis-tahmin-kilit", "/match", {"mock": "round_wrong_me"}, [], 2.2),
    ("04-mac", "4E", "tur-rakip-yanlis", "/match", {"mock": "round_wrong_opp"}, [], 2.2),
    ("04-mac", "4F", "tur-rakip-koptu", "/match", {"mock": "round_away"}, [], 2.2),
    ("04-mac", "4G", "tur-30-saniye", "/match", {"mock": "round_30"}, [], 2.5),
    ("04-mac", "5", "tur-sonu-sen-bildin", "/match", {"mock": "end_me"}, [], 2),
    ("04-mac", "5B", "tur-sonu-rakip-bildi", "/match", {"mock": "end_opp"}, [], 2),
    ("04-mac", "5C", "tur-sonu-kimse-bilemedi", "/match", {"mock": "end_nobody"}, [], 2),
    ("04-mac", "5D", "tur-sonu-rakip-takim-secmedi", "/match", {"mock": "end_pick_win"}, [], 2),
    ("04-mac", "5E", "tur-sonu-sen-takim-secmedin", "/match", {"mock": "end_pick_lose"}, [], 2),
    ("04-mac", "6", "ortak-oyuncu-yok", "/match", {"mock": "no_common"}, [], 1.6),
    ("04-mac", "7", "mac-sonu-kazandin", "/match", {"mock": "over_win"}, [], 3),
    ("04-mac", "7B", "mac-sonu-kaybettin", "/match", {"mock": "over_lose"}, [], 3),
    ("04-mac", "7C", "mac-sonu-berabere", "/match", {"mock": "over_draw"}, [], 3),
    ("04-mac", "7D", "mac-sonu-rakip-ayrildi", "/match", {"mock": "over_left"}, [], 2.2),
    ("04-mac", "7E", "mac-sonu-rovans-bekleniyor", "/match", {"mock": "over_rematch_wait"}, [], 3),
    ("04-mac", "7F", "mac-sonu-rakip-rovans-istiyor", "/match", {"mock": "over_opp_rematch"}, [], 3),
    # 05 tek oyna girişi
    ("05-tek-oyna", "1", "mod-menusu", "/single", {}, [], 3),
    ("05-tek-oyna", "1B", "mod-menusu-en-iyi-skorlar", "/single", {"best": "640"}, [], 3),
    ("05-tek-oyna", "2", "kapsam-donem-klasik", "/single/setup", {"mode": "ladder"}, [], 3),
    ("05-tek-oyna", "2B", "kapsam-donem-lig-secili", "/single/setup", {"mode": "blitz", "scope": "ES1", "era": "12"}, [], 3),
    ("05-tek-oyna", "2C", "kapsam-donem-kariyer-notu", "/single/setup", {"mode": "career", "scope": "TR1", "era": "2"}, [], 3),
    ("05-tek-oyna", "3", "yukleniyor", "/single/play", {"mode": "ladder", "mock": "single_fail"}, [], 1.5),
    ("05-tek-oyna", "3B", "sunucudan-cevap-gelmedi", "/single/play", {"mode": "ladder", "mock": "single_fail"}, [], 4.5),
    # 06 klasik merdiven
    ("06-klasik-merdiven", "1", "basamak", "/single/play", {"mode": "ladder", "mock": "ladder_play"}, [], 3),
    ("06-klasik-merdiven", "1B", "oneriler", "/single/play", {"mode": "ladder", "mock": "ladder_play"}, [("type", "zid", 2)], 4),
    ("06-klasik-merdiven", "1C", "yanlis-tahmin", "/single/play", {"mode": "ladder", "mock": "ladder_wrong"}, [], 3),
    ("06-klasik-merdiven", "1D", "sure-doldu-can-gitti", "/single/play", {"mode": "ladder", "mock": "ladder_timeout"}, [], 3),
    ("06-klasik-merdiven", "2", "sonuc-karti-rekor", "/single/play", {"mode": "ladder", "mock": "ladder_over"}, [], 3),
    ("06-klasik-merdiven", "2B", "sonuc-karti-uzun-liste", "/single/play", {"mode": "ladder", "mock": "ladder_over_many", "best": "2400", "scope": "top", "era": "28"}, [], 3),
    # 07 beşte bir
    ("07-beste-bir", "1", "soru", "/single/play", {"mode": "blitz", "mock": "blitz_play"}, [], 3),
    ("07-beste-bir", "2", "sonuc-karti", "/single/play", {"mode": "blitz", "mock": "blitz_over", "best": "460", "scope": "top", "era": "28"}, [], 3),
    # 08 kariyer yolu
    ("08-kariyer-yolu", "1", "ilk-kulup", "/single/career", {"mock": "career_first"}, [], 3),
    ("08-kariyer-yolu", "1B", "kulupler-aciliyor", "/single/career", {"mock": "career_mid"}, [], 3),
    ("08-kariyer-yolu", "1C", "oneriler", "/single/career", {"mock": "career_mid"}, [("type", "cris", 2)], 4),
    ("08-kariyer-yolu", "1D", "yanlis-tahmin", "/single/career", {"mock": "career_wrong"}, [], 3),
    ("08-kariyer-yolu", "1E", "dogru-siradaki-oyuncu", "/single/career", {"mock": "career_right"}, [], 3),
    ("08-kariyer-yolu", "2", "sonuc-karti", "/single/career", {"mock": "career_over"}, [], 3),
    # 09 sıradaki kulüp
    ("09-siradaki-kulup", "1", "ilk-kulup-sorusu", "/single/chain", {"mock": "chain_first"}, [], 3),
    ("09-siradaki-kulup", "1B", "sonraki-adim-ipuclari", "/single/chain", {"mock": "chain_mid"}, [], 3),
    ("09-siradaki-kulup", "1C", "oneriler", "/single/chain", {"mock": "chain_mid"}, [("type", "inter", 2)], 4),
    ("09-siradaki-kulup", "1D", "yanlis-tahmin", "/single/chain", {"mock": "chain_wrong"}, [], 3),
    ("09-siradaki-kulup", "2", "sonuc-karti", "/single/chain", {"mock": "chain_over"}, [], 3),
    # 10 o mu bu mu
    ("10-o-mu-bu-mu", "1", "soru", "/single/versus", {"mock": "versus_play"}, [], 3),
    ("10-o-mu-bu-mu", "1B", "kalan-oyuncunun-degeri-acik", "/single/versus", {"mock": "versus_shown"}, [], 3),
    ("10-o-mu-bu-mu", "1C", "yeni-kategori", "/single/versus", {"mock": "versus_newcat"}, [], 3),
    ("10-o-mu-bu-mu", "2", "sonuc-karti", "/single/versus", {"mock": "versus_over"}, [], 3),
    # 11 haftanın maçı
    ("11-haftanin-maci", "1", "giris-taraf-secilmemis", "/weekly", {"mock": "weekly_fresh"}, [], 4),
    ("11-haftanin-maci", "1B", "giris-taraf-secildi", "/weekly", {"mock": "weekly_fresh"}, [("tap", "Trabzonspor", 3.2)], 4.5),
    ("11-haftanin-maci", "1C", "giris-taraf-kilitli", "/weekly", {"mock": "weekly_locked"}, [], 4),
    ("11-haftanin-maci", "2", "soru", "/weekly/play", {"side": "b", "mock": "weekly_locked,weekly_play"}, [], 4),
    ("11-haftanin-maci", "3", "sonuc-karti", "/weekly/play", {"side": "b", "mock": "weekly_locked,weekly_over", "best": "1200"}, [], 4),
    # 13 sistem
    ("13-sistem", "1", "yeni-surum-karti", "/", {"mock": "update,weekly_fresh"}, [], 3.5),
]
# 12 nasıl oynanır: her modun her adımı (İleri'ye basarak)
LEARN = [("online", "/online", {}, 5), ("ladder", "/single/setup", {"mode": "ladder"}, 3), ("blitz", "/single/setup", {"mode": "blitz"}, 3), ("career", "/single/setup", {"mode": "career"}, 3),
         ("chain", "/single/setup", {"mode": "chain"}, 3), ("versus", "/single/setup", {"mode": "versus"}, 3), ("weekly", "/weekly", {"mock": "weekly_fresh"}, 3)]
NAMES = {"online": "online", "ladder": "klasik-merdiven", "blitz": "beste-bir", "career": "kariyer-yolu", "chain": "siradaki-kulup", "versus": "o-mu-bu-mu", "weekly": "haftanin-maci"}
for n, (mid, path, params, steps) in enumerate(LEARN, start=1):
    for k in range(steps):
        SHOTS.append(("12-nasil-oynanir", f"{n}{'' if k == 0 else chr(65 + k)}", f"{NAMES[mid]}-adim-{k + 1}", path, {**params, "learn": "1"},
                      [("tap", T("next"), 2.6 + 0.7 * j) for j in range(k)], 3.2 + 0.7 * k))
SHOTS.sort(key=lambda s: s[0])


async def shoot(sem, port, theme, shot):
    cat, num, name, path, params, actions, wait = shot
    q = {"nick": "kubi", "theme": {"acik": "light", "koyu": "dark"}[theme], "lang": A.lang, "learn": "0", **params}
    url = f"http://localhost:8081{path}?{urllib.parse.urlencode(q)}"
    out = pathlib.Path(A.out) / theme / cat / f"{num}-{name}.png"; out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(ROOT / "tools" / "cdp_shot.py"), str(out), url, "--wait", str(wait), "--size", A.size, "--port", str(port)]
    for kind, arg, at in actions: cmd += [f"--{kind}", f"{arg}@{at}"]
    async with sem:
        for attempt in range(2):
            p = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
            o, _ = await p.communicate()
            if p.returncode == 0 and out.exists():
                msg = o.decode().strip().splitlines()
                warn = [m for m in msg if "bulunamadı" in m]
                print(f"  {theme}/{cat}/{num}-{name}" + (f"   !! {warn[0].strip()}" if warn else ""), flush=True); return True
        print(f"  HATA {theme}/{cat}/{num}-{name}: {o.decode()[-200:]}", flush=True); return False


async def main():
    themes = ["acik", "koyu"] if A.theme == "ikisi" else [A.theme]
    shots = [s for s in SHOTS if s[0].startswith(A.only)]
    sem = asyncio.Semaphore(A.jobs)
    jobs = [shoot(sem, 9400 + i, th, s) for i, (th, s) in enumerate((th, s) for th in themes for s in shots)]
    res = await asyncio.gather(*jobs)
    print(f"bitti: {sum(res)}/{len(res)} görüntü → {A.out}")

asyncio.run(main())
