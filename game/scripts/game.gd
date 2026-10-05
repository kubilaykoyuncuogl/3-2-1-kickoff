extends Node
## Oyun mantığı. Aynı script iki tarafta da yüklü:
##  - sunucuda (Net.is_server): odalar, eşleşme, tur akışı, Elo, tek oyunculu oturumlar
##  - istemcide: sunucudan gelen durumun aynası + sinyaller
## Oyuncu→kulüp ilişkisi yalnızca Index servisinde; buradan istemciye ad listesi, sonuç ve tur sonu cevapları gider.

enum State { LOBBY, PICK_TEAMS, COUNTDOWN, REVEAL, ROUND, ROUND_END, GAME_OVER }
const ROUND_MS := 15000
const COUNTDOWN_MS := 3000
const REVEAL_MS := 1800
const PICK_MS := 45000          # takım seçimi süresi; dolunca seçmeyen turu kaybeder
const QUICK_AT_MS := 20000      # bu kadar geçince istemci hızlı seçenekleri gösterir
const PENALTY_MS := 5000
const ROUND_END_MS := 4000
const WIN_SCORE := 3
const MAX_INVALID_PAIRS := 3
const ELO_K := 32
const ELO_K_NEW := 40
const BAND_START := 75
const BAND_STEP := 50          # her BAND_STEP_MS'de
const BAND_STEP_MS := 20000
const BAND_MAX := 500
const CROSS_SCOPE_MS := 45000   # bu kadar bekleyenler kapsam fark etmeksizin eşleşir
const RECONNECT_MS := 10000
const SCOPE_ORDER := ["big5", "top", "all"]   # dar → geniş
const SINGLE_LIVES := {"ladder": 3, "blitz": 1, "career": 3, "chain": 3, "versus": 1}
const CAREER_REVEAL_MS := 4000      # kariyer yolu: bu aralıkla bir kulüp daha açılır
const CAREER_LAST_MS := 12000       # hepsi açıldıktan sonra son tahmin süresi
const CHAIN_STEP_MS := 20000

# ---------- istemci tarafı ----------
signal room_changed(d: Dictionary)
signal suggestions(kind: String, q: String, list: Array)
signal single_changed(d: Dictionary)
signal error(msg: String)
signal profile_changed(d: Dictionary)
var room := {}          # son oda durumu
var single := {}        # son tek oyunculu durumu
var my_id := 0

# ---------- sunucu tarafı ----------
var rooms := {}         # code -> room
var pid_room := {}      # pid -> code
var profiles := {}      # pid -> {nick, device, elo, games}
var queue: Array[int] = []      # eşleşme kuyruğu
var queue_since := {}   # pid -> msec
var singles := {}       # pid -> session
var packs := {}         # (kullanılmıyor: her oturum yeni paket)
var rate := {}          # pid -> Array[msec]
var _accounts := {}     # device -> {elo, games}
var words: PackedStringArray = []   # oda kodu kelimeleri (efsane soyadları)
var pending_rc := {}    # device -> {code, pid, until}  (kopan oyuncunun geri dönüş hakkı)

func _ready() -> void:
	my_id = 0
	if Net.is_server:
		multiplayer.peer_disconnected.connect(_on_leave)
		multiplayer.peer_connected.connect(func(pid): profiles[pid] = {"nick": "misafir", "device": "", "elo": 1000, "games": 0})
		_load_accounts()
		var f := FileAccess.open("res://assets/room_words.txt", FileAccess.READ)
		if f: words = f.get_as_text().split("\n", false)
		set_process(true)
	else:
		set_process(false)

func _process(_dt: float) -> void:
	if not Net.is_server: return
	_tick_queue()
	_tick_singles()

