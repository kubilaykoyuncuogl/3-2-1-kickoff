"""Haftanın maçı: iki kulübün oyuncularıyla "o mu bu mu". Her soruda bir A'lı, bir B'li; değer o kulüp formasıyla istatistik.
Oyuncu bir taraf seçer (hafta boyunca sabit), koşu puanı o tarafın toplamına yazılır; girişte iki tarafın toplamı görünür.

Veri: server/weekly/<slug>.json (tools/build_weekly.py, build_weekly_career.py). Etkin maçlar: active.json (slug listesi; aynı anda birden çok maç), yoksa current.json. Toplamlar hesap veritabanında (accounts.weekly_*), slug başına.
Oturum, tek oyunculu "versus" akışını kullanır (mode = "weekly": tek can, hız bonusu); istemciye değerler cevap verilince gider."""
import asyncio, json, pathlib, random

WEEKLY_DIR = pathlib.Path(__file__).resolve().parents[1] / "weekly"
WEEKLY_PATH = WEEKLY_DIR / "current.json"
SLUG_OK = lambda x: bool(x) and all(ch.isalnum() or ch == "-" for ch in x)      # dosya adı olarak kullanılır
CATS = ("apps", "goals", "assists", "yellow", "seasons")      # istemcide cat.w_<ad>
ROUNDS = 60
SEEN_KEEP = 70      # cihaz başına son koşularda görülen bu kadar isim, yeni koşuda mümkün oldukça yeniden sorulmaz


def make_pack(data: dict, rng: random.Random, n: int = ROUNDS, avoid=()) -> list:
    """Sorular kolaydan zora: önce en çok forma giymiş (tanınan) oyuncular ve büyük farklar, ilerledikçe havuz genişler, fark daralır.
    `avoid`: oyuncunun son koşularda gördüğü isimler; aday kaldıkça seçilmez (koşular kısa olduğu için havuzun başı hep aynı isimleri getiriyordu)."""
    avoid = set(avoid)
    pools = {s: sorted((p for p in data["players"] if p["side"] == s), key=lambda p: -p["apps"]) for s in ("a", "b")}
    if len(pools["a"]) < 8 or len(pools["b"]) < 8: return []
    out = []; recent: list = []
    for i in range(n):
        k = 30 + i * 4; need = max(1.08, 2.0 - i * 0.035)
        item = None
        for attempt in range(120):
            if attempt == 60: need = 1.0                      # bulunamadıysa farkı serbest bırak
            a = rng.choice(pools["a"][:k]); b = rng.choice(pools["b"][:k])
            if a["name"] in recent or b["name"] in recent or a["name"] == b["name"]: continue
            if attempt < 40 and (a["name"] in avoid or b["name"] in avoid): continue
            cat = rng.choice(CATS)
            va, vb = a.get(cat), b.get(cat)
            if va is None or vb is None or va == vb or max(va, vb) < 3: continue
            if min(va, vb) > 0 and max(va, vb) / min(va, vb) < need: continue
            item = {"cat": "w_" + cat, "fmt": "int", "names": [a["name"], b["name"]], "born": [a.get("born"), b.get("born")], "shown": [None, None],
                    "new_cat": False, "_values": [va, vb], "_answer": 0 if va > vb else 1,
                    "_p": [a, b], "_clubs": [data["a"]["short"], data["b"]["short"]]}
            recent = (recent + [a["name"], b["name"]])[-16:]
            break
        if item is None: break
        out.append(item)
    return out


CAREER_ROUNDS = 40

def make_career_pack(data: dict, side: str, rng: random.Random, n: int = CAREER_ROUNDS, avoid=()) -> list:
    """Kariyer yolu biçimi: yalnızca seçilen tarafın kulübünden geçmiş oyuncular, tanınandan az tanınana (liste toplam maça göre sıralı).
    Kimlik eşleşmesi dosyadaki index numarasıyla; ad da eşleşme sayılır (index yeniden üretilse de çalışsın)."""
    pool = (data.get("careers") or {}).get(side) or []
    if len(pool) < 10: return []
    avoid = set(avoid); used = set(); out = []
    for i in range(min(n, len(pool))):
        k = 24 + i * 7
        cand = [p for p in pool[:k] if p["name"] not in used]
        fresh = [p for p in cand if p["name"] not in avoid]
        if not (fresh or cand): cand = [p for p in pool if p["name"] not in used]
        if not (fresh or cand): break
        p = rng.choice(fresh or cand); used.add(p["name"])
        out.append({"_player_id": int(p["id"]), "_name": p["name"], "clubs": p["clubs"], "names": [p["name"]]})
    return out


