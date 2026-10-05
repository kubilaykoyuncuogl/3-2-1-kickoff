extends Control
## Klasik merdiven ve Blitz oynanış + koşu sonu. Sunucu otorite: soru, süre, puan hep sunucudan.
var mode := "ladder"
var body: VBoxContainer
var deadline := 0
var per_ms := 1
var timer_label: Label
var bar: ProgressBar
var ac: Autocomplete
var lock_until := 0
var strip: Label
var last_idx := -1
var over_shown := false

func _ready() -> void:
	body = UI.page(); add_child(body)
	Game.single_changed.connect(_on_state)
	Game.error.connect(_on_error)
	body.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Blitz", _quit))
	body.add_child(UI.label("Yükleniyor…", 14, 600, "muted"))

func _exit_tree() -> void:
	if Game.single_changed.is_connected(_on_state): Game.single_changed.disconnect(_on_state)
	if Game.error.is_connected(_on_error): Game.error.disconnect(_on_error)

func _quit() -> void:
	Game.c_single_quit(); App.pop()

func _on_error(msg: String) -> void:
	if strip: strip.text = msg

func _on_state(d: Dictionary) -> void:
	var now := Time.get_ticks_msec()
	deadline = now + int(d.remaining_ms); per_ms = maxi(1, int(d.per_ms)); lock_until = now + int(d.lock_ms)
	if d.over:
		if not over_shown: over_shown = true; _render_over(d)
		return
	if int(d.idx) != last_idx:
		last_idx = int(d.idx); _render_item(d)
	else:
		_update(d)

func _process(_dt: float) -> void:
	if over_shown or timer_label == null: return
	var now := Time.get_ticks_msec(); var rem := maxi(0, deadline - now)
	timer_label.text = str(ceili(rem / 1000.0)); bar.value = rem
	var hot := rem <= (5000 if mode == "ladder" else 2000)
	timer_label.add_theme_color_override("font_color", UI.c("no" if hot else "fg"))
	bar.add_theme_stylebox_override("fill", UI.box("no" if hot else "fg", "", 999, 0))
	if ac:
		var pen := maxi(0, lock_until - now)
		if pen > 0: ac.set_locked(true, "Yanlış · %d" % ceili(pen / 1000.0))
		elif ac.locked: ac.set_locked(false); ac.focus()

func _header(d: Dictionary) -> void:
	var h := UI.hbox(8)
	var left := UI.hbox(6); left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if mode == "ladder":
		left.add_child(UI.eyebrow("Basamak %d" % (int(d.idx) + 1)))
		var lives := ""; for i in 3: lives += "⚽" if i < int(d.lives) else "○"
		left.add_child(UI.label(lives, 13, 600, "muted"))
	else:
		left.add_child(UI.eyebrow("Soru %d" % (int(d.idx) + 1)))
		left.add_child(UI.chip("×%.1f" % float(d.combo), "ok"))
	h.add_child(left)
	timer_label = UI.label("", 28, 800); h.add_child(timer_label)
	body.add_child(h)
	bar = ProgressBar.new(); bar.max_value = per_ms; bar.value = per_ms; bar.show_percentage = false; bar.custom_minimum_size.y = 8
	bar.add_theme_stylebox_override("background", UI.box("line", "", 999, 0)); bar.add_theme_stylebox_override("fill", UI.box("fg", "", 999, 0))
	body.add_child(bar)
	var chips := UI.hbox(6); chips.alignment = BoxContainer.ALIGNMENT_CENTER
	chips.add_child(UI.chip(str(d.item.a_name), "violet")); chips.add_child(UI.chip(str(d.item.b_name), "amber"))
	body.add_child(chips)

