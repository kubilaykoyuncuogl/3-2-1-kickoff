extends Control
## Yeni tek oyunculu modların (kariyer, zincir, o mu bu mu) ortak iskeleti: yükleme, sayaç, başlık, koşu sonu.
## Alt sınıf: _init'te mode'u ayarlar, _on_state(d) ile ekranı kurar, _summary(d) ile koşu sonu satırını verir.
var mode := ""
var body: VBoxContainer
var deadline := 0
var per_ms := 1
var timer_label: Label
var bar: ProgressBar
var hot_ms := 3000
var over_shown := false
var started := false
var toast_slot: VBoxContainer
var prev_score := 0

func _ready() -> void:
	body = UI.page(); add_child(body)
	Game.single_changed.connect(_on_state_base)
	_loading()

func _exit_tree() -> void:
	if Game.single_changed.is_connected(_on_state_base): Game.single_changed.disconnect(_on_state_base)

func _title() -> String:
	return T.t("mode." + mode)

func _quit() -> void:
	Game.c_single_quit(); App.pop()

func _clear() -> void:
	for ch in body.get_children(): ch.queue_free()
	timer_label = null; bar = null; toast_slot = null

func _loading() -> void:
	_clear()
	body.add_child(UI.nav(_title(), _quit))
	body.add_child(UI.label(T.t("loading"), 14, 600, "muted"))
	await get_tree().create_timer(8.0).timeout
	if not is_inside_tree() or started: return
	_clear()
	body.add_child(UI.nav(_title(), _quit))
	body.add_child(UI.toast(T.t("net.no_reply") if Net.is_connected_to_server() else T.t("net.failed"), "no"))
	var retry := UI.button(T.t("retry"), "violet")
	retry.pressed.connect(func():
		if not Net.is_connected_to_server():
			Net.connect_to_server(); await Net.connected; Game.c_hello()
		Game.c_single_start(mode); _loading())
	body.add_child(retry)

func _on_state_base(d: Dictionary) -> void:
	if str(d.get("mode", "")) != mode: return
	started = true
	var now := Time.get_ticks_msec()
	deadline = now + int(d.remaining_ms); per_ms = maxi(1, int(d.per_ms))
	if d.over:
		if over_shown: return
		over_shown = true
		await _before_over(d)
		if is_inside_tree(): _render_over(d)
		return
	_on_state(d)

func _on_state(_d: Dictionary) -> void:
	pass

func _before_over(_d: Dictionary) -> void:
	pass

func _summary(_d: Dictionary) -> String:
	return ""

func _over_note(_d: Dictionary) -> String:
	return ""

func _process(_dt: float) -> void:
	if over_shown or timer_label == null or bar == null: return
	var rem := maxi(0, deadline - Time.get_ticks_msec())
	timer_label.text = str(ceili(rem / 1000.0)); bar.max_value = per_ms; bar.value = rem
	var hot := rem <= hot_ms
	timer_label.add_theme_color_override("font_color", UI.c("no" if hot else "fg"))
	bar.add_theme_stylebox_override("fill", UI.box("no" if hot else "fg", "", 999, 0))

## Başlık satırı: solda verilen kontroller, sağda sayaç; altında süre çubuğu
func _header(left: Array) -> void:
	var h := UI.hbox(8)
	var l := UI.hbox(8); l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for c in left: l.add_child(c)
	h.add_child(l)
	timer_label = UI.label("", 28, 800); h.add_child(timer_label)
	body.add_child(h)
	bar = ProgressBar.new(); bar.max_value = per_ms; bar.value = per_ms; bar.show_percentage = false; bar.custom_minimum_size.y = 8
	bar.add_theme_stylebox_override("background", UI.box("line", "", 999, 0)); bar.add_theme_stylebox_override("fill", UI.box("fg", "", 999, 0))
	body.add_child(bar)

func _toast(text: String, kind := "ok") -> void:
	if toast_slot == null: return
	for ch in toast_slot.get_children(): ch.queue_free()
	if text != "": toast_slot.add_child(UI.toast(text, kind))

func _render_over(d: Dictionary) -> void:
	_clear()
	body.add_child(UI.nav(T.t("sp.over"), App.pop))
	var score := int(d.score); var record: bool = score > int(App.best.get(mode, 0))
	if record: App.best[mode] = score; App.save_settings()
	var top := UI.panel("violet"); var tv := UI.vbox(2); tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var ey := UI.eyebrow(_title() + (T.t("sp.record") if record else T.t("sp.best") % int(App.best.get(mode, 0))), "ok" if record else "violet_ink")
	ey.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(ey)
	var big := UI.label(str(score), 64, 800, "violet_ink"); big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(big)
	var sl := UI.label(_summary(d), 14, 600, "violet_ink"); sl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; tv.add_child(sl)
	top.add_child(tv); body.add_child(top)
	var note := _over_note(d)
	if note != "": body.add_child(UI.toast(note, "no"))
	body.add_child(UI.spacer())
	var again := UI.button(T.t("again"), "amber")
	again.pressed.connect(func():
		over_shown = false; started = false; prev_score = 0; _reset()
		Game.c_single_start(mode); _loading())
	body.add_child(again)
	var share := UI.button(T.t("share"), "ghost")
	share.pressed.connect(func():
		DisplayServer.clipboard_set(T.t("sp.share_text") % [_title(), score])
		share.text = T.t("copied"))
	body.add_child(share)

func _reset() -> void:
	pass
