extends Node
## Uçtan uca test botu: `godot --headless --path game -- --bot ali --team galatasaray --guess sneijder`
## Ara ile eşleşir, takım seçer, hazır der, turda tahmin eder. Durumları stdout'a yazar.
var nick := "bot"; var team_q := "galatasaray"; var guess_q := "sneijder"
var picked := false; var guessed := false; var single_mode := ""; var delay := 0.0

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	print("[bot] start args=", args, " url=", Net.server_url)
	var secs := float(_arg(args, "--seconds", "0"))
	if secs > 0: get_tree().create_timer(secs).timeout.connect(func(): print("[%s] time up" % nick); get_tree().quit())
	nick = _arg(args, "--bot", nick); team_q = _arg(args, "--team", team_q); guess_q = _arg(args, "--guess", guess_q); single_mode = _arg(args, "--single", ""); delay = float(_arg(args, "--delay", "0"))
	App.nickname = nick; App.device_id = "dev-" + nick
	Game.room_changed.connect(_on_room); Game.suggestions.connect(_on_sugg); Game.error.connect(func(m): print("[%s] ERR %s" % [nick, m]))
	Game.single_changed.connect(_on_single)
	if "--acct" in args:       # hesap senaryosu: oluştur → bağlama kodu → çıkış → sil
		var steps := ["create", "create", "link_code", "logout", "link_code", "delete"]
		Game.profile_changed.connect(func(d): print("[%s] profile linked=%s nick=%s elo=%s devices=%s" % [nick, d.get("linked"), d.get("nick"), d.get("elo"), d.get("devices")]))
		Game.acct_done.connect(func(d):
			print("[%s] acct %s" % [nick, d])
			if steps.is_empty(): get_tree().quit()
			else: Game.c_acct(steps.pop_front()))
		Net.connected.connect(func():
			print("[%s] connected" % nick); Game.c_hello()
			await get_tree().create_timer(1.0).timeout
			Game.c_acct(steps.pop_front()))
		Net.connect_to_server(); return
	Net.connected.connect(func():
		print("[%s] connected" % nick); Game.c_hello()
		if single_mode != "": Game.c_single_start(single_mode)
		else: Game.c_find_match())
	Net.connect_failed.connect(func(): print("[%s] connect failed" % nick))
	Net.connect_to_server()

func _arg(args: PackedStringArray, key: String, def: String) -> String:
	var i := args.find(key)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else def

func _on_room(d: Dictionary) -> void:
	var st: int = int(d.get("state", -1))
	print("[%s] state=%s code=%s phase=%s last=%s scores=%s" % [nick, st, d.get("code", ""), d.get("phase_ms", ""), d.get("last", {}), d.get("players", []).map(func(p): return "%s:%s" % [p.nick, p.score])])
	if st == Game.State.PICK_TEAMS and not picked and Game.me().get("team", 0) == 0:
		Game.c_suggest("team", team_q)
	elif st == Game.State.PICK_TEAMS and Game.me().get("team", 0) != 0 and not Game.me().get("ready", false):
		Game.c_ready()
	elif st == Game.State.ROUND and not guessed:
		guessed = true
		if delay > 0: await get_tree().create_timer(delay).timeout
		if int(Game.room.get("state", -1)) == Game.State.ROUND: Game.c_suggest("player", guess_q)
	elif st == Game.State.ROUND_END:
		picked = false; guessed = false
		print("[%s] answers=%s total=%s" % [nick, d.get("answers", []), d.get("answers_total", 0)])
	elif st == Game.State.GAME_OVER:
		print("[%s] GAME OVER winner=%s elo_delta=%s" % [nick, d.get("winner"), Game.me().get("elo_delta")])
		get_tree().quit()

func _on_sugg(kind: String, _q: String, list: Array) -> void:
	if list.is_empty(): print("[%s] no suggestions for %s" % [nick, kind]); return
	print("[%s] sugg %s: %s" % [nick, kind, list.slice(0, 3).map(func(x): return x.name)])
	if kind == "team" and not picked:
		for it in list:
			if not it.get("used", false):
				picked = true; Game.c_pick_team(int(it.id), it.name); return
		print("[%s] all suggested teams used" % nick)
	elif kind == "player":
		Game.c_guess(int(list[0].id), list[0].name)

func _on_single(d: Dictionary) -> void:
	var it: Dictionary = d.item
	match str(d.mode):
		"career": print("[%s] career idx=%s lives=%s score=%s revealed=%s/%s last=%s clubs=%s" % [nick, d.idx, d.lives, d.score, it.get("revealed"), it.get("total"), d.get("last", {}), it.get("clubs", []).map(func(c): return c.club)])
		"chain": print("[%s] chain idx=%s step=%s/%s lives=%s score=%s player=%s hint=%s last=%s" % [nick, d.idx, it.get("step"), it.get("steps_total"), d.lives, d.score, it.get("name"), it.get("hint", {}), d.get("last", {})])
		"versus": print("[%s] versus idx=%s score=%s cat=%s %s shown=%s last=%s" % [nick, d.idx, d.score, it.get("cat"), it.get("names"), it.get("shown"), d.get("last", {})])
		_: print("[%s] single idx=%s lives=%s score=%s over=%s item=%s×%s opts=%s last=%s" % [nick, d.idx, d.lives, d.score, d.over, it.get("a_name"), it.get("b_name"), it.get("options", []), d.get("last", {})])
	if d.over:
		print("[%s] over score=%s done=%s" % [nick, d.score, d.get("done")]); get_tree().quit(); return
	match str(d.mode):
		"blitz": Game.c_single_answer(int(d.idx) % 5)
		"versus":
			# gösterilen değer varsa ona göre mantıklı tahmin: bilinmeyeni seç (çoğu zaman yanlış/doğru karışık)
			await get_tree().create_timer(0.3).timeout
			Game.c_single_answer(int(d.idx) % 2)
		"career":
			if int(it.get("revealed", 0)) >= 3 and str(d.get("last", {}).get("type", "")) != "wrong": Game.c_single_guess(0, "kesinlikle yanlis")
		"chain":
			await get_tree().create_timer(0.2).timeout
			Game.c_single_team(0, "yanlis kulup")
		_: Game.c_suggest("player", guess_q)
