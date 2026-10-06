extends Node
## Duman testi: her ekranı her dilde ve iki temada kurar; hata olursa çıktıda SCRIPT ERROR görünür.
## Çalıştırma: godot --headless --path game -- --smoke
var root: Control
var built := 0

func _ready() -> void:
	root = get_parent()
	App.bind_root(root)
	App.nickname = "smoke"
	for lang in T.available():
		T.load_lang(lang)
		for pm in [Palette.Mode.LIGHT, Palette.Mode.DARK]:
			Palette.mode = pm; UI._fonts.clear()
			for name in ["menu", "nickname", "single", "single_scope", "single_era", "settings"]:
				await _show(load("res://scripts/screens/%s.gd" % name).new())
			var how: Control = load("res://scripts/screens/howto.gd").new()
			root.add_child(how); await get_tree().process_frame
			for i in how.STEPS.size(): how.i = i; how._render(); await get_tree().process_frame
			how.queue_free(); built += 1
			Game.room = _room(Game.State.LOBBY, {}, 0)
			for m in ["menu", "searching", "room", "join"]:
				var on: Control = load("res://scripts/screens/online.gd").new(); on.mode = m
				await _show(on)
			await _matches()
			await _singles()
			await _new_modes()
			await _account()
		print("[smoke] %s ok" % lang)
	print("[smoke] done, screens built: %d, sample: %s | %s" % [built, T.t("menu.online"), T.t("sp.step") % 3])
	get_tree().quit()

func _show(s: Control) -> void:
	root.add_child(s); await get_tree().process_frame; await get_tree().process_frame
	s.queue_free(); built += 1

func _room(st: int, last: Dictionary, variant: int) -> Dictionary:
	var me := {"pid": multiplayer.get_unique_id(), "nick": "smoke", "elo": 1016, "team": 141 if variant > 0 else 0, "team_name": "Galatasaray" if variant > 0 else "",
		"picked": variant > 0, "ready": variant > 1, "score": 2, "penalty_ms": 3000 if variant == 1 else 0, "rematch": variant > 1, "elo_delta": 16, "away": false}
	var op := {"pid": 99, "nick": "rakip", "elo": 990, "team": 46, "team_name": "Brighton & Hove Albion", "picked": true, "ready": variant > 0, "score": 1,
		"penalty_ms": 2000, "rematch": variant == 1, "elo_delta": -16, "away": variant == 2}
	return {"code": "zidane", "ranked": true, "scope": "top", "state": st, "players": [me, op], "phase_ms": 9000, "last": last,
		"answers": ["Mauro Icardi", "Wesley Sneijder", "Lukas Podolski", "Felipe Melo", "Goran Pandev", "Caner Erkin", "Yuto Nagatomo", "Emre Belözoğlu", "Hakan Şükür"],
		"answers_total": 13, "winner": me.pid if variant < 2 else (0 if variant == 3 else 99), "used_teams": [], "quick_picks": [{"id": 418, "name": "Real Madrid"}, {"id": 131, "name": "FC Barcelona"}],
		"band": 125, "waiting": 3, "cross_in_ms": 12000}

func _matches() -> void:
	var me := multiplayer.get_unique_id()
	var lasts := [{}, {"type": "correct", "pid": me, "name": "Wesley Sneijder"}, {"type": "correct", "pid": 99, "name": "Mauro Icardi"},
		{"type": "wrong", "pid": me, "name": "Mesut Özil"}, {"type": "wrong", "pid": 99, "name": "Mesut Özil"}, {"type": "timeout"},
		{"type": "timeout", "no_common": true}, {"type": "pick_timeout", "pid": 99}, {"type": "pick_timeout", "pid": me}, {"type": "left"}]
	for st in [Game.State.PICK_TEAMS, Game.State.COUNTDOWN, Game.State.REVEAL, Game.State.ROUND, Game.State.ROUND_END, Game.State.GAME_OVER]:
		for li in lasts.size():
			for variant in [0, 1, 2, 3]:
				Game.room = _room(st, lasts[li], variant)
				var m: Control = load("res://scripts/screens/match.gd").new()
				root.add_child(m); await get_tree().process_frame
				if m.ac:
					m.ac._last_q = "ga"
					Game.suggestions.emit(m.ac.kind, "ga", [{"id": 1, "name": "Galatasaray", "used": true, "born": 1990.0}, {"id": 2, "name": "Gaziantep", "in_scope": false}, {"id": 3, "name": "Genoa"}])
				if m.quick_slot: m._show_quick_picks(Game.room.quick_picks)
				Game.room_changed.emit(Game.room)   # aynı durumda güncelleme yolu
				await get_tree().process_frame
				m.queue_free(); built += 1

