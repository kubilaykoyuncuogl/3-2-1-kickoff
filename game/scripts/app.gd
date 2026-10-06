extends Node
## Uygulama durumu: ayarlar (user://settings.cfg), tema, sayfa yığını ve geçişler.

const SETTINGS_PATH := "user://settings.cfg"
const SLIDE_MS := 0.22

var nickname := ""
var theme_mode := "system"       # system | light | dark
var sound := true
var music_vol := 0.7
var sfx_vol := 1.0
var haptics := true
var lang := "tr"
var reduce_motion := false
var elo := 1000
var verified := false
var linked := false          # cihaz bir hesaba bağlı mı (sunucudan gelir)
var devices := 1
var device_id := ""
var best := {"ladder": 0, "blitz": 0}   # cihazdaki en iyi tek oyunculu skorlar
var scope := "all"                      # kulüp kapsamı: all | top | big5
const SCOPES := ["all", "top", "big5"]
var era := 0                            # dönem: on yıl bit maskesi, 0 = tümü
const ERAS := [["80", 1], ["90", 2], ["00", 4], ["10", 8], ["20", 16]]

## Dönem düğmesi mantığı: Tümü tek başına; Tümü seçiliyken bir on yıla basınca yalnız o; sonra aç/kapa; hiçbiri kalmazsa Tümü
func era_toggle(bit: int) -> void:
	if bit == 0: era = 0
	elif era == 0: era = bit
	else: era ^= bit
	save_settings()

var _root: Control
var _stack: Array[Control] = []

const BASE_W := 400.0
const MAX_SCALE := 1.5

func _ready() -> void:
	load_settings()
	ensure_device_id()
	apply_theme()
	if not Net.is_server:
		get_tree().root.size_changed.connect(_fit_scale)
		_fit_scale()
		get_tree().node_added.connect(func(n): if n is Label: _fit_label.call_deferred(n))

## Taşma koruması: dikey kutudaki uzun yazı satıra sarılır; yatay kutuda esneyen yazı sığmazsa üç noktayla kesilir.
func _fit_label(l: Label) -> void:
	if not is_instance_valid(l) or not l.is_inside_tree(): return
	var p := l.get_parent()
	if p is HBoxContainer:
		if (l.size_flags_horizontal & Control.SIZE_EXPAND) and not l.clip_text and l.autowrap_mode == TextServer.AUTOWRAP_OFF:
			l.clip_text = true; l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		return
	if l.autowrap_mode != TextServer.AUTOWRAP_OFF or l.clip_text or l.text.length() < 22: return
	if p is VBoxContainer or p is PanelContainer or p is MarginContainer:
		var gp := p.get_parent()
		if p is VBoxContainer and gp is HBoxContainer and not (p.size_flags_horizontal & Control.SIZE_EXPAND): return   # daralan sütun: sarma harf harf böler
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

## Ölçek yalnızca genişlikten: telefon = 1.0, masaüstü en çok 1.5. Yükseklik (klavye açılınca kısalır) ölçeği etkilemez.
func _fit_scale() -> void:
	var root := get_tree().root
	var w := float(root.size.x); var h := float(root.size.y)
	if w <= 0 or h <= 0: return
	var scale := clampf(w / BASE_W, 1.0, MAX_SCALE)
	root.content_scale_size = Vector2i(int(round(w / scale)), int(round(h / scale)))

# ---------- ayarlar ----------
func load_settings() -> void:
	var cf := ConfigFile.new()
	if cf.load(SETTINGS_PATH) != OK: return
	nickname = cf.get_value("profile", "nickname", "")
	theme_mode = cf.get_value("look", "theme", "system")
	reduce_motion = cf.get_value("look", "reduce_motion", false)
	lang = cf.get_value("look", "lang", "tr")
	sound = cf.get_value("sound", "on", true)
	music_vol = cf.get_value("sound", "music", 0.7)
	sfx_vol = cf.get_value("sound", "sfx", 1.0)
	haptics = cf.get_value("sound", "haptics", true)
	elo = cf.get_value("online", "elo", 1000)
	device_id = cf.get_value("online", "device", "")
	best = cf.get_value("single", "best", {"ladder": 0, "blitz": 0})
	scope = cf.get_value("single", "scope", "all")
	era = int(cf.get_value("single", "era", 0)) & 31
	T.load_lang(lang)

