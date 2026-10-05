extends "res://scripts/screens/single_base.gd"
## Kariyer yolu: kulüpler ilk kulüpten başlayarak tek tek açılır; oyuncuyu ne kadar erken bilirsen o kadar puan.
var ac: Autocomplete
var list_box: VBoxContainer
var shown_idx := -1
var lives_slot: HBoxContainer
var score_label: Label

func _init() -> void:
	mode = "career"; hot_ms = 0

func _reset() -> void:
	shown_idx = -1

func _on_state(d: Dictionary) -> void:
	if int(d.idx) != shown_idx:
		shown_idx = int(d.idx); _build(d)
	_fill(d)

func _build(d: Dictionary) -> void:
	_clear(); ac = null
	body.add_child(UI.nav(_title(), _quit))
	lives_slot = UI.hbox(0)
	_header([UI.eyebrow(T.t("career.player_n") % (int(d.idx) + 1)), lives_slot])
	body.add_child(UI.label(T.t("career.prompt"), 22, 800))
	toast_slot = UI.vbox(0); body.add_child(toast_slot)
	ac = Autocomplete.new("player", T.t("ph.player"))
	ac.picked.connect(func(id, name): Game.c_single_guess(id, name); ac.clear())
	body.add_child(ac); ac.call_deferred("focus")
	list_box = UI.vbox(4); list_box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(list_box)
	score_label = UI.label("", 15, 800); body.add_child(score_label)

func _fill(d: Dictionary) -> void:
	for ch in lives_slot.get_children(): ch.queue_free()
	lives_slot.add_child(UI.lives(int(d.lives)))
	score_label.text = T.t("sp.score") % int(d.score)
	for ch in list_box.get_children(): ch.queue_free()
	var clubs: Array = d.item.clubs; var total := int(d.item.total)
	for i in total:
		var row := UI.hbox(8)
		if i < clubs.size():
			var c: Dictionary = clubs[i]
			var newest := i == clubs.size() - 1
			var yr := str(int(c.year)) if c.get("year") != null else "—"
			var n := UI.label("%d. %s" % [i + 1, c.club], 17 if newest else 15, 800 if newest else 500, "fg"); n.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			n.clip_text = true
			row.add_child(n)
			if str(c.kind) == "loan": row.add_child(UI.chip(T.t("kind.loan"), "amber"))
			row.add_child(UI.label(yr, 14, 600, "muted"))
		else:
			row.add_child(UI.label("%d. · · ·" % (i + 1), 15, 500, "muted"))
		list_box.add_child(row)
	var last: Dictionary = d.get("last", {})
	match str(last.get("type", "")):
		"correct": _toast("%s  +%d" % [last.get("name", ""), int(last.get("gained", 0))], "ok")
		"wrong":
			_toast(T.t("career.wrong") % str(last.get("name", "")), "no")
			if ac: UI.shake(ac.input)
		"timeout": _toast(T.t("career.timeout") % str(last.get("answer", "")), "no")
		_: _toast("")

func _summary(d: Dictionary) -> String:
	return T.t("career.summary") % int(d.get("done", 0))

func _over_note(d: Dictionary) -> String:
	var a := str(d.get("last", {}).get("answer", ""))
	return T.t("career.was") % a if a != "" else ""
