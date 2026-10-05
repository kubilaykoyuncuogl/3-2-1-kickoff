class_name Autocomplete
extends VBoxContainer
## Yazı kutusu + öneri listesi. Öneriler sunucudan (Game.suggestions) gelir. Öneriye dokunmak = seçmek.
signal picked(id: int, name: String)

var kind := "player"      # "team" | "player"
var input: LineEdit
var list: VBoxContainer
var locked := false
var _last_q := ""
var _debounce: Timer

func _init(k: String, placeholder: String) -> void:
	kind = k
	add_theme_constant_override("separation", 6)
	input = LineEdit.new()
	input.placeholder_text = placeholder
	input.custom_minimum_size.y = 56
	input.add_theme_font_override("font", UI.font(600))
	input.add_theme_font_size_override("font_size", 20)
	input.add_theme_color_override("font_color", UI.c("fg"))
	input.add_theme_color_override("font_placeholder_color", UI.c("muted"))
	input.add_theme_color_override("caret_color", UI.c("fg"))
	var st := UI.box("surface", "violet_fill", 12)
	input.add_theme_stylebox_override("normal", st); input.add_theme_stylebox_override("focus", st)
	input.add_theme_stylebox_override("read_only", UI.box("no_soft", "no", 12))
	input.text_changed.connect(_on_text)
	add_child(input)
	list = UI.vbox(4)
	add_child(list)

func _ready() -> void:
	Game.suggestions.connect(_on_suggestions)
	_debounce = Timer.new(); _debounce.one_shot = true; _debounce.wait_time = 0.12
	_debounce.timeout.connect(func(): if _last_q.length() >= 2 and not locked: Game.c_suggest(kind, _last_q))
	add_child(_debounce)

func focus() -> void:
	input.grab_focus()

func clear() -> void:
	input.text = ""; _last_q = ""
	for ch in list.get_children(): ch.queue_free()

func set_locked(v: bool, text := "") -> void:
	locked = v
	input.editable = not v
	if v:
		input.placeholder_text = text
		for ch in list.get_children(): ch.queue_free()
	else:
		input.placeholder_text = T.t("ph.player") if kind == "player" else T.t("ph.team")

func _on_text(t: String) -> void:
	if locked: return
	var q := t.strip_edges()
	if q.length() < 2:
		for ch in list.get_children(): ch.queue_free()
		return
	_last_q = q
	_debounce.start()   # yazma bitince tek istek; sıradaki tuşlar isteği erteler

func _on_suggestions(k: String, q: String, items: Array) -> void:
	if k != kind or not is_inside_tree(): return
	if q != _last_q: return   # eski cevap, yok say
	for ch in list.get_children(): ch.queue_free()
	for it in items.slice(0, 6):
		var b := Button.new()
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var nm: String = it.name
		if kind == "player" and it.get("born"): nm += "  ·  %d" % int(it.born)
		b.text = nm
		b.custom_minimum_size.y = 48
		b.add_theme_font_override("font", UI.font(600)); b.add_theme_font_size_override("font_size", 16)
		var used: bool = it.get("used", false) or not it.get("in_scope", true)
		var st := UI.box("surface", "line", 12, 2); st.content_margin_top = 8; st.content_margin_bottom = 8
		b.add_theme_stylebox_override("normal", st)
		var hv := UI.box("violet_soft", "violet_fill", 12, 2); hv.content_margin_top = 8; hv.content_margin_bottom = 8
		b.add_theme_stylebox_override("disabled", UI.box("", "line", 12, 2)); b.clip_text = true
		b.add_theme_stylebox_override("hover", hv); b.add_theme_stylebox_override("pressed", hv); b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		b.add_theme_color_override("font_color", UI.c("muted") if used else UI.c("fg")); b.add_theme_color_override("font_disabled_color", UI.c("muted"))
		b.add_theme_color_override("font_hover_color", UI.c("violet_ink")); b.add_theme_color_override("font_pressed_color", UI.c("violet_ink"))
		b.disabled = used
		if used: b.text += T.t("ac.used") if it.get("used", false) else T.t("ac.out_of_scope")
		if it.get("defunct", false):
			var di := UI.defunct_icon("muted", 16.0); di.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT)
			di.offset_left = -34; di.offset_right = -14; di.offset_top = -10; di.offset_bottom = 10
			b.add_child(di)
		var id := int(it.id); var name: String = it.name
		b.pressed.connect(func(): picked.emit(id, name))
		list.add_child(b)
