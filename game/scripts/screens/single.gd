extends Control
## Tek oyna: Klasik merdiven ve Blitz. Her başlatmada yeni merdiven / soru seti; kilit yok; en iyi skor cihazda.

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("menu.single"), App.pop))
	v.add_child(UI.label(T.t("single.intro"), 13, 500, "muted"))
	v.add_child(_mode_card(T.t("mode.ladder"), T.t("mode.ladder_sub"), "ladder"))
	v.add_child(_mode_card(T.t("mode.blitz"), T.t("mode.blitz_sub"), "blitz"))
	v.add_child(_mode_card(T.t("mode.career"), T.t("mode.career_sub"), "career"))
	v.add_child(_mode_card(T.t("mode.chain"), T.t("mode.chain_sub"), "chain"))
	v.add_child(_mode_card(T.t("mode.versus"), T.t("mode.versus_sub"), "versus"))
	v.add_child(UI.spacer())
	if not Net.is_connected_to_server(): Net.connect_to_server()

func _mode_card(title: String, sub: String, mode: String) -> Control:
	var tail := UI.hbox(8)
	var best := int(App.best.get(mode, 0))
	if best > 0:
		var bc := UI.chip("%s %d" % [T.t("single.best_short"), best], "amber"); bc.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		(bc.get_theme_stylebox("panel") as StyleBoxFlat).bg_color = UI.c("surface")
		tail.add_child(bc)
	tail.add_child(UI.chevron("amber_ink"))
	var b := UI.option_card(title, sub, null, tail, false, "amber", 92.0)
	b.pressed.connect(func():
		if mode in ["ladder", "blitz"]:      # kulüp kapsamı yalnızca kulüp çifti modlarında
			var sc = load("res://scripts/screens/single_scope.gd").new(); sc.mode = mode
			App.push(sc); return
		if not Net.is_connected_to_server():
			Game.error.emit(T.t("net.connecting")); Net.connect_to_server(); return
		App.push(load("res://scripts/screens/%s_play.gd" % mode).new()); Game.c_single_start(mode))
	return b
