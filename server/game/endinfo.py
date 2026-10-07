"""Koşu sonu kartı için bilgiler: "seni yakan soru" (burn) ve "biliyor muydun" (fact).
Sunucu yapılandırılmış veri gönderir, cümleyi istemci kendi dilinde kurar. Emin olunmayan bilgi gönderilmez
(ör. gol sayısı 0 ya da eksikse cümle golsüz kurulur); kart paylaşılacağı için yanlış sayı yazmaktansa satır hiç çıkmaz."""
import asyncio, random


def club_fact_kinds(p: dict) -> list:
    """Haftanın maçı "biliyor muydun" cümlesinin çeşitleri; yalnızca o oyuncunun verisiyle kurulabilenler döner, biri rastgele seçilir.
    base: maç + gol + asist · apps: yalnız maç · seasons: sezon + maç · minutes: dakika (≈ tam maç) · cards: sarı / kırmızı · rate: kaç maçta bir gol
    contrib: gol + asist katkısı · both: iki kulübün de formasını giymiş. Eşikler anlamsız cümleyi eler (3 maçta "her 3 maçta bir gol" gibi)."""
    apps = p.get("apps") or 0; goals = p.get("goals"); assists = p.get("assists"); mins = p.get("minutes") or 0
    kinds = ["base"] if goals is not None and assists is not None else ["apps"]
    if (p.get("seasons") or 0) >= 3: kinds.append("seasons")
    if apps >= 20 and mins >= apps * 30: kinds.append("minutes")      # dakika verisi eksik sezonları olanlar elenir
    if (p.get("yellow") or 0) >= 8: kinds.append("cards")
    if goals is not None and goals >= 10 and apps <= goals * 6: kinds.append("rate")      # yalnızca golcüler: "her 28 maçta bir gol" bilgi değil
    if goals is not None and assists is not None and goals >= 5 and assists >= 5: kinds.append("contrib")
    if p.get("both"): kinds.append("both")
    return kinds


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
            if ans.get("names"): out["fact"] = {"kind": "pair_players", "a": item.get("a_name", ""), "b": item.get("b_name", ""), "total": int(ans.get("total", 0)), "names": ans["names"][:5]}
        elif mode == "blitz":
            opts = item.get("options") or []; ai = int(item.get("_answer", 0)); name = opts[ai] if ai < len(opts) else ""
            if failed: out["burn"] = {"kind": "pick", "a": item.get("a_name", ""), "b": item.get("b_name", ""), "answer": name,
                                      "picked": opts[int(last["option"])] if last.get("type") == "wrong" and int(last.get("option", -1)) in range(len(opts)) else None}
            sp = await asyncio.to_thread(ix.club_spans, int(item["_answer_id"]), [int(item["a"]), int(item["b"])])
            # yıl aralıkları [ilk, son]; son None = hâlâ orada. Kronolojik sırayla verilir.
            parts = sorted(((item.get("a_name", ""), sp.get(int(item["a"])) or []), (item.get("b_name", ""), sp.get(int(item["b"])) or [])), key=lambda x: x[1][0][0] if x[1] else 9999)
            out["fact"] = {"kind": "two_clubs", "name": name, "spells": [{"club": c, "spans": s_[:3]} for c, s_ in parts]}      # spans: [[ilk, son | None], …]
        elif mode in ("career", "weekly_career"):
            if failed: out["burn"] = {"kind": "who", "answer": str(item["_name"]), "tried": last.get("name") if last.get("type") == "wrong" else None, "first": item["clubs"][0]["club"] if item.get("clubs") else ""}
            # haftanın maçında kimlik veri dosyasından gelir; index yeniden üretildiyse başka oyuncuya denk gelebilir: ad tutmuyorsa sayı yazılmaz
            su = await asyncio.to_thread(ix.player_summary, int(item["_player_id"]))
            if su and mode == "weekly_career" and su.get("name") != item["_name"]: su = None
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
                if p: out["fact"] = {"kind": "club_stats", "v": random.choice(club_fact_kinds(p)), "name": p["name"], "club": club, "apps": p.get("apps") or 0, "goals": p.get("goals"), "assists": p.get("assists"),
                                     "seasons": p.get("seasons") or 0, "yellow": p.get("yellow") or 0, "red": p.get("red") or 0, "minutes": p.get("minutes") or 0}
            else:
                ids = item.get("_ids") or []
                su = await asyncio.to_thread(ix.player_summary, int(ids[ai])) if len(ids) == 2 else None
                if su and su["apps"] > 0: out["fact"] = {"kind": "player", "name": su["name"], "apps": su["apps"], "goals": su["goals"], "n_clubs": su["n_clubs"]}
        return out
