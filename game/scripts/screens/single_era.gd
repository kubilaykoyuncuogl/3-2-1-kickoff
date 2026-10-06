extends Control
## Tek oyna, son adım: dönem. Tümü ya da bir / birkaç on yıl; oyuncu havuzu o on yıllarda en az bir maça çıkmış olanlardan kurulur.
var mode := "ladder"
var box: VBoxContainer

func _ready() -> void:
	var v := UI.page(); add_child(v)
	v.add_child(UI.nav(T.t("mode." + mode), App.pop))
	v.add_child(UI.label(T.t("era.title_q"), 22, 800))
	var sub := UI.label(T.t("era.sub"), 13, 500, "muted"); sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; v.add_child(sub)
	box = UI.vbox(12); v.add_child(box)
	v.add_child(UI.spacer())
	_render()
	if not Net.is_connected_to_server(): Net.connect_to_server()

func _render() -> void:
	for ch in box.get_children(): ch.queue_free()
	box.add_child(UI.era_picker(_render, true))
	var pick := UI.label(UI.era_label(App.era), 14, 700, "violet_ink"); pick.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(pick)
	var go := UI.button(T.t("era.start"), "violet", ">"); go.pressed.connect(_start); box.add_child(go)

func _start() -> void:
	if not Net.is_connected_to_server():
		Game.error.emit(T.t("net.connecting")); Net.connect_to_server(); return
	var play = load("res://scripts/screens/%s.gd" % ("single_play" if mode in ["ladder", "blitz"] else mode + "_play")).new()
	if mode in ["ladder", "blitz"]: play.mode = mode
	App.push(play); Game.c_single_start(mode)