func ensure_device_id() -> void:
	if device_id == "":
		var rng := RandomNumberGenerator.new(); rng.randomize()
		device_id = "%08x%08x%08x%08x" % [rng.randi(), rng.randi(), rng.randi(), rng.randi()]
		save_settings()

func save_settings() -> void:
	var cf := ConfigFile.new()
	cf.set_value("profile", "nickname", nickname)
	cf.set_value("look", "theme", theme_mode); cf.set_value("look", "reduce_motion", reduce_motion); cf.set_value("look", "lang", lang)
	cf.set_value("sound", "on", sound); cf.set_value("sound", "music", music_vol); cf.set_value("sound", "sfx", sfx_vol); cf.set_value("sound", "haptics", haptics)
	cf.set_value("online", "elo", elo); cf.set_value("online", "device", device_id)
	cf.set_value("single", "best", best); cf.set_value("single", "scope", scope); cf.set_value("single", "era", era)
	cf.save(SETTINGS_PATH)

func apply_theme() -> void:
	var dark := theme_mode == "dark" or (theme_mode == "system" and DisplayServer.is_dark_mode())
	Palette.mode = Palette.Mode.DARK if dark else Palette.Mode.LIGHT
	UI._fonts.clear()
	RenderingServer.set_default_clear_color(Palette.c("bg"))

# ---------- sayfa yığını ----------
func bind_root(root: Control) -> void:
	_root = root

func push(screen: Control) -> void:
	var prev: Control = _stack.back() if _stack.size() > 0 else null
	_stack.append(screen)
	_root.add_child(screen)
	screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	if prev and not reduce_motion:
		var w := _root.size.x
		screen.position.x = w
		var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
		tw.tween_property(screen, "position:x", 0.0, SLIDE_MS)
		tw.parallel().tween_property(prev, "position:x", -w * 0.25, SLIDE_MS)
		tw.tween_callback(func(): prev.visible = false)
	elif prev:
		prev.visible = false

func pop() -> void:
	if _stack.size() < 2: return
	var top: Control = _stack.pop_back()
	var prev: Control = _stack.back()
	prev.visible = true
	if not reduce_motion:
		var w := _root.size.x
		var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
		tw.tween_property(top, "position:x", w, SLIDE_MS)
		tw.parallel().tween_property(prev, "position:x", 0.0, SLIDE_MS)
		tw.tween_callback(top.queue_free)
	else:
		prev.position.x = 0; top.queue_free()

## Mevcut sayfayı aynı sınıftan yeniden kurar (tema değişimi sonrası)
func rebuild_top() -> void:
	if _stack.is_empty(): return
	var top: Control = _stack.pop_back()
	var fresh: Control = top.get_script().new()
	top.queue_free()
	_stack.append(fresh); _root.add_child(fresh)
	fresh.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

## Tema değişiminde: yığındaki her sayfayı aynı script'ten yeniden kurar (görünürlük ve sıra korunur)
func rebuild_all() -> void:
	var fresh: Array[Control] = []
	for i in _stack.size():
		var old: Control = _stack[i]
		var n: Control = old.get_script().new()
		for prop in ["mode"]:
			if prop in old and prop in n: n.set(prop, old.get(prop))
		_root.add_child(n)
		n.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		n.visible = i == _stack.size() - 1
		old.queue_free()
		fresh.append(n)
	_stack = fresh

func reset_to(screen: Control) -> void:
	for s in _stack: s.queue_free()
	_stack.clear()
	push(screen)
