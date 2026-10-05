extends Control
## Nasıl oynanır: 5 adım, ipucu balonu + örnek kart (v0: statik anlatım; v1'de gerçek ekranlarla tur)

const STEPS := [
	["İki takım seçin", "Sen bir takım seçersin, rakibin de. İkiniz de Hazırım deyince başlar. Takım adı rakibe hazır deyince gider.", "Galatasaray", "Inter Milan"],
	["3 · 2 · 1", "Paneller ortaya kayar, üç saniye geri sayılır. Sonra klavye açılır.", "", ""],
	["15 saniyede bul", "İki takımda da oynamış bir futbolcu yaz. Öneriye dokunmak gönderir. Örnek: Sneijder, Icardi, Podolski.", "Snei", "Wesley Sneijder"],
	["Yanlış dersen", "5 saniye yazamazsın. Rakibin yanlışını da görürsün, kimi elediğini bilirsin.", "Podolski yanlış", "5 sn kilit"],
	["3 puan maçı alır", "Bir maçta bir takım bir kez söylenir. Ortak oyuncusu olmayan çift seçilirse tur boş geçer; art arda üçünde maç berabere biter.", "3 : 1", "Kazandın"],
]
var i := 0
var body: VBoxContainer

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav("Nasıl oynanır", App.pop))
	body = UI.vbox(12); body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	_render()

func _render() -> void:
	for ch in body.get_children(): ch.queue_free()
	var s: Array = STEPS[i]
	var tip := PanelContainer.new()
	var st := UI.box("fg", "", 12, 0); tip.add_theme_stylebox_override("panel", st)
	var tl := UI.label(s[1], 14, 600, "bg"); tl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tip.add_child(tl); body.add_child(tip)
	body.add_child(UI.label("%d / %d  ·  %s" % [i + 1, STEPS.size(), s[0]], 13, 700, "muted"))
	var top := UI.panel("violet"); var tv := UI.vbox(4); tv.add_child(UI.eyebrow("Sen", "violet_ink")); tv.add_child(UI.label(s[2] if s[2] != "" else "Galatasaray", 22, 800, "violet_ink")); top.add_child(tv)
	top.size_flags_vertical = Control.SIZE_EXPAND_FILL; body.add_child(top)
	if i == 1:
		var big := UI.label("3", 72, 800); big.add_theme_font_override("font", UI.font(800, true)); big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		body.add_child(big)
	var bot := UI.panel("amber"); var bv := UI.vbox(4); bv.add_child(UI.eyebrow("Koç", "amber_ink")); bv.add_child(UI.label(s[3] if s[3] != "" else "Inter Milan", 22, 800, "amber_ink")); bot.add_child(bv)
	bot.size_flags_vertical = Control.SIZE_EXPAND_FILL; body.add_child(bot)
	var h := UI.hbox(8)
	var prev := UI.button("Geri", "line"); prev.size_flags_horizontal = Control.SIZE_EXPAND_FILL; prev.disabled = i == 0
	prev.pressed.connect(func(): i -= 1; _render())
	var last := i == STEPS.size() - 1
	var next := UI.button("Online oyna" if last else "İleri", "violet"); next.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	next.pressed.connect(func():
		if last: App.pop(); App.push(load("res://scripts/screens/online.gd").new())
		else: i += 1; _render())
	h.add_child(prev); h.add_child(next); body.add_child(h)
