extends Node
## Sunucu tarafı: Python index servisine HTTP köprüsü (yalnızca headless sunucuda kullanılır).
var base := "http://127.0.0.1:9081"

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var i := args.find("--index")
	if i >= 0 and i + 1 < args.size(): base = args[i + 1]

func get_json(path: String, params := {}) -> Variant:
	var url := base + path
	if not params.is_empty():
		var parts: PackedStringArray = []
		for k in params: parts.append("%s=%s" % [k, str(params[k]).uri_encode()])
		url += "?" + "&".join(parts)
	var req := HTTPRequest.new()
	req.timeout = 10
	add_child(req)
	var err := req.request(url)
	if err != OK:
		req.queue_free(); push_warning("index istek hatası %s %s" % [err, url]); return null
	var res: Array = await req.request_completed
	req.queue_free()
	if res[1] != 200:
		push_warning("index %s → %s" % [url, res[1]]); return null
	return JSON.parse_string(res[3].get_string_from_utf8())

func suggest_teams(q: String, scope := "all") -> Array:
	var r = await get_json("/teams/suggest", {"q": q, "scope": scope})
	return r if r is Array else []

func suggest_players(q: String) -> Array:
	var r = await get_json("/players/suggest", {"q": q})
	return r if r is Array else []

func quick_picks(scope: String, exclude: Array) -> Array:
	var r = await get_json("/quick_picks", {"scope": scope, "n": 5, "exclude": ",".join(exclude.map(func(x): return str(x)))})
	return r if r is Array else []

func club_in_scope(club_id: int, scope: String) -> bool:
	var r = await get_json("/club/%d" % club_id, {"scope": scope})
	return r is Dictionary and r.get("in_scope", false)

func check(player_id: int, a: int, b: int) -> bool:
	var r = await get_json("/check", {"player_id": player_id, "club_a": a, "club_b": b})
	return r is Dictionary and r.get("ok", false)

func answers(a: int, b: int) -> Dictionary:
	var r = await get_json("/pair/answers", {"club_a": a, "club_b": b})
	return r if r is Dictionary else {"names": [], "total": 0}

func ladder(seed: String, scope := "all") -> Array:
	var r = await get_json("/ladder", {"steps": 27, "scope": scope})   # seed yok → hazır havuzdan
	return r.get("steps", []) if r is Dictionary else []

func blitz_pack(seed: String, scope := "all") -> Array:
	## reveal=1: soru başına "_answer" (doğru şık indeksi) gelir; yalnızca sunucu bellekte tutar.
	var r = await get_json("/blitz/pack", {"n": 40, "reveal": 1, "scope": scope})   # seed yok → hazır havuzdan
	return r.get("questions", []) if r is Dictionary else []
