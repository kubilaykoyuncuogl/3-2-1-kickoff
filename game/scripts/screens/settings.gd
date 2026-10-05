extends Control
## Ayarlar: Profil, Hesap, Ses, Görünüm, Dil, Diğer (docs/screens.md 0e)

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("menu.settings"), App.pop))
	var scroll := ScrollContainer.new(); scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var body := UI.vbox(4); body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(body); v.add_child(scroll)

	body.add_child(_section(T.t("set.profile")))
	var nick := LineEdit.new(); nick.text = App.nickname; nick.max_length = 16
	_style_input(nick)
	nick.text_changed.connect(func(t): App.nickname = t.strip_edges(); App.save_settings())
	nick.focus_exited.connect(func(): if Net.is_connected_to_server(): Game.c_hello())
	body.add_child(_row(T.t("set.nick"), nick))
	body.add_child(_section(T.t("set.account")))
	var acc := UI.option_card(App.nickname if App.linked else T.t("acct.guest_title"),
		(T.t("verified") if App.verified else T.t("acct.linked_chip")) if App.linked else T.t("acct.create"),
		null, UI.chevron("violet_ink" if App.linked else "muted"), App.linked, "surface", 64.0)
	acc.pressed.connect(func(): App.push(load("res://scripts/screens/account.gd").new()))
	body.add_child(acc)

	body.add_child(_section(T.t("set.sound")))
	var snd := _toggle(App.sound, func(on): App.sound = on; App.save_settings(); App.rebuild_top())
	body.add_child(_row(T.t("set.sound"), snd))
	var music := _slider(App.music_vol, func(x): App.music_vol = x; App.save_settings()); music.editable = App.sound
	body.add_child(_row(T.t("set.music"), music, not App.sound))
	var sfx := _slider(App.sfx_vol, func(x): App.sfx_vol = x; App.save_settings()); sfx.editable = App.sound
	body.add_child(_row(T.t("set.sfx"), sfx, not App.sound))
	body.add_child(_row(T.t("set.haptics"), _toggle(App.haptics, func(on): App.haptics = on; App.save_settings())))

	body.add_child(_section(T.t("set.look")))
	body.add_child(_row(T.t("set.theme"), UI.segment(["system", "light", "dark"], [T.t("theme.system"), T.t("theme.light"), T.t("theme.dark")], App.theme_mode,
		func(val): App.theme_mode = val; App.save_settings(); App.apply_theme(); App.rebuild_all())))
	body.add_child(_row(T.t("set.reduce_motion"), _toggle(App.reduce_motion, func(on): App.reduce_motion = on; App.save_settings())))
	body.add_child(_section(T.t("set.lang")))
	var langs: Array = T.available()
	body.add_child(_row(T.t("set.lang"), UI.segment(langs, langs.map(func(l): return str(l).to_upper()), App.lang,
		func(val): App.lang = val; App.save_settings(); T.load_lang(val); App.rebuild_all())))
	body.add_child(_section(T.t("set.other")))
	var howto := UI.button(T.t("menu.howto"), "ghost"); howto.pressed.connect(func(): App.push(load("res://scripts/screens/howto.gd").new()))
	body.add_child(howto)
	body.add_child(UI.label("3-2-1 Kickoff v0.1 beta", 11, 500, "muted"))      # cihaz kimliği hesabın anahtarı: ekranda gösterilmez

func _section(t: String) -> Control:
	var l := UI.eyebrow(t); l.add_theme_constant_override("line_spacing", 0)
	var m := MarginContainer.new(); m.add_theme_constant_override("margin_top", 14); m.add_theme_constant_override("margin_bottom", 4)
	m.add_child(l); return m

func _row(title: String, ctrl: Control, dim := false) -> Control:
	var p := PanelContainer.new()
	var st := StyleBoxFlat.new(); st.bg_color = Color.TRANSPARENT; st.border_color = UI.c("line"); st.set_border_width_all(0); st.border_width_bottom = 2
	st.content_margin_top = 10; st.content_margin_bottom = 10
	p.add_theme_stylebox_override("panel", st)
	var h := UI.hbox(12)
	var l := UI.label(title, 14, 600, "muted" if dim else "fg"); l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(l); h.add_child(ctrl); p.add_child(h)
	if dim: p.modulate.a = 0.55
	return p

func _toggle(on: bool, cb: Callable) -> CheckButton:
	var c := CheckButton.new(); c.button_pressed = on
	c.toggled.connect(cb)
	return c

func _slider(v: float, cb: Callable) -> HSlider:
	var s := HSlider.new(); s.min_value = 0; s.max_value = 1; s.step = 0.05; s.value = v
	s.custom_minimum_size = Vector2(140, 24)
	s.value_changed.connect(cb)
	return s

func _style_input(e: LineEdit) -> void:
	e.custom_minimum_size = Vector2(160, 40)
	e.add_theme_font_override("font", UI.font(600)); e.add_theme_font_size_override("font_size", 14)
	e.add_theme_color_override("font_color", UI.c("fg"))
	var st := UI.box("surface", "line_strong", 10); st.content_margin_top = 6; st.content_margin_bottom = 6
	e.add_theme_stylebox_override("normal", st); e.add_theme_stylebox_override("focus", st)
