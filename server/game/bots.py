"""Gizli rakip botları: Ara'da gerçek rakip bulunamayınca oyuncunun Elo'suna denk bir bot atanır. İstemciye "bot" bilgisi hiç gitmez.

Parçalar
  BOTS            kod adları (yalnızca sunucu ve log), taban Elo ve mizaç (hız, yanlış eğilimi).
  model           plan_round / pick_tier: botun bir turda bilip bilmeyeceği, ne zaman cevap vereceği, yanlış yapıp yapmayacağı.
                  Güç (theta) Elo biriminde ve sınırsız: oyuncu Elo'su yükseldikçe karşısına aynı güçte oynayan bot çıkar (taban Elo yalnızca kişilik seçer).
  BotsMixin       Engine'e eklenir: eşleşmede bot ataması ve botu sürükleyen döngü. Bot, motorun normal yollarını kullanır
                  (pick_team, set_ready, guess, rematch); ayrı kural yoktur.
Ayar: tools/bot_sim.py botları birbirine on binlerce maç oynatır, Elo farkı ↔ kazanma oranı tutarlı olacak şekilde
      bot_params.json'ı yazar (yoksa DEFAULT_PARAMS).
"""
import asyncio, json, math, pathlib, random

from .consts import *

HERE = pathlib.Path(__file__).resolve().parent
PARAMS_PATH = HERE / "bot_params.json"
NAMES_PATH = HERE.parent / "bot_names.txt"

# kod adı, taban Elo, hız çarpanı (<1 hızlı), yanlış çarpanı (>1 sık yanılır)
BOTS = [
    ("ridvan", 820, 1.25, 1.3), ("serhat", 860, 0.85, 1.6), ("ali", 900, 1.30, 0.8), ("bulent", 940, 1.10, 1.1),
    ("sinan", 980, 1.00, 1.0), ("tumer", 1000, 1.00, 1.0), ("gokmen", 1020, 1.05, 0.9), ("ugur", 1060, 0.95, 1.0),
    ("levent", 1100, 0.85, 1.3), ("nihat", 1140, 1.15, 0.6), ("guntekin", 1180, 1.00, 0.9), ("abdulkerim", 1230, 0.85, 1.0),
    ("erman", 1280, 0.95, 0.8), ("hasan", 1340, 0.85, 0.8), ("emre", 1400, 0.95, 0.6), ("omer", 1480, 0.90, 0.35),
]
BOT_WAIT_MS = (17000, 23000)      # bu kadar bekleyip gerçek rakip bulamayan oyuncuya bot atanır (rastgele: hep aynı saniyede gelmesin)
REMATCH_P = 0.30
EQUAL_P, UP_P = 0.70, 0.15        # denk / bir üst; kalan bir alt
EQUAL_SPREAD, STEP_RANGE = 40, (60, 140)
MIN_ANSWER_MS, MIN_MEDIAN_MS = 2800.0, 3600.0      # telefonda bir adı yazıp öneriye dokunmanın alt sınırı: bot bundan hızlı cevap vermez
BOT_GAMES = 50                    # Elo K katsayısı için: bot "yeni oyuncu" sayılmaz

# S_K: bilme olasılığının eğimi · T_EL: güç farkının cevap süresine etkisi · T_BASE / T_SIGMA: cevap süresi (ms) ve dağılımı
# OFFSET: botların gerçek oyunculara göre topluca güçlendirilmesi / zayıflatılması (Elo). Canlı sonuçlara göre elle ayarlanır:
#         loglardaki [bot] result satırlarında denk botlara karşı oyuncular %50'den çok kazanıyorsa artır.
DEFAULT_PARAMS = {"S_K": 400.0, "T_EL": 1200.0, "T_BASE": 7000.0, "T_SIGMA": 0.40, "OFFSET": 0.0}


def load_params() -> dict:
    p = dict(DEFAULT_PARAMS)
    try: p.update(json.loads(PARAMS_PATH.read_text()))
    except (OSError, ValueError): pass
    return p


def load_names() -> list:
    try: return [w.strip() for w in NAMES_PATH.read_text().splitlines() if w.strip() and not w.startswith("#")]
    except OSError: return []


# ---------- model (saf fonksiyonlar; simülasyon da bunları kullanır) ----------
def difficulty(best_rank, total: int) -> float:
    """Çiftin zorluğu, Elo biriminde: en bilinen ortak oyuncunun ün sırası (0 = en ünlü; None = ünlü havuzunda yok) ve ortak oyuncu sayısı."""
    d = 1450.0 if best_rank is None else 760.0 + 230.0 * math.log10(1.0 + best_rank / 15.0)
    return d - 50.0 * math.log10(max(1, total))


def traits_of(code: str) -> dict:
    for c, _base, speed, wrong in BOTS:
        if c == code: return {"speed": speed, "wrong": wrong}
    return {"speed": 1.0, "wrong": 1.0}


