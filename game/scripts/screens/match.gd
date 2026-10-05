extends Control
## Maç ekranı: PICK_TEAMS / COUNTDOWN / ROUND / ROUND_END / GAME_OVER. Her durum değişiminde yeniden kurulur.
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

func _ready() -> void:
	body = UI.page(); add_child(body)
	Game.room_changed.connect(_on_room)
	Game.error.connect(_on_error)
	_on_room(Game.room)

func _exit_tree() -> void:
	if Game.room_changed.is_connected(_on_room): Game.room_changed.disconnect(_on_room)
	if Game.error.is_connected(_on_error): Game.error.disconnect(_on_error)

func _on_error(msg: String) -> void:
	if strip: strip.text = msg

func _on_room(d: Dictionary) -> void:
	if d.get("left", false) or d.get("players", []).size() < 1:
		App.pop(); return
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
			if pen > 0: ac.set_locked(true, "Yanlış · %d" % ceili(pen / 1000.0))
			elif ac.locked: ac.set_locked(false); ac.focus()
			elif not ac.input.has_focus() and get_viewport().gui_get_focus_owner() == null: ac.focus()
	elif state == Game.State.COUNTDOWN and countdown_label:
		countdown_label.text = str(maxi(1, ceili(rem / 1000.0)))

# ---------- kurulum ----------
func _render(d: Dictionary) -> void:
	for ch in body.get_children(): ch.queue_free()
	timer_label = null; timer_bar = null; countdown_label = null; ac = null; strip = null; opp_label = null
	match state:
		Game.State.PICK_TEAMS: _render_pick(d)
		Game.State.COUNTDOWN: _render_countdown(d)
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
			if strip and last.get("type", "") == "wrong":
				if int(last.pid) == multiplayer.get_unique_id(): strip.text = "Yanlış: %s" % last.name
				else: strip.text = "Rakip: %s yanlış, %d sn kilitli" % [last.name, ceili(int(Game.opponent().get("penalty_ms", 0)) / 1000.0)]
		Game.State.GAME_OVER: _render(d)

func _side_panel(p: Dictionary, side: String, sub: Control = null) -> PanelContainer:
	var pan := UI.panel(side); var v := UI.vbox(3)
	var ink := side + "_ink"
	v.add_child(UI.eyebrow(("Sen" if side == "violet" else "Rakip") + " · " + str(p.get("nick", "")), ink))
	v.add_child(UI.label(str(p.get("team_name", "")) if p.get("team_name", "") != "" else "—", 22, 800, ink))
	if sub: v.add_child(sub)
	pan.add_child(v); return pan

func _score_row(d: Dictionary) -> HBoxContainer:
	var me := Game.me(); var op := Game.opponent()
	var h := UI.hbox(8); h.alignment = BoxContainer.ALIGNMENT_CENTER
	h.add_child(UI.chip(str(me.get("nick", "")), "violet"))
	h.add_child(UI.label("%d : %d" % [me.get("score", 0), op.get("score", 0)], 28, 800))
	h.add_child(UI.chip(str(op.get("nick", "")), "amber"))
	return h

