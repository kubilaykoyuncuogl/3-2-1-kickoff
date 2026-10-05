extends "res://scripts/screens/single_base.gd"
## Kariyer yolu: kulüpler ilk kulüpten başlayarak tek tek açılır; oyuncuyu ne kadar erken bilirsen o kadar puan.
## Liste en yeni kulüp üstte olacak şekilde dizilir (mobilde klavye açıkken görünür kalsın).
var ac: Autocomplete
var list_box: VBoxContainer
var head_slot: VBoxContainer
var shown_idx := -1

func _init() -> void:
	mode = "career"; hot_ms = 0

func _reset() -> void:
	shown_idx = -1

func _on_state(d: Dictionary) -> void:
	if int(d.idx) != shown_idx:
		shown_idx = int(d.idx); _build()
	_fill(d)

func _build() -> void:
	_clear(); ac = null
	body.add_child(UI.nav(_title(), _quit))
	head_slot = UI.vbox(12); body.add_child(head_slot)
	body.add_child(UI.label(T.t("career.prompt"), 20, 800))
	toast_slot = UI.vbox(0); body.add_child(toast_slot)
	ac = Autocomplete.new("player", T.t("ph.player"))
	ac.picked.connect(func(id, name): Game.c_single_guess(id, name); ac.clear())
	body.add_child(ac); ac.call_deferred("focus")
	var scroll := ScrollContainer.new(); scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	list_box = UI.vbox(6); list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list_box); body.add_child(scroll)

func _fill(d: Dictionary) -> void:
	# üst bilgi her durumda yeniden kurulur (can ve puan değişir); yazı kutusu yerinde kalır
	for ch in head_slot.get_children(): ch.queue_free()
	var keep := body; body = head_slot
	_header([UI.eyebrow(T.t("career.player_n") % (int(d.idx) + 1)), UI.lives(int(d.lives))], int(d.score))
	body = keep
	for ch in list_box.get_children(): ch.queue_free()
	var clubs: Array = d.item.clubs; var total := int(d.item.total)
	if total > clubs.size():
		list_box.add_child(UI.row("?", T.t("career.more") % (total - clubs.size()), "", null, "hidden"))
	for i in range(clubs.size() - 1, -1, -1):
		var c: Dictionary = clubs[i]
		var right := UI.hbox(6)
		if str(c.kind) == "loan": right.add_child(UI.chip(T.t("kind.loan"), "amber"))
		if c.get("year") != null: right.add_child(UI.label(str(int(c.year)), 15, 800, "violet_ink" if i == clubs.size() - 1 else "muted"))
		for ch in right.get_children(): ch.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		list_box.add_child(UI.row(str(i + 1), str(c.club), UI.country(c.get("country")), right, "new" if i == clubs.size() - 1 else "", bool(c.get("defunct", false))))
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
