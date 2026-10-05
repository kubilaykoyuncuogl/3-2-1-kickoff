class_name Palette
## Renk tokenları. docs/palette.md ile aynı. Tema: Palette.set_theme(Palette.Theme.DARK)
enum Theme { LIGHT, DARK }
static var theme: Theme = Theme.LIGHT

const LIGHT := {
	"bg": Color("#F2F2F5"), "surface": Color("#FFFFFF"), "fg": Color("#1B1A21"),
	"muted": Color("#5F5D6B"), "line": Color("#DCDBE3"),
	"violet_fill": Color("#5E4BC9"), "violet_ink": Color("#4A3AAE"), "violet_soft": Color("#E9E5FA"), "violet_on": Color("#FFFFFF"),
	"orchid_fill": Color("#B83E8E"), "orchid_ink": Color("#9A2E77"), "orchid_soft": Color("#FAE4F2"), "orchid_on": Color("#FFFFFF"),
	"ok": Color("#167A52"), "ok_soft": Color("#DCF3E8"),
	"no": Color("#BE2F28"), "no_soft": Color("#FBE3E0"),
}
const DARK := {
	"bg": Color("#131218"), "surface": Color("#1C1B23"), "fg": Color("#ECEBF2"),
	"muted": Color("#A09EAD"), "line": Color("#2E2D38"),
	"violet_fill": Color("#8C7CF0"), "violet_ink": Color("#B3A7FF"), "violet_soft": Color("#272443"), "violet_on": Color("#131218"),
	"orchid_fill": Color("#E57DC2"), "orchid_ink": Color("#F09BD4"), "orchid_soft": Color("#3E1F34"), "orchid_on": Color("#131218"),
	"ok": Color("#4FCF93"), "ok_soft": Color("#163528"),
	"no": Color("#FF7A6B"), "no_soft": Color("#3E1F1A"),
}

static func c(token: String) -> Color:
	return (DARK if theme == Theme.DARK else LIGHT)[token]

## side: 0 = mor (A), 1 = orkide (B)
static func side(side_idx: int, role: String) -> Color:
	return c(("violet_" if side_idx == 0 else "orchid_") + role)