class WeeklyMixin:
    _weekly_seen: dict = {}      # (cihaz, slug) -> son görülen isimler
    def _weekly_file(self, path: pathlib.Path):
        """Bir hafta dosyası; değişince yeniden okunur. Okunamıyorsa None."""
        try: mt = path.stat().st_mtime
        except OSError: return None
        cache = self.__dict__.setdefault("_weekly_cache", {})
        c = cache.get(path)
        if c is None or c[0] != mt:
            try: cache[path] = c = (mt, json.loads(path.read_text()))
            except (OSError, ValueError): return None
        return c[1]

    def _weekly_all(self) -> list:
        """Etkin maçlar, menüdeki sırayla. active.json (slug listesi) varsa oradakiler, yoksa tek maç: current.json. Hiçbiri yoksa düğme çıkmaz."""
        slugs = self._weekly_file(WEEKLY_DIR / "active.json")
        if isinstance(slugs, list):
            return [d for d in (self._weekly_file(WEEKLY_DIR / (str(x) + ".json")) for x in slugs[:4] if SLUG_OK(str(x))) if isinstance(d, dict)]
        d = self._weekly_file(WEEKLY_PATH)
        return [d] if isinstance(d, dict) else []

    def _weekly_data(self, slug: str = ""):
        """Slug'ı verilen etkin maç; slug yoksa / bulunamazsa ilki."""
        every = self._weekly_all()
        return next((d for d in every if d["slug"] == slug), every[0] if every else None)

    async def _weekly_state(self, pid: int, data: dict) -> dict:
        dev = self.profiles.get(pid, {}).get("device", "")
        st = await asyncio.to_thread(self.accounts.weekly_state, data["slug"], dev)
        side = lambda k: {"name": data[k]["name"], "short": data[k]["short"], "colors": data[k]["colors"], **st["totals"][k]}
        return {"slug": data["slug"], "date": data.get("date", ""), "format": data.get("format", "versus"), "years": data.get("years"), "a": side("a"), "b": side("b"), "me": st.get("me")}

    async def weekly_info(self, pid: int) -> None:
        every = [await self._weekly_state(pid, d) for d in self._weekly_all()]
        self.send(pid, {"t": "weekly_state", "d": every[0] if every else None, "all": every})      # d: ilk maç (eski alan), all: etkin maçların hepsi

    async def weekly_start(self, pid: int, side: str, slug: str = "") -> None:
        data = self._weekly_data(slug)
        if not data or side not in ("a", "b"): self.err(pid, "err.pack_failed"); return
        dev = self.profiles.get(pid, {}).get("device", "")
        if not dev: return
        st = await asyncio.to_thread(self.accounts.weekly_state, data["slug"], dev)
        if st.get("me") and st["me"]["side"] != side: side = st["me"]["side"]      # taraf hafta boyunca sabit
        self._leave_everything(pid)
        career = data.get("format") == "career"
        seen = self._weekly_seen.get((dev, data["slug"]), ())
        items = make_career_pack(data, side, random.Random(), avoid=seen) if career else make_pack(data, random.Random(), avoid=seen)
        if not items: self.err(pid, "err.pack_failed"); return
        self.singles[pid] = {"mode": "weekly_career" if career else "weekly", "seed": "", "era": 0, "items": items, "idx": 0, "lives": 3 if career else 1, "score": 0, "combo": 1.0, "deadline": 0,
                             "lock_until": 0, "over": False, "best_combo": 1.0, "gen": 0, "revealed": 1, "step": 0, "done": 0, "per_ms": 0, "last": {},
                             "side": side, "slug": data["slug"]}
        self._single_next(pid, True)

    async def _weekly_finish(self, pid: int, s: dict) -> None:
        """Koşu bitti: puan tarafın toplamına yazılır, güncel durum oyuncuya gider."""
        dev = self.profiles.get(pid, {}).get("device", "")
        if dev:      # bu koşuda görülen isimler: sonraki koşularda öne alınmaz (bellekte; sunucu yeniden başlayınca sıfırlanır)
            shown = [n for it in s["items"][:int(s["idx"]) + 1] for n in it["names"]]
            key = (dev, s["slug"])
            self._weekly_seen[key] = (list(self._weekly_seen.get(key, ())) + shown)[-SEEN_KEEP:]
        if dev and int(s["score"]) > 0:
            await asyncio.to_thread(self.accounts.weekly_add, s["slug"], dev, s["side"], int(s["score"]))
        if pid in self.profiles: await self.weekly_info(pid)
