class_name UI
## Tema ve yapı taşları. Tüm renkler Palette'ten, tüm yazılar Sora'dan gelir.
## Ölçek: 11 / 13 / 15 / 18 / 22 / 28 / 56 (docs/palette.md, docs/screens.md)

const FONT_PATH := "res://assets/fonts/Sora[wght].ttf"
const RADIUS := 14
const BORDER := 2

static var _fonts := {}

static func font(weight: int, slant := false) -> FontVariation:
	var key := "%d%s" % [weight, "s" if slant else ""]
	if not _fonts.has(key):
		var fv := FontVariation.new()
		fv.base_font = load(FONT_PATH)
		fv.variation_opentype = {0x77676874: weight}   # "wght" tag
		if slant: fv.variation_transform = Transform2D(Vector2(1.0, 0.0524), Vector2(0.0, 1.0), Vector2.ZERO)
		_fonts[key] = fv
	return _fonts[key]

static func c(token: String) -> Color:
	return Palette.c(token)

# ---------- metin ----------
static func label(text: String, size := 16, weight := 500, color := "fg") -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font(weight))
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", c(color))
	return l

static func eyebrow(text: String, color := "muted") -> Label:
	var l := label(text.to_upper(), 11, 700, color)
	l.add_theme_constant_override("line_spacing", 0)
	return l

static func wordmark() -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 0)
	var big := label("3·2·1", 44, 800)
	big.add_theme_font_override("font", font(800, true))
	var small := eyebrow("KICKOFF")
	v.add_child(big); v.add_child(small)
	return v

# ---------- kutular ----------
static func box(bg: String, border := "", radius := RADIUS, border_w := BORDER, shadow := "") -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = c(bg) if bg != "" else Color.TRANSPARENT
	s.set_corner_radius_all(radius)
	if border != "":
		s.set_border_width_all(border_w); s.border_color = c(border)
	if shadow != "":
		s.shadow_color = c(shadow); s.shadow_size = 0; s.shadow_offset = Vector2(0, 2)
		s.set_expand_margin_all(0)
	s.content_margin_left = 16; s.content_margin_right = 16
	s.content_margin_top = 12; s.content_margin_bottom = 12
	return s

## kind: "violet" | "amber" | "line" | "ghost"
static func button(text: String, kind := "violet", right_text := "") -> Button:
	var b := Button.new()
	b.text = text.to_upper() if kind != "ghost" else text
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT if right_text != "" else HORIZONTAL_ALIGNMENT_CENTER
	b.custom_minimum_size = Vector2(0, 56 if kind != "ghost" else 44)
	b.add_theme_font_override("font", font(800 if kind != "ghost" else 600))
	b.add_theme_font_size_override("font_size", 16)
	var normal: StyleBoxFlat; var fg: String
	match kind:
		"violet": normal = box("violet_fill", "", RADIUS, 0, "violet_shade"); fg = "violet_on"
		"amber": normal = box("amber_fill", "", RADIUS, 0, "amber_shade"); fg = "amber_on"
		"line": normal = box("", "line_strong"); fg = "fg"
		_: normal = box(""); fg = "muted"
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.shadow_offset = Vector2.ZERO
	pressed.bg_color = normal.bg_color.darkened(0.08) if kind in ["violet", "amber"] else c("bg")
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = normal.bg_color.lightened(0.05) if kind in ["violet", "amber"] else c("bg")
	for st in ["normal", "disabled"]: b.add_theme_stylebox_override(st, normal)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for st in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(st, c(fg))
	b.add_theme_color_override("font_disabled_color", c(fg).darkened(0.3))
	if right_text != "":
		var r := label(right_text, 18, 800, fg)
		r.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT)
		r.offset_left = -80; r.offset_right = -16; r.offset_top = -14; r.offset_bottom = 14
		r.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		b.add_child(r)
	return b

## side: "violet" | "amber" | "" (çerçeveli kart)
static func panel(side := "") -> PanelContainer:
	var p := PanelContainer.new()
	var st: StyleBoxFlat
	match side:
		"violet": st = box("violet_soft", "", 16, 0)
		"amber": st = box("amber_soft", "", 16, 0)
		_: st = box("surface", "line", 16)
	p.add_theme_stylebox_override("panel", st)
	return p

static func chip(text: String, kind := "violet") -> PanelContainer:
	var p := PanelContainer.new()
	var bg: String = {"violet": "violet_soft", "amber": "amber_soft", "ok": "ok_soft", "no": "no_soft", "line": ""}[kind]
	var fg: String = {"violet": "violet_ink", "amber": "amber_ink", "ok": "ok", "no": "no", "line": "fg"}[kind]
	var st := box(bg, "line" if kind == "line" else "", 999, BORDER if kind == "line" else 0)
	st.content_margin_left = 10; st.content_margin_right = 10; st.content_margin_top = 4; st.content_margin_bottom = 4
	p.add_theme_stylebox_override("panel", st)
	p.add_child(label(text, 13, 600, fg))
	return p

