class_name T
## Dil paketi. Metinler res://lang/<kod>.json içinde (anahtar → metin).
## Kullanım: T.t("menu.online")  ·  T.t("sp.step") % 3  ·  T.t("anahtar", [a, b])
## Eksik anahtar önce Türkçeye, o da yoksa anahtarın kendisine düşer (sunucudan gelen hata anahtarları da buradan çevrilir).
const DIR := "res://lang/"
const FALLBACK := "tr"
static var lang := "tr"
static var _d := {}
static var _fb := {}

static func available() -> Array:
	var out: Array = []
	for f in DirAccess.get_files_at(DIR):
		if f.ends_with(".json"): out.append(f.trim_suffix(".json"))
	if out.is_empty(): out = ["tr", "en"]
	out.sort()
	if FALLBACK in out: out.erase(FALLBACK); out.push_front(FALLBACK)
	return out

static func load_lang(code: String) -> void:
	if _fb.is_empty(): _fb = _read(FALLBACK)
	lang = code if FileAccess.file_exists(DIR + code + ".json") else FALLBACK
	_d = _fb if lang == FALLBACK else _read(lang)

static func _read(code: String) -> Dictionary:
	var f := FileAccess.open(DIR + code + ".json", FileAccess.READ)
	if f == null: return {}
	var v = JSON.parse_string(f.get_as_text())
	return v if v is Dictionary else {}

static func t(key: String, args: Array = []) -> String:
	if _fb.is_empty(): load_lang(lang)
	var s: String = str(_d.get(key, _fb.get(key, key)))
	return s % args if not args.is_empty() else s
