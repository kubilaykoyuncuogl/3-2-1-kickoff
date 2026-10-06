#!/usr/bin/env python3
"""Başsız Chrome'u gerçek zamanlı sürüp ekran görüntüsü alır (CDP). Süresi dolan koşu, maç sonu gibi beklemek gereken ekranlar için.

  .venv/bin/python tools/cdp_shot.py OUT.png URL [--wait 12] [--size 400x880] [--click "x,y@saniye" ...] [--type "metin@saniye" ...]
Önce Expo web çalışıyor olmalı (./run_local.sh). --click / --type verilen saniyede uygulanır (sayfa açılışından itibaren)."""
import argparse, asyncio, base64, json, subprocess, tempfile, time, urllib.request, shutil

import websockets

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("url"); ap.add_argument("--wait", type=float, default=8); ap.add_argument("--size", default="400x880")
ap.add_argument("--click", action="append", default=[]); ap.add_argument("--type", action="append", default=[], dest="types")
ap.add_argument("--port", type=int, default=9333)
A = ap.parse_args()
W, H = map(int, A.size.split("x"))


async def main():
    prof = tempfile.mkdtemp()
    proc = subprocess.Popen(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", f"--user-data-dir={prof}", f"--remote-debugging-port={A.port}",
                             f"--window-size={W},{H}", "--hide-scrollbars", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{A.port}/json", timeout=1)); break
            except Exception: time.sleep(0.2)
        tab = next(t for t in tabs if t["type"] == "page")
        async with websockets.connect(tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            n = 0
            async def cmd(method, **params):
                nonlocal n; n += 1; mid = n
                await ws.send(json.dumps({"id": mid, "method": method, "params": params}))
                while True:
                    m = json.loads(await ws.recv())
                    if m.get("id") == mid: return m.get("result", {})
            await cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1, mobile=False)
            await cmd("Page.navigate", url=A.url)
            t0 = time.time()
            events = [(float(c.rsplit("@", 1)[1]), "click", c.rsplit("@", 1)[0]) for c in A.click] + [(float(c.rsplit("@", 1)[1]), "type", c.rsplit("@", 1)[0]) for c in A.types]
            for at, kind, arg in sorted(events):
                await asyncio.sleep(max(0, at - (time.time() - t0)))
                if kind == "click":
                    x, y = map(float, arg.split(","))
                    for typ in ("mousePressed", "mouseReleased"):
                        await cmd("Input.dispatchMouseEvent", type=typ, x=x, y=y, button="left", clickCount=1)
                else:
                    await cmd("Input.insertText", text=arg)
            await asyncio.sleep(max(0, A.wait - (time.time() - t0)))
            r = await cmd("Page.captureScreenshot", format="png")
            open(A.out, "wb").write(base64.b64decode(r["data"]))
    finally:
        proc.terminate(); shutil.rmtree(prof, ignore_errors=True)

asyncio.run(main()); print(A.out)