func _render_item(d: Dictionary) -> void:
	for ch in body.get_children(): ch.queue_free()
	ac = null
	body.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Blitz", _quit))
	_header(d)
	if mode == "ladder":
		ac = Autocomplete.new("player", "Oyuncu adı yaz…"); ac.size_flags_vertical = Control.SIZE_EXPAND_FILL
		ac.picked.connect(func(id, name): Game.c_single_guess(id, name); ac.clear())
		body.add_child(ac); ac.call_deferred("focus")
		strip = UI.label("", 12, 600, "muted"); body.add_child(strip)
		var last: Dictionary = d.get("last", {})
		if last.get("type", "") == "correct": strip.text = "%s ✓" % last.name
		elif last.get("type", "") == "timeout": strip.text = "Süre doldu, 1 can gitti"
		body.add_child(UI.label("Puan %d" % int(d.score), 13, 700))
	else:
		var opts := UI.vbox(8); opts.size_flags_vertical = Control.SIZE_EXPAND_FILL; opts.alignment = BoxContainer.ALIGNMENT_CENTER
		for i in d.item.options.size():
			var b := UI.button(str(d.item.options[i]), "line"); b.text = str(d.item.options[i]); b.custom_minimum_size.y = 60
			var idx: int = i
			b.pressed.connect(func(): Game.c_single_answer(idx))
			opts.add_child(b)
		body.add_child(opts)
		body.add_child(UI.label("Puan %d" % int(d.score), 13, 700))

func _update(d: Dictionary) -> void:
	var last: Dictionary = d.get("last", {})
	if strip and last.get("type", "") == "wrong": strip.text = "%s yanlış · 1 can gitti" % last.get("name", "")

func _render_over(d: Dictionary) -> void:
	for ch in body.get_children(): ch.queue_free()
	timer_label = null; ac = null
	body.add_child(UI.nav("Koşu sonu", App.pop))
	var top := UI.panel("violet"); var tv := UI.vbox(2); tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var ey := UI.eyebrow(("Blitz" if mode == "blitz" else "Klasik") + (" · pratik" if d.practice else " · bugün"), "violet_ink"); ey.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(ey)
	var big := UI.label(str(int(d.score)), 64, 800, "violet_ink"); big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(big)
	var sub := "%d basamak" % int(d.idx) if mode == "ladder" else "%d soru · en iyi kombo ×%.1f" % [int(d.idx), float(d.best_combo)]
	var sl := UI.label(sub, 13, 600, "violet_ink"); sl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(sl)
	var last: Dictionary = d.get("last", {})
	if mode == "blitz" and last.get("type", "") == "wrong":
		var al := UI.label("Doğru: %s" % d.item.options[int(last.answer)], 13, 700, "violet_ink"); al.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(al)
	top.add_child(tv); body.add_child(top)
	if int(d.rank) > 0: body.add_child(UI.label("Bugünkü sıran #%d" % int(d.rank), 14, 700))
	var board: Array = d.get("board", [])
	if board.size() > 0:
		var lb := UI.vbox(2)
		for i in mini(10, board.size()):
			var row := UI.hbox(); var mine: bool = int(board[i].get("pid", -1)) == multiplayer.get_unique_id()
			var n := UI.label("%d · %s" % [i + 1, board[i].nick], 13, 700 if mine else 500, "violet_ink" if mine else "fg"); n.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			row.add_child(n); row.add_child(UI.label(str(int(board[i].score)), 13, 700 if mine else 500, "violet_ink" if mine else "fg"))
			lb.add_child(row)
		body.add_child(lb)
	body.add_child(UI.spacer())
	var again := UI.button("Tekrar", "amber")
	again.pressed.connect(func(): over_shown = false; last_idx = -1; Game.c_single_start(mode, d.practice))
	body.add_child(again)
	var share := UI.button("Paylaş", "ghost")
	share.pressed.connect(func():
		DisplayServer.clipboard_set("3-2-1 Kickoff · %s · %d puan · %s" % ["Blitz" if mode == "blitz" else "Klasik", int(d.score), Time.get_date_string_from_system(true)])
		share.text = "Kopyalandı")
	body.add_child(share)
