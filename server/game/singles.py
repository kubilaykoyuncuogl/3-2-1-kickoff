"""Tek oyunculu oturumlar: Klasik merdiven, Beşte Bir, Kariyer yolu, Sıradaki kulüp, O mu bu mu.
game.gd'deki single_* RPC'leri ve _single_* / _tick_singles / _chain_advance karşılıkları. Engine'e karışım olarak eklenir."""
import random
from .consts import *


class SinglesMixin:
    # ---------- istemciden gelenler ----------
    async def single_start(self, pid: int, mode: str, scope: str, era: int) -> None:
        self._leave_everything(pid)
        if mode not in SINGLE_LIVES: return
        seed = "%d-%d" % (self.now(), random.randrange(1 << 30))   # her oturum farklı merdiven / soru seti
        era = era_ok(era); sc = scope_ok(scope)
        items = await self.index_pack(mode, sc, era)
        if not items: self.err(pid, "err.pack_failed"); return
        self.singles[pid] = {"mode": mode, "seed": seed, "era": era, "items": items, "idx": 0, "lives": SINGLE_LIVES[mode],
                             "score": 0, "combo": 1.0, "deadline": 0, "lock_until": 0, "over": False, "best_combo": 1.0, "gen": 0,
                             "revealed": 1, "step": 0, "done": 0, "per_ms": 0, "last": {}}
        self._single_next(pid, True)

    async def single_guess(self, pid: int, player_id: int, name: str) -> None:   # ladder, career
        s = self.singles.get(pid)
        if s is None or s["over"] or s["mode"] not in ("ladder", "career"): return
        if s["lock_until"] > self.now() or not self._allow("%d:guess" % pid, 30, 60000): return
        gen = s["gen"]; item = s["items"][s["idx"]]
        if s["mode"] == "career":
            hit = player_id == int(item["_player_id"]) or self.norm(name) == self.norm(str(item["_name"]))
            if hit:
                hidden = len(item["clubs"]) - int(s["revealed"])
                gained = 100 + 60 * hidden            # erken bilen çok alır
                s["score"] += gained; s["done"] += 1
                s["last"] = {"type": "correct", "name": str(item["_name"]), "gained": gained}
                self._single_next(pid, False)
            else:
                s["lives"] -= 1
                s["last"] = {"type": "wrong", "name": name}
                if s["lives"] <= 0:
                    s["last"]["answer"] = str(item["_name"]); self._single_over(pid)
                else: self._single_send(pid)
            return
        ok = await self.index_check(player_id, int(item["a"]), int(item["b"]), int(s["era"]))
        if self.singles.get(pid) is not s or s["gen"] != gen or s["over"]: return
        if ok:
            remaining = max(0, s["deadline"] - self.now()) // 1000
            s["score"] += 100 + remaining * 5
            s["last"] = {"type": "correct", "name": name}
            self._single_next(pid, False)
        else:
            s["lives"] -= 1                           # kilit yok: hemen yeni tahmin
            s["last"] = {"type": "wrong", "name": name}
            if s["lives"] <= 0: self._single_over(pid)
            else: self._single_send(pid)

    def single_answer(self, pid: int, option: int) -> None:   # blitz, versus
        s = self.singles.get(pid)
        if s is None or s["over"] or s["mode"] not in ("blitz", "versus"): return
        item = s["items"][s["idx"]]
        if s["mode"] == "versus":
            if option == int(item["_answer"]):
                bonus = int(max(0, s["deadline"] - self.now()) / 100.0)   # hız bonusu: kalan saniye × 10
                s["score"] += 100 + bonus; s["done"] += 1
                s["last"] = {"type": "correct", "option": option, "values": item["_values"], "bonus": bonus}
                self._single_next(pid, False)
            else:
                s["last"] = {"type": "wrong", "option": option, "answer": int(item["_answer"]), "values": item["_values"]}
                self._single_over(pid)
            return
        if option == int(item["_answer"]):
            s["score"] += int(round(100 * s["combo"])); s["combo"] = min(2.0, s["combo"] + 0.1); s["best_combo"] = max(s["best_combo"], s["combo"])
            s["last"] = {"type": "correct", "option": option}
            self._single_next(pid, False)
        else:
            s["last"] = {"type": "wrong", "option": option, "answer": int(item["_answer"])}
            self._single_over(pid)

    def single_team(self, pid: int, team_id: int, name: str) -> None:   # chain: sıradaki kulüp tahmini
        s = self.singles.get(pid)
        if s is None or s["over"] or s["mode"] != "chain": return
        if not self._allow("%d:guess" % pid, 30, 60000): return
        item = s["items"][s["idx"]]
        st = item["_steps"][s["step"]]
        if team_id == int(st["club_id"]):
            bonus = int(max(0, s["deadline"] - self.now()) / 1000.0) * 5
            s["score"] += 100 + bonus
            self._chain_advance(pid, {"type": "correct", "name": str(st["club"]), "gained": 100 + bonus})
        else:
            s["lives"] -= 1
            self._chain_advance(pid, {"type": "wrong", "name": name, "answer": str(st["club"])})

    def single_quit(self, pid: int) -> None:
        self.singles.pop(pid, None)

    # ---------- iç ----------
    def _chain_advance(self, pid: int, last: dict) -> None:
        """Zincirde bir adım bitti (doğru, yanlış ya da süre): cevap açılır, sıradaki adıma ya da oyuncuya geçilir."""
        s = self.singles[pid]
        s["last"] = last
        if s["lives"] <= 0: self._single_over(pid); return
        item = s["items"][s["idx"]]
        s["step"] += 1
        if s["step"] >= len(item["_steps"]):
            s["done"] += 1; self._single_next(pid, False)
        else:
            s["gen"] += 1; s["per_ms"] = CHAIN_STEP_MS; s["deadline"] = self.now() + CHAIN_STEP_MS
            self._single_send(pid)

    def _single_next(self, pid: int, first: bool) -> None:
        s = self.singles[pid]
        if not first: s["idx"] += 1
        if s["idx"] >= len(s["items"]): self._single_over(pid); return
        s["gen"] += 1; s["lock_until"] = 0
        mode, idx = s["mode"], s["idx"]
        if mode == "ladder": per_ms = max(10000, 20000 - 2000 * (idx // 5))
        elif mode == "career": per_ms = CAREER_REVEAL_MS; s["revealed"] = 1
        elif mode == "chain": per_ms = CHAIN_STEP_MS; s["step"] = 0
        elif mode == "versus": per_ms = max(4000, 9000 - 500 * (idx // 5))
        else: per_ms = max(3000, 8000 - 1000 * (idx // 5))
        s["deadline"] = self.now() + per_ms; s["per_ms"] = per_ms
        self._single_send(pid)

    def _tick_singles(self) -> None:
        now = self.now()
        for pid in list(self.singles):
            s = self.singles.get(pid)
            if s is None or s["over"] or s["deadline"] == 0 or now < s["deadline"]: continue
            item = s["items"][s["idx"]]
            mode = s["mode"]
            if mode == "career":
                if int(s["revealed"]) < len(item["clubs"]):      # bir kulüp daha aç
                    s["revealed"] += 1; s["last"] = {}
                    s["per_ms"] = CAREER_REVEAL_MS if int(s["revealed"]) < len(item["clubs"]) else CAREER_LAST_MS
                    s["deadline"] = now + int(s["per_ms"])
                    self._single_send(pid); continue
                s["lives"] -= 1
                s["last"] = {"type": "timeout", "answer": str(item["_name"])}
                if s["lives"] <= 0: self._single_over(pid)
                else: self._single_next(pid, False)
                continue
            if mode == "chain":
                s["lives"] -= 1
                self._chain_advance(pid, {"type": "timeout", "answer": str(item["_steps"][s["step"]]["club"])})
                continue
            if mode == "versus":
                s["last"] = {"type": "timeout", "answer": int(item["_answer"]), "values": item["_values"]}
                self._single_over(pid); continue
            s["last"] = {"type": "timeout"}
            if mode == "ladder":
                s["lives"] -= 1
                if s["lives"] <= 0: self._single_over(pid)
                else: self._single_next(pid, False)
            else:
                self._single_over(pid)

    def _single_over(self, pid: int) -> None:
        s = self.singles[pid]
        s["over"] = True; s["deadline"] = 0
        dev = self.profiles.get(pid, {}).get("device", "")
        if dev and int(s["score"]) > 0: self.spawn(self.acct_best(dev, s["mode"], int(s["score"])))
        self._single_send(pid)

    def _single_send(self, pid: int) -> None:
        s = self.singles[pid]
        now = self.now()
        item = s["items"][min(s["idx"], len(s["items"]) - 1)]
        mode = s["mode"]
        if mode == "career":
            pub = {"clubs": item["clubs"][:int(s["revealed"])], "total": len(item["clubs"]), "revealed": int(s["revealed"])}
        elif mode == "chain":
            steps = item["_steps"]; st = min(int(s["step"]), len(steps))
            pub = {"name": item["name"], "born": item.get("born"), "pos": item.get("pos"), "step": st, "steps_total": len(steps),
                   "history": [{"club": x["club"], "year": x.get("year"), "kind": x["kind"], "fee": x.get("fee"), "country": x.get("country"),
                                "defunct": x.get("defunct", False)} for x in steps[:st]]}
            if st < len(steps):      # ipucu: yıl, tür, bedel, gittiği ülke ve lig (ilk kulüp için de ülke/lig)
                pub["hint"] = {"year": steps[st].get("year"), "kind": steps[st]["kind"], "fee": steps[st].get("fee"),
                               "country": steps[st].get("country"), "league": steps[st].get("league")}
        elif mode == "versus":
            pub = {k: v for k, v in item.items() if not str(k).startswith("_")}
        else:
            pub = {"a_name": item.get("a_name", ""), "b_name": item.get("b_name", ""), "a": int(item.get("a", 0)), "b": int(item.get("b", 0)),
                   "a_defunct": item.get("a_defunct", False), "b_defunct": item.get("b_defunct", False)}
            if mode == "blitz": pub["options"] = item["options"]
        self.send(pid, {"t": "single_state", "d": {
            "mode": mode, "idx": s["idx"], "total": len(s["items"]), "lives": s["lives"], "score": s["score"], "combo": s["combo"],
            "done": int(s.get("done", 0)), "best_combo": s["best_combo"], "remaining_ms": max(0, s["deadline"] - now), "per_ms": s.get("per_ms", 0),
            "lock_ms": 0, "over": s["over"], "item": pub, "last": s.get("last", {}), "era": int(s.get("era", 0))}})
