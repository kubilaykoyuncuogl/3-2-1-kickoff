extends "res://scripts/screens/single_base.gd"
## Sıradaki kulüp: oyuncu verilir; önce ilk profesyonel kulübü, sonra her transferin hedefi tahmin edilir.
## İpuçları karo olarak gösterilir: yıl, tür, bedel, gittiği ülke, lig.
var ac: Autocomplete

func _init() -> void:
	mode = "chain"; hot_ms = 5000

func _move_text(st: Dictionary) -> String:
	var parts: PackedStringArray = []
	if st.get("year") != null: parts.append(str(int(st.year)))
	if str(st.kind) != "start": parts.append(T.t("kind." + str(st.kind)))
	if st.get("fee") != null: parts.append(UI.money(int(st.fee)))
	return " · ".join(parts)

func _on_state(d: Dictionary) -> void:
	_clear(); ac = null
	var it: Dictionary = d.item
	body.add_child(UI.nav(_title(), _quit))
	_header([UI.eyebrow(T.t("career.player_n") % (int(d.idx) + 1)), UI.lives(int(d.lives))], int(d.score))
	var who := UI.vbox(0)
	who.add_child(UI.label(str(it.name), 26, 800))
	var sub: PackedStringArray = []
	if it.get("born") != null: sub.append(T.t("chain.born") % int(it.born))
	if it.get("pos") != null: sub.append(str(it.pos))
	sub.append(T.t("chain.step_n") % [mini(int(it.step) + 1, int(it.steps_total)), int(it.steps_total)])
	who.add_child(UI.label("  ·  ".join(sub), 13, 600, "muted"))
	body.add_child(who)
	toast_slot = UI.vbox(0); body.add_child(toast_slot)
	var last: Dictionary = d.get("last", {})
	match str(last.get("type", "")):
		"correct": _toast("%s  +%d" % [last.get("name", ""), int(last.get("gained", 0))], "ok")
		"wrong": _toast(T.t("chain.wrong") % [str(last.get("name", "")), str(last.get("answer", ""))], "no")
		"timeout": _toast(T.t("chain.timeout") % str(last.get("answer", "")), "no")
	# soru + ipucu karoları
	var q := UI.panel("violet"); var qv := UI.vbox(8)
	var hint: Dictionary = it.get("hint", {})
	var first := int(it.step) == 0
	qv.add_child(UI.label(T.t("chain.first_q") if first else T.t("chain.next_q"), 18, 800, "violet_ink"))
	var fl := UI.flow(6)
	if hint.get("year") != null: fl.add_child(UI.kv(T.t("chain.k_year"), str(int(hint.year))))
	if not first: fl.add_child(UI.kv(T.t("chain.k_type"), T.t("kind." + str(hint.get("kind", "free")))))
	if hint.get("fee") != null: fl.add_child(UI.kv(T.t("chain.k_fee"), UI.money(int(hint.fee))))
	if hint.get("country") != null: fl.add_child(UI.kv(T.t("chain.k_country") if first else T.t("chain.to_country"), UI.country(hint.country)))
	if hint.get("league") != null: fl.add_child(UI.kv(T.t("chain.league"), str(hint.league)))
	if fl.get_child_count() > 0: qv.add_child(fl)
	q.add_child(qv); body.add_child(q)
	ac = Autocomplete.new("team", T.t("ph.team"))
	ac.picked.connect(func(id, nm): Game.c_single_team(id, nm); ac.clear())
	body.add_child(ac); ac.call_deferred("focus")
	# bilinen yol, en yeni üstte
	var hist: Array = it.get("history", [])
	var scroll := ScrollContainer.new(); scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var hv := UI.vbox(6); hv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for i in range(hist.size() - 1, -1, -1):
		var st: Dictionary = hist[i]
		var mt := _move_text(st)
		hv.add_child(UI.row(str(i + 1), str(st.club), UI.country(st.get("country")), UI.label(mt, 12, 600, "muted") if mt != "" else null, "new" if i == hist.size() - 1 else "", bool(st.get("defunct", false))))
	scroll.add_child(hv); body.add_child(scroll)

func _summary(d: Dictionary) -> String:
	return T.t("chain.summary") % int(d.get("done", 0))

func _over_note(d: Dictionary) -> String:
	var a := str(d.get("last", {}).get("answer", ""))
	return T.t("chain.was") % a if a != "" else ""
