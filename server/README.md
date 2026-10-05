# Sunucu

Aynı Godot projesi headless çalışır:
```
godot --headless --path ../game -- --server --port 9080
```
Prod için: küçük bir VPS + `Dockerfile` (Godot headless export template). İndex (`game/data/index.sqlite`) sunucuda belleğe alınır; istemciye gitmez.
