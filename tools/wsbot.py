#!/usr/bin/env python3
"""Uçtan uca test botu (game/scripts/test_bot.gd'nin Python/WebSocket karşılığı).

  python3 tools/wsbot.py --bot ali --team galatasaray --guess sneijder            Ara ile eşleş, takım seç, hazır de, turda tahmin et
  python3 tools/wsbot.py --bot ali --single ladder --guess zidane --era 2         tek oyunculu
  python3 tools/wsbot.py --bot ali --acct                                         hesap senaryosu
  python3 tools/wsbot.py --bot ali --create                                       oda kur, kodu yazdır   /  --join <kod>
Seçenekler: --url ws://127.0.0.1:9081/ws  --seconds 30  --delay 0  --era 0  --scope all  --drop 5 (5 sn sonra bağlantıyı kes, 3 sn sonra geri gel)
Durumları stdout'a yazar; satırlar test_bot.gd ile aynı biçimde ([ad] state=… / sugg … / single …)."""
import argparse, asyncio, json, random, sys, time

import websockets

ap = argparse.ArgumentParser()
ap.add_argument("--bot", default="bot"); ap.add_argument("--team", default="galatasaray"); ap.add_argument("--guess", default="sneijder")
ap.add_argument("--single", default=""); ap.add_argument("--era", type=int, default=0); ap.add_argument("--scope", default="all")
ap.add_argument("--seconds", type=float, default=30); ap.add_argument("--delay", type=float, default=0)
ap.add_argument("--url", default="ws://127.0.0.1:9081/ws"); ap.add_argument("--acct", action="store_true")
ap.add_argument("--create", action="store_true"); ap.add_argument("--join", default=""); ap.add_argument("--drop", type=float, default=0)
ap.add_argument("--proto", type=int, default=5); ap.add_argument("--round", type=int, default=15)
A = ap.parse_args()
nick = A.bot
device = "dev-" + nick + "-" + "x" * max(0, 8 - len(nick))
picked = False; guessed_gen = None; last_single = None


def log(*a): print("[%s]" % nick, *a, flush=True)


async def run(ws, drop_once, rejoin=False):
    global picked
    await ws.send(json.dumps({"t": "hello", "nick": nick, "device": device, "proto": A.proto}))
    started = time.time(); said_start = rejoin; pending = {"pick": False, "ready": False, "guess": False}
    if A.acct:
        steps = ["create", "create", "link_code", "logout", "link_code", "delete"]
    async for raw in ws:
        m = json.loads(raw); t = m.get("t")
        if t == "welcome": log("connected pid=%s proto=%s" % (m["pid"], m["proto"])); continue
        if t == "err": log("ERR", m["key"]); continue
        if t == "profile_state":
            d = m["d"]; log("profile linked=%s nick=%s elo=%s devices=%s" % (d.get("linked"), d.get("nick"), d.get("elo"), d.get("devices")))
            if not said_start:
                said_start = True
                if A.acct: await ws.send(json.dumps({"t": "acct", "op": steps.pop(0)}))
                elif A.single: await ws.send(json.dumps({"t": "single_start", "mode": A.single, "scope": A.scope, "era": A.era}))
                elif A.create: await ws.send(json.dumps({"t": "create_room", "scope": A.scope, "era": A.era, "round": A.round}))
                elif A.join: await ws.send(json.dumps({"t": "join_room", "code": A.join}))
                else: await ws.send(json.dumps({"t": "find_match", "scope": A.scope, "era": A.era, "round": A.round}))
            continue
        if t == "acct_result":
            log("acct", m["d"])
            if steps: await ws.send(json.dumps({"t": "acct", "op": steps.pop(0)}))
            else: return
            continue
        if t == "suggest_result":
            lst = m["list"]
            if not lst: log("no suggestions for", m["kind"]); continue
            log("sugg %s: %s" % (m["kind"], [x["name"] for x in lst[:3]]))
            if m["kind"] == "team" and not picked:
                for it in lst:
                    if not it.get("used", False):
                        picked = True; await ws.send(json.dumps({"t": "pick_team", "team_id": int(it["id"]), "team_name": it["name"]})); break
                else: log("all suggested teams used")
            elif m["kind"] == "player":
                msg = "single_guess" if A.single else "guess"
                await ws.send(json.dumps({"t": msg, "player_id": int(lst[0]["id"]), "name": lst[0]["name"]}))
            continue
        if t == "single_state":
            await on_single(ws, m["d"]); continue
        if t == "room_state":
            d = m["d"]
            if d.get("searching"): log("searching band=%s waiting=%s" % (d.get("band"), d.get("waiting"))); continue
            if d.get("left"): log("left"); continue
            players = d.get("players", []); me = d.get("me")
            scores = ["%s:%s" % (p["nick"], p["score"]) for p in players]
            log("state=%s code=%s phase=%s last=%s scores=%s" % (d["state"], d.get("code"), d.get("phase_ms"), json.dumps(d.get("last", {}), ensure_ascii=False), scores))
            if A.create and len(players) == 1: log("ROOM CODE", d.get("code"))
            mine = next((p for p in players if p["pid"] == me), {})
            if d["state"] != 1: pending["pick"] = False; pending["ready"] = False
            if d["state"] != 4: pending["guess"] = False
            if d["state"] == 1:
                if not mine.get("picked"):
                    picked = False
                    if not pending["pick"]:          # gecikme seçim aşaması başına bir kez (her oda güncellemesinde değil)
                        pending["pick"] = True
                        if A.delay: await asyncio.sleep(A.delay)
                        await ws.send(json.dumps({"t": "suggest", "kind": "team", "q": A.team}))
                elif not mine.get("ready") and not pending["ready"]:
                    pending["ready"] = True
                    await ws.send(json.dumps({"t": "set_ready"}))
            elif d["state"] == 4:
                if drop_once and A.drop and time.time() - started > A.drop:
                    log("dropping connection"); return "drop"
                if not pending["guess"] or (d.get("last", {}).get("type") == "wrong" and d["last"].get("pid") == me):
                    pending["guess"] = True
                    await asyncio.sleep(A.delay)
                    await ws.send(json.dumps({"t": "suggest", "kind": "player", "q": A.guess}))
            elif d["state"] == 6:
                log("over winner=%s me=%s" % (d.get("winner"), me))
                for h in d.get("history") or []: log("  tur:", json.dumps(h, ensure_ascii=False))
                return


