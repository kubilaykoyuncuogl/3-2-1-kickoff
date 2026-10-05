extends Node
## Oyun mantığı. Aynı script iki tarafta da yüklü:
##  - sunucuda (Net.is_server): odalar, eşleşme, tur akışı, Elo, tek oyunculu oturumlar
##  - istemcide: sunucudan gelen durumun aynası + sinyaller
## Oyuncu→kulüp ilişkisi yalnızca Index servisinde; buradan istemciye ad listesi, sonuç ve tur sonu cevapları gider.

enum State { LOBBY, PICK_TEAMS, COUNTDOWN, ROUND, ROUND_END, GAME_OVER }
const ROUND_MS := 15000
const COUNTDOWN_MS := 3000
const PENALTY_MS := 5000
const ROUND_END_MS := 4000
const WIN_SCORE := 3
const MAX_INVALID_PAIRS := 3
const ELO_K := 32
const ELO_K_NEW := 40

# ---------- istemci tarafı ----------
signal room_changed(d: Dictionary)
signal suggestions(kind: String, list: Array)
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
var packs := {}         # "ladder:day" / "blitz:day" -> Array
var daily := {}         # day -> {mode: [{nick, score}]}
var rate := {}          # pid -> Array[msec]
var _accounts := {}     # device -> {elo, games}

func _ready() -> void:
	my_id = 0
	if Net.is_server:
		multiplayer.peer_disconnected.connect(_on_leave)
		multiplayer.peer_connected.connect(func(pid): profiles[pid] = {"nick": "misafir", "device": "", "elo": 1000, "games": 0})
		_load_accounts()
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
	profiles[pid] = {"nick": nick.strip_edges().substr(0, 16), "device": device, "elo": acc.elo, "games": acc.games}
	_send_profile(pid)

@rpc("any_peer", "call_remote", "reliable")
func create_room() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	_leave_everything(pid)
	var code := _new_code()
	rooms[code] = _new_room(code, false)
	_join(code, pid)