func _single(mode: String, idx: int, last: Dictionary, over: bool) -> Dictionary:
	var item := {"a_name": "Ajax Amsterdam", "b_name": "Sevilla FC", "a": 1, "b": 2}
	if mode == "blitz": item["options"] = ["A", "B", "C", "D", "E"]
	return {"mode": mode, "idx": idx, "total": 27, "lives": 2, "score": 185 * (idx + 1), "combo": 1.3, "best_combo": 1.6, "remaining_ms": 9000, "per_ms": 20000,
		"lock_ms": 0, "over": over, "item": item, "last": last}

func _singles() -> void:
	for mode in ["ladder", "blitz"]:
		var sp: Control = load("res://scripts/screens/single_play.gd").new(); sp.mode = mode
		root.add_child(sp); await get_tree().process_frame
		Game.single_changed.emit(_single(mode, 0, {}, false)); await get_tree().process_frame
		Game.single_changed.emit(_single(mode, 0, {"type": "wrong", "name": "Mesut Özil", "option": 1, "answer": 2}, false)); await get_tree().process_frame
		Game.single_changed.emit(_single(mode, 1, {"type": "correct", "name": "Dennis Bergkamp", "option": 2}, false))
		await get_tree().create_timer(0.5).timeout
		Game.single_changed.emit(_single(mode, 2, {"type": "correct", "name": "Jesús Navas", "option": 0}, false))
		await get_tree().create_timer(0.5).timeout
		Game.single_changed.emit(_single(mode, 3, {"type": "timeout"}, false)); await get_tree().process_frame
		Game.single_changed.emit(_single(mode, 3, {"type": "wrong", "name": "Mesut Özil", "option": 1, "answer": 2}, true))
		await get_tree().create_timer(1.6).timeout
		sp.queue_free(); built += 1

func _state(mode: String, idx: int, item: Dictionary, last: Dictionary, over: bool) -> Dictionary:
	return {"mode": mode, "idx": idx, "total": 30, "lives": 2, "score": 260 * (idx + 1), "combo": 1.0, "best_combo": 1.0, "done": idx, "remaining_ms": 3500, "per_ms": 4000,
		"lock_ms": 0, "over": over, "item": item, "last": last}