def plan_round(theta: float, d: float, traits: dict, rng: random.Random, P: dict) -> list:
    """Bir turda botun yapacakları: [(ms, "wrong" | "right")], zamana göre sıralı. Boş liste = bilemedi."""
    events = []
    wrong_p = min(0.32, max(0.03, 0.26 - (theta - 800.0) / 3200.0)) * traits["wrong"]
    t_wrong = rng.uniform(2500, 10000) if rng.random() < wrong_p else None
    p_know = 1.0 / (1.0 + 10.0 ** ((d - theta) / P["S_K"]))
    if rng.random() < p_know:
        med = min(13000.0, max(MIN_MEDIAN_MS, P["T_BASE"] * 10.0 ** ((d - theta) / P["T_EL"]) * traits["speed"]))
        t = max(MIN_ANSWER_MS, med * math.exp(rng.gauss(0.0, P["T_SIGMA"])))
        if t_wrong is not None:
            if t < t_wrong: t_wrong = None                      # doğruyu önce buldu
            else: t = max(t, t_wrong + PENALTY_MS + rng.uniform(300, 1500))   # yanlıştan sonra kilit biter, sonra doğru
        if t < ROUND_MS - 400: events.append((t, "right"))
    if t_wrong is not None: events.append((t_wrong, "wrong"))
    return sorted(events)


def max_tier(theta: float) -> int:
    """Botun takım seçerken inebileceği en derin tier: zayıf bot yalnızca çok bilinen kulüpleri seçer."""
    return int(min(7, max(2, round(2 + (theta - 800.0) / 170.0))))


def choose_bot(target: float, avoid: str, rng: random.Random) -> str:
    """Hedef güce tabanı en yakın botlardan biri (az önceki hariç). Hedef listenin dışındaysa uçtaki bot oynar."""
    ranked = sorted((b for b in BOTS if b[0] != avoid), key=lambda b: abs(b[1] - target))
    return rng.choice(ranked[:3])[0]


def target_elo(player_elo: float, rng: random.Random) -> float:
    x = rng.random()
    if x < EQUAL_P: return player_elo + rng.uniform(-EQUAL_SPREAD, EQUAL_SPREAD)
    step = rng.uniform(*STEP_RANGE)
    return player_elo + step if x < EQUAL_P + UP_P else player_elo - step


