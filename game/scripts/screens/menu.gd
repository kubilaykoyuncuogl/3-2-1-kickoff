extends Control
## Ana menü: dört madde (docs/screens.md 0a)

func _ready() -> void:
	var v := UI.page()
	add_child(v)
	var top := UI.hbox()
	var wm := UI.wordmark(); wm.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(wm)
	var right := UI.vbox(6); right.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var beta := UI.chip("BETA", "amber"); beta.size_flags_horizontal = Control.SIZE_SHRINK_END
	var who := UI.chip(App.nickname if App.nickname != "" else "misafir", "line"); who.size_flags_horizontal = Control.SIZE_SHRINK_END
	right.add_child(beta); right.add_child(who)
	top.add_child(right)
	v.add_child(top)
	v.add_child(UI.spacer(16))
	var online := UI.button("Online oyna", "violet", str(App.elo))
	online.pressed.connect(func(): App.push(load("res://scripts/screens/online.gd").new()))
	var single := UI.button("Tek oyna", "amber", ">")
	single.pressed.connect(func(): App.push(load("res://scripts/screens/single.gd").new()))
	var howto := UI.button("Nasıl oynanır", "line")
	howto.pressed.connect(func(): App.push(load("res://scripts/screens/howto.gd").new()))
	var settings := UI.button("Ayarlar", "line")
	settings.pressed.connect(func(): App.push(load("res://scripts/screens/settings.gd").new()))
	for b in [online, single, howto, settings]: v.add_child(b)
	var elo_label: Label = online.get_child(0)
	Game.profile_changed.connect(func(_d): if is_instance_valid(elo_label): elo_label.text = str(App.elo))
	v.add_child(UI.spacer())
	var ver := UI.label("v0.1 beta · hatalar olabilir, bildir", 11, 600, "muted"); ver.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(ver)
	if App.nickname == "":
		call_deferred("_ask_nickname")

func _ask_nickname() -> void:
	App.push(load("res://scripts/screens/nickname.gd").new())
