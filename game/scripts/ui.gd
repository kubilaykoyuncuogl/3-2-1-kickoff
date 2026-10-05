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
static func label(text: String, size := 17, weight := 500, color := "fg") -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font(weight))
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", c(color))
	return l

static func eyebrow(text: String, color := "muted") -> Label:
	var l := label(text.to_upper(), 12, 700, color)
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

## İkon: beyaz SVG, tema rengine boyanır
static func icon(path: String, size: float, color: String) -> TextureRect:
	var ic := TextureRect.new(); ic.texture = load(path); ic.custom_minimum_size = Vector2(size, size)
	ic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; ic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	ic.self_modulate = c(color); ic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	ic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return ic

static func chevron(color := "muted", left := false, size := 18.0) -> TextureRect:
	var ic := icon("res://assets/icons/chevron.svg", size, color); ic.flip_h = left
	return ic

## kind: "violet" | "amber" | "line" | "ghost".  right_text: ">" ok işareti çizer, başka metin sağa yazılır
static func button(text: String, kind := "violet", right_text := "") -> Button:
	var b := Button.new()
	b.text = text
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT if right_text != "" else HORIZONTAL_ALIGNMENT_CENTER
	b.custom_minimum_size = Vector2(0, 54 if kind != "ghost" else 44)
	b.add_theme_font_override("font", font(700 if kind != "ghost" else 600))
	b.add_theme_font_size_override("font_size", 16)
	b.clip_text = true
	var normal: StyleBoxFlat; var fg: String
	match kind:
		"violet": normal = box("violet_fill", "", RADIUS, 0, "violet_shade"); fg = "violet_on"
		"amber": normal = box("amber_fill", "", RADIUS, 0, "amber_shade"); fg = "amber_on"
		"line": normal = box("surface", "line"); fg = "fg"
		_: normal = box(""); fg = "muted"
	normal.content_margin_left = 18; normal.content_margin_right = 18
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.shadow_offset = Vector2.ZERO
	pressed.bg_color = normal.bg_color.darkened(0.08) if kind in ["violet", "amber"] else c("bg")
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = normal.bg_color.lightened(0.05) if kind in ["violet", "amber"] else c("bg")
	if kind == "line": hover.border_color = c("line_strong"); pressed.border_color = c("line_strong")
	var dis := normal.duplicate() as StyleBoxFlat
	if kind in ["violet", "amber"]: dis.bg_color = Color(normal.bg_color, 0.45); dis.shadow_color = Color.TRANSPARENT
	b.add_theme_stylebox_override("normal", normal); b.add_theme_stylebox_override("disabled", dis)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for st in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_disabled_color"]:
		b.add_theme_color_override(st, c(fg))
	if right_text != "":
		var r: Control = chevron(fg) if right_text == ">" else label(right_text, 17, 800, fg)
		r.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT)
		r.offset_left = -90; r.offset_right = -16; r.offset_top = -12; r.offset_bottom = 12
		if r is Label: r.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		else: r.offset_left = -36
		r.mouse_filter = Control.MOUSE_FILTER_IGNORE
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
	p.add_child(label(text, 14, 600, fg))
	return p

## Renkli bildirim şeridi. kind: "ok" | "no" | "muted"
static func toast(text: String, kind := "ok") -> PanelContainer:
	var p := PanelContainer.new()
	var bg: String = {"ok": "ok_soft", "no": "no_soft", "muted": "surface"}[kind]
	var fg: String = {"ok": "ok", "no": "no", "muted": "muted"}[kind]
	var st := box(bg, fg if kind != "muted" else "line", 12, 2)
	st.content_margin_top = 10; st.content_margin_bottom = 10
	p.add_theme_stylebox_override("panel", st)
	var l := label(text, 16, 700, fg)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	p.add_child(l)
	return p

## Sıra numarası / küçük etiket rozeti (26 px)
static func badge(text: String, kind := "muted") -> PanelContainer:
	var p := PanelContainer.new()
	var bg: String = {"muted": "bg", "violet": "violet_fill", "amber": "amber_fill", "ok": "ok_soft", "no": "no_soft"}[kind]
	var fg: String = {"muted": "muted", "violet": "violet_on", "amber": "amber_on", "ok": "ok", "no": "no"}[kind]
	var st := box(bg, "", 9, 0); st.content_margin_left = 0; st.content_margin_right = 0; st.content_margin_top = 0; st.content_margin_bottom = 0
	p.add_theme_stylebox_override("panel", st)
	p.custom_minimum_size = Vector2(28, 28); p.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var l := label(text, 13, 800, fg); l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	p.add_child(l)
	return p

