extends "res://scripts/screens/single_base.gd"
## O mu bu mu: iki futbolcu, bir kategori. Değeri büyük olana dokun; doğruysa o kalır, karşısına yenisi gelir. Yanana kadar.
var buttons: Array[Button] = []
var value_labels: Array[Label] = []
var shown_idx := -1
var fmt := "int"

func _init() -> void:
	mode = "versus"; hot_ms = 2500

func _reset() -> void:
	shown_idx = -1; buttons = []; value_labels = []

func _val(v) -> String:
	if v == null: return "?"
	return UI.money(int(v)) if fmt == "money" else str(int(v))

func _on_state(d: Dictionary) -> void:
	if int(d.idx) == shown_idx: return
	var last: Dictionary = d.get("last", {})
	if shown_idx >= 0 and str(last.get("type", "")) == "correct" and buttons.size() == 2:
		_reveal(int(last.get("option", -1)), int(last.get("option", -1)), last.get("values", []))
		await get_tree().create_timer(0.9).timeout
		if not is_inside_tree(): return
	shown_idx = int(d.idx)
	_build(d)

func _before_over(d: Dictionary) -> void:
	var last: Dictionary = d.get("last", {})
	if buttons.size() == 2 and last.has("values"):
		_reveal(int(last.get("option", -1)), int(last.get("answer", -1)), last.get("values", []))
		await get_tree().create_timer(1.5).timeout

func _reveal(pressed: int, answer: int, values: Array) -> void:
	for i in buttons.size():
		var b := buttons[i]
		if not is_instance_valid(b): continue
		b.disabled = true
		if i < values.size() and is_instance_valid(value_labels[i]): value_labels[i].text = _val(values[i])
		var kind := "ok" if i == answer else ("no" if i == pressed else "")
		if kind != "":
			for st in ["normal", "disabled"]: b.add_theme_stylebox_override(st, UI.box(kind + "_soft", kind, 16))
			if kind == "no": UI.shake(b)

func _build(d: Dictionary) -> void:
	_clear(); buttons = []; value_labels = []
	var it: Dictionary = d.item
	fmt = str(it.get("fmt", "int"))
	body.add_child(UI.nav(_title(), _quit))
	_header([UI.eyebrow(T.t("versus.round") % (int(d.idx) + 1))], int(d.score))
	toast_slot = UI.vbox(0); body.add_child(toast_slot)
	if it.get("new_cat", false): _toast(T.t("versus.new_cat"), "ok")
	var q := UI.label(T.t("cat." + str(it.cat)), 20, 800); q.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; q.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(q)
	for i in 2:
		if i == 1:
			var vs := UI.badge("VS", "muted"); vs.custom_minimum_size = Vector2(44, 28); vs.size_flags_horizontal = Control.SIZE_SHRINK_CENTER; body.add_child(vs)
		var side := "violet" if i == 0 else "amber"
		var b := Button.new(); b.size_flags_vertical = Control.SIZE_EXPAND_FILL; b.custom_minimum_size.y = 110
		for st in ["normal", "disabled"]: b.add_theme_stylebox_override(st, UI.box(side + "_soft", "", 16, 0))
		for st in ["hover", "pressed"]: b.add_theme_stylebox_override(st, UI.box(side + "_soft", side + "_fill", 16))
		b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		var v := UI.vbox(2); v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); v.alignment = BoxContainer.ALIGNMENT_CENTER
		v.offset_left = 12; v.offset_right = -12
		var n := UI.label(str(it.names[i]), 24, 800, side + "_ink"); n.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; n.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var born = it.get("born", [null, null])[i]
		var s := UI.label(T.t("chain.born") % int(born) if born != null else "", 12, 500, side + "_ink"); s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		var val := UI.label(_val(it.shown[i]), 30, 800, side + "_ink"); val.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		for c in [n, s, val]: c.mouse_filter = Control.MOUSE_FILTER_IGNORE; v.add_child(c)
		v.mouse_filter = Control.MOUSE_FILTER_IGNORE
		b.add_child(v)
		var idx: int = i
		b.pressed.connect(func():
			for ob in buttons: ob.disabled = true
			Game.c_single_answer(idx))
		body.add_child(b); buttons.append(b); value_labels.append(val)

func _summary(d: Dictionary) -> String:
	return T.t("versus.summary") % int(d.get("done", 0))

func _over_note(d: Dictionary) -> String:
	return T.t("sp.time_up") if str(d.get("last", {}).get("type", "")) == "timeout" else ""
