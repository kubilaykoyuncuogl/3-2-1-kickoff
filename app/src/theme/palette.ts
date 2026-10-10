// Renk tokenları: Forest Lime (design/forest-lime/tokens/tokens.json, 2026-10-10). Tek tema; açık tema kaldırıldı (etkinlik temaları sonra).
// Kit adları (canvas, surface, raised, primary, text, …) asıl adlardır. Eski adlar (violet_*, amber_*, ok, no…) eski ekranlar yeniden yazılana kadar
// aynı renklere takma addır: violet = ana eylem / seçili (lime + aktif yeşil), amber = rakip / uyarı (kitte ikinci aksan yok, warning tonu kullanılır).
const KIT = {
  canvas: "#013026", surface: "#043A2F", raised: "#124B38",
  primary: "#DAEC5A", primary_pressed: "#C3DB46", on_primary: "#013026",
  text: "#FFFBEA", text_muted: "#B6C6B9",
  border_quiet: "#3E7862", border_control: "#78A38A",
  active_surface: "#235C3C", active_border: "#6C9A5B",
  success: "#DAEC5A", error: "#FFB3AD", warning: "#F7D680",
  scrim: "#001A14CC", nav_solid: "#093D2E", nav_surface: "rgba(9,61,46,0.94)",
};
export const DARK = {
  ...KIT,
  // eski adlar → kit renkleri
  bg: KIT.canvas, surface_subtle: KIT.raised, fg: KIT.text,
  muted: KIT.text_muted, line: KIT.border_quiet, line_strong: "#5E8F74", control: KIT.border_control,
  violet_shade: "#BFD24A", amber_shade: KIT.primary_pressed,
  violet_fill: KIT.primary, violet_pressed: KIT.primary_pressed, violet_ink: KIT.primary, violet_soft: KIT.active_surface, violet_soft_pressed: "#2C6B47", violet_on: KIT.on_primary,
  // rakip / ikincil: zemin koyu çam yeşili (aktif yeşilden ayrışsın), yazı kitin uyarı sarısı; dolgu düğmesi lime (kitte ikinci aksan yok)
  amber_fill: KIT.primary, amber_ink: KIT.warning, amber_soft: "#0B3D3A", amber_on: KIT.on_primary,
  ok: KIT.success, ok_soft: "#1E4A2E",
  no: KIT.error, no_soft: "#4A2320",
};
export const LIGHT = DARK;      // tek tema (eski içe aktarmalar bozulmasın)
export type Token = keyof typeof DARK;
export type Colors = typeof DARK;