@rpc("any_peer", "call_remote", "reliable")
func join_room(code: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	code = code.strip_edges()
	if not rooms.has(code): err.rpc_id(pid, "Oda bulunamadı"); return
	if rooms[code].players.size() >= 2: err.rpc_id(pid, "Oda dolu"); return
	_leave_everything(pid)
	_join(code, pid)

@rpc("any_peer", "call_remote", "reliable")
func find_match() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	_leave_everything(pid)
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
	if r.used_teams.has(team_id): err.rpc_id(pid, "Bu takım bu maçta kullanıldı"); return
	for other in r.teams:
		if other != pid and r.teams[other] == team_id: err.rpc_id(pid, "Rakip bu takımı seçti, başka seç"); return
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
	if not _allow(pid, 20, 60000): return
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
	if q.length() < 2 or not _allow(pid, 6, 1000): return
	var list: Array
	if kind == "team": list = await IndexAPI.suggest_teams(q)
	else: list = await IndexAPI.suggest_players(q)
	if kind == "team":
		var r = _room_of(pid)
		if r != null:
			for item in list:
				item["used"] = r.used_teams.has(int(item.id)) or (r.teams.values().has(int(item.id)))
	suggest_result.rpc_id(pid, kind, q, list)

@rpc("any_peer", "call_remote", "reliable")
func rematch() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var r = _room_of(pid)
	if r == null or r.state != State.GAME_OVER: return
	r.rematch[pid] = true
	if r.players.size() == 2 and r.rematch.size() == 2:
		_reset_match(r); r.state = State.PICK_TEAMS
	_broadcast(r)

# ---------- tek oyunculu ----------
@rpc("any_peer", "call_remote", "reliable")
func single_start(mode: String, practice: bool) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	_leave_everything(pid)
	var day := Time.get_date_string_from_system(true)
	var items: Array = await _pack(mode, day)
	if items.is_empty(): err.rpc_id(pid, "Paket yüklenemedi"); return
	singles[pid] = {"mode": mode, "day": day, "practice": practice, "items": items, "idx": 0, "lives": 3 if mode == "ladder" else 1,
		"score": 0, "combo": 1.0, "deadline": 0, "lock_until": 0, "over": false, "best_combo": 1.0, "gen": 0}
	_single_next(pid, true)

@rpc("any_peer", "call_remote", "reliable")
func single_guess(player_id: int, name: String) -> void:   # ladder
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var s = singles.get(pid)
	if s == null or s.over or s.mode != "ladder": return
	var now := Time.get_ticks_msec()
	if s.lock_until > now or not _allow(pid, 20, 60000): return
	var gen: int = s.gen; var item: Dictionary = s.items[s.idx]
	var ok: bool = await IndexAPI.check(player_id, int(item.a), int(item.b))
	if singles.get(pid) != s or s.gen != gen or s.over: return
	if ok:
		var remaining := maxi(0, s.deadline - Time.get_ticks_msec()) / 1000
		s.score += 100 + remaining * 5
		s.last = {"type": "correct", "name": name}
		_single_next(pid, false)
	else:
		s.lives -= 1; s.lock_until = Time.get_ticks_msec() + 3000
		s.last = {"type": "wrong", "name": name}
		if s.lives <= 0: _single_over(pid)
		else: _single_send(pid)

@rpc("any_peer", "call_remote", "reliable")
func single_answer(option: int) -> void:   # blitz
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	var s = singles.get(pid)
	if s == null or s.over or s.mode != "blitz": return
	var item: Dictionary = s.items[s.idx]
	if option == int(item._answer):
		s.score += int(round(100 * s.combo)); s.combo = minf(2.0, s.combo + 0.1); s.best_combo = maxf(s.best_combo, s.combo)
		s.last = {"type": "correct", "option": option}
		_single_next(pid, false)
	else:
		s.last = {"type": "wrong", "option": option, "answer": int(item._answer)}
		_single_over(pid)

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
	suggestions.emit(kind, list)

@rpc("authority", "call_remote", "reliable")
func single_state(d: Dictionary) -> void:
	single = d; single_changed.emit(d)

@rpc("authority", "call_remote", "reliable")
func profile_state(d: Dictionary) -> void:
	App.elo = int(d.get("elo", App.elo)); App.save_settings(); profile_changed.emit(d)

@rpc("authority", "call_remote", "reliable")
func err(msg: String) -> void:
	error.emit(msg)

# ============================================================ sunucu iç mantık
func _new_room(code: String, ranked: bool) -> Dictionary:
	var r := {"code": code, "ranked": ranked, "players": [], "state": State.LOBBY, "gen": 0, "rematch": {}, "last": {}}
	_reset_match(r)
	return r

func _reset_match(r: Dictionary) -> void:
	r.teams = {}; r.team_names = {}; r.ready = {}; r.score = {}; r.penalty_until = {}; r.used_teams = {}
	r.invalid_streak = 0; r.phase_end = 0; r.answers = []; r.answers_total = 0; r.winner = 0; r.rematch = {}; r.last = {}
	r.elo_delta = {}; r.gen += 1

func _new_code() -> String:
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
		r.state = State.PICK_TEAMS
	_broadcast(r)

func _leave_everything(pid: int) -> void:
	queue.erase(pid); queue_since.erase(pid); singles.erase(pid)
	var r = _room_of(pid)
	if r == null: return
	r.players.erase(pid); pid_room.erase(pid)
	if r.players.is_empty():
		rooms.erase(r.code); return
	# rakip gitti: maç ortasındaysa kalan kazanır
	if r.state in [State.PICK_TEAMS, State.COUNTDOWN, State.ROUND, State.ROUND_END]:
		r.gen += 1
		r.state = State.GAME_OVER; r.winner = r.players[0]; r.last = {"type": "left"}
		if r.ranked: _apply_elo(r, r.players[0], pid)
	elif r.state == State.GAME_OVER:
		r.last = {"type": "left"}
	_broadcast(r)

func _on_leave(pid: int) -> void:
	_leave_everything(pid); profiles.erase(pid); rate.erase(pid)

func _start_countdown(r: Dictionary) -> void:
	for t in r.teams.values(): r.used_teams[t] = true
	r.state = State.COUNTDOWN; r.phase_end = Time.get_ticks_msec() + COUNTDOWN_MS; r.last = {}
	_broadcast(r)
	var gen: int = r.gen
	await get_tree().create_timer(COUNTDOWN_MS / 1000.0).timeout
	if r.gen != gen or r.state != State.COUNTDOWN: return
	r.state = State.ROUND; r.phase_end = Time.get_ticks_msec() + ROUND_MS
	_broadcast(r)
	await get_tree().create_timer(ROUND_MS / 1000.0).timeout
	if r.gen != gen or r.state != State.ROUND: return
	_end_round(r, {"type": "timeout"})

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
	r.state = State.PICK_TEAMS
	_broadcast(r)

func _broadcast(r: Dictionary) -> void:
	var now := Time.get_ticks_msec()
	var players := []
	for pid in r.players:
		var p: Dictionary = profiles.get(pid, {"nick": "?", "elo": 1000})
		players.append({"pid": pid, "nick": p.nick, "elo": p.elo, "team": r.teams.get(pid, 0), "team_name": r.team_names.get(pid, ""),
			"ready": r.ready.get(pid, false), "score": r.score.get(pid, 0), "penalty_ms": maxi(0, r.penalty_until.get(pid, 0) - now),
			"rematch": r.rematch.get(pid, false), "elo_delta": r.elo_delta.get(pid, 0)})
	var d := {"code": r.code, "ranked": r.ranked, "state": r.state, "players": players, "phase_ms": maxi(0, r.phase_end - now),
		"last": r.last, "answers": r.answers, "answers_total": r.answers_total, "winner": r.winner, "used_teams": r.used_teams.keys()}
	var peers := multiplayer.get_peers()
	for pid in r.players:
		if pid in peers: room_state.rpc_id(pid, d)

func _send_queue(pid: int) -> void:
	var band := _band(pid)
	room_state.rpc_id(pid, {"state": State.LOBBY, "searching": true, "band": band, "elo": profiles[pid].elo})

func _band(pid: int) -> int:
	var waited: int = Time.get_ticks_msec() - int(queue_since.get(pid, Time.get_ticks_msec()))
	return 100 + 100 * int(waited / 10000)

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
			if absi(int(pa.elo) - int(pb.elo)) <= mini(_band(a), _band(b)):
				queue.erase(b); queue.erase(a); queue_since.erase(a); queue_since.erase(b)
				var code := _new_code(); rooms[code] = _new_room(code, true)
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
		if p.device != "": _accounts[p.device] = {"elo": p.elo, "games": p.games}
		_send_profile(pid)
	_save_accounts()

func _send_profile(pid: int) -> void:
	if pid not in multiplayer.get_peers(): return
	var p: Dictionary = profiles[pid]
	profile_state.rpc_id(pid, {"elo": p.elo, "games": p.games})

func _allow(pid: int, max_n: int, window_ms: int) -> bool:
	var now := Time.get_ticks_msec()
	var arr: Array = rate.get(pid, [])
	arr = arr.filter(func(t): return now - t < window_ms)
	if arr.size() >= max_n: rate[pid] = arr; return false
	arr.append(now); rate[pid] = arr; return true

# ---------- tek oyunculu iç ----------
func _pack(mode: String, day: String) -> Array:
	var key := "%s:%s" % [mode, day]
	if not packs.has(key):
		if mode == "ladder": packs[key] = await IndexAPI.ladder(day)
		else: packs[key] = await IndexAPI.blitz_pack(day)
	return packs[key]

func _single_next(pid: int, first: bool) -> void:
	var s: Dictionary = singles[pid]
	if not first: s.idx += 1
	if s.idx >= s.items.size(): _single_over(pid); return
	s.gen += 1; s.lock_until = 0
	var per_ms: int
	if s.mode == "ladder": per_ms = maxi(10000, 20000 - 2000 * int(s.idx / 5))
	else: per_ms = maxi(3000, 8000 - 1000 * int(s.idx / 5))
	s.deadline = Time.get_ticks_msec() + per_ms; s.per_ms = per_ms
	_single_send(pid)

func _tick_singles() -> void:
	var now := Time.get_ticks_msec()
	for pid in singles.keys():
		var s: Dictionary = singles[pid]
		if s.over or s.deadline == 0 or now < s.deadline: continue
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
	var board := []
	if not s.practice:
		var d: Dictionary = daily.get(s.day, {}); var lst: Array = d.get(s.mode, [])
		lst.append({"nick": profiles.get(pid, {"nick": "?"}).nick, "score": s.score, "pid": pid})
		lst.sort_custom(func(x, y): return x.score > y.score)
		d[s.mode] = lst.slice(0, 100); daily[s.day] = d; board = d[s.mode]
	s.board = board
	_single_send(pid)

func _single_send(pid: int) -> void:
	var s: Dictionary = singles[pid]
	var now := Time.get_ticks_msec()
	var item: Dictionary = s.items[mini(s.idx, s.items.size() - 1)]
	var pub := {"a_name": item.get("a_name", ""), "b_name": item.get("b_name", ""), "a": int(item.get("a", 0)), "b": int(item.get("b", 0))}
	if s.mode == "blitz": pub["options"] = item.options
	var rank := 0
	if s.over:
		for i in s.get("board", []).size():
			if s.board[i].pid == pid: rank = i + 1; break
	single_state.rpc_id(pid, {"mode": s.mode, "idx": s.idx, "total": s.items.size(), "lives": s.lives, "score": s.score, "combo": s.combo,
		"best_combo": s.best_combo, "remaining_ms": maxi(0, s.deadline - now), "per_ms": s.get("per_ms", 0), "lock_ms": maxi(0, s.lock_until - now),
		"over": s.over, "item": pub, "last": s.get("last", {}), "board": s.get("board", []).slice(0, 10), "rank": rank, "practice": s.practice})

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
func c_create_room() -> void: create_room.rpc_id(1)
func c_join_room(code: String) -> void: join_room.rpc_id(1, code)
func c_find_match() -> void: find_match.rpc_id(1)
func c_cancel_find() -> void: cancel_find.rpc_id(1)
func c_leave() -> void: leave_room.rpc_id(1)
func c_pick_team(id: int, name: String) -> void: pick_team.rpc_id(1, id, name)
func c_ready() -> void: set_ready.rpc_id(1)
func c_guess(id: int, name: String) -> void: guess.rpc_id(1, id, name)
func c_suggest(kind: String, q: String) -> void: suggest.rpc_id(1, kind, q)
func c_rematch() -> void: rematch.rpc_id(1)
func c_single_start(mode: String, practice: bool) -> void: single_start.rpc_id(1, mode, practice)
func c_single_guess(id: int, name: String) -> void: single_guess.rpc_id(1, id, name)
func c_single_answer(i: int) -> void: single_answer.rpc_id(1, i)
func c_single_quit() -> void: single_quit.rpc_id(1)

func me() -> Dictionary:
	for p in room.get("players", []):
		if p.pid == multiplayer.get_unique_id(): return p
	return {}

func opponent() -> Dictionary:
	for p in room.get("players", []):
		if p.pid != multiplayer.get_unique_id(): return p
	return {}
