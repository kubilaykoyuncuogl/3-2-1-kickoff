extends Control
## Tek oyna, 2. adım: kulüp kapsamı. Alt alta üç ikonlu düğme: Tümü (dünya), Üst ligler (taç), 5 büyük lig (5).
var mode := "ladder"

const OPTIONS := [
	["all", "Tümü", "Bütün kulüpler, köy takımlarına kadar", "res://assets/icons/globe.svg"],
	["top", "Üst ligler", "Yalnızca ülkelerin en üst ligleri", "res://assets/icons/crown.svg"],
	["big5", "5 büyük lig", "İngiltere, İspanya, İtalya, Almanya, Fransa", "res://assets/icons/five.svg"],
]

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav("Klasik merdiven" if mode == "ladder" else "Blitz", App.pop))
	v.add_child(UI.label("Hangi kulüpler?", 22, 800))
	v.add_child(UI.label("En iyin: %d" % int(App.best.get(mode, 0)), 13, 500, "muted"))
	for o in OPTIONS: v.add_child(_option(o[0], o[1], o[2], o[3]))
	v.add_child(UI.spacer())
	if not Net.is_connected_to_server(): Net.connect_to_server()

func _option(scope: String, title: String, sub: String, icon: String) -> Button:
	var selected := App.scope == scope
	var b := Button.new()
	b.custom_minimum_size.y = 84
	var side := "violet" if selected else ""
	b.add_theme_stylebox_override("normal", UI.box("violet_soft" if selected else "surface", "violet_fill" if selected else "line_strong", 16))
	b.add_theme_stylebox_override("hover", UI.box("violet_soft", "violet_fill", 16))
	b.add_theme_stylebox_override("pressed", UI.box("violet_soft", "violet_fill", 16))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var h := UI.hbox(14); h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); h.offset_left = 16; h.offset_right = -16; h.offset_top = 12; h.offset_bottom = -12
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var ic := TextureRect.new(); ic.texture = load(icon); ic.custom_minimum_size = Vector2(40, 40)
	ic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; ic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	ic.self_modulate = UI.c("violet_ink" if selected else "fg"); ic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(ic)
	var tv := UI.vbox(2); tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL; tv.alignment = BoxContainer.ALIGNMENT_CENTER; tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tv.add_child(UI.label(title, 18, 800, "violet_ink" if selected else "fg"))
	var s := UI.label(sub, 12, 500, "violet_ink" if selected else "muted"); s.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; tv.add_child(s)
	for ch in tv.get_children(): ch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.add_child(tv)
	var arrow := UI.label(">", 22, 800, "violet_ink" if selected else "muted"); arrow.mouse_filter = Control.MOUSE_FILTER_IGNORE; arrow.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(arrow)
	b.add_child(h)
	b.pressed.connect(func():
		App.scope = scope; App.save_settings()
		if not Net.is_connected_to_server(): Game.error.emit("Sunucuya bağlanılıyor…"); Net.connect_to_server(); return
		var play = load("res://scripts/screens/single_play.gd").new(); play.mode = mode
		App.push(play); Game.c_single_start(mode))
	return b
