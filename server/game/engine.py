"""Oyun motoru: profiller, odalar, maç durum makinesi, eşleşme, Elo, hesap işlemleri. game.gd'nin sunucu tarafı.

Taşıma kuralları
- Zamanlayıcılar `asyncio` görevleri; her biri uyandığında `gen` ve `state` kontrol eder (geç kalan görev eski turu bozmaz).
- Index ve hesap çağrıları eşzamanlı (sqlite, kilitli) → `asyncio.to_thread` ile; olay döngüsü bloklanmaz.
- İstemciye giden sözlükler game.gd'deki `_broadcast`, `_single_send`, `_send_profile`, `_send_queue` ile aynı alan adlarını taşır
  (+ `me`: izleyenin kendi pid'i). Mesaj zarfı: {"t": tip, "d": sözlük}.
"""
import asyncio, math, pathlib, random, sys, time
from typing import Callable

from .consts import *
from .bots import BOT_WAIT_MS, BotsMixin
from .singles import SinglesMixin
from .weekly import WeeklyMixin

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from normalize import normalize   # noqa: E402

WORDS_PATH = pathlib.Path(__file__).resolve().parents[1] / "words.txt"


class Engine(SinglesMixin, BotsMixin, WeeklyMixin):
    def __init__(self, send: Callable[[int, dict], None], index, accounts):
        self.send = send              # send(pid, msg): bağlı değilse sessizce düşer
        self.index = index            # server.index_service modülü (fonksiyonları doğrudan çağrılır)
        self.accounts = accounts      # server.accounts modülü
        self.rooms: dict[str, dict] = {}
        self.pid_room: dict[int, str] = {}
        self.profiles: dict[int, dict] = {}
        self.peers: set[int] = set()
        self.queue: list[int] = []
        self.queue_since: dict[int, int] = {}
        self.singles: dict[int, dict] = {}
        self.rate: dict[str, list[int]] = {}
        self.pending_rc: dict[str, dict] = {}   # device -> {code, pid, until}: kopan oyuncunun geri dönüş hakkı
        self.words = [w for w in WORDS_PATH.read_text().split() if w.isalpha()] if WORDS_PATH.exists() else []
        self._tasks: set[asyncio.Task] = set()
        self._queue_tick = 0
        self._pid_seq = 10 ** 6
        self.alloc_pid = self._alloc_pid_default      # ws.setup bunu bağlantı sayacıyla değiştirir
        self._init_bots()

    def _alloc_pid_default(self) -> int:
        self._pid_seq += 1; return self._pid_seq

    # ---------- yardımcılar ----------
    @staticmethod
    def now() -> int:
        return int(time.monotonic() * 1000)

    @staticmethod
    def norm(s: str) -> str:
        return normalize(s)

    def spawn(self, coro) -> asyncio.Task:
        t = asyncio.create_task(coro); self._tasks.add(t); t.add_done_callback(self._tasks.discard); return t

    def err(self, pid: int, key: str) -> None:
        self.send(pid, {"t": "err", "key": key})

    def _allow(self, key: str, max_n: int, window_ms: int) -> bool:
        now = self.now()
        arr = [t for t in self.rate.get(key, []) if now - t < window_ms]
        if len(arr) >= max_n: self.rate[key] = arr; return False
        arr.append(now); self.rate[key] = arr; return True

    # ---------- index / hesap köprüleri (iş parçacığında) ----------
    async def index_check(self, player_id: int, a: int, b: int, era: int) -> bool:
        r = await asyncio.to_thread(self.index.check, player_id, a, b, era)
        return bool(r.get("ok", False))

    async def index_answers(self, a: int, b: int, era: int) -> dict:
        try: return await asyncio.to_thread(self.index.pair_answers, a, b, 12, era)
        except Exception: return {"names": [], "total": -1}

    async def index_pack(self, mode: str, sc: str, era: int) -> list:
        try:
            if mode == "ladder": return (await asyncio.to_thread(self.index.ladder, "", 27, "", sc, era)).get("steps", [])
            if mode == "blitz": return (await asyncio.to_thread(self.index.blitz_pack, "", 40, 1, "", sc, era)).get("questions", [])
            if mode == "career": return await asyncio.to_thread(self.index.career_pack, 30, "", era, sc)
            if mode == "chain": return await asyncio.to_thread(self.index.chain_pack, 15, "", era, sc)
            if mode == "versus": return await asyncio.to_thread(self.index.versus_pack, 80, "", era, sc)
        except Exception as e:
            print("[engine] pack failed", mode, e, flush=True)
        return []

    async def index_in_scope(self, club_id: int, sc: str) -> bool:
        try: return bool((await asyncio.to_thread(self.index.club, club_id, sc)).get("in_scope", False))
        except Exception: return False

    async def acct_post(self, op: str, body: dict):
        fn = getattr(self.accounts, op, None)
        if fn is None: return None
        try: return await asyncio.to_thread(fn, body)
        except Exception as e:
            print("[engine] acct", op, "failed:", e, flush=True); return None

    async def acct_best(self, device: str, mode: str, score: int) -> None:
        await self.acct_post("best", {"device": device, "mode": mode, "score": score})

    # ---------- bağlantı ----------
    def on_connect(self, pid: int) -> None:
        self.peers.add(pid)
        self.profiles[pid] = {"nick": "misafir", "device": "", "elo": 1000, "games": 0}
        self.send(pid, {"t": "welcome", "pid": pid, "proto": PROTO})

    def on_disconnect(self, pid: int) -> None:
        self.peers.discard(pid)
        self.spawn(self._on_leave(pid))

    async def handle(self, pid: int, m: dict) -> None:
        """İstemciden gelen tek mesaj. Bilinmeyen tip ve bozuk alan sessizce düşer (Godot'daki RPC imza uyuşmazlığı gibi)."""
        t = m.get("t")
        s = lambda k, n=64: str(m.get(k, "") or "")[:n]
        def i(k):
            try: return int(m.get(k, 0) or 0)
            except (TypeError, ValueError): return 0
        if t == "hello": await self.hello(pid, s("nick", 16), s("device", 64), i("proto"))
        elif t == "create_room": self.create_room(pid, s("scope", 8), i("era"), i("round"))
        elif t == "join_room": self.join_room(pid, s("code", 24))
        elif t == "find_match": self.find_match(pid, s("scope", 8), i("era"), i("round"))
        elif t == "cancel_find": self.cancel_find(pid)
        elif t == "leave_room": self.leave_room(pid)
        elif t == "pick_team": await self.pick_team(pid, i("team_id"), s("team_name", 80))
        elif t == "set_ready": self.set_ready(pid)
        elif t == "guess": await self.guess(pid, i("player_id"), s("name", 80))
        elif t == "suggest": await self.suggest(pid, s("kind", 8), s("q", 40))
        elif t == "rematch": self.rematch(pid)
        elif t == "single_start": await self.single_start(pid, s("mode", 8), s("scope", 8), i("era"))
        elif t == "single_guess": await self.single_guess(pid, i("player_id"), s("name", 80))
        elif t == "single_answer": self.single_answer(pid, i("option"))
        elif t == "single_team": self.single_team(pid, i("team_id"), s("name", 80))
        elif t == "single_quit": self.single_quit(pid)
        elif t == "acct": await self.acct(pid, s("op", 12), s("a", 64), s("b", 64))
        elif t == "weekly_info": await self.weekly_info(pid)
        elif t == "weekly_start": await self.weekly_start(pid, s("side", 1))

    # ---------- istemci → sunucu ----------
    async def hello(self, pid: int, nick: str, device: str, proto: int) -> None:
        if len(device) < 8: return
        prev = self.profiles.get(pid, {})
        self.profiles[pid] = {"nick": nick.strip()[:16], "device": device, "elo": int(prev.get("elo", 1000)), "games": int(prev.get("games", 0)),
                              "last_opp": prev.get("last_opp", ""), "linked": False, "verified": False, "bests": {}, "proto": proto}
        res = await self.acct_post("hello", {"device": device, "nick": nick})
        if pid not in self.profiles or self.profiles[pid]["device"] != device: return
        if isinstance(res, dict): self._apply_profile(pid, res)
        self._send_profile(pid)
        if isinstance(res, dict) and res.get("error"): self.err(pid, "err." + str(res["error"]))
        if proto != PROTO: self.err(pid, "err.proto")
        prc = self.pending_rc.pop(device, None)
        if prc:
            r = self.rooms.get(prc["code"])
            if r is not None and prc["pid"] in r["players"]: self._rebind(r, prc["pid"], pid)

    def create_room(self, pid: int, scope: str, era: int, round_s: int = 0) -> None:
        self._leave_everything(pid)
        code = self._new_code()
        self.rooms[code] = self._new_room(code, False, scope_ok(scope), era_ok(era), round_ok(round_s))
        self._join(code, pid)

    def join_room(self, pid: int, code: str) -> None:
        code = self.norm(code).replace(" ", "")
        r = self.rooms.get(code)
        if r is None: self.err(pid, "err.room_not_found"); return
        if len(r["players"]) >= 2: self.err(pid, "err.room_full"); return
        self._leave_everything(pid)
        self._join(code, pid)

    def find_match(self, pid: int, scope: str, era: int, round_s: int = 0) -> None:
        self._leave_everything(pid)
        p = self.profiles[pid]; p["scope"] = scope_ok(scope); p["era"] = era_ok(era); p["round_ms"] = round_ok(round_s)
        if pid not in self.queue:
            self.queue.append(pid); self.queue_since[pid] = self.now()
            p["bot_after"] = random.uniform(*BOT_WAIT_MS)      # gerçek rakip çıkmazsa bu kadar sonra bot
        self._send_queue(pid)

    def cancel_find(self, pid: int) -> None:
        if pid in self.queue: self.queue.remove(pid)
        self.queue_since.pop(pid, None)
        self.send(pid, {"t": "room_state", "d": {"state": State.LOBBY, "left": True, "me": pid}})

    def leave_room(self, pid: int) -> None:
        self._leave_everything(pid)
        self.send(pid, {"t": "room_state", "d": {"state": State.LOBBY, "left": True, "me": pid}})

    async def pick_team(self, pid: int, team_id: int, team_name: str) -> None:
        r = self._room_of(pid)
        if r is None or r["state"] != State.PICK_TEAMS or r["ready"].get(pid, False): return
        if team_id == 0:
            r["teams"].pop(pid, None); r["team_names"].pop(pid, None); self._broadcast(r); return
        if team_id in r["used_teams"]: self.err(pid, "err.team_used"); return
        if self._team_clash(r, pid, team_id): return
        if r["scope"] != "all":
            ok = await self.index_in_scope(team_id, r["scope"])
            if not ok: self.err(pid, "err.out_of_scope"); return
            if r["state"] != State.PICK_TEAMS or r["ready"].get(pid, False): return
            # kapsam sorgusu beklerken rakip aynı takımı seçmiş olabilir: yeniden bak (iki oyuncu aynı anda aynı takımı alabiliyordu)
            if team_id in r["used_teams"]: self.err(pid, "err.team_used"); return
            if self._team_clash(r, pid, team_id): return
        r["teams"][pid] = team_id; r["team_names"][pid] = team_name
        self._broadcast(r)

    def _team_clash(self, r: dict, pid: int, team_id: int) -> bool:
        """İki oyuncu aynı takımı seçti: ikisinin seçimi de iptal olur ve ikisi de yeniden seçer.
        (Yalnızca ikinciyi reddetmek, ona rakibin ne seçtiğini söylerken rakibin seçimini yerinde bırakıyordu.)"""
        other = next((o for o, tid in r["teams"].items() if o != pid and tid == team_id), None)
        if other is None: return False
        for p in (pid, other):
            r["teams"].pop(p, None); r["team_names"].pop(p, None); r["ready"].pop(p, None)
            self.err(p, "err.team_clash")
        self._broadcast(r)
        return True

    def set_ready(self, pid: int) -> None:
        r = self._room_of(pid)
        if r is None or r["state"] != State.PICK_TEAMS or pid not in r["teams"] or r["ready"].get(pid, False): return   # tekrar "hazır": yok sayılır (yoksa her biri yeni geri sayım başlatırdı)
        r["ready"][pid] = True
        self._broadcast(r)
        if len(r["players"]) == 2 and len(r["ready"]) == 2: self.spawn(self._start_countdown(r))

    async def guess(self, pid: int, player_id: int, name: str) -> None:
        r = self._room_of(pid)
        if r is None or r["state"] != State.ROUND: return
        if r["penalty_until"].get(pid, 0) > self.now(): return
        if not self._allow("%d:guess" % pid, 30, 60000): return
        gen = r["gen"]
        t = list(r["teams"].values())
        ok = await self.index_check(player_id, t[0], t[1], int(r["era"]))
        if r["gen"] != gen or r["state"] != State.ROUND: return
        if ok:
            r["score"][pid] = r["score"].get(pid, 0) + 1
            self._finish_round(r, {"type": "correct", "pid": pid, "name": name})
        else:
            r["penalty_until"][pid] = self.now() + PENALTY_MS
            r["last"] = {"type": "wrong", "pid": pid, "name": name}
            self._broadcast(r)

    async def suggest(self, pid: int, kind: str, q: str) -> None:
        if len(q) < 2 or not self._allow("%d:suggest" % pid, 12, 1000): return
        r = self._room_of(pid)
        if kind == "team":
            lst = await asyncio.to_thread(self.index.teams_suggest, q, 8, r["scope"] if r else "all")
            if r is not None:
                # yalnızca önceki turlarda kullanılmış takımlar işaretlenir; rakibin O ANKİ seçimi işaretlenmez (öneri listesi rakibin seçimini sızdırıyordu)
                for item in lst:
                    if isinstance(item, dict) and item.get("id") is not None:
                        item["used"] = int(item["id"]) in r["used_teams"]
        else:
            sp = self.singles.get(pid)      # dönem seçiliyse yalnızca o dönemin oyuncuları önerilir
            era = int(r["era"]) if r else (int(sp.get("era", 0)) if sp else 0)
            lst = await asyncio.to_thread(self.index.players_suggest, q, 8, era)
        self.send(pid, {"t": "suggest_result", "kind": kind, "q": q, "list": lst})

    def rematch(self, pid: int) -> None:
        r = self._room_of(pid)
        if r is None or r["state"] != State.GAME_OVER: return
        r["rematch"][pid] = True
        if len(r["players"]) == 2 and len(r["rematch"]) == 2:
            self._reset_match(r); self.spawn(self._start_pick(r)); return
        self._broadcast(r)

    async def acct(self, pid: int, op: str, a: str, b: str) -> None:
        """Hesap işlemleri: create | link_code | link | recover | logout | delete. Cihaz kimliği sunucudaki kayıttan alınır."""
        p = self.profiles.get(pid, {}); device = p.get("device", "")
        if not device or op not in ("create", "link_code", "link", "recover", "logout", "delete"): return
        if not self._allow("%d:acct" % pid, 12, 60000): self.send(pid, {"t": "acct_result", "d": {"op": op, "ok": False, "error": "too_many"}}); return
        if self._room_of(pid) is not None or pid in self.queue: self.send(pid, {"t": "acct_result", "d": {"op": op, "ok": False, "error": "busy"}}); return
        body = {"device": device}
        if op == "link": body["code"] = a
        if op == "recover": body["nick"] = a; body["recovery"] = b
        res = await self.acct_post(op, body)
        if pid not in self.profiles: return
        if not isinstance(res, dict): self.send(pid, {"t": "acct_result", "d": {"op": op, "ok": False, "error": "server"}}); return
        prof = res if res.get("ok", False) else res.get("profile", {})
        if prof:
            self._apply_profile(pid, prof)
            if op in ("logout", "delete") and str(prof.get("nick", "")) == "": self.profiles[pid]["nick"] = ""
            self._send_profile(pid)
        out = {"op": op, "ok": bool(res.get("ok", False)), "error": str(res.get("error", ""))}
        for k in ("recovery", "code", "ttl"):
            if k in res: out[k] = res[k]
        self.send(pid, {"t": "acct_result", "d": out})

    # ---------- oda ----------
    def _new_room(self, code: str, ranked: bool, scope: str = "all", era: int = 0, round_ms: int = ROUND_MS) -> dict:
        r = {"code": code, "ranked": ranked, "scope": scope, "era": era, "round_ms": round_ms, "players": [], "state": State.LOBBY, "gen": 0, "rematch": {}, "last": {}}
        self._reset_match(r)
        return r

    @staticmethod
    def _reset_match(r: dict) -> None:
        r.update(teams={}, team_names={}, ready={}, score={}, penalty_until={}, used_teams={}, invalid_streak=0, phase_end=0, answers=[],
                 answers_total=0, winner=0, rematch={}, last={}, elo_delta={}, away={}, quick_picks=[])
        r["gen"] += 1

    def _new_code(self) -> str:
        if self.words:
            for _ in range(20):
                w = random.choice(self.words)
                if w not in self.rooms: return w
            for _ in range(50):
                w2 = "%s%d" % (random.choice(self.words), random.randrange(10, 100))
                if w2 not in self.rooms: return w2
        while True:
            code = "%04d" % random.randrange(10000)
            if code not in self.rooms: return code

    def _room_of(self, pid: int):
        code = self.pid_room.get(pid)
        return self.rooms.get(code) if code is not None else None

    def _join(self, code: str, pid: int) -> None:
        r = self.rooms[code]
        r["players"].append(pid); self.pid_room[pid] = code
        if len(r["players"]) == 2:
            self.spawn(self._start_pick(r)); return
        self._broadcast(r)

    def _leave_everything(self, pid: int) -> None:
        if pid in self.queue: self.queue.remove(pid)
        self.queue_since.pop(pid, None); self.singles.pop(pid, None)
        r = self._room_of(pid)
        if r is None: return
        r["players"].remove(pid); self.pid_room.pop(pid, None)
        if not r["players"]:
            self.rooms.pop(r["code"], None); return
        if r["state"] in IN_MATCH:          # rakip gitti: maç ortasındaysa kalan kazanır
            r["gen"] += 1
            r["state"] = State.GAME_OVER; r["winner"] = r["players"][0]; r["last"] = {"type": "left"}
            if r["ranked"]: self._apply_elo(r, r["players"][0], pid)
        elif r["state"] == State.GAME_OVER:
            r["last"] = {"type": "left"}
        self._broadcast(r)

    async def _on_leave(self, pid: int) -> None:
        r = self._room_of(pid)
        dev = self.profiles.get(pid, {}).get("device", "")
        if r is not None and dev and len(r["players"]) == 2 and r["state"] in IN_MATCH:
            # 10 sn içinde aynı cihaz geri gelirse maç devam eder
            self.pending_rc[dev] = {"code": r["code"], "pid": pid, "until": self.now() + RECONNECT_MS}
            r["away"][pid] = True; self._broadcast(r)
            if pid in self.queue: self.queue.remove(pid)
            self.queue_since.pop(pid, None); self.singles.pop(pid, None)
            saved = self.profiles[pid]
            await asyncio.sleep(RECONNECT_MS / 1000)
            if self.pending_rc.get(dev, {}).get("pid", -1) == pid:
                self.pending_rc.pop(dev, None); self.profiles[pid] = saved
                self._leave_everything(pid); self.profiles.pop(pid, None)
            self._forget_rate(pid)
            return
        self._leave_everything(pid); self.profiles.pop(pid, None); self._forget_rate(pid)

    def _forget_rate(self, pid: int) -> None:
        for k in ("guess", "suggest", "acct"): self.rate.pop("%d:%s" % (pid, k), None)

    def _rebind(self, r: dict, old: int, new: int) -> None:
        if old in r["players"]: r["players"][r["players"].index(old)] = new
        for key in ("teams", "team_names", "ready", "score", "penalty_until", "rematch", "elo_delta", "away"):
            d = r[key]
            if old in d: d[new] = d.pop(old)
        r["away"].pop(new, None)
        self.pid_room.pop(old, None); self.pid_room[new] = r["code"]
        self._broadcast(r)

    # ---------- maç akışı ----------
    async def _start_countdown(self, r: dict) -> None:
        # ortak oyuncu yoksa tur hiç oynanmaz: uyarı gösterilir, takımlar harcanmaz, seçime dönülür
        r["gen"] += 1
        pre_gen = r["gen"]
        pair = list(r["teams"].values())
        pre = await self.index_answers(pair[0], pair[1], int(r["era"]))
        if r["gen"] != pre_gen or r["state"] != State.PICK_TEAMS or len(r["teams"]) < 2: return
        if int(pre["total"]) == 0: r["gen"] += 1; self.spawn(self._no_common(r, r["gen"])); return
        for t in r["teams"].values(): r["used_teams"][t] = True
        r["gen"] += 1
        r["state"] = State.COUNTDOWN; r["phase_end"] = self.now() + COUNTDOWN_MS; r["last"] = {}
        self._broadcast(r)
        gen = r["gen"]
        await asyncio.sleep(COUNTDOWN_MS / 1000)
        if r["gen"] != gen or r["state"] != State.COUNTDOWN: return
        r["state"] = State.REVEAL; r["phase_end"] = self.now() + REVEAL_MS
        self._broadcast(r)
        await asyncio.sleep(REVEAL_MS / 1000)
        if r["gen"] != gen or r["state"] != State.REVEAL: return
        r["state"] = State.ROUND; r["phase_end"] = self.now() + r["round_ms"]
        self._broadcast(r)
        await asyncio.sleep(r["round_ms"] / 1000)
        if r["gen"] != gen or r["state"] != State.ROUND: return
        self._finish_round(r, {"type": "timeout"})

    async def _no_common(self, r: dict, gen: int) -> None:
        r["invalid_streak"] += 1
        r["answers"] = []; r["answers_total"] = 0; r["last"] = {"type": "timeout", "no_common": True}
        if r["invalid_streak"] >= MAX_INVALID_PAIRS:
            r["state"] = State.GAME_OVER; r["winner"] = 0; r["last"]["draw"] = True; self._broadcast(r); return
        r["state"] = State.ROUND_END; r["phase_end"] = self.now() + NO_COMMON_MS
        self._broadcast(r)
        await asyncio.sleep(NO_COMMON_MS / 1000)
        if r["gen"] != gen or r["state"] != State.ROUND_END: return
        self._clear_round(r)
        await self._start_pick(r)

    @staticmethod
    def _clear_round(r: dict) -> None:
        r.update(teams={}, team_names={}, ready={}, penalty_until={}, last={}, answers=[])

    async def _start_pick(self, r: dict) -> None:
        r["gen"] += 1
        gen = r["gen"]
        r["state"] = State.PICK_TEAMS; r["phase_end"] = self.now() + PICK_MS
        r["quick_picks"] = []
        self._broadcast(r)
        try: qp = await asyncio.to_thread(self.index.quick_picks, r["scope"], 5, ",".join(str(x) for x in r["used_teams"]))
        except Exception: qp = []
        if r["gen"] == gen and r["state"] == State.PICK_TEAMS:
            r["quick_picks"] = qp; self._broadcast(r)
        await asyncio.sleep(PICK_MS / 1000)
        if r["gen"] != gen or r["state"] != State.PICK_TEAMS or len(r["players"]) < 2: return
        ready_players = [p for p in r["players"] if r["ready"].get(p, False)]
        if len(ready_players) == 1:
            winner = ready_players[0]
            slow = r["players"][0] if r["players"][1] == winner else r["players"][1]
            r["score"][winner] = r["score"].get(winner, 0) + 1
            r["gen"] += 1
            r["answers"] = []; r["answers_total"] = 0; r["last"] = {"type": "pick_timeout", "pid": slow}
            for p in r["players"]:
                if r["score"].get(p, 0) >= WIN_SCORE:
                    r["state"] = State.GAME_OVER; r["winner"] = p
                    if r["ranked"]: self._apply_elo(r, p, slow)
                    self._broadcast(r); return
            r["state"] = State.ROUND_END; r["phase_end"] = self.now() + ROUND_END_MS
            self._broadcast(r)
            g2 = r["gen"]
            await asyncio.sleep(ROUND_END_MS / 1000)
            if r["gen"] != g2 or r["state"] != State.ROUND_END: return
            self._clear_round(r)
            await self._start_pick(r)
        else:
            await self._start_pick(r)   # ikisi de seçmedi: süre yenilenir

    def _finish_round(self, r: dict, last: dict) -> None:
        """Turu kapatır. gen burada, eşzamanlı olarak artar: aynı anda gelen ikinci doğru tahmin (index cevabı beklerken) sayılmaz."""
        r["gen"] += 1
        self.spawn(self._end_round(r, last, r["gen"]))

    async def _end_round(self, r: dict, last: dict, gen: int) -> None:
        t = list(r["teams"].values())
        ans = await self.index_answers(t[0], t[1], int(r["era"]))
        if r["gen"] != gen: return
        r["answers"] = ans.get("names", []); r["answers_total"] = int(ans.get("total", 0)); r["last"] = last
        if r["answers_total"] == 0:
            r["invalid_streak"] += 1; r["last"]["no_common"] = True
            if r["invalid_streak"] >= MAX_INVALID_PAIRS:
                r["state"] = State.GAME_OVER; r["winner"] = 0; r["last"]["draw"] = True; self._broadcast(r); return
        else:
            r["invalid_streak"] = 0
        for pid in r["players"]:
            if r["score"].get(pid, 0) >= WIN_SCORE:
                r["state"] = State.GAME_OVER; r["winner"] = pid
                if r["ranked"]:
                    loser = r["players"][0] if r["players"][1] == pid else r["players"][1]
                    self._apply_elo(r, pid, loser)
                self._broadcast(r); return
        r["state"] = State.ROUND_END; r["phase_end"] = self.now() + ROUND_END_MS
        self._broadcast(r)
        await asyncio.sleep(ROUND_END_MS / 1000)
        if r["gen"] != gen or r["state"] != State.ROUND_END: return
        self._clear_round(r)
        await self._start_pick(r)

    def _broadcast(self, r: dict) -> None:
        now = self.now()
        for viewer in r["players"]:
            if viewer not in self.peers: continue
            players = []
            for pid in r["players"]:
                p = self.profiles.get(pid, {"nick": "?", "elo": 1000})
                hide = r["state"] == State.PICK_TEAMS and pid != viewer   # rakibin seçimi ikisi de hazır olana kadar gizli
                players.append({"pid": pid, "nick": p.get("nick", "?"), "elo": p.get("elo", 1000), "team": 0 if hide else r["teams"].get(pid, 0),
                                "team_name": "" if hide else r["team_names"].get(pid, ""), "picked": r["teams"].get(pid, 0) != 0,
                                "ready": r["ready"].get(pid, False), "score": r["score"].get(pid, 0),
                                "penalty_ms": max(0, r["penalty_until"].get(pid, 0) - now), "rematch": r["rematch"].get(pid, False),
                                "elo_delta": r["elo_delta"].get(pid, 0), "away": r["away"].get(pid, False)})
            d = {"me": viewer, "code": r["code"], "ranked": r["ranked"], "scope": r["scope"], "era": r["era"], "round_ms": r["round_ms"], "state": r["state"], "players": players,
                 "phase_ms": max(0, r["phase_end"] - now), "last": r["last"], "answers": r["answers"], "answers_total": r["answers_total"],
                 "winner": r["winner"], "used_teams": list(r["used_teams"]), "quick_picks": r.get("quick_picks", [])}
            self.send(viewer, {"t": "room_state", "d": d})

    # ---------- eşleşme ----------
    def _waited(self, pid: int) -> int:
        return self.now() - self.queue_since.get(pid, self.now())

    def _band(self, pid: int) -> int:
        return min(BAND_MAX, BAND_START + BAND_STEP * (self._waited(pid) // BAND_STEP_MS))

    def _send_queue(self, pid: int) -> None:
        self.send(pid, {"t": "room_state", "d": {"me": pid, "state": State.LOBBY, "searching": True, "band": self._band(pid),
                                                 "elo": self.profiles[pid]["elo"], "waiting": len(self.queue),
                                                 "cross_in_ms": max(0, CROSS_SCOPE_MS - self._waited(pid))}})

    def _tick_queue(self) -> None:
        now = self.now()
        if now - self._queue_tick < 1000: return
        self._queue_tick = now
        i = 0
        while i < len(self.queue):
            a = self.queue[i]; matched = False
            for j in range(i + 1, len(self.queue)):
                b = self.queue[j]
                pa = self.profiles[a]; pb = self.profiles[b]
                if pa.get("verified", False) != pb.get("verified", False): continue
                cross = self._waited(a) >= CROSS_SCOPE_MS and self._waited(b) >= CROSS_SCOPE_MS
                ea = pa.get("era", 0); eb = pb.get("era", 0)
                ra = pa.get("round_ms", ROUND_MS); rb = pb.get("round_ms", ROUND_MS)
                if (pa.get("scope", "all") != pb.get("scope", "all") or ea != eb or ra != rb) and not cross: continue   # aynı kapsam, dönem ve tur süresi; 45 sn sonra serbest
                same_last = pa.get("last_opp", "") == pb.get("device", "") and pb.get("device", "") != ""
                if same_last and (self._waited(a) < SAME_OPP_MS or self._waited(b) < SAME_OPP_MS): continue   # az önceki rakip, 20 sn bekle
                if abs(int(pa["elo"]) - int(pb["elo"])) <= min(self._band(a), self._band(b)):
                    self.queue.remove(b); self.queue.remove(a); self.queue_since.pop(a, None); self.queue_since.pop(b, None)
                    pa["last_opp"] = pb.get("device", ""); pb["last_opp"] = pa.get("device", "")
                    era = ea if ea == eb else (0 if ea == 0 or eb == 0 else era_ok(ea | eb))
                    code = self._new_code(); self.rooms[code] = self._new_room(code, True, widen_scope(pa.get("scope", "all"), pb.get("scope", "all")), era, max(ra, rb))
                    self._join(code, a); self._join(code, b); matched = True; break
            if not matched:
                # öncelik gerçek oyuncu: ancak bu turda kimseyle eşleşemedi ve yeterince bekledi ise bot
                if self._waited(a) >= self.profiles[a].get("bot_after", 10 ** 9) and not self.profiles[a].get("verified", False):
                    self._start_bot_match(a); continue
                self._send_queue(a); i += 1

    # ---------- Elo ve profil ----------
    def _apply_elo(self, r: dict, winner: int, loser: int) -> None:
        pw = self.profiles.get(winner); pl = self.profiles.get(loser)
        if pw is None or pl is None: return
        ea = 1.0 / (1.0 + math.pow(10.0, (float(pl["elo"]) - float(pw["elo"])) / 400.0))
        kw = ELO_K_NEW if int(pw["games"]) < 20 else ELO_K
        kl = ELO_K_NEW if int(pl["games"]) < 20 else ELO_K
        dw = int(round(kw * (1.0 - ea))); dl = -int(round(kl * (1.0 - ea)))
        pw["elo"] += dw; pl["elo"] += dl; pw["games"] += 1; pl["games"] += 1
        r["elo_delta"] = {winner: dw, loser: dl}
        for pid in (winner, loser):
            p = self.profiles[pid]
            if p.get("device"): self.spawn(self.acct_post("save", {"device": p["device"], "elo": int(p["elo"]), "games": int(p["games"])}))
            self._send_profile(pid)

    def _send_profile(self, pid: int) -> None:
        if pid not in self.peers: return
        p = self.profiles[pid]
        self.send(pid, {"t": "profile_state", "d": {"elo": p["elo"], "games": p["games"], "nick": p["nick"], "linked": p.get("linked", False),
                                                    "verified": p.get("verified", False), "bests": p.get("bests", {}),
                                                    "devices": p.get("devices", 1), "proto": PROTO}})

    def _apply_profile(self, pid: int, res: dict) -> None:
        """Hesap servisinden gelen profili bellekteki oyuncuya işler."""
        p = self.profiles[pid]
        p["elo"] = int(res.get("elo", p["elo"])); p["games"] = int(res.get("games", p["games"]))
        if str(res.get("nick", "")) != "": p["nick"] = str(res["nick"])
        p["linked"] = bool(res.get("linked", False)); p["verified"] = bool(res.get("verified", False))
        p["bests"] = res.get("bests", {}); p["devices"] = int(res.get("devices", 1))

    # ---------- döngü ----------
    async def run(self) -> None:
        """Eşleşme ve tek oyunculu süre kontrolü (Godot _process karşılığı)."""
        while True:
            try:
                self._tick_queue(); self._tick_singles()
            except Exception as e:
                print("[engine] tick error:", repr(e), flush=True)
            await asyncio.sleep(0.1)