## Liste satırı: [rozet] başlık (+ alt satır) ……… [sağ kontrol].  state: "" | "new" (vurgulu) | "hidden" (henüz açılmamış)
static func row(index: String, title: String, sub := "", right: Control = null, state := "") -> PanelContainer:
	var p := PanelContainer.new()
	var st: StyleBoxFlat
	match state:
		"new": st = box("violet_soft", "violet_fill", 12, 2)
		"hidden": st = box("", "line", 12, 2)
		_: st = box("surface", "line", 12, 2)
	st.content_margin_left = 10; st.content_margin_right = 12; st.content_margin_top = 8; st.content_margin_bottom = 8
	p.add_theme_stylebox_override("panel", st)
	p.custom_minimum_size.y = 48
	var h := hbox(10)
	h.add_child(badge(index, "violet" if state == "new" else "muted"))
	var tv := vbox(0); tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL; tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var t := label(title, 16, 700, "violet_ink" if state == "new" else ("muted" if state == "hidden" else "fg"))
	t.clip_text = true; t.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	tv.add_child(t)
	if sub != "":
		var sl := label(sub, 12, 500, "violet_ink" if state == "new" else "muted"); sl.clip_text = true; sl.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		tv.add_child(sl)
	h.add_child(tv)
	if right != null:
		right.size_flags_vertical = Control.SIZE_SHRINK_CENTER; h.add_child(right)
	p.add_child(h)
	return p

## İpucu karosu: küçük başlık + değer
static func kv(key: String, value: String, kind := "violet") -> PanelContainer:
	var p := PanelContainer.new()
	var st := box("surface", "", 10, 0); st.content_margin_left = 12; st.content_margin_right = 12; st.content_margin_top = 8; st.content_margin_bottom = 8
	p.add_theme_stylebox_override("panel", st)
	var v := vbox(0)
	v.add_child(label(key.to_upper(), 10, 700, "muted"))
	v.add_child(label(value, 17, 800, kind + "_ink"))
	p.add_child(v)
	return p

static func flow(sep := 8) -> HFlowContainer:
	var f := HFlowContainer.new(); f.add_theme_constant_override("h_separation", sep); f.add_theme_constant_override("v_separation", sep); return f

## Sayaç kutusu: [PanelContainer, Label]
static func timer_box() -> Array:
	var p := PanelContainer.new()
	var st := box("surface", "line", 12, 2); st.content_margin_left = 10; st.content_margin_right = 10; st.content_margin_top = 2; st.content_margin_bottom = 2
	p.add_theme_stylebox_override("panel", st); p.custom_minimum_size = Vector2(56, 40); p.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var l := label("", 22, 800); l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	p.add_child(l)
	return [p, l]

static func progress(max_v: float) -> ProgressBar:
	var bar := ProgressBar.new(); bar.max_value = max_v; bar.value = max_v; bar.show_percentage = false; bar.custom_minimum_size.y = 6
	bar.add_theme_stylebox_override("background", box("line", "", 999, 0)); bar.add_theme_stylebox_override("fill", box("fg", "", 999, 0))
	return bar

## Seçenek kartı: [ön kontrol] başlık + açıklama ……… [arka kontrol].  kind: "surface" | "amber" | "violet"
static func option_card(title: String, sub: String, lead: Control = null, tail: Control = null, selected := false, kind := "surface", height := 76.0) -> Button:
	var b := Button.new()
	b.custom_minimum_size.y = height
	var bg := "violet_soft" if selected else ({"surface": "surface", "amber": "amber_soft", "violet": "violet_soft"}[kind] as String)
	var edge := "violet_fill" if selected else ("line" if kind == "surface" else "")
	var hover_edge: String = {"surface": "line_strong", "amber": "amber_fill", "violet": "violet_fill"}[kind]
	b.add_theme_stylebox_override("normal", box(bg, edge, 16, 2))
	for stn in ["hover", "pressed"]: b.add_theme_stylebox_override(stn, box(bg, "violet_fill" if selected else hover_edge, 16, 2))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var ink: String = "violet_ink" if selected else ({"surface": "fg", "amber": "amber_ink", "violet": "violet_ink"}[kind] as String)
	var sub_ink: String = "violet_ink" if selected else ({"surface": "muted", "amber": "amber_ink", "violet": "violet_ink"}[kind] as String)
	var h := hbox(12); h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	h.offset_left = 14; h.offset_right = -14; h.offset_top = 8; h.offset_bottom = -8
	if lead != null: h.add_child(lead)
	var tv := vbox(2); tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL; tv.alignment = BoxContainer.ALIGNMENT_CENTER
	var tl := label(title, 17, 800, ink); tl.clip_text = true; tl.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	tv.add_child(tl)
	if sub != "":
		var sl := label(sub, 12, 500, sub_ink); sl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; sl.max_lines_visible = 2
		tv.add_child(sl)
	h.add_child(tv)
	if tail != null:
		tail.size_flags_vertical = Control.SIZE_SHRINK_CENTER; h.add_child(tail)
	_ignore_mouse(h)
	b.add_child(h)
	return b

