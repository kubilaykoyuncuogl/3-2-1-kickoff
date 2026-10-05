extends Control
## Tek oyna, 2. adım: kulüp kapsamı. Alt alta üç ikonlu düğme: Tümü (dünya), Üst ligler (taç), 5 büyük lig (5).
var mode := "ladder"

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Beşte Bir", App.pop))
	v.add_child(UI.label("Hangi kulüpler?", 22, 800))
	v.add_child(UI.label("En iyin: %d" % int(App.best.get(mode, 0)), 13, 500, "muted"))
	for sc in App.SCOPES:
		v.add_child(UI.scope_button(sc, App.scope == sc, _start))
	v.add_child(UI.spacer())
	if not Net.is_connected_to_server(): Net.connect_to_server()

func _start(scope: String) -> void:
	App.scope = scope; App.save_settings()
	if not Net.is_connected_to_server():
		Game.error.emit("Sunucuya bağlanılıyor…"); Net.connect_to_server(); return
	var play = load("res://scripts/screens/single_play.gd").new(); play.mode = mode
	App.push(play); Game.c_single_start(mode)
