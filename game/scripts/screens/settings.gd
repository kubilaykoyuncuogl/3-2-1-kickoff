extends Control
## Ayarlar: hesap, takma ad, ses, titreşim, tema, hareket, dil, nasıl oynanır; tek ekran, kaydırmasız

func _ready() -> void:
	# Tek ekrana sığar: bölüm başlıkları yok, satırlar sıkı. Kaydırma kutusu yalnızca çok kısa pencereler için yedek.
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("menu.settings"), App.pop))
	var scroll := ScrollContainer.new(); scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var body := UI.vbox(0); body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(body); v.add_child(scroll)

	var acc := UI.option_card(App.nickname if App.linked else T.t("acct.guest_title"),
		(T.t("verified") if App.verified else T.t("acct.linked_chip")) if App.linked else T.t("acct.create"),
		null, UI.chevron("violet_ink" if App.linked else "muted"), App.linked, "surface", 60.0)
	acc.pressed.connect(func(): App.push(load("res://scripts/screens/account.gd").new()))
	body.add_child(acc)
	var nick := LineEdit.new(); nick.text = App.nickname; nick.max_length = 16
	_style_input(nick)
	nick.text_changed.connect(func(t): App.nickname = t.strip_edges(); App.save_settings())
	nick.focus_exited.connect(func(): if Net.is_connected_to_server(): Game.c_hello())
	body.add_child(_row(T.t("set.nick"), nick))
	# ses düzeyi kaydırıcıları oyuna ses eklenince geri gelecek (docs/TODO.md); ayarları App'te duruyor
	body.add_child(_row(T.t("set.sound"), _toggle(App.sound, func(on): App.sound = on; App.save_settings())))
	body.add_child(_row(T.t("set.haptics"), _toggle(App.haptics, func(on): App.haptics = on; App.save_settings())))
	body.add_child(_row(T.t("set.theme"), UI.segment(["system", "light", "dark"], [T.t("theme.system"), T.t("theme.light"), T.t("theme.dark")], App.theme_mode,
		func(val): App.theme_mode = val; App.save_settings(); App.apply_theme(); App.rebuild_all())))
	body.add_child(_row(T.t("set.reduce_motion"), _toggle(App.reduce_motion, func(on): App.reduce_motion = on; App.save_settings())))
	var langs: Array = T.available()
	body.add_child(_row(T.t("set.lang"), UI.segment(langs, langs.map(func(l): return str(l).to_upper()), App.lang,
		func(val): App.lang = val; App.save_settings(); T.load_lang(val); App.rebuild_all())))
	var gap := Control.new(); gap.custom_minimum_size.y = 12; body.add_child(gap)
	var howto := UI.button(T.t("menu.howto"), "line"); howto.pressed.connect(func(): App.push(load("res://scripts/screens/howto.gd").new()))
	body.add_child(howto)
	var ver := UI.label("3-2-1 Kickoff v0.1 beta", 11, 500, "muted"); ver.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER      # cihaz kimliği hesabın anahtarı: ekranda gösterilmez
	var vm := MarginContainer.new(); vm.add_theme_constant_override("margin_top", 10); vm.add_child(ver); body.add_child(vm)

func _row(title: String, ctrl: Control, dim := false) -> Control:
	var p := PanelContainer.new()
	var st := StyleBoxFlat.new(); st.bg_color = Color.TRANSPARENT; st.border_color = UI.c("line"); st.set_border_width_all(0); st.border_width_bottom = 2
	st.content_margin_top = 7; st.content_margin_bottom = 7
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

func _style_input(e: LineEdit) -> void:
	e.custom_minimum_size = Vector2(160, 40)
	e.add_theme_font_override("font", UI.font(600)); e.add_theme_font_size_override("font_size", 14)
	e.add_theme_color_override("font_color", UI.c("fg"))
	var st := UI.box("surface", "line_strong", 10); st.content_margin_top = 6; st.content_margin_bottom = 6
	e.add_theme_stylebox_override("normal", st); e.add_theme_stylebox_override("focus", st)
