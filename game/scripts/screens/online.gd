extends Control
## Online oyna: Elo kartı, Ara, Oda kur, Odaya katıl. Arama / oda bekleme de bu sayfada (mode değişkeni).
## Oda 2 kişi olunca match.gd'ye geçilir.

var mode := "menu"      # menu | searching | room | join
var body: VBoxContainer
var status: Label
var _since := 0

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav("Online oyna", _back))
	body = UI.vbox(12); body.size_flags_vertical = Control.SIZE_EXPAND_FILL; v.add_child(body)
	Game.room_changed.connect(_on_room)
	Game.error.connect(_on_error)
	Game.profile_changed.connect(_on_profile)
	Net.connected.connect(_on_connected); Net.connect_failed.connect(_on_failed); Net.disconnected.connect(_on_failed)
	if not Net.is_connected_to_server(): Net.connect_to_server()
	_render()

func _on_profile(_d: Dictionary) -> void:
	if mode == "menu": _render()

func _exit_tree() -> void:
	if Game.profile_changed.is_connected(_on_profile): Game.profile_changed.disconnect(_on_profile)
	if Game.room_changed.is_connected(_on_room): Game.room_changed.disconnect(_on_room)
	if Game.error.is_connected(_on_error): Game.error.disconnect(_on_error)

func _back() -> void:
	match mode:
		"searching": Game.c_cancel_find(); mode = "menu"; _render()
		"room": Game.c_leave(); mode = "menu"; _render()
		"join": mode = "menu"; _render()
		_: App.pop()

func _on_connected() -> void:
	Game.c_hello(); _render()

func _on_failed() -> void:
	if status: status.text = "Sunucuya bağlanılamadı · " + Net.server_url

func _on_error(msg: String) -> void:
	if status: status.text = msg

func _on_room(d: Dictionary) -> void:
	if d.get("left", false):
		mode = "menu"; _render(); return
	if d.get("searching", false):
		mode = "searching"; _render(); return
	if d.get("players", []).size() >= 2 and d.state != Game.State.LOBBY:
		App.push(load("res://scripts/screens/match.gd").new()); return
	mode = "room"; _render()

func _process(_dt: float) -> void:
	if mode == "searching" and status:
		var d := Game.room
		var band: int = d.get("band", 100); var elo: int = d.get("elo", App.elo)
		status.text = "%d – %d  ·  %d sn" % [elo - band, elo + band, (Time.get_ticks_msec() - _since) / 1000]

func _render() -> void:
	for ch in body.get_children(): ch.queue_free()
	status = null
	match mode:
		"menu": _render_menu()
		"searching": _render_searching()
		"room": _render_room()
		"join": _render_join()

func _render_menu() -> void:
	var card := UI.panel(); var cv := UI.vbox(2)
	var h := UI.hbox(); var n := UI.label(App.nickname, 15, 700); n.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var e := UI.label(str(App.elo), 32, 800); h.add_child(n); h.add_child(e); cv.add_child(h)
	cv.add_child(UI.label("Elo · satranç gibi, yalnızca Ara maçları işler", 11, 500, "muted"))
	card.add_child(cv); body.add_child(card)
	body.add_child(UI.scope_picker(func(_v): pass))
	var ara := UI.button("Ara", "violet", ">")
	ara.disabled = not Net.is_connected_to_server()
	ara.pressed.connect(func(): _since = Time.get_ticks_msec(); Game.c_find_match())
	body.add_child(ara)
	var two := UI.hbox(8)
	var kur := UI.button("Oda kur", "line"); kur.size_flags_horizontal = Control.SIZE_EXPAND_FILL; kur.disabled = ara.disabled
	kur.pressed.connect(func(): Game.c_create_room())
	var katil := UI.button("Odaya katıl", "line"); katil.size_flags_horizontal = Control.SIZE_EXPAND_FILL; katil.disabled = ara.disabled
	katil.pressed.connect(func(): mode = "join"; _render())
	two.add_child(kur); two.add_child(katil); body.add_child(two)
	var note := UI.label("Oda maçları dostluk, Elo'ya işlenmez", 11, 500, "muted"); note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(note)
	status = UI.label("" if Net.is_connected_to_server() else "Sunucuya bağlanılıyor…", 12, 600, "no"); status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(status)
	body.add_child(UI.spacer())

