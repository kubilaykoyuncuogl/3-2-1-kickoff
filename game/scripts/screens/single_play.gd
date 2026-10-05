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
var toast_slot: VBoxContainer
var opt_buttons: Array[Button] = []
var prev_score := 0

func _ready() -> void:
	body = UI.page(); add_child(body)
	Game.single_changed.connect(_on_state)
	Game.error.connect(_on_error)
	body.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Blitz", _quit))
	body.add_child(UI.label("Yükleniyor…", 14, 600, "muted"))
	_loading_watch()

func _loading_watch() -> void:
	await get_tree().create_timer(8.0).timeout
	if not is_inside_tree() or last_idx >= 0 or over_shown: return
	for ch in body.get_children(): ch.queue_free()
	body.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Blitz", _quit))
	body.add_child(UI.toast("Sunucudan cevap gelmedi" if Net.is_connected_to_server() else "Sunucuya bağlanılamadı", "no"))
	var retry := UI.button("Tekrar dene", "violet")
	retry.pressed.connect(func():
		for ch in body.get_children(): ch.queue_free()
		body.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Blitz", _quit))
		body.add_child(UI.label("Yükleniyor…", 14, 600, "muted"))
		if not Net.is_connected_to_server(): Net.connect_to_server(); await Net.connected; Game.c_hello()
		Game.c_single_start(mode); _loading_watch())
	body.add_child(retry)

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
	var last: Dictionary = d.get("last", {})
	if d.over:
		if over_shown: return
		over_shown = true
		if mode == "blitz" and last.get("type", "") == "wrong" and opt_buttons.size() == 5:
			_flash_options(int(last.get("option", -1)), int(last.get("answer", -1)))
			await get_tree().create_timer(1.3).timeout
		elif mode == "blitz" and last.get("type", "") == "timeout" and opt_buttons.size() == 5:
			_flash_options(-1, -1)
			await get_tree().create_timer(1.0).timeout
		_render_over(d)
		return
	if int(d.idx) != last_idx:
		if mode == "blitz" and last.get("type", "") == "correct" and opt_buttons.size() == 5 and last_idx >= 0:
			_flash_options(int(last.get("option", -1)), int(last.get("option", -1)))
			await get_tree().create_timer(0.35).timeout
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
		elif not ac.input.has_focus() and get_viewport().gui_get_focus_owner() == null: ac.focus()

func _header(d: Dictionary) -> void:
	var h := UI.hbox(8)
	var left := UI.hbox(6); left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if mode == "ladder":
		left.add_child(UI.eyebrow("Basamak %d" % (int(d.idx) + 1)))
		left.add_child(UI.lives(int(d.lives)))
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
	toast_slot = UI.vbox(0); body.add_child(toast_slot)
	_show_toast(d)

func _show_toast(d: Dictionary) -> void:
	if toast_slot == null: return
	for ch in toast_slot.get_children(): ch.queue_free()
	var last: Dictionary = d.get("last", {})
	var t: String = last.get("type", "")
	var gained := int(d.score) - prev_score
	match t:
		"correct":
			var txt := "%s  +%d" % [last.get("name", "Doğru"), gained] if mode == "ladder" else "Doğru  +%d  ·  kombo ×%.1f" % [gained, float(d.combo)]
			toast_slot.add_child(UI.toast(txt, "ok"))
		"wrong":
			toast_slot.add_child(UI.toast("%s yanlış  ·  1 can gitti" % last.get("name", ""), "no"))
			if ac: UI.shake(ac.input)
		"timeout":
			toast_slot.add_child(UI.toast("Süre doldu  ·  1 can gitti", "no"))
	prev_score = int(d.score)

func _flash_options(pressed: int, answer: int) -> void:
	for i in opt_buttons.size():
		var b := opt_buttons[i]
		if not is_instance_valid(b): continue
		if i == answer:
			b.add_theme_stylebox_override("normal", UI.box("ok_soft", "ok", 12)); b.add_theme_stylebox_override("disabled", UI.box("ok_soft", "ok", 12))
			b.add_theme_color_override("font_color", UI.c("ok")); b.add_theme_color_override("font_disabled_color", UI.c("ok"))
		elif i == pressed:
			b.add_theme_stylebox_override("normal", UI.box("no_soft", "no", 12)); b.add_theme_stylebox_override("disabled", UI.box("no_soft", "no", 12))
			b.add_theme_color_override("font_color", UI.c("no")); b.add_theme_color_override("font_disabled_color", UI.c("no"))
			UI.shake(b)
		b.disabled = true

