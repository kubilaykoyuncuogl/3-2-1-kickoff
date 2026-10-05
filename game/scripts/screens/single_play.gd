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
var history: Array = []   # Klasik: bilinen oyuncular, en yeni başta: {name, gained, bonus}

func _mode_title() -> String:
	return T.t("mode.ladder") if mode == "ladder" else T.t("mode.blitz")


func _ready() -> void:
	body = UI.page(); add_child(body)
	Game.single_changed.connect(_on_state)
	Game.error.connect(_on_error)
	body.add_child(UI.nav(_mode_title(), _quit))
	body.add_child(UI.label(T.t("loading"), 14, 600, "muted"))
	_loading_watch()

func _loading_watch() -> void:
	await get_tree().create_timer(8.0).timeout
	if not is_inside_tree() or last_idx >= 0 or over_shown: return
	for ch in body.get_children(): ch.queue_free()
	body.add_child(UI.nav(_mode_title(), _quit))
	body.add_child(UI.toast(T.t("net.no_reply") if Net.is_connected_to_server() else T.t("net.failed"), "no"))
	var retry := UI.button(T.t("retry"), "violet")
	retry.pressed.connect(func():
		for ch in body.get_children(): ch.queue_free()
		body.add_child(UI.nav(_mode_title(), _quit))
		body.add_child(UI.label(T.t("loading"), 14, 600, "muted"))
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
		if pen > 0: ac.set_locked(true, T.t("locked_fmt") % ceili(pen / 1000.0))
		elif ac.locked: ac.set_locked(false); ac.focus()
		elif not ac.input.has_focus() and get_viewport().gui_get_focus_owner() == null: ac.focus()

func _header(d: Dictionary) -> void:
	var h := UI.hbox(8)
	var left := UI.hbox(6); left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if mode == "ladder":
		left.add_child(UI.eyebrow(T.t("sp.step") % (int(d.idx) + 1)))
		left.add_child(UI.lives(int(d.lives)))
	else:
		left.add_child(UI.eyebrow(T.t("sp.question") % (int(d.idx) + 1)))
		left.add_child(UI.chip("×%.1f" % float(d.combo), "ok"))
	for ch in left.get_children(): ch.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(left)
	var sc := UI.chip(T.t("sp.score") % int(d.score), "ok"); sc.size_flags_vertical = Control.SIZE_SHRINK_CENTER; h.add_child(sc)
	var tb := UI.timer_box(); timer_label = tb[1]; h.add_child(tb[0])
	body.add_child(h)
	bar = UI.progress(per_ms)
	body.add_child(bar)
	var card := UI.panel(""); body.add_child(card)
	var pair := UI.vbox(0); card.add_child(pair)
	var a := UI.label(str(d.item.a_name), 22, 800, "violet_ink"); a.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; a.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var x := UI.label("×", 14, 700, "muted"); x.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var b := UI.label(str(d.item.b_name), 22, 800, "amber_ink"); b.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if d.item.get("a_defunct", false):
		var ia := UI.defunct_icon("violet_ink"); ia.size_flags_horizontal = Control.SIZE_SHRINK_CENTER; pair.add_child(ia)
	pair.add_child(a); pair.add_child(x); pair.add_child(b)
	if d.item.get("b_defunct", false):
		var ib := UI.defunct_icon("amber_ink"); ib.size_flags_horizontal = Control.SIZE_SHRINK_CENTER; pair.add_child(ib)
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
			var bonus := maxi(0, gained - 100)
			var txt := "%s  +%d" % [last.get("name", T.t("correct")), gained] if mode == "ladder" else T.t("sp.correct_combo") % [gained, float(d.combo)]
			if mode == "ladder" and bonus > 0: txt += T.t("sp.speed_bonus") % bonus
			toast_slot.add_child(UI.toast(txt, "ok"))
			if mode == "ladder" and gained > 0 and (history.is_empty() or history[0].get("idx", -1) != int(d.idx) - 1):
				history.push_front({"name": str(last.get("name", "")), "gained": gained, "bonus": bonus, "idx": int(d.idx) - 1})
		"wrong":
			toast_slot.add_child(UI.toast(T.t("sp.wrong") % last.get("name", ""), "no"))
			if ac: UI.shake(ac.input)
		"timeout":
			toast_slot.add_child(UI.toast(T.t("sp.timeout"), "no"))
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
	body.add_child(UI.nav(_mode_title(), _quit))
	_header(d)
	if mode == "ladder":
		ac = Autocomplete.new("player", T.t("ph.player")); ac.size_flags_vertical = Control.SIZE_EXPAND_FILL
		ac.picked.connect(func(id, name): Game.c_single_guess(id, name); ac.clear())
		body.add_child(ac); ac.call_deferred("focus")
		strip = UI.label("", 12, 600, "muted"); body.add_child(strip)
		if not history.is_empty():
			var hv := UI.vbox(6)
			hv.add_child(UI.eyebrow(T.t("sp.history")))
			for i in mini(history.size(), 4):
				var h: Dictionary = history[i]
				var pts := UI.label("+%d" % int(h.gained), 15, 800, "ok")
				hv.add_child(UI.row(str(int(h.idx) + 1), str(h.name), (T.t("sp.speed_short") % int(h.bonus)).strip_edges() if int(h.bonus) > 0 else "", pts, "new" if i == 0 else ""))
			body.add_child(hv)
	else:
		var opts := UI.vbox(8); opts.size_flags_vertical = Control.SIZE_EXPAND_FILL; opts.alignment = BoxContainer.ALIGNMENT_CENTER
		for i in d.item.options.size():
			var b := UI.button(str(d.item.options[i]), "line"); b.custom_minimum_size.y = 58
			var idx: int = i
			b.pressed.connect(func():
				for ob in opt_buttons: ob.disabled = true
				Game.c_single_answer(idx))
			opts.add_child(b); opt_buttons.append(b)
		body.add_child(opts)

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
	body.add_child(UI.nav(T.t("sp.over"), App.pop))
	var top := UI.panel("violet"); var tv := UI.vbox(2); tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var score := int(d.score); var record: bool = score > int(App.best.get(mode, 0))
	if record: App.best[mode] = score; App.save_settings()
	var ey := UI.eyebrow((T.t("mode.blitz") if mode == "blitz" else T.t("mode.ladder_short")) + (T.t("sp.record") if record else T.t("sp.best") % int(App.best.get(mode, 0))), "ok" if record else "violet_ink"); ey.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(ey)
	var big := UI.label(str(int(d.score)), 64, 800, "violet_ink"); big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(big)
	var sub := T.t("sp.ladder_summary") % int(d.idx) if mode == "ladder" else T.t("sp.blitz_summary") % [int(d.idx), float(d.best_combo)]
	var sl := UI.label(sub, 13, 600, "violet_ink"); sl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(sl)
	var last: Dictionary = d.get("last", {})
	if mode == "blitz" and last.get("type", "") == "wrong":
		var al := UI.label(T.t("sp.answer_was") % d.item.options[int(last.answer)], 13, 700, "violet_ink"); al.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(al)
	top.add_child(tv); body.add_child(top)
	body.add_child(UI.spacer())
	var again := UI.button(T.t("again"), "amber")
	again.pressed.connect(func(): over_shown = false; last_idx = -1; prev_score = 0; opt_buttons = []; history = []; Game.c_single_start(mode))
	body.add_child(again)
	var share := UI.button(T.t("share"), "ghost")
	share.pressed.connect(func():
		DisplayServer.clipboard_set(T.t("sp.share_text") % [T.t("mode.blitz") if mode == "blitz" else T.t("mode.ladder_short"), int(d.score)])
		share.text = T.t("copied"))
	body.add_child(share)