# ============================================================ RPC: istemci → sunucu
@rpc("any_peer", "call_remote", "reliable")
func hello(nick: String, device: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var acc: Dictionary = _accounts.get(device, {"elo": 1000, "games": 0})
	profiles[pid] = {"nick": nick.strip_edges().substr(0, 16), "device": device, "elo": acc.elo, "games": acc.games, "last_opp": acc.get("last_opp", "")}
	_send_profile(pid)
	if device != "" and pending_rc.has(device):
		var prc: Dictionary = pending_rc[device]; pending_rc.erase(device)
		var r = rooms.get(prc.code)
		if r != null and prc.pid in r.players: _rebind(r, prc.pid, pid)

@rpc("any_peer", "call_remote", "reliable")
func create_room(scope: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	_leave_everything(pid)
	var code := _new_code()
	rooms[code] = _new_room(code, false, _scope_ok(scope))
	_join(code, pid)

@rpc("any_peer", "call_remote", "reliable")
func join_room(code: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	code = Normalize.norm(code).replace(" ", "")
	if not rooms.has(code): err.rpc_id(pid, "err.room_not_found"); return
	if rooms[code].players.size() >= 2: err.rpc_id(pid, "err.room_full"); return
	_leave_everything(pid)
	_join(code, pid)

@rpc("any_peer", "call_remote", "reliable")
func find_match(scope: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	_leave_everything(pid)
	profiles[pid]["scope"] = _scope_ok(scope)
	if pid not in queue:
		queue.append(pid); queue_since[pid] = Time.get_ticks_msec()
	_send_queue(pid)

@rpc("any_peer", "call_remote", "reliable")
func cancel_find() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	queue.erase(pid); queue_since.erase(pid)
	room_state.rpc_id(pid, {"state": State.LOBBY, "left": true})

@rpc("any_peer", "call_remote", "reliable")
func leave_room() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	_leave_everything(pid)
	room_state.rpc_id(pid, {"state": State.LOBBY, "left": true})

@rpc("any_peer", "call_remote", "reliable")
func pick_team(team_id: int, team_name: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var r = _room_of(pid)
	if r == null or r.state != State.PICK_TEAMS or r.ready.get(pid, false): return
	if team_id == 0:
		r.teams.erase(pid); r.team_names.erase(pid); _broadcast(r); return
	if r.used_teams.has(team_id): err.rpc_id(pid, "err.team_used"); return
	for other in r.teams:
		if other != pid and r.teams[other] == team_id: err.rpc_id(pid, "err.team_taken"); return
	if r.scope != "all":
		var ok: bool = await IndexAPI.club_in_scope(team_id, r.scope)
		if not ok: err.rpc_id(pid, "err.out_of_scope"); return
		if r.state != State.PICK_TEAMS or r.ready.get(pid, false): return
	r.teams[pid] = team_id; r.team_names[pid] = team_name
	_broadcast(r)

@rpc("any_peer", "call_remote", "reliable")
func set_ready() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var r = _room_of(pid)
	if r == null or r.state != State.PICK_TEAMS or not r.teams.has(pid): return
	r.ready[pid] = true
	_broadcast(r)
	if r.players.size() == 2 and r.ready.size() == 2: _start_countdown(r)

@rpc("any_peer", "call_remote", "reliable")
func guess(player_id: int, name: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var r = _room_of(pid)
	if r == null or r.state != State.ROUND: return
	var now := Time.get_ticks_msec()
	if r.penalty_until.get(pid, 0) > now: return
	if not _allow("%d:guess" % pid, 30, 60000): return
	var gen: int = r.gen
	var t: Array = r.teams.values()
	var ok: bool = await IndexAPI.check(player_id, t[0], t[1])
	if r.gen != gen or r.state != State.ROUND: return
	if ok:
		r.score[pid] = r.score.get(pid, 0) + 1
		_end_round(r, {"type": "correct", "pid": pid, "name": name})
	else:
		r.penalty_until[pid] = Time.get_ticks_msec() + PENALTY_MS
		r.last = {"type": "wrong", "pid": pid, "name": name}
		_broadcast(r)

@rpc("any_peer", "call_remote", "reliable")
func suggest(kind: String, q: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	if q.length() < 2 or not _allow("%d:suggest" % pid, 12, 1000): return
	var list: Array
	if kind == "team":
		var r0 = _room_of(pid)
		list = await IndexAPI.suggest_teams(q, r0.scope if r0 != null else "all")
	else: list = await IndexAPI.suggest_players(q)
	if kind == "team":
		var r = _room_of(pid)
		if r != null:
			for item in list:
				if not (item is Dictionary) or item.get("id") == null: continue
				var tid := int(item.id)
				item["used"] = r.used_teams.has(tid) or r.teams.values().has(tid)
	suggest_result.rpc_id(pid, kind, q, list)

@rpc("any_peer", "call_remote", "reliable")
func rematch() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var r = _room_of(pid)
	if r == null or r.state != State.GAME_OVER: return
	r.rematch[pid] = true
	if r.players.size() == 2 and r.rematch.size() == 2:
		_reset_match(r); _start_pick(r); return
	_broadcast(r)

# ---------- tek oyunculu ----------
@rpc("any_peer", "call_remote", "reliable")
func single_start(mode: String, scope: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	_leave_everything(pid)
	var seed := "%d-%d" % [Time.get_ticks_usec(), randi()]   # her oturum farklı merdiven / soru seti
	if mode not in SINGLE_LIVES: return
	var items: Array
	match mode:
		"ladder": items = await IndexAPI.ladder(seed, _scope_ok(scope))
		"blitz": items = await IndexAPI.blitz_pack(seed, _scope_ok(scope))
		"career": items = await IndexAPI.pack("/career/pack", {"n": 30})
		"chain": items = await IndexAPI.pack("/chain/pack", {"n": 15})
		"versus": items = await IndexAPI.pack("/versus/pack", {"rounds": 80})
	if items.is_empty(): err.rpc_id(pid, "err.pack_failed"); return
	singles[pid] = {"mode": mode, "seed": seed, "items": items, "idx": 0, "lives": SINGLE_LIVES[mode],
		"score": 0, "combo": 1.0, "deadline": 0, "lock_until": 0, "over": false, "best_combo": 1.0, "gen": 0,
		"revealed": 1, "step": 0, "done": 0}
	_single_next(pid, true)

@rpc("any_peer", "call_remote", "reliable")
func single_guess(player_id: int, name: String) -> void:   # ladder
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var s = singles.get(pid)
	if s == null or s.over or s.mode not in ["ladder", "career"]: return
	var now := Time.get_ticks_msec()
	if s.lock_until > now or not _allow("%d:guess" % pid, 30, 60000): return
	var gen: int = s.gen; var item: Dictionary = s.items[s.idx]
	if s.mode == "career":
		var hit: bool = player_id == int(item._player_id) or Normalize.norm(name) == Normalize.norm(str(item._name))
		if hit:
			var hidden: int = item.clubs.size() - int(s.revealed)
			var gained := 100 + 60 * hidden       # erken bilen çok alır
			s.score += gained; s.done += 1
			s.last = {"type": "correct", "name": str(item._name), "gained": gained}
			_single_next(pid, false)
		else:
			s.lives -= 1
			s.last = {"type": "wrong", "name": name}
			if s.lives <= 0:
				s.last["answer"] = str(item._name); _single_over(pid)
			else: _single_send(pid)
		return
	var ok: bool = await IndexAPI.check(player_id, int(item.a), int(item.b))
	if singles.get(pid) != s or s.gen != gen or s.over: return
	if ok:
		var remaining := maxi(0, s.deadline - Time.get_ticks_msec()) / 1000
		s.score += 100 + remaining * 5
		s.last = {"type": "correct", "name": name}
		_single_next(pid, false)
	else:
		s.lives -= 1   # kilit yok: hemen yeni tahmin
		s.last = {"type": "wrong", "name": name}
		if s.lives <= 0: _single_over(pid)
		else: _single_send(pid)

@rpc("any_peer", "call_remote", "reliable")
func single_answer(option: int) -> void:   # blitz
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var s = singles.get(pid)
	if s == null or s.over or s.mode not in ["blitz", "versus"]: return
	var item: Dictionary = s.items[s.idx]
	if s.mode == "versus":
		if option == int(item._answer):
			var bonus := int(maxi(0, s.deadline - Time.get_ticks_msec()) / 100.0)   # hız bonusu: kalan saniye × 10
			s.score += 100 + bonus; s.done += 1
			s.last = {"type": "correct", "option": option, "values": item._values, "bonus": bonus}
			_single_next(pid, false)
		else:
			s.last = {"type": "wrong", "option": option, "answer": int(item._answer), "values": item._values}
			_single_over(pid)
		return
	if option == int(item._answer):
		s.score += int(round(100 * s.combo)); s.combo = minf(2.0, s.combo + 0.1); s.best_combo = maxf(s.best_combo, s.combo)
		s.last = {"type": "correct", "option": option}
		_single_next(pid, false)
	else:
		s.last = {"type": "wrong", "option": option, "answer": int(item._answer)}
		_single_over(pid)

@rpc("any_peer", "call_remote", "reliable")
func single_team(team_id: int, name: String) -> void:   # chain: sıradaki kulüp tahmini
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var s = singles.get(pid)
	if s == null or s.over or s.mode != "chain": return
	if not _allow("%d:guess" % pid, 30, 60000): return
	var item: Dictionary = s.items[s.idx]
	var st: Dictionary = item._steps[s.step]
	if team_id == int(st.club_id):
		var bonus := int(maxi(0, s.deadline - Time.get_ticks_msec()) / 1000.0) * 5
		s.score += 100 + bonus
		_chain_advance(pid, {"type": "correct", "name": str(st.club), "gained": 100 + bonus})
	else:
		s.lives -= 1
		_chain_advance(pid, {"type": "wrong", "name": name, "answer": str(st.club)})

## Zincirde bir adım bitti (doğru, yanlış ya da süre): cevap açılır, sıradaki adıma ya da oyuncuya geçilir.
func _chain_advance(pid: int, last: Dictionary) -> void:
	var s: Dictionary = singles[pid]
	s.last = last
	if s.lives <= 0: _single_over(pid); return
	var item: Dictionary = s.items[s.idx]
	s.step += 1
	if s.step >= item._steps.size():
		s.done += 1; _single_next(pid, false)
	else:
		s.gen += 1; s.per_ms = CHAIN_STEP_MS; s.deadline = Time.get_ticks_msec() + CHAIN_STEP_MS
		_single_send(pid)

@rpc("any_peer", "call_remote", "reliable")
func single_quit() -> void:
	if not multiplayer.is_server(): return
	singles.erase(multiplayer.get_remote_sender_id())

# ============================================================ RPC: sunucu → istemci
@rpc("authority", "call_remote", "reliable")
func room_state(d: Dictionary) -> void:
	room = d; room_changed.emit(d)

@rpc("authority", "call_remote", "reliable")
func suggest_result(kind: String, q: String, list: Array) -> void:
	suggestions.emit(kind, q, list)

@rpc("authority", "call_remote", "reliable")
func single_state(d: Dictionary) -> void:
	single = d; single_changed.emit(d)

@rpc("authority", "call_remote", "reliable")
func profile_state(d: Dictionary) -> void:
	App.elo = int(d.get("elo", App.elo)); App.save_settings(); profile_changed.emit(d)

@rpc("authority", "call_remote", "reliable")
func err(msg: String) -> void:
	error.emit(T.t(msg))   # sunucu anahtar gönderir (err.*), istemci kendi dilinde gösterir

# ============================================================ sunucu iç mantık
func _scope_ok(s: String) -> String:
	return s if s in ["all", "top", "big5"] else "all"

func _new_room(code: String, ranked: bool, scope := "all") -> Dictionary:
	var r := {"code": code, "ranked": ranked, "scope": scope, "players": [], "state": State.LOBBY, "gen": 0, "rematch": {}, "last": {}}
	_reset_match(r)
	return r

func _reset_match(r: Dictionary) -> void:
	r.teams = {}; r.team_names = {}; r.ready = {}; r.score = {}; r.penalty_until = {}; r.used_teams = {}
	r.invalid_streak = 0; r.phase_end = 0; r.answers = []; r.answers_total = 0; r.winner = 0; r.rematch = {}; r.last = {}
	r.elo_delta = {}; r.away = {}; r.quick_picks = []; r.gen += 1

func _new_code() -> String:
	if words.size() > 0:
		for i in 20:
			var w := String(words[randi() % words.size()])
			if not rooms.has(w): return w
		for i in 50:
			var w2 := "%s%d" % [words[randi() % words.size()], randi() % 90 + 10]
			if not rooms.has(w2): return w2
	while true:
		var code := "%04d" % (randi() % 10000)
		if not rooms.has(code): return code
	return "0000"

func _room_of(pid: int):
	var code = pid_room.get(pid)
	return rooms.get(code) if code != null else null

func _join(code: String, pid: int) -> void:
	var r: Dictionary = rooms[code]
	r.players.append(pid); pid_room[pid] = code
	if r.players.size() == 2:
		_start_pick(r); return
	_broadcast(r)

func _leave_everything(pid: int) -> void:
	queue.erase(pid); queue_since.erase(pid); singles.erase(pid)
	var r = _room_of(pid)
	if r == null: return
	r.players.erase(pid); pid_room.erase(pid)
	if r.players.is_empty():
		rooms.erase(r.code); return
	# rakip gitti: maç ortasındaysa kalan kazanır
	if r.state in [State.PICK_TEAMS, State.COUNTDOWN, State.REVEAL, State.ROUND, State.ROUND_END]:
		r.gen += 1
		r.state = State.GAME_OVER; r.winner = r.players[0]; r.last = {"type": "left"}
		if r.ranked: _apply_elo(r, r.players[0], pid)
	elif r.state == State.GAME_OVER:
		r.last = {"type": "left"}
	_broadcast(r)

func _on_leave(pid: int) -> void:
	var r = _room_of(pid)
	var dev: String = profiles.get(pid, {}).get("device", "")
	if r != null and dev != "" and r.players.size() == 2 and r.state in [State.PICK_TEAMS, State.COUNTDOWN, State.REVEAL, State.ROUND, State.ROUND_END]:
		# 10 sn içinde aynı cihaz geri gelirse maç devam eder
		pending_rc[dev] = {"code": r.code, "pid": pid, "until": Time.get_ticks_msec() + RECONNECT_MS}
		r.away[pid] = true; _broadcast(r)
		queue.erase(pid); queue_since.erase(pid); singles.erase(pid)
		var saved: Dictionary = profiles[pid]
		await get_tree().create_timer(RECONNECT_MS / 1000.0).timeout
		if pending_rc.get(dev, {}).get("pid", -1) == pid:
			pending_rc.erase(dev); profiles[pid] = saved
			_leave_everything(pid); profiles.erase(pid)
		rate.erase("%d:guess" % pid); rate.erase("%d:suggest" % pid)
		return
	_leave_everything(pid); profiles.erase(pid); rate.erase("%d:guess" % pid); rate.erase("%d:suggest" % pid)

func _rebind(r: Dictionary, old: int, new: int) -> void:
	var i: int = r.players.find(old)
	if i >= 0: r.players[i] = new
	for key in ["teams", "team_names", "ready", "score", "penalty_until", "rematch", "elo_delta", "away"]:
		var d: Dictionary = r[key]
		if d.has(old): d[new] = d[old]; d.erase(old)
	r.away.erase(new)
	pid_room.erase(old); pid_room[new] = r.code
	_broadcast(r)

func _start_countdown(r: Dictionary) -> void:
	for t in r.teams.values(): r.used_teams[t] = true
	r.gen += 1
	r.state = State.COUNTDOWN; r.phase_end = Time.get_ticks_msec() + COUNTDOWN_MS; r.last = {}
	_broadcast(r)
	var gen: int = r.gen
	await get_tree().create_timer(COUNTDOWN_MS / 1000.0).timeout
	if r.gen != gen or r.state != State.COUNTDOWN: return
	r.state = State.REVEAL; r.phase_end = Time.get_ticks_msec() + REVEAL_MS
	_broadcast(r)
	await get_tree().create_timer(REVEAL_MS / 1000.0).timeout
	if r.gen != gen or r.state != State.REVEAL: return
	r.state = State.ROUND; r.phase_end = Time.get_ticks_msec() + ROUND_MS
	_broadcast(r)
	await get_tree().create_timer(ROUND_MS / 1000.0).timeout
	if r.gen != gen or r.state != State.ROUND: return
	_end_round(r, {"type": "timeout"})

func _start_pick(r: Dictionary) -> void:
	r.gen += 1
	var gen: int = r.gen
	r.state = State.PICK_TEAMS; r.phase_end = Time.get_ticks_msec() + PICK_MS
	r.quick_picks = []
	_broadcast(r)
	var qp: Array = await IndexAPI.quick_picks(r.scope, r.used_teams.keys())
	if r.gen == gen and r.state == State.PICK_TEAMS:
		r.quick_picks = qp; _broadcast(r)
	await get_tree().create_timer(PICK_MS / 1000.0).timeout
	if r.gen != gen or r.state != State.PICK_TEAMS or r.players.size() < 2: return
	var ready_players: Array = r.players.filter(func(p): return r.ready.get(p, false))
	if ready_players.size() == 1:
		var winner: int = ready_players[0]
		var slow: int = r.players[0] if r.players[1] == winner else r.players[1]
		r.score[winner] = r.score.get(winner, 0) + 1
		r.gen += 1
		r.answers = []; r.answers_total = 0; r.last = {"type": "pick_timeout", "pid": slow}
		for p in r.players:
			if r.score.get(p, 0) >= WIN_SCORE:
				r.state = State.GAME_OVER; r.winner = p
				if r.ranked: _apply_elo(r, p, slow)
				_broadcast(r); return
		r.state = State.ROUND_END; r.phase_end = Time.get_ticks_msec() + ROUND_END_MS
		_broadcast(r)
		var g2: int = r.gen
		await get_tree().create_timer(ROUND_END_MS / 1000.0).timeout
		if r.gen != g2 or r.state != State.ROUND_END: return
		r.teams = {}; r.team_names = {}; r.ready = {}; r.penalty_until = {}; r.last = {}
		_start_pick(r)
	else:
		_start_pick(r)   # ikisi de seçmedi: süre yenilenir

func _end_round(r: Dictionary, last: Dictionary) -> void:
	r.gen += 1
	var gen: int = r.gen
	var t: Array = r.teams.values()
	var ans: Dictionary = await IndexAPI.answers(t[0], t[1])
	if r.gen != gen: return
	r.answers = ans.names; r.answers_total = int(ans.total); r.last = last
	if r.answers_total == 0:
		r.invalid_streak += 1; r.last["no_common"] = true
		if r.invalid_streak >= MAX_INVALID_PAIRS:
			r.state = State.GAME_OVER; r.winner = 0; r.last["draw"] = true; _broadcast(r); return
	else:
		r.invalid_streak = 0
	for pid in r.players:
		if r.score.get(pid, 0) >= WIN_SCORE:
			r.state = State.GAME_OVER; r.winner = pid
			if r.ranked:
				var loser: int = r.players[0] if r.players[1] == pid else r.players[1]
				_apply_elo(r, pid, loser)
			_broadcast(r); return
	r.state = State.ROUND_END; r.phase_end = Time.get_ticks_msec() + ROUND_END_MS
	_broadcast(r)
	await get_tree().create_timer(ROUND_END_MS / 1000.0).timeout
	if r.gen != gen or r.state != State.ROUND_END: return
	r.teams = {}; r.team_names = {}; r.ready = {}; r.penalty_until = {}; r.last = {}; r.answers = []
	_start_pick(r)

func _broadcast(r: Dictionary) -> void:
	var now := Time.get_ticks_msec()
	var peers := multiplayer.get_peers()
	for viewer in r.players:
		if viewer not in peers: continue
		var players := []
		for pid in r.players:
			var p: Dictionary = profiles.get(pid, {"nick": "?", "elo": 1000})
			var hide: bool = r.state == State.PICK_TEAMS and pid != viewer   # rakibin seçimi ikisi de hazır olana kadar gizli
			players.append({"pid": pid, "nick": p.nick, "elo": p.elo, "team": 0 if hide else r.teams.get(pid, 0),
				"team_name": "" if hide else r.team_names.get(pid, ""), "picked": r.teams.get(pid, 0) != 0,
				"ready": r.ready.get(pid, false), "score": r.score.get(pid, 0), "penalty_ms": maxi(0, r.penalty_until.get(pid, 0) - now),
				"rematch": r.rematch.get(pid, false), "elo_delta": r.elo_delta.get(pid, 0), "away": r.away.get(pid, false)})
		var d := {"code": r.code, "ranked": r.ranked, "scope": r.scope, "state": r.state, "players": players, "phase_ms": maxi(0, r.phase_end - now),
			"last": r.last, "answers": r.answers, "answers_total": r.answers_total, "winner": r.winner, "used_teams": r.used_teams.keys(),
			"quick_picks": r.get("quick_picks", [])}
		room_state.rpc_id(viewer, d)

func _send_queue(pid: int) -> void:
	var waited: int = Time.get_ticks_msec() - int(queue_since.get(pid, Time.get_ticks_msec()))
	room_state.rpc_id(pid, {"state": State.LOBBY, "searching": true, "band": _band(pid), "elo": profiles[pid].elo,
		"waiting": queue.size(), "cross_in_ms": maxi(0, CROSS_SCOPE_MS - waited)})

func _band(pid: int) -> int:
	var waited: int = Time.get_ticks_msec() - int(queue_since.get(pid, Time.get_ticks_msec()))
	return mini(BAND_MAX, BAND_START + BAND_STEP * int(waited / BAND_STEP_MS))

func _waited(pid: int) -> int:
	return Time.get_ticks_msec() - int(queue_since.get(pid, Time.get_ticks_msec()))

var _queue_tick := 0
func _tick_queue() -> void:
	var now := Time.get_ticks_msec()
	if now - _queue_tick < 1000: return
	_queue_tick = now
	var i := 0
	while i < queue.size():
		var a: int = queue[i]; var matched := false
		for j in range(i + 1, queue.size()):
			var b: int = queue[j]
			var pa: Dictionary = profiles[a]; var pb: Dictionary = profiles[b]
			if pa.get("verified", false) != pb.get("verified", false): continue
			var cross := _waited(a) >= CROSS_SCOPE_MS and _waited(b) >= CROSS_SCOPE_MS
			if pa.get("scope", "all") != pb.get("scope", "all") and not cross: continue   # aynı kapsam; 45 sn sonra serbest
			var same_last: bool = pa.get("last_opp", "") == pb.get("device", "") and pb.get("device", "") != ""
			if same_last and (_waited(a) < 20000 or _waited(b) < 20000): continue      # az önceki rakip, 20 sn bekle
			if absi(int(pa.elo) - int(pb.elo)) <= mini(_band(a), _band(b)):
				queue.erase(b); queue.erase(a); queue_since.erase(a); queue_since.erase(b)
				var scope_idx := maxi(SCOPE_ORDER.find(pa.get("scope", "all")), SCOPE_ORDER.find(pb.get("scope", "all")))
				pa["last_opp"] = pb.get("device", ""); pb["last_opp"] = pa.get("device", "")
				for dp in [pa, pb]:
					if dp.device != "": _accounts[dp.device] = {"elo": dp.elo, "games": dp.games, "last_opp": dp.last_opp}
				var code := _new_code(); rooms[code] = _new_room(code, true, SCOPE_ORDER[scope_idx])
				_join(code, a); _join(code, b); matched = true; break
		if not matched:
			_send_queue(a); i += 1

func _apply_elo(r: Dictionary, winner: int, loser: int) -> void:
	var pw: Dictionary = profiles.get(winner); var pl: Dictionary = profiles.get(loser)
	if pw == null or pl == null: return
	var ea := 1.0 / (1.0 + pow(10.0, (float(pl.elo) - float(pw.elo)) / 400.0))
	var kw := ELO_K_NEW if int(pw.games) < 20 else ELO_K
	var kl := ELO_K_NEW if int(pl.games) < 20 else ELO_K
	var dw := int(round(kw * (1.0 - ea))); var dl := -int(round(kl * (1.0 - ea)))
	pw.elo += dw; pl.elo += dl; pw.games += 1; pl.games += 1
	r.elo_delta = {winner: dw, loser: dl}
	for pid in [winner, loser]:
		var p: Dictionary = profiles[pid]
		if p.device != "": _accounts[p.device] = {"elo": p.elo, "games": p.games, "last_opp": p.get("last_opp", "")}
		_send_profile(pid)
	_save_accounts()

func _send_profile(pid: int) -> void:
	if pid not in multiplayer.get_peers(): return
	var p: Dictionary = profiles[pid]
	profile_state.rpc_id(pid, {"elo": p.elo, "games": p.games})

func _allow(key: String, max_n: int, window_ms: int) -> bool:
	var now := Time.get_ticks_msec()
	var arr: Array = rate.get(key, [])
	arr = arr.filter(func(t): return now - t < window_ms)
	if arr.size() >= max_n: rate[key] = arr; return false
	arr.append(now); rate[key] = arr; return true

# ---------- tek oyunculu iç ----------
func _single_next(pid: int, first: bool) -> void:
	var s: Dictionary = singles[pid]
	if not first: s.idx += 1
	if s.idx >= s.items.size(): _single_over(pid); return
	s.gen += 1; s.lock_until = 0
	var per_ms: int
	match s.mode:
		"ladder": per_ms = maxi(10000, 20000 - 2000 * int(s.idx / 5))
		"career": per_ms = CAREER_REVEAL_MS; s.revealed = 1
		"chain": per_ms = CHAIN_STEP_MS; s.step = 0
		"versus": per_ms = maxi(4000, 9000 - 500 * int(s.idx / 5))
		_: per_ms = maxi(3000, 8000 - 1000 * int(s.idx / 5))
	s.deadline = Time.get_ticks_msec() + per_ms; s.per_ms = per_ms
	_single_send(pid)

func _tick_singles() -> void:
	var now := Time.get_ticks_msec()
	for pid in singles.keys():
		var s: Dictionary = singles[pid]
		if s.over or s.deadline == 0 or now < s.deadline: continue
		var item: Dictionary = s.items[s.idx]
		if s.mode == "career":
			if int(s.revealed) < item.clubs.size():      # bir kulüp daha aç
				s.revealed += 1; s.last = {}
				s.per_ms = CAREER_REVEAL_MS if int(s.revealed) < item.clubs.size() else CAREER_LAST_MS
				s.deadline = now + int(s.per_ms)
				_single_send(pid); continue
			s.lives -= 1
			s.last = {"type": "timeout", "answer": str(item._name)}
			if s.lives <= 0: _single_over(pid)
			else: _single_next(pid, false)
			continue
		if s.mode == "chain":
			s.lives -= 1
			_chain_advance(pid, {"type": "timeout", "answer": str(item._steps[s.step].club)})
			continue
		if s.mode == "versus":
			s.last = {"type": "timeout", "answer": int(item._answer), "values": item._values}
			_single_over(pid); continue
		s.last = {"type": "timeout"}
		if s.mode == "ladder":
			s.lives -= 1
			if s.lives <= 0: _single_over(pid)
			else: _single_next(pid, false)
		else:
			_single_over(pid)

func _single_over(pid: int) -> void:
	var s: Dictionary = singles[pid]
	s.over = true; s.deadline = 0
	_single_send(pid)

func _single_send(pid: int) -> void:
	var s: Dictionary = singles[pid]
	var now := Time.get_ticks_msec()
	var item: Dictionary = s.items[mini(s.idx, s.items.size() - 1)]
	var pub := {}
	match s.mode:
		"career":
			pub = {"clubs": item.clubs.slice(0, int(s.revealed)), "total": item.clubs.size(), "revealed": int(s.revealed)}
		"chain":
			var steps: Array = item._steps
			var st: int = mini(int(s.step), steps.size())
			pub = {"name": item.name, "born": item.get("born"), "pos": item.get("pos"), "step": st, "steps_total": steps.size(),
				"history": steps.slice(0, st).map(func(x): return {"club": x.club, "year": x.get("year"), "kind": x.kind, "fee": x.get("fee")})}
			if st > 0 and st < steps.size():
				pub["hint"] = {"year": steps[st].get("year"), "kind": steps[st].kind, "fee": steps[st].get("fee")}
		"versus":
			for k in item:
				if not str(k).begins_with("_"): pub[k] = item[k]
		_:
			pub = {"a_name": item.get("a_name", ""), "b_name": item.get("b_name", ""), "a": int(item.get("a", 0)), "b": int(item.get("b", 0))}
			if s.mode == "blitz": pub["options"] = item.options
	single_state.rpc_id(pid, {"mode": s.mode, "idx": s.idx, "total": s.items.size(), "lives": s.lives, "score": s.score, "combo": s.combo, "done": int(s.get("done", 0)),
		"best_combo": s.best_combo, "remaining_ms": maxi(0, s.deadline - now), "per_ms": s.get("per_ms", 0), "lock_ms": 0,
		"over": s.over, "item": pub, "last": s.get("last", {})})

# ---------- kalıcılık ----------
func _load_accounts() -> void:
	var f := FileAccess.open("user://accounts.json", FileAccess.READ)
	if f:
		var d = JSON.parse_string(f.get_as_text())
		if d is Dictionary: _accounts = d

func _save_accounts() -> void:
	var f := FileAccess.open("user://accounts.json", FileAccess.WRITE)
	if f: f.store_string(JSON.stringify(_accounts))

# ============================================================ istemci yardımcıları
func c_hello() -> void: hello.rpc_id(1, App.nickname, App.device_id)
func c_create_room() -> void: create_room.rpc_id(1, App.scope)
func c_join_room(code: String) -> void: join_room.rpc_id(1, code)
func c_find_match() -> void: find_match.rpc_id(1, App.scope)
func c_cancel_find() -> void: cancel_find.rpc_id(1)
func c_leave() -> void: leave_room.rpc_id(1)
func c_pick_team(id: int, name: String) -> void: pick_team.rpc_id(1, id, name)
func c_ready() -> void: set_ready.rpc_id(1)
func c_guess(id: int, name: String) -> void: guess.rpc_id(1, id, name)
func c_suggest(kind: String, q: String) -> void: suggest.rpc_id(1, kind, q)
func c_rematch() -> void: rematch.rpc_id(1)
func c_single_start(mode: String) -> void: single_start.rpc_id(1, mode, App.scope)
func c_single_guess(id: int, name: String) -> void: single_guess.rpc_id(1, id, name)
func c_single_answer(i: int) -> void: single_answer.rpc_id(1, i)
func c_single_team(id: int, name: String) -> void: single_team.rpc_id(1, id, name)
func c_single_quit() -> void: single_quit.rpc_id(1)

func me() -> Dictionary:
	for p in room.get("players", []):
		if p.pid == multiplayer.get_unique_id(): return p
	return {}

func opponent() -> Dictionary:
	for p in room.get("players", []):
		if p.pid != multiplayer.get_unique_id(): return p
	return {}
