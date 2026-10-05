extends Control
## Giriş: sunucuda hiçbir UI kurulmaz; istemcide sayfa yığını başlar.

func _ready() -> void:
	print("[main] ready server=", Net.is_server)
	if Net.is_server:
		return
	if "--smoke" in OS.get_cmdline_user_args():
		add_child(load("res://scripts/smoke.gd").new()); return
	if "--bot" in OS.get_cmdline_user_args():
		add_child(load("res://scripts/test_bot.gd").new()); return
	App.bind_root(self)
	App.push(load("res://scripts/screens/menu.gd").new())
	Game.error.connect(func(msg): print("[err] ", msg))
	var oda := ""
	if OS.has_feature("web"):
		oda = str(JavaScriptBridge.eval("new URLSearchParams(location.search).get('oda') || ''"))
	Net.connected.connect(func():
		Game.c_hello()
		if oda != "" and App.nickname != "":
			App.push(load("res://scripts/screens/online.gd").new())
			Game.c_join_room(oda); oda = "")
	Net.connect_to_server()
