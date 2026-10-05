extends Control
## Tek oyna: günlük kart, Klasik merdiven, Blitz, pratik anahtarı (docs/screens.md 0c)
var practice := false

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav("Tek oyna", App.pop))
	var daily := UI.panel("violet"); var dv := UI.vbox(2)
	dv.add_child(UI.eyebrow("Bugünün koşusu · " + Time.get_date_string_from_system(true), "violet_ink"))
	dv.add_child(UI.label("Herkese aynı merdiven, aynı sorular", 14, 700, "violet_ink"))
	dv.add_child(UI.label("Skorun koşu sonunda tabloya yazılır", 11, 500, "violet_ink"))
	daily.add_child(dv); v.add_child(daily)
	v.add_child(_mode_card("Klasik merdiven", "İki kulüp, oyuncuyu yaz · 3 can · basamak başına 20 sn", "ladder"))
	v.add_child(_mode_card("Blitz", "5 isim, doğruya dokun · tek can · hızlanır", "blitz"))
	v.add_child(UI.spacer())
	var h := UI.hbox(); var l := UI.label("Pratik\ntablosuz, günlük sayılmaz", 13, 600); l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var t := CheckButton.new(); t.toggled.connect(func(on): practice = on)
	h.add_child(l); h.add_child(t); v.add_child(h)
	if not Net.is_connected_to_server(): Net.connect_to_server()
	Net.connected.connect(func(): Game.c_hello())

func _mode_card(title: String, sub: String, mode: String) -> Control:
	var b := Button.new()
	b.custom_minimum_size.y = 84
	b.add_theme_stylebox_override("normal", UI.box("amber_soft", "", 16, 0))
	b.add_theme_stylebox_override("hover", UI.box("amber_soft", "amber_fill", 16))
	b.add_theme_stylebox_override("pressed", UI.box("amber_soft", "amber_fill", 16))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var v := UI.vbox(2); v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); v.offset_left = 16; v.offset_right = -16; v.offset_top = 14; v.offset_bottom = -14
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(UI.label(title, 18, 800, "amber_ink")); var s := UI.label(sub, 12, 500, "amber_ink"); s.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; v.add_child(s)
	for ch in v.get_children(): ch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	b.pressed.connect(func():
		if not Net.is_connected_to_server(): Game.error.emit("Sunucuya bağlanılıyor…"); Net.connect_to_server(); return
		var play = load("res://scripts/screens/single_play.gd").new(); play.mode = mode
		App.push(play); Game.c_single_start(mode, practice))
	return b
