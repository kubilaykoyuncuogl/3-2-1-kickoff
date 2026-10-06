extends Control
## Maç ekranı: PICK_TEAMS / COUNTDOWN / ROUND / ROUND_END / GAME_OVER. Her durum değişiminde yeniden kurulur (eski içerik sönüp yenisi belirir).
## Sen hep üstte, rakip altta (docs/screens.md).

var body: VBoxContainer
var state := -1
var phase_end := 0           # yerel saat, sunucudan kalan ms ile
var timer_label: Label
var timer_bar: ProgressBar
var countdown_label: Label
var ac: Autocomplete
var penalty_until := 0
var strip: Label
var opp_label: Label
var pick_sig := ""
var toast_slot: VBoxContainer
var pick_timer: Label
var quick_slot: VBoxContainer
var quick_shown := false
var notice: Control
const FADE_OUT := 0.12
const FADE_IN := 0.20
const NOTICE_MS := 3.0

func _ready() -> void:
	Game.room_changed.connect(_on_room)
	Game.error.connect(_on_error)
	_on_room(Game.room)

func _exit_tree() -> void:
	if Game.room_changed.is_connected(_on_room): Game.room_changed.disconnect(_on_room)
	if Game.error.is_connected(_on_error): Game.error.disconnect(_on_error)

func _on_error(msg: String) -> void:
	if state == Game.State.PICK_TEAMS: _show_notice(msg)
	elif strip: strip.text = msg

