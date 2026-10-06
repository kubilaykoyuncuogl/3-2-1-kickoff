extends Control
## Nasıl oynanır: online maç (5 adım) + her tek oyunculu mod için birer adım; ipucu balonu + örnek kart

## Adım: [grup anahtarı, başlık anahtarı, metin anahtarı, üst etiket, üst yazı, alt etiket, alt yazı]. Etiket ve yazılar dil anahtarıysa çevrilir, değilse aynen yazılır.
const STEPS := [
	["menu.online", "howto.1.title", "howto.1.body", "you", "Galatasaray", "coach", "Inter Milan"],
	["menu.online", "howto.2.title", "howto.2.body", "you", "Galatasaray", "coach", "Inter Milan"],
	["menu.online", "howto.3.title", "howto.3.body", "you", "Snei", "coach", "Wesley Sneijder"],
	["menu.online", "howto.4.title", "howto.4.body", "you", "howto.4.a", "coach", "howto.4.b"],
	["menu.online", "howto.5.title", "howto.5.body", "you", "3 : 1", "coach", "won"],
	["menu.single", "mode.ladder", "howto.ladder", "howto.ex.clubs", "Real Madrid × Juventus", "howto.ex.answer", "Zinédine Zidane"],
	["menu.single", "mode.blitz", "howto.blitz", "howto.ex.clubs", "Chelsea × AC Milan", "howto.ex.one_of_five", "Andriy Shevchenko"],
	["menu.single", "mode.career", "howto.career", "howto.ex.path", "Sporting → Man United → Real Madrid", "howto.ex.answer", "Cristiano Ronaldo"],
	["menu.single", "mode.chain", "howto.chain", "howto.ex.player", "Wesley Sneijder", "howto.ex.next_club", "Ajax → Real Madrid → ?"],
	["menu.single", "mode.versus", "howto.versus", "howto.ex.more_goals", "Hakan Şükür", "howto.ex.or", "Burak Yılmaz"],
]
var i := 0
var body: VBoxContainer

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("menu.howto"), App.pop))
	body = UI.vbox(12); body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	_render()

func _render() -> void:
	for ch in body.get_children(): ch.queue_free()
	var s: Array = STEPS[i]
	var tip := PanelContainer.new()
	var st := UI.box("fg", "", 12, 0); tip.add_theme_stylebox_override("panel", st)
	var tl := UI.label(T.t(s[2]), 14, 600, "bg"); tl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tip.add_child(tl); body.add_child(tip)
	body.add_child(UI.label("%s  ·  %d / %d  ·  %s" % [T.t(s[0]).to_upper(), i + 1, STEPS.size(), T.t(s[1])], 13, 700, "muted"))
	var top := UI.panel("violet"); var tv := UI.vbox(4); tv.add_child(UI.eyebrow(_tx(s[3]), "violet_ink"))
	var tl1 := UI.label(_tx(s[4]), 22, 800, "violet_ink"); tl1.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; tv.add_child(tl1); top.add_child(tv)
	top.size_flags_vertical = Control.SIZE_EXPAND_FILL; body.add_child(top)
	if i == 1:
		var big := UI.label("3", 72, 800); big.add_theme_font_override("font", UI.font(800, true)); big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		body.add_child(big)
	var bot := UI.panel("amber"); var bv := UI.vbox(4); bv.add_child(UI.eyebrow(_tx(s[5]), "amber_ink"))
	var tl2 := UI.label(_tx(s[6]), 22, 800, "amber_ink"); tl2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; bv.add_child(tl2); bot.add_child(bv)
	bot.size_flags_vertical = Control.SIZE_EXPAND_FILL; body.add_child(bot)
	var h := UI.hbox(8)
	var prev := UI.button(T.t("back"), "line"); prev.size_flags_horizontal = Control.SIZE_EXPAND_FILL; prev.disabled = i == 0
	prev.pressed.connect(func(): i -= 1; _render())
	var last := i == STEPS.size() - 1
	var next := UI.button(T.t("menu.single") if last else T.t("next"), "violet"); next.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	next.pressed.connect(func():
		if last: App.pop(); App.push(load("res://scripts/screens/single.gd").new())
		else: i += 1; _render())
	h.add_child(prev); h.add_child(next); body.add_child(h)

func _tx(k: String) -> String:      # dil anahtarıysa çevir, değilse (kulüp / oyuncu adı) aynen
	return T.t(k)
