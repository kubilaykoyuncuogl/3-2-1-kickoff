"""Koşu sonu kartı için bilgiler: "seni yakan soru" (burn) ve "biliyor muydun" (fact).
Sunucu yapılandırılmış veri gönderir, cümleyi istemci kendi dilinde kurar. Emin olunmayan bilgi gönderilmez
(ör. gol sayısı 0 ya da eksikse cümle golsüz kurulur); kart paylaşılacağı için yanlış sayı yazmaktansa satır hiç çıkmaz."""
import asyncio


class EndInfoMixin:
    async def _single_end(self, pid: int, s: dict) -> None:
        """Koşu bitti: kart bilgisini hesaplar ve durumu yeniden gönderir (ilk "bitti" durumu beklemeden gitmiştir)."""
        try: s["end"] = await self._end_info(s)
        except Exception as e:
            print("[end] info failed:", s.get("mode"), repr(e), flush=True); return
        if self.singles.get(pid) is s: self._single_send(pid)

    async def _end_info(self, s: dict) -> dict:
        ix = self.index; mode = s["mode"]; last = s.get("last") or {}
        item = s["items"][min(s["idx"], len(s["items"]) - 1)]
        failed = last.get("type") in ("wrong", "timeout")
        out: dict = {"burn": None, "fact": None}
        if mode == "ladder":
            ans = await asyncio.to_thread(ix.pair_answers, int(item["a"]), int(item["b"]), 5, int(s.get("era", 0)))
            if failed: out["burn"] = {"kind": "pair", "a": item.get("a_name", ""), "b": item.get("b_name", ""), "tried": last.get("name") if last.get("type") == "wrong" else None}
            if ans.get("names"): out["fact"] = {"kind": "pair_players", "a": item.get("a_name", ""), "b": item.get("b_name", ""), "total": int(ans.get("total", 0)), "names": ans["names"][:4]}
        elif mode == "blitz":
            opts = item.get("options") or []; ai = int(item.get("_answer", 0)); name = opts[ai] if ai < len(opts) else ""
            if failed: out["burn"] = {"kind": "pick", "a": item.get("a_name", ""), "b": item.get("b_name", ""), "answer": name,
                                      "picked": opts[int(last["option"])] if last.get("type") == "wrong" and int(last.get("option", -1)) in range(len(opts)) else None}
            ys = await asyncio.to_thread(ix.club_join_years, int(item["_answer_id"]), [int(item["a"]), int(item["b"])])
            out["fact"] = {"kind": "two_clubs", "name": name, "a": item.get("a_name", ""), "ay": ys.get(int(item["a"])), "b": item.get("b_name", ""), "by": ys.get(int(item["b"]))}
        elif mode == "career":
            if failed: out["burn"] = {"kind": "who", "answer": str(item["_name"]), "tried": last.get("name") if last.get("type") == "wrong" else None, "first": item["clubs"][0]["club"] if item.get("clubs") else ""}
            su = await asyncio.to_thread(ix.player_summary, int(item["_player_id"]))
            out["fact"] = {"kind": "career", "name": str(item["_name"]), "clubs": [c["club"] for c in item.get("clubs", [])], "apps": (su or {}).get("apps", 0), "goals": (su or {}).get("goals", 0)}
        elif mode == "chain":
            steps = item.get("_steps") or []; k = min(int(s.get("step", 0)), len(steps) - 1)
            if steps:
                st = steps[k]; prev = steps[k - 1]["club"] if k > 0 else None
                if failed: out["burn"] = {"kind": "club", "player": item.get("name", ""), "answer": st["club"], "tried": last.get("name") if last.get("type") == "wrong" else None}
                out["fact"] = {"kind": "move", "name": item.get("name", ""), "year": st.get("year"), "from": prev, "to": st["club"], "move": st.get("kind"), "fee": st.get("fee")}
        elif mode in ("versus", "weekly"):
            vals = item.get("_values") or [0, 0]; ai = int(item.get("_answer", 0)); names = item.get("names") or ["", ""]
            if failed: out["burn"] = {"kind": "vs", "cat": item.get("cat"), "fmt": item.get("fmt", "int"), "names": names, "values": vals,
                                      "picked": int(last["option"]) if last.get("type") == "wrong" else None}
            if mode == "weekly":
                p = (item.get("_p") or [None, None])[ai]; club = (item.get("_clubs") or ["", ""])[ai]
                if p: out["fact"] = {"kind": "club_stats", "name": p["name"], "club": club, "apps": p.get("apps") or 0, "goals": p.get("goals"), "assists": p.get("assists"), "seasons": p.get("seasons") or 0}
            else:
                ids = item.get("_ids") or []
                su = await asyncio.to_thread(ix.player_summary, int(ids[ai])) if len(ids) == 2 else None
                if su and su["apps"] > 0: out["fact"] = {"kind": "player", "name": su["name"], "apps": su["apps"], "goals": su["goals"], "n_clubs": su["n_clubs"]}
        return out
