extends Control
## Hesap: misafir → hesap oluştur / var olan hesaba bağlan; hesaplı → cihaz ekle, çıkış, silme.
## Google ve Apple ile giriş henüz yok (docs/TODO.md); bağlandıklarında `verified` olur.
var body: VBoxContainer
var view := "main"        # main | recovery | have | code | confirm_delete
var have_tab := "code"    # code | recovery
var msg := ""             # son işlem mesajı
var msg_kind := "ok"
var recovery := ""
var link_code := ""
var code_until := 0
var code_label: Label
var busy := false

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("acct.title"), _back))
	body = UI.vbox(12); body.size_flags_vertical = Control.SIZE_EXPAND_FILL; v.add_child(body)
	Game.acct_done.connect(_on_done)
	Game.profile_changed.connect(_on_profile)
	if not Net.is_connected_to_server(): Net.connect_to_server()
	_render()

func _exit_tree() -> void:
	if Game.acct_done.is_connected(_on_done): Game.acct_done.disconnect(_on_done)
	if Game.profile_changed.is_connected(_on_profile): Game.profile_changed.disconnect(_on_profile)

func _back() -> void:
	if view in ["have", "code", "confirm_delete"]:
		view = "main"; msg = ""; _render()
	elif view == "recovery":
		pass      # kod kaydedilmeden çıkılmasın: "Kaydettim" ile kapanır
	else:
		App.pop(); App.rebuild_top()

func _on_profile(_d: Dictionary) -> void:
	if view == "main": _render()

func _send(op: String, a := "", b := "") -> void:
	if busy: return
	if not Net.is_connected_to_server():
		msg = T.t("acct.need_conn"); msg_kind = "no"; Net.connect_to_server(); _render(); return
	busy = true; Game.c_acct(op, a, b)

func _on_done(d: Dictionary) -> void:
	busy = false
	if not d.get("ok", false):
		msg = T.t("err." + str(d.get("error", "server"))); msg_kind = "no"; _render(); return
	msg = ""; msg_kind = "ok"
	match str(d.op):
		"create": recovery = str(d.get("recovery", "")); view = "recovery"
		"link_code": link_code = str(d.get("code", "")); code_until = Time.get_ticks_msec() + int(d.get("ttl", 600)) * 1000; view = "code"
		"link", "recover": view = "main"; msg = T.t("acct.done_link")
		"logout": view = "main"; msg = T.t("acct.done_logout")
		"delete": view = "main"; msg = T.t("acct.done_delete")
	_render()

func _process(_dt: float) -> void:
	if view == "code" and code_label:
		var rem := maxi(0, code_until - Time.get_ticks_msec()) / 1000
		code_label.text = "%d:%02d" % [rem / 60, rem % 60]
		if rem <= 0: view = "main"; _render()

func _input_box(placeholder: String, big := false, numeric := false) -> LineEdit:
	var e := LineEdit.new(); e.placeholder_text = placeholder; e.custom_minimum_size.y = 64 if big else 54
	if big: e.alignment = HORIZONTAL_ALIGNMENT_CENTER; e.max_length = 6
	if numeric: e.virtual_keyboard_type = LineEdit.KEYBOARD_TYPE_NUMBER
	e.add_theme_font_override("font", UI.font(800 if big else 600)); e.add_theme_font_size_override("font_size", 28 if big else 17)
	e.add_theme_color_override("font_color", UI.c("fg")); e.add_theme_color_override("font_placeholder_color", UI.c("muted")); e.add_theme_color_override("caret_color", UI.c("fg"))
	var st := UI.box("surface", "violet_fill", 12, 2); e.add_theme_stylebox_override("normal", st); e.add_theme_stylebox_override("focus", st)
	return e

func _render() -> void:
	for ch in body.get_children(): ch.queue_free()
	code_label = null
	if msg != "": body.add_child(UI.toast(msg, msg_kind))
	match view:
		"recovery": _render_recovery()
		"have": _render_have()
		"code": _render_code()
		"confirm_delete": _render_confirm()
		_: _render_main()

