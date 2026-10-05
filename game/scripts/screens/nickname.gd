extends Control
## İlk açılış: takma ad (tek alan + Devam)

func _ready() -> void:
	var v := UI.page(); add_child(v)
	# Her şey üstte: mobilde klavye açılınca kutu ve Devam görünür kalsın
	v.add_child(UI.wordmark())
	v.add_child(UI.label(T.t("nick.title"), 22, 800))
	v.add_child(UI.label(T.t("nick.sub"), 13, 500, "muted"))
	var inp := LineEdit.new()
	inp.placeholder_text = T.t("nick.placeholder"); inp.max_length = 16; inp.custom_minimum_size.y = 56
	inp.add_theme_font_override("font", UI.font(700)); inp.add_theme_font_size_override("font_size", 20)
	inp.add_theme_color_override("font_color", UI.c("fg")); inp.add_theme_color_override("font_placeholder_color", UI.c("muted"))
	var st := UI.box("surface", "violet_fill", 14); inp.add_theme_stylebox_override("normal", st); inp.add_theme_stylebox_override("focus", st)
	v.add_child(inp)
	var go := UI.button(T.t("continue"), "violet")
	go.disabled = true
	inp.text_changed.connect(func(t): go.disabled = t.strip_edges().length() < 2)
	var submit := func():
		App.nickname = inp.text.strip_edges(); App.save_settings()
		if Net.is_connected_to_server(): Game.c_hello()
		App.pop(); App.rebuild_top()
	go.pressed.connect(submit)
	inp.text_submitted.connect(func(_t):
		if not go.disabled: submit.call())
	v.add_child(go)
	v.add_child(UI.label(T.t("nick.hint"), 12, 500, "muted"))
	v.add_child(UI.spacer())
	inp.call_deferred("grab_focus")