## Büyük renkli bildirim şeridi. kind: "ok" | "no" | "muted"
static func toast(text: String, kind := "ok") -> PanelContainer:
	var p := PanelContainer.new()
	var bg: String = {"ok": "ok_soft", "no": "no_soft", "muted": "surface"}[kind]
	var fg: String = {"ok": "ok", "no": "no", "muted": "muted"}[kind]
	var st := box(bg, fg, 12, 2)
	st.content_margin_top = 12; st.content_margin_bottom = 12
	p.add_theme_stylebox_override("panel", st)
	var l := label(text, 16, 800, fg)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	p.add_child(l)
	return p

## Can göstergesi: dolu daireler kalan, boş daireler giden
static func lives(n: int, total := 3) -> HBoxContainer:
	var h := hbox(6); h.alignment = BoxContainer.ALIGNMENT_CENTER
	for i in total:
		var d := Panel.new(); d.custom_minimum_size = Vector2(16, 16)
		d.size_flags_vertical = Control.SIZE_SHRINK_CENTER; d.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		var alive := i < n
		var st := StyleBoxFlat.new(); st.set_corner_radius_all(999)
		if alive:
			st.bg_color = c("ok") if n >= 2 else c("no")
		else:
			st.bg_color = Color.TRANSPARENT; st.set_border_width_all(2); st.border_color = c("line_strong")
		d.add_theme_stylebox_override("panel", st)
		h.add_child(d)
	return h

## Yanlışta yatay sallanma
static func shake(node: Control) -> void:
	if node == null or not node.is_inside_tree(): return
	var x := node.position.x
	var tw := node.create_tween()
	for dx in [10, -10, 7, -7, 0]:
		tw.tween_property(node, "position:x", x + dx, 0.045)

## Segment seçici (Sistem / Açık / Koyu gibi)
static func segment(vals: Array, labels: Array, current: String, cb: Callable) -> HBoxContainer:
	var h := hbox(4)
	for i in vals.size():
		var b := Button.new(); b.text = labels[i]; b.toggle_mode = true; b.button_pressed = vals[i] == current
		b.custom_minimum_size = Vector2(0, 36)
		b.add_theme_font_override("font", font(600)); b.add_theme_font_size_override("font_size", 12)
		var on := box("fg", "", 8, 0); on.content_margin_left = 10; on.content_margin_right = 10; on.content_margin_top = 4; on.content_margin_bottom = 4
		var off := box("", "line_strong", 8); off.content_margin_left = 10; off.content_margin_right = 10; off.content_margin_top = 4; off.content_margin_bottom = 4
		b.add_theme_stylebox_override("normal", off); b.add_theme_stylebox_override("hover", off); b.add_theme_stylebox_override("pressed", on); b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		b.add_theme_color_override("font_color", c("fg")); b.add_theme_color_override("font_pressed_color", c("bg")); b.add_theme_color_override("font_hover_color", c("fg"))
		var val: String = vals[i]
		b.pressed.connect(func(): cb.call(val))
		h.add_child(b)
	return h

## Kulüp kapsamı seçici (Tümü / Üst ligler / 5 büyük lig); App.scope'a yazar
static func scope_picker(on_change: Callable) -> VBoxContainer:
	var v := vbox(4)
	v.add_child(eyebrow("Kulüp kapsamı"))
	var seg := segment(App.SCOPES, App.SCOPE_LABELS, App.scope, func(val):
		App.scope = val; App.save_settings(); on_change.call(val))
	seg.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	v.add_child(seg)
	return v

static func scope_label(s: String) -> String:
	var i := App.SCOPES.find(s)
	return App.SCOPE_LABELS[i] if i >= 0 else "Tümü"

static func vbox(sep := 10) -> VBoxContainer:
	var v := VBoxContainer.new(); v.add_theme_constant_override("separation", sep); return v

static func hbox(sep := 10) -> HBoxContainer:
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", sep); return h

static func spacer(min_h := 0) -> Control:
	var s := Control.new()
	s.size_flags_vertical = Control.SIZE_EXPAND_FILL
	s.custom_minimum_size.y = min_h
	return s

static func nav(title: String, on_back: Callable) -> HBoxContainer:
	var h := hbox(8)
	var back := Button.new()
	back.text = "<"; back.flat = true; back.custom_minimum_size = Vector2(44, 44)
	back.add_theme_font_override("font", font(600)); back.add_theme_font_size_override("font_size", 28)
	back.add_theme_color_override("font_color", c("fg"))
	back.pressed.connect(on_back)
	var t := eyebrow(title); t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var pad := Control.new(); pad.custom_minimum_size.x = 44
	h.add_child(back); h.add_child(t); h.add_child(pad)
	return h

## Sayfa iskeleti: güvenli alan + 20 px kenar boşluğu + dikey kutu
const MAX_COL := 520.0
static func page() -> VBoxContainer:
	var v := vbox(12)
	v.set_anchors_preset(Control.PRESET_FULL_RECT)
	v.tree_entered.connect(func(): _layout_page(v); v.get_viewport().size_changed.connect(func(): _layout_page(v)))
	return v

static func _layout_page(v: VBoxContainer) -> void:
	if not v.is_inside_tree(): return
	var w := v.get_viewport_rect().size.x
	var half := minf(MAX_COL, w - 40.0) / 2.0
	v.anchor_left = 0.5; v.anchor_right = 0.5; v.anchor_top = 0.0; v.anchor_bottom = 1.0
	v.offset_left = -half; v.offset_right = half; v.offset_top = 16; v.offset_bottom = -16
