extends Control
## Giriş: sunucuda hiçbir UI kurulmaz; istemcide sayfa yığını başlar.

func _ready() -> void:
	print("[main] ready server=", Net.is_server)
	if Net.is_server:
		return
	if "--bot" in OS.get_cmdline_user_args():
		add_child(load("res://scripts/test_bot.gd").new()); return
	App.bind_root(self)
	App.push(load("res://scripts/screens/menu.gd").new())
	Game.error.connect(func(msg): print("[err] ", msg))
