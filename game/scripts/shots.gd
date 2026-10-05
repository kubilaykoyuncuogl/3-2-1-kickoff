extends "res://scripts/smoke.gd"
## Ekran görüntüsü aracı: seçili ekranları sahte durumla kurup PNG kaydeder (tasarım kontrolü için).
## godot --path game --resolution 400x880 -- --shots <klasör> [--theme dark] [--lang en]
var dir := ""

func _ready() -> void:
	root = get_parent()
	App.bind_root(root); App.nickname = "kubi"; App.elo = 1016; App.best = {"ladder": 740, "blitz": 1250, "career": 520, "chain": 0, "versus": 2310}
	var args := OS.get_cmdline_user_args()
	dir = args[args.find("--shots") + 1]
	DirAccess.make_dir_recursive_absolute(dir)
	Palette.mode = Palette.Mode.DARK if args.find("--theme") >= 0 and args[args.find("--theme") + 1] == "dark" else Palette.Mode.LIGHT
	RenderingServer.set_default_clear_color(Palette.c("bg"))
	T.load_lang(args[args.find("--lang") + 1] if args.find("--lang") >= 0 else "tr")
	var me := multiplayer.get_unique_id()
	await _scr("01_menu", "menu")
	Game.room = _room(Game.State.LOBBY, {}, 0)
	await _scr("02_online", "online")
	await _scr("03_online_room", "online", func(s): s.mode = "room")
	await _scr("04_online_search", "online", func(s): s.mode = "searching")
	await _scr("05_single", "single")
	await _scr("06_scope", "single_scope")
	await _scr("07_settings", "settings")
	App.linked = false
	await _scr("08_account_guest", "account")
	await _scr("08b_account_have", "account", func(x): x.view = "have")
	await _scr("08c_account_recovery", "account", func(x): x.view = "recovery"; x.recovery = "zidane-pirlo-xavi-4821")
	App.linked = true; App.devices = 2
	await _scr("09_account_linked", "account")
	await _scr("09b_account_code", "account", func(x): x.view = "code"; x.link_code = "946757"; x.code_until = Time.get_ticks_msec() + 583000)
	await _scr("09c_settings_linked", "settings")
	App.linked = false
	await _match("10_pick", Game.State.PICK_TEAMS, {}, 0, true)
	await _match("11_pick_ready", Game.State.PICK_TEAMS, {}, 2, false)
	await _match("12_countdown", Game.State.COUNTDOWN, {}, 2, false)
	await _match("13_reveal", Game.State.REVEAL, {}, 2, false)
	await _match("14_round", Game.State.ROUND, {"type": "wrong", "pid": 99, "name": "Mesut Özil"}, 0, true)
	await _match("15_round_end", Game.State.ROUND_END, {"type": "correct", "pid": me, "name": "Wesley Sneijder"}, 2, false)
	await _match("16_over", Game.State.GAME_OVER, {"type": "correct", "pid": me, "name": "Wesley Sneijder"}, 1, false)
	# tek oyunculu
	var sp: Control = load("res://scripts/screens/single_play.gd").new(); sp.mode = "ladder"; _add(sp); await _frames(2)
	Game.single_changed.emit(_single("ladder", 0, {}, false)); await _frames(2)
	Game.single_changed.emit(_single("ladder", 1, {"type": "correct", "name": "Dennis Bergkamp"}, false)); await _frames(2)
	Game.single_changed.emit(_single("ladder", 2, {"type": "correct", "name": "Jesús Navas"}, false)); await _frames(3)
	if sp.ac: sp.ac._last_q = "ber"; Game.suggestions.emit("player", "ber", [{"id": 1, "name": "Dennis Bergkamp", "born": 1969.0}, {"id": 2, "name": "Bernardo Silva", "born": 1994.0}, {"id": 3, "name": "Bertrand Traoré", "born": 1995.0}])
	await _save("20_ladder"); sp.queue_free()
	sp = load("res://scripts/screens/single_play.gd").new(); sp.mode = "blitz"; _add(sp); await _frames(2)
	var bi := _single("blitz", 4, {}, false); bi.item.options = ["Ricardo Quaresma", "Fabri", "Pepe", "Mario Gómez", "Jackson Martínez"]; bi.item.a_name = "Beşiktaş JK"; bi.item.b_name = "FC Porto"
	Game.single_changed.emit(bi); await _save("21_blitz"); sp.queue_free()
	var clubs := [{"club": "Danubio FC", "year": 1982, "kind": "start", "country": "Uruguay"}, {"club": "Real Zaragoza", "year": 1985, "kind": "sale", "country": "Spain"}, {"club": "SS Lazio", "year": 1988, "kind": "sale", "country": "Italy"}, {"club": "Inter Milan", "year": 1992, "kind": "loan", "country": "Italy"}, {"club": "Borussia Dortmund", "year": 1995, "kind": "sale", "country": "Germany"}]
	var car: Control = load("res://scripts/screens/career_play.gd").new(); _add(car); await _frames(2)
	Game.single_changed.emit(_state("career", 0, {"clubs": clubs, "total": 10, "revealed": 5}, {"type": "wrong", "name": "Diego Forlán"}, false)); await _save("22_career"); car.queue_free()
	var hist := [{"club": "Arsenal FC", "year": 2013, "kind": "start", "fee": null, "country": "England"}, {"club": "West Bromwich Albion", "year": 2015, "kind": "loan", "fee": null, "country": "England"}, {"club": "SV Werder Bremen", "year": 2016, "kind": "sale", "fee": 5000000, "country": "Germany"}]
	var chn: Control = load("res://scripts/screens/chain_play.gd").new(); _add(chn); await _frames(2)
	Game.single_changed.emit(_state("chain", 0, {"name": "Serge Gnabry", "born": 1995, "pos": "SS", "step": 3, "steps_total": 6, "history": hist, "hint": {"year": 2017, "kind": "sale", "fee": 8000000, "country": "Germany", "league": "Bundesliga"}}, {"type": "correct", "name": "SV Werder Bremen", "gained": 165}, false))
	await _save("23_chain"); chn.queue_free()
	chn = load("res://scripts/screens/chain_play.gd").new(); _add(chn); await _frames(2)
	Game.single_changed.emit(_state("chain", 1, {"name": "Alan Shearer", "born": 1970, "pos": "CF", "step": 0, "steps_total": 3, "history": [], "hint": {"year": null, "kind": "start", "fee": null, "country": "England", "league": "Premier League"}}, {}, false))
	await _save("24_chain_first"); chn.queue_free()
	var ver: Control = load("res://scripts/screens/versus_play.gd").new(); _add(ver); await _frames(2)
	Game.single_changed.emit(_state("versus", 3, {"cat": "max_fee", "fmt": "money", "names": ["Didier Drogba", "Adrien Rabiot"], "born": [1978, 1995], "shown": [38500000, null], "new_cat": false}, {}, false))
	await _save("25_versus")
	Game.single_changed.emit(_state("versus", 3, {"cat": "max_fee", "fmt": "money", "names": ["Didier Drogba", "Adrien Rabiot"], "born": [1978, 1995], "shown": [38500000, null], "new_cat": false}, {"type": "wrong", "option": 1, "answer": 0, "values": [38500000, 450000]}, true))
	await get_tree().create_timer(1.8).timeout; await _save("26_over"); ver.queue_free()
	print("[shots] done → ", dir); get_tree().quit()