## Takım seçimindeki uyarılar (rakip aynı takımı seçti, takım kullanıldı, kapsam dışı): ortada kart, 3 sn sonra seçime döner
func _show_notice(msg: String) -> void:
	if notice and is_instance_valid(notice): notice.queue_free()
	var ov := ColorRect.new(); notice = ov
	var dim: Color = UI.c("bg"); dim.a = 0.82; ov.color = dim
	ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var cc := CenterContainer.new(); cc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); cc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var card := PanelContainer.new(); card.custom_minimum_size.x = 300; card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var st := UI.box("surface", "no", 18, 2)
	st.content_margin_left = 22; st.content_margin_right = 22; st.content_margin_top = 22; st.content_margin_bottom = 18
	card.add_theme_stylebox_override("panel", st)
	var v := UI.vbox(10)
	var t := UI.label(msg, 21, 800); t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; t.custom_minimum_size.x = 256
	var sub := UI.label(T.t("match.back_to_pick"), 13, 500, "muted"); sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var bar := UI.progress(1000); bar.value = 1000
	bar.add_theme_stylebox_override("fill", UI.box("no", "", 999, 0))
	v.add_child(t); v.add_child(sub); v.add_child(bar); card.add_child(v); cc.add_child(card); ov.add_child(cc); add_child(ov)
	var oid := ov.get_instance_id()      # lambda düğümü değil kimliğini tutar: ekran kapanırken düğüm önce silinebilir
	var close := func():
		var o := instance_from_id(oid) as Control
		if o == null or o.is_queued_for_deletion() or notice != o: return
		notice = null
		var out := o.create_tween(); out.tween_property(o, "modulate:a", 0.0, FADE_OUT); out.tween_callback(o.queue_free)
		if ac and state == Game.State.PICK_TEAMS: ac.clear(); ac.focus()
	ov.gui_input.connect(func(e): if e is InputEventMouseButton and e.pressed: close.call())
	ov.modulate.a = 0.0; card.pivot_offset = Vector2(150, 60); card.scale = Vector2(0.94, 0.94)
	var tw := ov.create_tween()
	tw.tween_property(ov, "modulate:a", 1.0, 0.16)
	tw.parallel().tween_property(card, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(bar, "value", 0.0, NOTICE_MS)
	tw.tween_callback(close)

func _on_room(d: Dictionary) -> void:
	if d.get("left", false) or d.get("players", []).size() < 1:
		if App.top() == self: App.pop()
		return
	var now := Time.get_ticks_msec()
	phase_end = now + int(d.get("phase_ms", 0))
	var me := Game.me()
	penalty_until = now + int(me.get("penalty_ms", 0))
	if int(d.state) != state:
		state = int(d.state); _render(d)
	else:
		_update(d)

func _process(_dt: float) -> void:
	var now := Time.get_ticks_msec()
	var rem := maxi(0, phase_end - now)
	if state == Game.State.ROUND and timer_label:
		var s := ceili(rem / 1000.0)
		timer_label.text = str(s)
		timer_bar.value = rem
		var hot := rem <= 5000
		timer_label.add_theme_color_override("font_color", UI.c("no" if hot else "fg"))
		timer_bar.add_theme_stylebox_override("fill", UI.box("no" if hot else "fg", "", 999, 0))
		if ac:
			var pen := maxi(0, penalty_until - now)
			if pen > 0: ac.set_locked(true, T.t("locked_fmt") % ceili(pen / 1000.0))
			elif ac.locked: ac.set_locked(false); ac.focus()
			elif not ac.input.has_focus() and get_viewport().gui_get_focus_owner() == null: ac.focus()
	elif state == Game.State.COUNTDOWN and countdown_label:
		countdown_label.text = str(maxi(1, ceili(rem / 1000.0)))
	elif state == Game.State.PICK_TEAMS:
		if pick_timer: pick_timer.text = "%d" % ceili(rem / 1000.0); pick_timer.add_theme_color_override("font_color", UI.c("no" if rem <= 10000 else "muted"))
		if quick_slot and not quick_shown and rem <= Game.PICK_MS - Game.QUICK_AT_MS and Game.me().get("team", 0) == 0:
			quick_shown = true; _show_quick_picks(Game.room.get("quick_picks", []))

# ---------- kurulum ----------
func _render(d: Dictionary) -> void:
	# eski içerik söner, yenisi ardından belirir; anlık değişim "hoplama" gibi görünüyordu
	var old := body
	body = UI.page(); add_child(body)
	if notice and is_instance_valid(notice): move_child(notice, -1)
	if old:
		if App.reduce_motion: old.queue_free()
		else:
			var out := old.create_tween(); out.tween_property(old, "modulate:a", 0.0, FADE_OUT); out.tween_callback(old.queue_free)
			body.modulate.a = 0.0
			var tin := body.create_tween(); tin.tween_interval(FADE_OUT * 0.7); tin.tween_property(body, "modulate:a", 1.0, FADE_IN)
	timer_label = null; timer_bar = null; countdown_label = null; ac = null; strip = null; opp_label = null; toast_slot = null
	pick_timer = null; quick_slot = null; quick_shown = false
	match state:
		Game.State.PICK_TEAMS: _render_pick(d)
		Game.State.COUNTDOWN: _render_countdown(d)
		Game.State.REVEAL: _render_reveal(d)
		Game.State.ROUND: _render_round(d)
		Game.State.ROUND_END: _render_round_end(d)
		Game.State.GAME_OVER: _render_over(d)
		_: _render_pick(d)

func _update(d: Dictionary) -> void:
	match state:
		Game.State.PICK_TEAMS:
			var me := Game.me()
			var sig := "%s|%s" % [me.get("team", 0), me.get("ready", false)]
			if sig != pick_sig: _render(d)
			elif opp_label: opp_label.text = _opp_pick_text(Game.opponent())
		Game.State.ROUND:
			var last: Dictionary = d.get("last", {})
			if toast_slot and Game.opponent().get("away", false):
				for ch in toast_slot.get_children(): ch.queue_free()
				toast_slot.add_child(UI.toast(T.t("match.opp_away"), "muted"))
			if toast_slot and last.get("type", "") == "wrong":
				for ch in toast_slot.get_children(): ch.queue_free()
				if int(last.pid) == multiplayer.get_unique_id():
					toast_slot.add_child(UI.toast(T.t("match.wrong_me") % last.name, "no"))
					if ac: UI.shake(ac.input)
				else:
					toast_slot.add_child(UI.toast(T.t("match.wrong_opp") % [last.name, ceili(int(Game.opponent().get("penalty_ms", 0)) / 1000.0)], "muted"))
		Game.State.GAME_OVER: _render(d)

func _side_panel(p: Dictionary, side: String, sub: Control = null) -> PanelContainer:
	var pan := UI.panel(side); var v := UI.vbox(3)
	var ink := side + "_ink"
	v.add_child(UI.eyebrow((T.t("you") if side == "violet" else T.t("opponent")) + " · " + str(p.get("nick", "")), ink))
	v.add_child(UI.label(str(p.get("team_name", "")) if p.get("team_name", "") != "" else "—", 26, 800, ink))
	if sub: v.add_child(sub)
	pan.add_child(v); return pan

func _score_row(d: Dictionary) -> HBoxContainer:
	var me := Game.me(); var op := Game.opponent()
	var h := UI.hbox(8); h.alignment = BoxContainer.ALIGNMENT_CENTER
	h.add_child(UI.chip(str(me.get("nick", "")), "violet"))
	h.add_child(UI.label("%d : %d" % [me.get("score", 0), op.get("score", 0)], 40, 800))
	h.add_child(UI.chip(str(op.get("nick", "")), "amber"))
	return h

func _render_pick(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	var nav := UI.nav(T.t("match.pick_title") % [UI.scope_label(str(d.get("scope", "all"))), d.get("code", "")], func(): Game.c_leave(); App.pop())
	pick_timer = UI.label("45", 20, 800, "muted"); pick_timer.custom_minimum_size.x = 44; pick_timer.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	nav.get_child(2).queue_free(); nav.add_child(pick_timer)
	body.add_child(nav)
	body.add_child(_score_row(d))
	# üst: sen
	var mine := UI.panel("violet"); mine.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var mv := UI.vbox(8)
	mv.add_child(UI.eyebrow(T.t("you") + " · " + str(me.get("nick", "")), "violet_ink"))
	if me.get("ready", false):
		mv.add_child(UI.label(str(me.team_name), 26, 800, "violet_ink"))
		var ch := UI.chip(T.t("ready"), "ok"); ch.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN; mv.add_child(ch)
		mv.add_child(UI.label(T.t("match.waiting_opp"), 12, 500, "violet_ink"))
	else:
		if me.get("team", 0) != 0:
			mv.add_child(UI.label(str(me.team_name), 26, 800, "violet_ink"))
			var h := UI.hbox(8)
			var change := UI.button(T.t("change"), "line"); change.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			change.pressed.connect(func(): Game.c_pick_team(0, ""); _show_picker())
			var ready := UI.button(T.t("ready_btn"), "violet"); ready.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			ready.pressed.connect(func(): Game.c_ready())
			h.add_child(change); h.add_child(ready); mv.add_child(h)
		else:
			ac = Autocomplete.new("team", T.t("ph.team"))
			ac.picked.connect(func(id, name): Game.c_pick_team(id, name))
			mv.add_child(ac)
			quick_slot = UI.vbox(6); mv.add_child(quick_slot)
			ac.call_deferred("focus")
	mine.add_child(mv); body.add_child(mine)
	# alt: rakip (takımı ikisi de hazır olana kadar gizli)
	pick_sig = "%s|%s" % [me.get("team", 0), me.get("ready", false)]
	var opp := UI.panel("amber"); var ov := UI.vbox(3)
	ov.add_child(UI.eyebrow(T.t("opponent") + " · " + str(op.get("nick", "?")), "amber_ink"))
	opp_label = UI.label(_opp_pick_text(op), 24, 800, "amber_ink")
	ov.add_child(opp_label)
	opp.add_child(ov); body.add_child(opp)
	strip = UI.label("", 12, 600, "no"); body.add_child(strip)

func _opp_pick_text(op: Dictionary) -> String:
	if op.get("away", false): return T.t("match.away_short")
	if op.get("ready", false): return T.t("match.opp_ready")
	return T.t("match.opp_picked") if op.get("picked", false) else T.t("match.opp_thinking")

func _show_quick_picks(list: Array) -> void:
	if quick_slot == null or list.is_empty(): return
	for ch in quick_slot.get_children(): ch.queue_free()
	quick_slot.add_child(UI.label(T.t("match.quick"), 13, 600, "violet_ink"))
	var fl := UI.flow(6)
	for it in list:
		var b := UI.button(str(it.name), "line"); b.custom_minimum_size.y = 40; b.clip_text = false
		b.add_theme_font_size_override("font_size", 14)
		var id := int(it.id); var nm: String = str(it.name)
		b.pressed.connect(func(): Game.c_pick_team(id, nm))
		fl.add_child(b)
	quick_slot.add_child(fl)

func _show_picker() -> void:
	pass  # pick_team(0) sunucudan boş takım döner → _update → _render

func _render_countdown(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	body.add_child(UI.spacer())
	var top := UI.panel("violet"); var tv := UI.vbox(2); tv.add_child(UI.eyebrow(T.t("you") + " · " + str(me.get("nick", "")), "violet_ink")); tv.add_child(UI.label(T.t("ready"), 22, 800, "violet_ink")); top.add_child(tv); body.add_child(top)
	countdown_label = UI.label("3", 140, 800); countdown_label.add_theme_font_override("font", UI.font(800, true))
	countdown_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(countdown_label)
	var bot := UI.panel("amber"); var bv := UI.vbox(2); bv.add_child(UI.eyebrow(T.t("opponent") + " · " + str(op.get("nick", "")), "amber_ink")); bv.add_child(UI.label(T.t("ready"), 22, 800, "amber_ink")); bot.add_child(bv); body.add_child(bot)
	body.add_child(UI.spacer())

func _render_reveal(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	body.add_child(UI.spacer())
	var top := UI.panel("violet"); var tv := UI.vbox(4); tv.add_child(UI.eyebrow(T.t("you") + " · " + str(me.get("nick", "")), "violet_ink"))
	var t1 := UI.label(str(me.get("team_name", "")), 34, 800, "violet_ink"); t1.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; tv.add_child(t1); top.add_child(tv); body.add_child(top)
	var x := UI.label("×", 56, 800, "muted"); x.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; body.add_child(x)
	var bot := UI.panel("amber"); var bv := UI.vbox(4); bv.add_child(UI.eyebrow(T.t("opponent") + " · " + str(op.get("nick", "")), "amber_ink"))
	var t2 := UI.label(str(op.get("team_name", "")), 34, 800, "amber_ink"); t2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; bv.add_child(t2); bot.add_child(bv); body.add_child(bot)
	body.add_child(UI.spacer())

func _render_round(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	var h := UI.hbox(8)
	# alt alta, tek satır: uzun adlar yan yana sığmayınca harf harf alt alta diziliyordu
	var chips := UI.vbox(4); chips.size_flags_horizontal = Control.SIZE_EXPAND_FILL; chips.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	chips.add_child(_team_chip(str(me.get("team_name", "")), "violet")); chips.add_child(_team_chip(str(op.get("team_name", "")), "amber"))
	h.add_child(chips)
	var tb := UI.timer_box(); timer_label = tb[1]; h.add_child(tb[0])
	body.add_child(h)
	timer_bar = UI.progress(Game.ROUND_MS)
	body.add_child(timer_bar)
	ac = Autocomplete.new("player", T.t("ph.player"))
	ac.size_flags_vertical = Control.SIZE_EXPAND_FILL
	ac.picked.connect(func(id, name): Game.c_guess(id, name); ac.clear())
	body.add_child(ac)
	toast_slot = UI.vbox(0); body.add_child(toast_slot)
	var sc := _score_row(d); body.add_child(sc)
	ac.call_deferred("focus")

func _team_chip(text: String, kind: String) -> PanelContainer:
	var ch := UI.chip(text, kind); ch.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	var l: Label = ch.get_child(0)
	l.autowrap_mode = TextServer.AUTOWRAP_OFF; l.clip_text = true; l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	l.custom_minimum_size.x = minf(UI.font(600).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x + 4, 250)
	return ch

## Ortak oyuncusu olmayan çift: iki takım, ortada uyarı kartı, süre çubuğu; sunucu 3 sn sonra seçime döndürür
func _render_no_common(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	body.add_child(_score_row(d))
	body.add_child(UI.spacer())
	for it in [[me, "violet"], [op, "amber"]]:
		var pan := UI.panel(it[1]); var t := UI.label(str(it[0].get("team_name", "—")), 24, 800, it[1] + "_ink")
		t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		pan.add_child(t); body.add_child(pan)
		if it[1] == "violet":
			var x := UI.label("×", 34, 800, "muted"); x.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; body.add_child(x)
	var card := PanelContainer.new()
	var st := UI.box("surface", "no", 18, 2)
	st.content_margin_left = 20; st.content_margin_right = 20; st.content_margin_top = 20; st.content_margin_bottom = 16
	card.add_theme_stylebox_override("panel", st)
	var v := UI.vbox(10)
	var msg := UI.label(T.t("match.no_common"), 21, 800); msg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; msg.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var sub := UI.label(T.t("match.back_to_pick"), 13, 500, "muted"); sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var bar := UI.progress(1000); bar.add_theme_stylebox_override("fill", UI.box("no", "", 999, 0))
	v.add_child(msg); v.add_child(sub); v.add_child(bar); card.add_child(v)
	var gap := Control.new(); gap.custom_minimum_size.y = 10; body.add_child(gap); body.add_child(card)
	body.add_child(UI.spacer())
	bar.create_tween().tween_property(bar, "value", 0.0, maxf(0.2, (phase_end - Time.get_ticks_msec()) / 1000.0))

func _render_round_end(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	var last: Dictionary = d.get("last", {})
	if last.get("no_common", false): _render_no_common(d); return
	var my := multiplayer.get_unique_id()
	var t: String = last.get("type", "")
	var i_won: bool = (t == "correct" and int(last.get("pid", 0)) == my) or (t == "pick_timeout" and int(last.get("pid", 0)) != my)
	var they_won: bool = (t == "correct" and int(last.get("pid", 0)) != my) or (t == "pick_timeout" and int(last.get("pid", 0)) == my)
	var ans: Array = d.get("answers", []); var total: int = int(d.get("answers_total", 0))
	var answer_name: String = str(last.get("name", ""))
	var others: Array = ans.filter(func(n): return n != answer_name).slice(0, 6)
	var rest := maxi(0, total - others.size() - (1 if answer_name != "" else 0))

	var winner_sub := UI.vbox(8)
	if t == "pick_timeout":
		winner_sub.add_child(UI.toast(T.t("match.pick_to_win") if i_won else T.t("match.pick_to_lose"), "ok" if i_won else "no"))
	elif t == "correct":
		winner_sub.add_child(UI.toast("%s  +1" % answer_name, "ok" if i_won else "no"))
	else:
		var note := T.t("match.no_common") if last.get("no_common", false) else T.t("match.nobody")
		winner_sub.add_child(UI.toast(note, "no"))
	if not others.is_empty():
		var head := (T.t("match.others") if t == "correct" else T.t("match.possible")).strip_edges().trim_suffix(":")
		var foot := (T.t("match.more") % rest).strip_edges().trim_prefix("…").strip_edges() if rest > 0 else ""
		winner_sub.add_child(UI.list_card(head, others, foot))

	# kazanan taraf büyür, diğerine doğru basar
	var top_weight := 1.6 if i_won else (0.6 if they_won else 1.0)
	var bot_weight := 1.6 if they_won else (0.6 if i_won else 1.0)
	var top := _side_panel(me, "violet", winner_sub if (i_won or (not they_won)) else null)
	top.size_flags_vertical = Control.SIZE_EXPAND_FILL; top.size_flags_stretch_ratio = top_weight; body.add_child(top)
	body.add_child(_score_row(d))
	var bot := _side_panel(op, "amber", winner_sub if they_won else null)
	bot.size_flags_vertical = Control.SIZE_EXPAND_FILL; bot.size_flags_stretch_ratio = bot_weight; body.add_child(bot)

func _render_over(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	var last: Dictionary = d.get("last", {})
	var winner: int = int(d.get("winner", 0)); var my := multiplayer.get_unique_id()
	var title := T.t("draw") if winner == 0 else (T.t("won") if winner == my else T.t("lost"))
	if last.get("type", "") == "left": title = T.t("match.opp_left")
	var top := UI.panel("violet"); top.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var tv := UI.vbox(4); tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var t := UI.eyebrow(title, "violet_ink"); t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(t)
	var sc := UI.label("%d : %d" % [me.get("score", 0), op.get("score", 0)], 64, 800, "violet_ink"); sc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(sc)
	if d.get("ranked", false) and int(me.get("elo_delta", 0)) != 0:
		var de: int = int(me.elo_delta)
		var el := UI.label("Elo %d  (%s%d)" % [App.elo, "+" if de > 0 else "", de], 13, 600, "violet_ink"); el.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(el)
	top.add_child(tv); body.add_child(top)
	var bot := UI.panel("amber"); bot.modulate.a = 0.8; var bv := UI.vbox(2)
	bv.add_child(UI.eyebrow(str(op.get("nick", "")) + " · " + str(op.get("elo", "")), "amber_ink"))
	bv.add_child(UI.label(T.t("match.wants_rematch") if op.get("rematch", false) else T.t("match.gg"), 20, 800, "amber_ink"))
	bot.add_child(bv); body.add_child(bot)
	if last.get("type", "") != "left":
		var rv := UI.button(T.t("rematch") + (T.t("match.waiting_paren") if me.get("rematch", false) else ""), "violet"); rv.disabled = me.get("rematch", false)
		rv.pressed.connect(func(): Game.c_rematch()); body.add_child(rv)
	var leave := UI.button(T.t("leave"), "ghost"); leave.pressed.connect(func(): Game.c_leave(); App.pop()); body.add_child(leave)