func _render_searching() -> void:
	body.add_child(UI.spacer())
	var t := UI.label("Rakip aranıyor", 22, 800); t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; body.add_child(t)
	status = UI.label("", 13, 600, "muted"); status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; body.add_child(status)
	var row := UI.hbox(6); row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_child(UI.chip("Doğrulanmış havuz" if App.verified else "Genel havuz", "ok" if App.verified else "line"))
	row.add_child(UI.chip(UI.scope_label(App.scope), "violet"))
	body.add_child(row)
	body.add_child(UI.spacer())
	var cancel := UI.button("İptal", "ghost"); cancel.pressed.connect(_back); body.add_child(cancel)

func _render_room() -> void:
	var d := Game.room
	var me := UI.panel("violet"); var mv := UI.vbox(2); mv.add_child(UI.eyebrow("Sen", "violet_ink")); mv.add_child(UI.label(App.nickname, 20, 800, "violet_ink")); me.add_child(mv)
	body.add_child(me)
	body.add_child(UI.spacer())
	var ey := UI.eyebrow("Oda kodu"); ey.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; body.add_child(ey)
	var code := UI.label(str(d.get("code", "----")), 56, 800); code.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	code.add_theme_constant_override("outline_size", 0); body.add_child(code)
	var sc := UI.chip(UI.scope_label(str(d.get("scope", "all"))), "violet"); sc.size_flags_horizontal = Control.SIZE_SHRINK_CENTER; body.add_child(sc)
	var h := UI.hbox(8); h.alignment = BoxContainer.ALIGNMENT_CENTER
	var copy := UI.button("Kopyala", "line"); copy.custom_minimum_size.x = 140
	copy.pressed.connect(func(): DisplayServer.clipboard_set(str(d.get("code", ""))); copy.text = "KOPYALANDI")
	h.add_child(copy); body.add_child(h)
	body.add_child(UI.spacer())
	var op := UI.panel("amber"); op.modulate.a = 0.65; var ov := UI.vbox(2); ov.add_child(UI.eyebrow("Rakip", "amber_ink")); ov.add_child(UI.label("Bekleniyor…", 20, 800, "amber_ink")); op.add_child(ov)
	body.add_child(op)
	status = UI.label("", 12, 600, "no"); body.add_child(status)

func _render_join() -> void:
	body.add_child(UI.spacer())
	var ey := UI.eyebrow("Arkadaşının kodu"); ey.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; body.add_child(ey)
	var inp := LineEdit.new(); inp.max_length = 4; inp.placeholder_text = "0000"; inp.alignment = HORIZONTAL_ALIGNMENT_CENTER
	inp.custom_minimum_size.y = 72; inp.virtual_keyboard_type = LineEdit.KEYBOARD_TYPE_NUMBER
	inp.add_theme_font_override("font", UI.font(800)); inp.add_theme_font_size_override("font_size", 40)
	inp.add_theme_color_override("font_color", UI.c("fg")); inp.add_theme_color_override("font_placeholder_color", UI.c("line_strong"))
	var st := UI.box("surface", "violet_fill", 14); inp.add_theme_stylebox_override("normal", st); inp.add_theme_stylebox_override("focus", st)
	body.add_child(inp)
	status = UI.label("4 hane", 12, 600, "muted"); status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; body.add_child(status)
	inp.text_changed.connect(func(t):
		if t.length() == 4: Game.c_join_room(t))
	inp.text_submitted.connect(func(t): if t.length() == 4: Game.c_join_room(t))
	body.add_child(UI.spacer())
	inp.call_deferred("grab_focus")
