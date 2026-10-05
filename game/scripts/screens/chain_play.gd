extends "res://scripts/screens/single_base.gd"
## Sıradaki kulüp: oyuncu verilir; önce ilk profesyonel kulübü, sonra her transferin hedefi (yıl, tür, bedel ipucuyla) tahmin edilir.
var ac: Autocomplete

func _init() -> void:
	mode = "chain"; hot_ms = 5000

func _kind_text(k: String) -> String:
	return T.t("kind." + k)

func _move_text(st: Dictionary) -> String:
	var parts: PackedStringArray = []
	if st.get("year") != null: parts.append(str(int(st.year)))
	parts.append(_kind_text(str(st.kind)))
	if st.get("fee") != null: parts.append(UI.money(int(st.fee)))
	return "  ·  ".join(parts)

func _on_state(d: Dictionary) -> void:
	_clear(); ac = null
	var it: Dictionary = d.item
	body.add_child(UI.nav(_title(), _quit))
	_header([UI.eyebrow(T.t("career.player_n") % (int(d.idx) + 1)), UI.lives(int(d.lives))])
	var title_l := UI.label(str(it.name), 28, 800); title_l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; body.add_child(title_l)
	var sub: PackedStringArray = []
	if it.get("born") != null: sub.append(T.t("chain.born") % int(it.born))
	if it.get("pos") != null: sub.append(str(it.pos))
	body.add_child(UI.label("  ·  ".join(sub), 13, 600, "muted"))
	toast_slot = UI.vbox(0); body.add_child(toast_slot)
	var last: Dictionary = d.get("last", {})
	match str(last.get("type", "")):
		"correct": _toast("%s  +%d" % [last.get("name", ""), int(last.get("gained", 0))], "ok")
		"wrong": _toast(T.t("chain.wrong") % [str(last.get("name", "")), str(last.get("answer", ""))], "no")
		"timeout": _toast(T.t("chain.timeout") % str(last.get("answer", "")), "no")
	# soru
	var q := UI.panel("violet"); var qv := UI.vbox(4)
	if it.has("hint"):
		qv.add_child(UI.eyebrow(T.t("chain.next_q"), "violet_ink"))
		qv.add_child(UI.label(_move_text(it.hint) + "  →  ?", 20, 800, "violet_ink"))
	else:
		qv.add_child(UI.eyebrow(T.t("chain.step_n") % [int(it.step) + 1, int(it.steps_total)], "violet_ink"))
		qv.add_child(UI.label(T.t("chain.first_q"), 20, 800, "violet_ink"))
	q.add_child(qv); body.add_child(q)
	ac = Autocomplete.new("team", T.t("ph.team"))
	ac.picked.connect(func(id, nm): Game.c_single_team(id, nm); ac.clear())
	body.add_child(ac); ac.call_deferred("focus")
	# bilinen yol, en yeni başta
	var hist: Array = it.get("history", [])
	if not hist.is_empty():
		var hv := UI.vbox(4); hv.size_flags_vertical = Control.SIZE_EXPAND_FILL
		for i in range(hist.size() - 1, -1, -1):
			var st: Dictionary = hist[i]
			var row := UI.hbox(8)
			var n := UI.label("%d. %s" % [i + 1, st.club], 15, 700 if i == hist.size() - 1 else 500, "fg" if i == hist.size() - 1 else "muted")
			n.size_flags_horizontal = Control.SIZE_EXPAND_FILL; n.clip_text = true
			row.add_child(n); row.add_child(UI.label(_move_text(st), 12, 500, "muted"))
			hv.add_child(row)
		body.add_child(hv)
	else:
		body.add_child(UI.spacer())
	body.add_child(UI.label(T.t("sp.score") % int(d.score), 15, 800))

func _summary(d: Dictionary) -> String:
	return T.t("chain.summary") % int(d.get("done", 0))

func _over_note(d: Dictionary) -> String:
	var a := str(d.get("last", {}).get("answer", ""))
	return T.t("chain.was") % a if a != "" else ""