func _render_item(d: Dictionary) -> void:
	for ch in body.get_children(): ch.queue_free()
	ac = null; opt_buttons = []
	body.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Blitz", _quit))
	_header(d)
	if mode == "ladder":
		ac = Autocomplete.new("player", "Oyuncu adı yaz…"); ac.size_flags_vertical = Control.SIZE_EXPAND_FILL
		ac.picked.connect(func(id, name): Game.c_single_guess(id, name); ac.clear())
		body.add_child(ac); ac.call_deferred("focus")
		strip = UI.label("", 12, 600, "muted"); body.add_child(strip)
		body.add_child(UI.label("Puan %d" % int(d.score), 15, 800))
	else:
		var opts := UI.vbox(8); opts.size_flags_vertical = Control.SIZE_EXPAND_FILL; opts.alignment = BoxContainer.ALIGNMENT_CENTER
		for i in d.item.options.size():
			var b := UI.button(str(d.item.options[i]), "line"); b.text = str(d.item.options[i]); b.custom_minimum_size.y = 60
			var idx: int = i
			b.pressed.connect(func():
				for ob in opt_buttons: ob.disabled = true
				Game.c_single_answer(idx))
			opts.add_child(b); opt_buttons.append(b)
		body.add_child(opts)
		body.add_child(UI.label("Puan %d" % int(d.score), 15, 800))

func _update(d: Dictionary) -> void:
	# aynı basamak, yeni olay (yanlış tahmin): başlıktaki canları ve şeridi tazele
	var last: Dictionary = d.get("last", {})
	if last.get("type", "") == "wrong":
		_show_toast(d)
		var hdr := body.get_child(1) if body.get_child_count() > 1 else null
		if hdr is HBoxContainer and hdr.get_child(0).get_child_count() > 1 and mode == "ladder":
			var left: HBoxContainer = hdr.get_child(0)
			left.get_child(1).queue_free(); left.add_child(UI.lives(int(d.lives)))

func _render_over(d: Dictionary) -> void:
	for ch in body.get_children(): ch.queue_free()
	timer_label = null; ac = null
	body.add_child(UI.nav("Koşu sonu", App.pop))
	var top := UI.panel("violet"); var tv := UI.vbox(2); tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var score := int(d.score); var record: bool = score > int(App.best.get(mode, 0))
	if record: App.best[mode] = score; App.save_settings()
	var ey := UI.eyebrow(("Blitz" if mode == "blitz" else "Klasik") + (" · yeni rekor" if record else " · en iyin %d" % int(App.best.get(mode, 0))), "ok" if record else "violet_ink"); ey.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(ey)
	var big := UI.label(str(int(d.score)), 64, 800, "violet_ink"); big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(big)
	var sub := "%d basamak" % int(d.idx) if mode == "ladder" else "%d soru · en iyi kombo ×%.1f" % [int(d.idx), float(d.best_combo)]
	var sl := UI.label(sub, 13, 600, "violet_ink"); sl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(sl)
	var last: Dictionary = d.get("last", {})
	if mode == "blitz" and last.get("type", "") == "wrong":
		var al := UI.label("Doğru: %s" % d.item.options[int(last.answer)], 13, 700, "violet_ink"); al.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(al)
	top.add_child(tv); body.add_child(top)
	body.add_child(UI.spacer())
	var again := UI.button("Tekrar", "amber")
	again.pressed.connect(func(): over_shown = false; last_idx = -1; prev_score = 0; opt_buttons = []; Game.c_single_start(mode))
	body.add_child(again)
	var share := UI.button("Paylaş", "ghost")
	share.pressed.connect(func():
		DisplayServer.clipboard_set("3-2-1 Kickoff · %s · %d puan" % ["Blitz" if mode == "blitz" else "Klasik", int(d.score)])
		share.text = "Kopyalandı")
	body.add_child(share)