async def on_single(ws, d):
    it = d["item"]; mode = d["mode"]
    if mode == "career": log("career idx=%s lives=%s score=%s revealed=%s/%s last=%s clubs=%s" % (d["idx"], d["lives"], d["score"], it.get("revealed"), it.get("total"), d.get("last"), it.get("clubs")))
    elif mode == "chain": log("chain idx=%s step=%s/%s lives=%s score=%s name=%s hint=%s last=%s" % (d["idx"], it.get("step"), it.get("steps_total"), d["lives"], d["score"], it.get("name"), it.get("hint"), d.get("last")))
    elif mode == "versus": log("versus idx=%s score=%s cat=%s %s shown=%s last=%s" % (d["idx"], d["score"], it.get("cat"), it.get("names"), it.get("shown"), d.get("last")))
    else: log("single idx=%s lives=%s score=%s over=%s item=%s×%s opts=%s last=%s" % (d["idx"], d["lives"], d["score"], d["over"], it.get("a_name"), it.get("b_name"), it.get("options", []), d.get("last")))
    if d["over"]: log("over score=%s done=%s" % (d["score"], d.get("done"))); return
    await asyncio.sleep(A.delay)
    if mode == "ladder": await ws.send(json.dumps({"t": "suggest", "kind": "player", "q": A.guess}))
    elif mode in ("blitz", "versus"): await ws.send(json.dumps({"t": "single_answer", "option": random.randrange(5 if mode == "blitz" else 2)}))
    elif mode == "career": await ws.send(json.dumps({"t": "single_guess", "player_id": 0, "name": A.guess}))
    elif mode == "chain": await ws.send(json.dumps({"t": "single_team", "team_id": 0, "name": A.guess}))


async def main():
    log("start", vars(A))
    try:
        async with websockets.connect(A.url) as ws:
            res = await asyncio.wait_for(run(ws, True), A.seconds)
        if res == "drop":
            await asyncio.sleep(3)
            log("reconnecting")
            async with websockets.connect(A.url) as ws:
                await asyncio.wait_for(run(ws, False, rejoin=True), A.seconds)
    except asyncio.TimeoutError: log("time up")
    except (OSError, websockets.exceptions.WebSocketException) as e: log("connect failed", repr(e))


asyncio.run(main())
