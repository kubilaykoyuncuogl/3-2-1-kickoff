"""Web build'i yerelde servis eder. Godot web export SharedArrayBuffer istemese de (thread_support=false) COOP/COEP başlıklarını verir.
Kullanım: python server/serve_web.py [port=8080] [dir=build/web]
"""
import sys, http.server, functools
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
root = sys.argv[2] if len(sys.argv) > 2 else "build/web"
class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".wasm": "application/wasm", ".pck": "application/octet-stream"}
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
http.server.ThreadingHTTPServer(("0.0.0.0", port), functools.partial(H, directory=root)).serve_forever()
