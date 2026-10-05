extends Node
## Oyun durum makinesi. Sunucu otorite; istemciler sadece state_changed sinyalini dinler.
enum State { LOBBY, PICK_TEAMS, COUNTDOWN, ROUND, ROUND_END, GAME_OVER }
const ROUND_SECONDS := 15.0
const COUNTDOWN_SECONDS := 3.0
const PENALTY_SECONDS := 5.0
const WIN_SCORE := 3

signal state_changed(state: State, payload: Dictionary)

var state: State = State.LOBBY
var players: Array[int] = []            # peer id'ler
var teams := {}                          # peer id -> team id
var ready_set := {}                      # peer id -> bool
var score := {}                          # peer id -> int
var penalty_until := {}                  # peer id -> msec
var round_end_msec := 0

# ---------- istemci -> sunucu ----------
@rpc("any_peer", "call_remote", "reliable")
func pick_team(team_id: int) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	if state != State.PICK_TEAMS: return
	if teams.values().has(team_id): return   # aynı takım iki kez seçilemez
	teams[pid] = team_id
	_broadcast()

@rpc("any_peer", "call_remote", "reliable")
func set_ready() -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	if state != State.PICK_TEAMS or not teams.has(pid): return
	ready_set[pid] = true
	if ready_set.size() == 2: _start_countdown()

@rpc("any_peer", "call_remote", "reliable")
func guess(name: String) -> void:
	if not multiplayer.is_server(): return
	var pid := multiplayer.get_remote_sender_id()
	if state != State.ROUND: return
	var now := Time.get_ticks_msec()
	if penalty_until.get(pid, 0) > now: return
	var t := teams.values()
	if Index.played_for_both(Normalize.norm(name), t[0], t[1]):
		score[pid] = score.get(pid, 0) + 1
		_end_round({"winner": pid, "answer": name})
	else:
		penalty_until[pid] = now + int(PENALTY_SECONDS * 1000)
		_broadcast({"penalty": pid})

# ---------- sunucu iç akış ----------
func _start_countdown() -> void:
	state = State.COUNTDOWN; _broadcast()
	await get_tree().create_timer(COUNTDOWN_SECONDS).timeout
	state = State.ROUND
	round_end_msec = Time.get_ticks_msec() + int(ROUND_SECONDS * 1000)
	_broadcast()
	await get_tree().create_timer(ROUND_SECONDS).timeout
	if state == State.ROUND: _end_round({"winner": 0})

func _end_round(payload: Dictionary) -> void:
	var t := teams.values()
	payload["answers"] = Index.common_players(t[0], t[1])
	for pid in players:
		if score.get(pid, 0) >= WIN_SCORE:
			state = State.GAME_OVER; _broadcast(payload); return
	state = State.ROUND_END; _broadcast(payload)
	await get_tree().create_timer(4.0).timeout
	teams.clear(); ready_set.clear(); penalty_until.clear()
	state = State.PICK_TEAMS; _broadcast()

func _broadcast(extra := {}) -> void:
	var payload := {"teams": teams, "ready": ready_set, "score": score,
		"round_end_msec": round_end_msec, "penalty_until": penalty_until}
	payload.merge(extra)
	_sync.rpc(state, payload)

@rpc("authority", "call_local", "reliable")
func _sync(s: State, payload: Dictionary) -> void:
	state = s
	state_changed.emit(s, payload)
