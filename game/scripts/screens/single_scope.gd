extends Control
## Tek oyna, 2. adım: kulüp kapsamı. Alt alta üç ikonlu düğme: Tümü (dünya), Üst ligler (taç), 5 büyük lig (5).
var mode := "ladder"

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("mode.ladder") if mode == "ladder" else T.t("mode.blitz"), App.pop))
	v.add_child(UI.label(T.t("scope.title_q"), 22, 800))
	v.add_child(UI.label(T.t("scope.best") % int(App.best.get(mode, 0)), 13, 500, "muted"))
	for sc in App.SCOPES:
		v.add_child(UI.scope_button(sc, App.scope == sc, _start))
	v.add_child(UI.spacer())
	if not Net.is_connected_to_server(): Net.connect_to_server()

func _start(scope: String) -> void:
	App.scope = scope; App.save_settings()
	var e = load("res://scripts/screens/single_era.gd").new(); e.mode = mode
	App.push(e)