func _add(s: Control) -> void:
	root.add_child(s); s.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

func _frames(n: int) -> void:
	for i in n: await get_tree().process_frame

func _save(name: String) -> void:
	await _frames(4); await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(dir.path_join(name + ".png"))

func _scr(name: String, screen: String, setup := Callable()) -> void:
	var s: Control = load("res://scripts/screens/%s.gd" % screen).new()
	if setup.is_valid(): setup.call(s)
	_add(s); await _save(name); s.queue_free(); await _frames(1)

func _match(name: String, st: int, last: Dictionary, variant: int, suggest: bool) -> void:
	Game.room = _room(st, last, variant)
	var m: Control = load("res://scripts/screens/match.gd").new(); _add(m); await _frames(2)
	Game.room_changed.emit(Game.room); await _frames(2)
	if suggest and m.ac:
		var team: bool = m.ac.kind == "team"
		m.ac.input.text = "gala" if team else "snei"; m.ac._last_q = m.ac.input.text
		Game.suggestions.emit(m.ac.kind, m.ac._last_q, [{"id": 1, "name": "Galatasaray"}, {"id": 2, "name": "Los Angeles Galaxy", "used": true}, {"id": 3, "name": "SC Otelul Galati", "in_scope": false}] if team else [{"id": 1, "name": "Wesley Sneijder", "born": 1984.0}, {"id": 2, "name": "Rodney Sneijder", "born": 1991.0}, {"id": 3, "name": "Jeffrey Sneijder", "born": 1982.0}])
	if st == Game.State.PICK_TEAMS and m.quick_slot and suggest == false: m._show_quick_picks(Game.room.quick_picks)
	await _save(name); m.queue_free(); await _frames(1)
