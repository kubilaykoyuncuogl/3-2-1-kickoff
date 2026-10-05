extends Control
## Tek oyna: Klasik merdiven ve Blitz. Her başlatmada yeni merdiven / soru seti; kilit yok; en iyi skor cihazda.

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("menu.single"), App.pop))
	v.add_child(UI.label(T.t("single.intro"), 13, 500, "muted"))
	v.add_child(_mode_card(T.t("mode.ladder"), T.t("mode.ladder_sub"), "ladder"))
	v.add_child(_mode_card(T.t("mode.blitz"), T.t("mode.blitz_sub"), "blitz"))
	v.add_child(UI.spacer())
	if not Net.is_connected_to_server(): Net.connect_to_server()

func _mode_card(title: String, sub: String, mode: String) -> Control:
	var b := Button.new()
	b.custom_minimum_size.y = 96
	b.add_theme_stylebox_override("normal", UI.box("amber_soft", "", 16, 0))
	b.add_theme_stylebox_override("hover", UI.box("amber_soft", "amber_fill", 16))
	b.add_theme_stylebox_override("pressed", UI.box("amber_soft", "amber_fill", 16))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var v := UI.vbox(2); v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); v.offset_left = 16; v.offset_right = -16; v.offset_top = 14; v.offset_bottom = -14
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var h := UI.hbox(8); var t := UI.label(title, 18, 800, "amber_ink"); t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(t); h.add_child(UI.label(T.t("single.best") % int(App.best.get(mode, 0)), 13, 700, "amber_ink"))
	v.add_child(h)
	var s := UI.label(sub, 12, 500, "amber_ink"); s.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; v.add_child(s)
	for ch in v.get_children(): ch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for ch in h.get_children(): ch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	b.pressed.connect(func():
		var sc = load("res://scripts/screens/single_scope.gd").new(); sc.mode = mode
		App.push(sc))
	return b