# ---------- motor tarafı ----------
class BotsMixin:
    def _init_bots(self) -> None:
        self.bot_params = load_params()
        self.bot_names = load_names()
        self.bot_stats = {"matches": 0, "bot_wins": 0, "human_wins": 0, "draws": 0, "left": 0}

    def is_bot(self, pid: int) -> bool:
        return bool(self.profiles.get(pid, {}).get("bot"))

    def _bot_nick(self, rng: random.Random, human_nick: str) -> str:
        """Kayıtlı bir hesabın adı olmayan, rakibin adından farklı bir ad."""
        names = list(self.bot_names) or ["kaan07", "emir_", "mertcan", "tolgaa"]
        rng.shuffle(names)
        taken = getattr(self.accounts, "nick_registered", lambda n: False)
        for n in names[:40]:
            if self.norm(n) != self.norm(human_nick) and not taken(self.norm(n)): return n
        return names[0]

    def _start_bot_match(self, human: int) -> None:
        """Kuyrukta bekleyen oyuncuya bot rakip atar (yalnızca Ara; oyuncunun kapsamı ve dönemiyle)."""
        rng = random.Random()
        hp = self.profiles[human]
        theta = target_elo(float(hp["elo"]), rng)
        code_name = choose_bot(theta, hp.get("last_bot", ""), rng)
        bot = self.alloc_pid()                                 # gerçek bağlantılarla aynı sayaçtan: kimlikten bot olduğu anlaşılmaz; peers'ta olmadığı için ona mesaj gitmez
        self.profiles[bot] = {"nick": self._bot_nick(rng, hp.get("nick", "")), "device": "", "elo": int(round(theta)), "games": BOT_GAMES,
                              "bot": code_name, "skill": theta, "linked": False, "verified": False}
        hp["last_bot"] = code_name; hp["last_opp"] = ""
        waited = self._waited(human)
        self.queue.remove(human); self.queue_since.pop(human, None)
        code = self._new_code()
        self.rooms[code] = self._new_room(code, True, hp.get("scope", "all"), hp.get("era", 0))
        self.bot_stats["matches"] += 1
        print("[bot] match room=%s bot=%s skill=%d vs %r elo=%d waited=%.1fs scope=%s era=%s" %
              (code, code_name, theta, hp.get("nick"), hp["elo"], waited / 1000, hp.get("scope"), hp.get("era")), flush=True)
        order = [human, bot] if rng.random() < 0.5 else [bot, human]
        for p in order: self._join(code, p)
        self.spawn(self._bot_loop(code, bot))

    def _bot_cleanup(self, code: str, bot: int) -> None:
        r = self.rooms.get(code)
        if r is not None and bot in r["players"]:
            r["players"].remove(bot)
            if not r["players"]: self.rooms.pop(code, None)
        self.pid_room.pop(bot, None); self.profiles.pop(bot, None); self._forget_rate(bot)

    async def _bot_loop(self, code: str, bot: int) -> None:
        rng = random.Random()
        prof = self.profiles[bot]; P = self.bot_params; theta = float(prof["skill"]) + float(P.get("OFFSET", 0.0)); traits = traits_of(prof["bot"])
        seen = None; plan: dict = {}; logged = False
        try:
            while True:
                await asyncio.sleep(0.2)
                r = self.rooms.get(code)
                if r is None or bot not in r["players"]: break
                humans = [p for p in r["players"] if p != bot]
                if not humans:                                   # oyuncu ayrıldı
                    if not logged: self.bot_stats["left"] += 1
                    break
                now = self.now(); st = r["state"]; key = (st, r["gen"])
                if st == State.PICK_TEAMS:
                    if seen != key and bot not in r["teams"]:
                        seen = key; plan = {"pick_at": now + rng.uniform(4000, 13000), "ready_at": None}
                    if bot not in r["teams"]:
                        if now >= plan.get("pick_at", 0):
                            used = set(r["used_teams"]) | set(r["teams"].values())
                            other = next((t for p, t in r["teams"].items() if p != bot), None)
                            club = None
                            for _try in range(5):      # rakip seçmişse ortak oyuncusu olan bir kulüp dene: boş turlar oyunu sıkıcı yapar (cevabı bilmek değil, yalnızca "ortak var mı")
                                club = await asyncio.to_thread(self.index.bot_pick, r["scope"], used, max_tier(theta), rng.random())
                                if not club or other is None: break
                                if (await asyncio.to_thread(self.index.bot_pair_info, int(club["id"]), other, int(r["era"]), 1))["total"] > 0: break
                            if club: await self.pick_team(bot, int(club["id"]), club["name"])
                            plan["pick_at"] = now + 1500; plan["ready_at"] = self.now() + rng.uniform(900, 3000)
                    elif not r["ready"].get(bot) and now >= (plan.get("ready_at") or 0):
                        self.set_ready(bot)
                elif st == State.ROUND:
                    if seen != key:
                        seen = key
                        t = list(r["teams"].values())
                        info = await asyncio.to_thread(self.index.bot_pair_info, t[0], t[1], int(r["era"]))
                        d = difficulty(info.get("best_rank"), int(info.get("total", 0)))
                        plan = {"start": r["phase_end"] - ROUND_MS, "events": plan_round(theta, d, traits, rng, P), "info": info, "teams": t}
                        continue
                    ev = plan.get("events") or []
                    if ev and now - plan["start"] >= ev[0][0] and r["penalty_until"].get(bot, 0) <= now:
                        _t, kind = ev.pop(0)
                        if kind == "right":
                            cands = plan["info"].get("players") or []
                            if cands:
                                c = cands[min(len(cands) - 1, int(abs(rng.gauss(0, 1.2))))]      # çoğunlukla en bilinen isim
                                await self.guess(bot, int(c["id"]), c["name"])
                        else:
                            w = await asyncio.to_thread(self.index.bot_wrong, plan["teams"][0], plan["teams"][1], int(r["era"]), rng.random())
                            if w: await self.guess(bot, int(w["id"]), w["name"])
                elif st == State.GAME_OVER:
                    if seen != key:
                        seen = key
                        if not logged:
                            logged = True
                            w = r.get("winner", 0)
                            self.bot_stats["draws" if w == 0 else "bot_wins" if w == bot else "human_wins"] += 1
                            print("[bot] result room=%s bot=%s %s score=%s" % (code, prof["bot"], "draw" if w == 0 else "bot" if w == bot else "human",
                                                                              {("bot" if p == bot else "human"): r["score"].get(p, 0) for p in r["players"]}), flush=True)
                        again = rng.random() < REMATCH_P
                        plan = {"rematch_at": now + rng.uniform(2000, 5000) if again else None,
                                "leave_at": now + (rng.uniform(15000, 25000) if again else rng.uniform(4000, 9000))}
                    if plan.get("rematch_at") and now >= plan["rematch_at"] and not r["rematch"].get(bot):
                        logged = False; self.rematch(bot)
                    elif now >= plan.get("leave_at", 0):
                        self._leave_everything(bot); break
        except Exception as e:
            print("[bot] loop error room=%s: %r" % (code, e), flush=True)
        finally:
            self._bot_cleanup(code, bot)
