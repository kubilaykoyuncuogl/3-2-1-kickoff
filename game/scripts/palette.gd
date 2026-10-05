class_name Palette
## Renk tokenları. docs/palette.md ile aynı. Tema: Palette.mode = Palette.Mode.DARK
enum Mode { LIGHT, DARK }
static var mode: Mode = Mode.LIGHT

const LIGHT := {
	"bg": Color("#F2F2F5"), "surface": Color("#FFFFFF"), "fg": Color("#1B1A21"),
	"muted": Color("#5F5D6B"), "line": Color("#C9C8D3"), "line_strong": Color("#9F9DAD"),
	"violet_shade": Color("#3E3193"), "amber_shade": Color("#B57618"),
	"violet_fill": Color("#5E4BC9"), "violet_ink": Color("#4A3AAE"), "violet_soft": Color("#E9E5FA"), "violet_on": Color("#FFFFFF"),
	"amber_fill": Color("#E9A23B"), "amber_ink": Color("#9A6207"), "amber_soft": Color("#FBEFD8"), "amber_on": Color("#1B1A21"),
	"ok": Color("#167A52"), "ok_soft": Color("#DCF3E8"),
	"no": Color("#C2334F"), "no_soft": Color("#FBE1E7"),
}
const DARK := {
	"bg": Color("#131218"), "surface": Color("#1C1B23"), "fg": Color("#ECEBF2"),
	"muted": Color("#A09EAD"), "line": Color("#3A3946"), "line_strong": Color("#5B5A6B"),
	"violet_shade": Color("#6657C4"), "amber_shade": Color("#C58C34"),
	"violet_fill": Color("#8C7CF0"), "violet_ink": Color("#B3A7FF"), "violet_soft": Color("#272443"), "violet_on": Color("#131218"),
	"amber_fill": Color("#F0B45A"), "amber_ink": Color("#F4C77A"), "amber_soft": Color("#3A2D14"), "amber_on": Color("#131218"),
	"ok": Color("#4FCF93"), "ok_soft": Color("#163528"),
	"no": Color("#FF7D96"), "no_soft": Color("#3C1B25"),
}

static func c(token: String) -> Color:
	return (DARK if mode == Mode.DARK else LIGHT)[token]

## side: 0 = mor (A), 1 = amber (B)
static func side(side_idx: int, role: String) -> Color:
	return c(("violet_" if side_idx == 0 else "amber_") + role)