func _render_main() -> void:
	if App.linked:
		var card := UI.panel("violet"); var cv := UI.vbox(6)
		cv.add_child(UI.label(App.nickname, 24, 800, "violet_ink"))
		var chips := UI.hbox(6)
		chips.add_child(UI.chip(T.t("verified") if App.verified else T.t("acct.linked_chip"), "ok"))
		var dc := UI.chip(T.t("acct.devices") % App.devices, "line"); chips.add_child(dc)
		cv.add_child(chips)
		cv.add_child(UI.label("Elo %d" % App.elo, 14, 700, "violet_ink"))
		card.add_child(cv); body.add_child(card)
		var add := UI.button(T.t("acct.add_device"), "violet", ">"); add.pressed.connect(func(): _send("link_code")); body.add_child(add)
		body.add_child(UI.label(T.t("acct.providers"), 12, 500, "muted"))
		body.add_child(UI.spacer())
		var out := UI.button(T.t("acct.logout"), "line"); out.pressed.connect(func(): _send("logout")); body.add_child(out)
		var del := UI.button(T.t("acct.delete"), "ghost"); del.add_theme_color_override("font_color", UI.c("no")); del.add_theme_color_override("font_hover_color", UI.c("no"))
		del.pressed.connect(func(): view = "confirm_delete"; msg = ""; _render()); body.add_child(del)
	else:
		var card := UI.panel(""); var cv := UI.vbox(6)
		cv.add_child(UI.label(T.t("acct.guest_title"), 18, 800))
		cv.add_child(UI.label(T.t("acct.guest_body"), 13, 500, "muted"))
		card.add_child(cv); body.add_child(card)
		var nick := UI.row("@", App.nickname if App.nickname != "" else T.t("guest"), T.t("set.nick"), UI.label("Elo %d" % App.elo, 14, 800, "muted"))
		body.add_child(nick)
		var mk := UI.button(T.t("acct.create"), "violet", ">"); mk.pressed.connect(func(): _send("create")); body.add_child(mk)
		var have := UI.button(T.t("acct.have"), "line", ">"); have.pressed.connect(func(): view = "have"; msg = ""; _render()); body.add_child(have)
		body.add_child(UI.label(T.t("acct.providers"), 12, 500, "muted"))
		body.add_child(UI.spacer())

func _render_recovery() -> void:
	body.add_child(UI.label(T.t("acct.recovery_title"), 20, 800))
	var card := UI.panel("amber"); var cv := UI.vbox(8)
	var code := UI.label(recovery, 22, 800, "amber_ink"); code.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; code.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY
	cv.add_child(code); card.add_child(cv); body.add_child(card)
	body.add_child(UI.label(T.t("acct.recovery_body"), 13, 500, "muted"))
	var copy := UI.button(T.t("acct.copy"), "line")
	copy.pressed.connect(func(): DisplayServer.clipboard_set(recovery); copy.text = T.t("copied"))
	body.add_child(copy)
	body.add_child(UI.spacer())
	var ok := UI.button(T.t("acct.saved"), "violet")
	ok.pressed.connect(func(): recovery = ""; view = "main"; _render()); body.add_child(ok)

func _render_code() -> void:
	body.add_child(UI.label(T.t("acct.code_title"), 20, 800))
	var card := UI.panel("violet"); var cv := UI.vbox(4)
	var code := UI.label(link_code.substr(0, 3) + " " + link_code.substr(3), 44, 800, "violet_ink"); code.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cv.add_child(code)
	code_label = UI.label("", 14, 700, "violet_ink"); code_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; cv.add_child(code_label)
	card.add_child(cv); body.add_child(card)
	body.add_child(UI.label(T.t("acct.code_body"), 13, 500, "muted"))
	body.add_child(UI.spacer())

func _render_have() -> void:
	body.add_child(UI.segment(["code", "recovery"], [T.t("acct.tab_code"), T.t("acct.tab_recovery")], have_tab, func(val): have_tab = val; msg = ""; _render()))
	if have_tab == "code":
		body.add_child(UI.label(T.t("acct.enter_code"), 13, 600, "muted"))
		var inp := _input_box("000000", true, true); body.add_child(inp)
		var go := UI.button(T.t("acct.link"), "violet")
		var submit := func(): if inp.text.strip_edges().length() >= 6: _send("link", inp.text.strip_edges())
		go.pressed.connect(submit); inp.text_submitted.connect(func(_t): submit.call())
		body.add_child(go); inp.call_deferred("grab_focus")
	else:
		var nick := _input_box(T.t("acct.enter_nick")); nick.max_length = 16; body.add_child(nick)
		var rec := _input_box(T.t("acct.enter_recovery")); rec.max_length = 60; body.add_child(rec)
		var go := UI.button(T.t("acct.link"), "violet")
		var submit := func(): if nick.text.strip_edges() != "" and rec.text.strip_edges() != "": _send("recover", nick.text.strip_edges(), rec.text.strip_edges())
		go.pressed.connect(submit); rec.text_submitted.connect(func(_t): submit.call())
		body.add_child(go); nick.call_deferred("grab_focus")
	body.add_child(UI.spacer())

func _render_confirm() -> void:
	body.add_child(UI.label(T.t("acct.delete"), 20, 800))
	body.add_child(UI.toast(T.t("acct.delete_confirm"), "no"))
	body.add_child(UI.spacer())
	var yes := UI.button(T.t("acct.delete_yes"), "line"); yes.add_theme_color_override("font_color", UI.c("no")); yes.add_theme_color_override("font_hover_color", UI.c("no"))
	yes.pressed.connect(func(): _send("delete")); body.add_child(yes)
	var no := UI.button(T.t("acct.cancel"), "violet"); no.pressed.connect(func(): view = "main"; _render()); body.add_child(no)