func _render_pick(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	body.add_child(UI.nav("Takım seçimi · oda %s" % d.get("code", ""), func(): Game.c_leave(); App.pop()))
	body.add_child(_score_row(d))
	# üst: sen
	var mine := UI.panel("violet"); mine.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var mv := UI.vbox(8)
	mv.add_child(UI.eyebrow("Sen · " + str(me.get("nick", "")), "violet_ink"))
	if me.get("ready", false):
		mv.add_child(UI.label(str(me.team_name), 24, 800, "violet_ink"))
		var ch := UI.chip("Hazır", "ok"); mv.add_child(ch)
		mv.add_child(UI.label("Rakip bekleniyor…", 12, 500, "violet_ink"))
	else:
		if me.get("team", 0) != 0:
			mv.add_child(UI.label(str(me.team_name), 24, 800, "violet_ink"))
			var h := UI.hbox(8)
			var change := UI.button("Değiştir", "line"); change.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			change.pressed.connect(func(): Game.c_pick_team(0, ""); _show_picker())
			var ready := UI.button("Hazırım", "violet"); ready.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			ready.pressed.connect(func(): Game.c_ready())
			h.add_child(change); h.add_child(ready); mv.add_child(h)
		else:
			ac = Autocomplete.new("team", "Takım adı yaz…")
			ac.picked.connect(func(id, name): Game.c_pick_team(id, name))
			mv.add_child(ac)
			ac.call_deferred("focus")
	mine.add_child(mv); body.add_child(mine)
	# alt: rakip
	var opp_text := "Hazır" if op.get("ready", false) else ("Seçti, hazır değil" if op.get("team", 0) != 0 else "Düşünüyor…")
	var opp := UI.panel("amber"); var ov := UI.vbox(3)
	ov.add_child(UI.eyebrow("Rakip · " + str(op.get("nick", "?")), "amber_ink"))
	ov.add_child(UI.label(str(op.team_name) if op.get("ready", false) else opp_text, 22, 800, "amber_ink"))
	opp.add_child(ov); body.add_child(opp)
	strip = UI.label("", 12, 600, "no"); body.add_child(strip)

func _opp_pick_text(op: Dictionary) -> String:
	if op.get("ready", false): return str(op.get("team_name", "")) + "  ·  hazır"
	return "Seçti, hazır değil" if op.get("team", 0) != 0 else "Düşünüyor…"

func _show_picker() -> void:
	pass  # pick_team(0) sunucudan boş takım döner → _update → _render

func _render_countdown(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	body.add_child(UI.spacer())
	var top := _side_panel(me, "violet"); body.add_child(top)
	countdown_label = UI.label("3", 120, 800); countdown_label.add_theme_font_override("font", UI.font(800, true))
	countdown_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(countdown_label)
	var bot := _side_panel(op, "amber"); body.add_child(bot)
	body.add_child(UI.spacer())

func _render_round(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	var h := UI.hbox(8)
	var chips := UI.hbox(6); chips.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	chips.add_child(UI.chip(str(me.get("team_name", "")), "violet")); chips.add_child(UI.chip(str(op.get("team_name", "")), "amber"))
	h.add_child(chips)
	timer_label = UI.label("15", 28, 800); h.add_child(timer_label)
	body.add_child(h)
	timer_bar = ProgressBar.new(); timer_bar.max_value = Game.ROUND_MS; timer_bar.value = Game.ROUND_MS; timer_bar.show_percentage = false
	timer_bar.custom_minimum_size.y = 8
	timer_bar.add_theme_stylebox_override("background", UI.box("line", "", 999, 0)); timer_bar.add_theme_stylebox_override("fill", UI.box("fg", "", 999, 0))
	body.add_child(timer_bar)
	ac = Autocomplete.new("player", "Oyuncu adı yaz…")
	ac.size_flags_vertical = Control.SIZE_EXPAND_FILL
	ac.picked.connect(func(id, name): Game.c_guess(id, name); ac.clear())
	body.add_child(ac)
	strip = UI.label("", 12, 600, "muted"); body.add_child(strip)
	var sc := _score_row(d); body.add_child(sc)
	ac.call_deferred("focus")

func _render_round_end(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	var last: Dictionary = d.get("last", {})
	var i_won: bool = last.get("type", "") == "correct" and int(last.get("pid", 0)) == multiplayer.get_unique_id()
	var they_won: bool = last.get("type", "") == "correct" and not i_won
	var mine_sub: Control = UI.chip("%s +1" % last.get("name", ""), "ok") if i_won else null
	var top := _side_panel(me, "violet", mine_sub); top.size_flags_vertical = Control.SIZE_EXPAND_FILL; body.add_child(top)
	body.add_child(_score_row(d))
	var note: String
	if last.get("no_common", false): note = "Bu iki takımın ortak oyuncusu yok"
	elif last.get("type", "") == "timeout": note = "Kimse bilemedi"
	elif they_won: note = "%s bildi" % last.get("name", "")
	else: note = ""
	var ans: Array = d.get("answers", []); var total: int = d.get("answers_total", 0)
	var ans_text := ""
	if total > 0:
		ans_text = "Olası: " + ", ".join(ans.slice(0, 4)) + (" … +%d" % (total - 4) if total > 4 else "")
	var sub := UI.vbox(2)
	if note != "": sub.add_child(UI.label(note, 14, 700, "amber_ink"))
	if ans_text != "":
		var l := UI.label(ans_text, 12, 500, "amber_ink"); l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; sub.add_child(l)
	var bot := _side_panel(op, "amber", sub); bot.size_flags_vertical = Control.SIZE_EXPAND_FILL; body.add_child(bot)

func _render_over(d: Dictionary) -> void:
	var me := Game.me(); var op := Game.opponent()
	var last: Dictionary = d.get("last", {})
	var winner: int = int(d.get("winner", 0)); var my := multiplayer.get_unique_id()
	var title := "Berabere" if winner == 0 else ("Kazandın" if winner == my else "Kaybettin")
	if last.get("type", "") == "left": title = "Rakip ayrıldı"
	var top := UI.panel("violet"); top.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var tv := UI.vbox(4); tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var t := UI.eyebrow(title, "violet_ink"); t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(t)
	var sc := UI.label("%d : %d" % [me.get("score", 0), op.get("score", 0)], 64, 800, "violet_ink"); sc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(sc)
	if d.get("ranked", false) and int(me.get("elo_delta", 0)) != 0:
		var de: int = int(me.elo_delta)
		var el := UI.label("Elo %d → %d (%s%d)" % [App.elo - de, App.elo, "+" if de > 0 else "", de], 13, 600, "violet_ink"); el.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(el)
	top.add_child(tv); body.add_child(top)
	var bot := UI.panel("amber"); bot.modulate.a = 0.8; var bv := UI.vbox(2)
	bv.add_child(UI.eyebrow(str(op.get("nick", "")) + " · " + str(op.get("elo", "")), "amber_ink"))
	bv.add_child(UI.label("Rövanş istiyor" if op.get("rematch", false) else "İyi oyundu", 20, 800, "amber_ink"))
	bot.add_child(bv); body.add_child(bot)
	if last.get("type", "") != "left":
		var rv := UI.button("Rövanş" + (" (bekliyor)" if me.get("rematch", false) else ""), "violet"); rv.disabled = me.get("rematch", false)
		rv.pressed.connect(func(): Game.c_rematch()); body.add_child(rv)
	var leave := UI.button("Ayrıl", "ghost"); leave.pressed.connect(func(): Game.c_leave(); App.pop()); body.add_child(leave)