func _new_modes() -> void:
	var clubs := [{"club": "Karlsruher SC", "year": null, "kind": "start"}, {"club": "Hamburger SV", "year": 2012, "kind": "sale"}, {"club": "Karlsruher SC", "year": 2012, "kind": "loan"}]
	var car: Control = load("res://scripts/screens/career_play.gd").new(); root.add_child(car); await get_tree().process_frame
	for st in [_state("career", 0, {"clubs": clubs.slice(0, 1), "total": 6, "revealed": 1}, {}, false),
			_state("career", 0, {"clubs": clubs, "total": 6, "revealed": 3}, {"type": "wrong", "name": "Mesut Özil"}, false),
			_state("career", 1, {"clubs": clubs.slice(0, 1), "total": 4, "revealed": 1}, {"type": "correct", "name": "Hakan Çalhanoğlu", "gained": 280}, false),
			_state("career", 2, {"clubs": clubs.slice(0, 2), "total": 4, "revealed": 2}, {"type": "timeout", "answer": "Hakan Çalhanoğlu"}, false),
			_state("career", 2, {"clubs": clubs, "total": 4, "revealed": 3}, {"type": "wrong", "name": "X", "answer": "Hakan Çalhanoğlu"}, true)]:
		Game.single_changed.emit(st); await get_tree().process_frame; await get_tree().process_frame
	car.queue_free(); built += 1
	var hist := [{"club": "Karlsruher SC", "year": null, "kind": "start", "fee": null}, {"club": "Hamburger SV", "year": 2012, "kind": "sale", "fee": 2500000}]
	var chn: Control = load("res://scripts/screens/chain_play.gd").new(); root.add_child(chn); await get_tree().process_frame
	for st in [_state("chain", 0, {"name": "Hakan Çalhanoğlu", "born": 1994, "pos": "CM", "step": 0, "steps_total": 6, "history": []}, {}, false),
			_state("chain", 0, {"name": "Hakan Çalhanoğlu", "born": 1994, "pos": "CM", "step": 2, "steps_total": 6, "history": hist, "hint": {"year": 2014, "kind": "sale", "fee": 15250000}}, {"type": "correct", "name": "Hamburger SV", "gained": 175}, false),
			_state("chain", 0, {"name": "Hakan Çalhanoğlu", "born": null, "pos": null, "step": 2, "steps_total": 6, "history": hist, "hint": {"year": null, "kind": "loan", "fee": null}}, {"type": "wrong", "name": "Inter Milan", "answer": "AC Milan"}, false),
			_state("chain", 1, {"name": "Alan Shearer", "born": 1970, "pos": "CF", "step": 1, "steps_total": 3, "history": hist.slice(0, 1), "hint": {"year": 1992, "kind": "free", "fee": 450000}}, {"type": "timeout", "answer": "Blackburn Rovers"}, false),
			_state("chain", 1, {"name": "Alan Shearer", "born": 1970, "pos": "CF", "step": 3, "steps_total": 3, "history": hist}, {"type": "wrong", "name": "X", "answer": "Newcastle United"}, true)]:
		Game.single_changed.emit(st); await get_tree().process_frame; await get_tree().process_frame
	chn.queue_free(); built += 1
	var ver: Control = load("res://scripts/screens/versus_play.gd").new(); root.add_child(ver); await get_tree().process_frame
	var it1 := {"cat": "goals", "fmt": "int", "names": ["Didier Drogba", "Yaya Touré"], "born": [1978, 1983], "shown": [null, null], "new_cat": false}
	var it2 := {"cat": "max_fee", "fmt": "money", "names": ["Didier Drogba", "Adrien Rabiot"], "born": [1978, null], "shown": [38500000, null], "new_cat": true}
	Game.single_changed.emit(_state("versus", 0, it1, {}, false)); await get_tree().process_frame
	Game.single_changed.emit(_state("versus", 1, it2, {"type": "correct", "option": 0, "values": [365, 120], "bonus": 42}, false))
	await get_tree().create_timer(1.1).timeout
	Game.single_changed.emit(_state("versus", 1, it2, {"type": "wrong", "option": 1, "answer": 0, "values": [38500000, 450000]}, true))
	await get_tree().create_timer(1.8).timeout
	ver.queue_free(); built += 1
	for cat in ["goals", "apps", "assists", "yellow", "red", "best_season", "goals_big5", "pens", "mv_max", "max_fee", "fee_sum", "n_clubs"]:
		assert(T.t("cat." + cat) != "cat." + cat, "eksik kategori çevirisi: " + cat)

func _account() -> void:
	for linked in [false, true]:
		App.linked = linked; App.devices = 2
		var ac: Control = load("res://scripts/screens/account.gd").new(); root.add_child(ac); await get_tree().process_frame
		for step in [{"op": "create", "ok": true, "recovery": "zidane-pirlo-xavi-4821"}, {"op": "link_code", "ok": true, "code": "946757", "ttl": 600},
				{"op": "link", "ok": false, "error": "bad_code"}, {"op": "recover", "ok": true}, {"op": "logout", "ok": true}, {"op": "delete", "ok": false, "error": "too_many"}]:
			Game.acct_done.emit(step); await get_tree().process_frame; await get_tree().process_frame
		for v in ["have", "confirm_delete", "main"]:
			ac.view = v; ac._render(); await get_tree().process_frame
		ac.have_tab = "recovery"; ac.view = "have"; ac._render(); await get_tree().process_frame
		ac.queue_free(); built += 1
	App.linked = false