static func _ignore_mouse(n: Node) -> void:
	if n is Control: n.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for ch in n.get_children(): _ignore_mouse(ch)

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

const SCOPE_INFO := {   # [başlık anahtarı, açıklama anahtarı, ikon: svg yolu ya da "text:<glif>" (Sora ExtraBold)]
	"all": ["scope.all.title", "scope.all.sub", "res://assets/icons/globe.svg"],
	"top": ["scope.top.title", "scope.top.sub", "res://assets/icons/crown.svg"],
	"big5": ["scope.big5.title", "scope.big5.sub", "text:5"],
}

static func _scope_icon(src: String, ink: String, compact: bool) -> Control:
	var sz := 28.0 if compact else 36.0
	if src.begins_with("text:"):
		var l := label(src.substr(5), int(sz * 1.2), 800, ink)
		l.custom_minimum_size = Vector2(sz, sz)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		return l
	return icon(src, sz, ink)

## İkonlu kapsam düğmesi. compact: Online'da seçim (seçili işaretli), değilse Tek oyna'da ileri oklu
static func scope_button(scope: String, selected: bool, on_press: Callable, compact := false) -> Button:
	var info: Array = SCOPE_INFO[scope]
	var ink := "violet_ink" if selected else "fg"
	var tail: Control = null
	if not compact: tail = chevron("violet_ink" if selected else "muted")
	elif selected: tail = badge(T.t("selected"), "violet"); tail.custom_minimum_size = Vector2(58, 26)
	var b := option_card(T.t(info[0]), T.t(info[1]), _scope_icon(info[2], ink, compact), tail, selected, "surface", 72.0 if compact else 76.0)
	b.pressed.connect(func(): on_press.call(scope))
	return b

## Kulüp kapsamı seçici: alt alta üç ikonlu düğme; App.scope'a yazar
static func scope_picker(on_change: Callable) -> VBoxContainer:
	var v := vbox(6)
	v.add_child(eyebrow(T.t("scope.header")))
	for sc in App.SCOPES:
		v.add_child(scope_button(sc, App.scope == sc, func(val):
			App.scope = val; App.save_settings(); on_change.call(val), true))
	return v

static func scope_label(s: String) -> String:
	return T.t("scope.%s.title" % (s if s in App.SCOPES else "all"))

## Ülke adı: dil paketinde karşılığı varsa o, yoksa kaynak ad
static func country(name) -> String:
	if name == null or str(name) == "": return ""
	var k := "country." + str(name); var v := T.t(k)
	return str(name) if v == k else v

## Para biçimi: 23300000 → "€23,3M", 450000 → "€450K"
static func money(v: int) -> String:
	if v >= 1000000:
		var m := v / 1000000.0
		var s := ("%.1f" % m).trim_suffix(".0")
		return "€%sM" % (s.replace(".", ",") if T.lang == "tr" else s)
	if v >= 1000: return "€%dK" % int(v / 1000.0)
	return "€%d" % v

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
	back.custom_minimum_size = Vector2(40, 40); back.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var st := box("surface", "line", 12, 2); st.content_margin_left = 0; st.content_margin_right = 0; st.content_margin_top = 0; st.content_margin_bottom = 0
	var st2 := st.duplicate() as StyleBoxFlat; st2.border_color = c("line_strong")
	back.add_theme_stylebox_override("normal", st); back.add_theme_stylebox_override("hover", st2); back.add_theme_stylebox_override("pressed", st2)
	back.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var ch := chevron("fg", true, 18.0); ch.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); back.add_child(ch)
	back.pressed.connect(on_back)
	var t := eyebrow(title); t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; t.clip_text = true
	var pad := Control.new(); pad.custom_minimum_size.x = 40
	h.add_child(back); h.add_child(t); h.add_child(pad)
	return h

## Sayfa iskeleti: güvenli alan + 20 px kenar boşluğu + dikey kutu
const MAX_COL := 520.0
static func page() -> VBoxContainer:
	var v := vbox(12)
	v.set_anchors_preset(Control.PRESET_FULL_RECT)
	v.tree_entered.connect(func():
		_layout_page(v)
		var vp := v.get_viewport(); var cb := func(): _layout_page(v)
		vp.size_changed.connect(cb)
		v.tree_exiting.connect(func(): if vp.size_changed.is_connected(cb): vp.size_changed.disconnect(cb)))
	return v

static func _layout_page(v: VBoxContainer) -> void:
	if not v.is_inside_tree(): return
	var w := v.get_viewport_rect().size.x
	var half := minf(MAX_COL, w - 40.0) / 2.0
	v.anchor_left = 0.5; v.anchor_right = 0.5; v.anchor_top = 0.0; v.anchor_bottom = 1.0
	v.offset_left = -half; v.offset_right = half; v.offset_top = 16; v.offset_bottom = -16
