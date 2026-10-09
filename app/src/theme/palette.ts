// Renk tokenları. Değer kaynağı: design/tokens.json (tasarım kiti v0.2); adlar bizim kısa adlarımız.
// Kitle gelenler: control (yazı kutusu / gerekli kontrol sınırı), surface_subtle (devre dışı ve basılı nötr yüzey), violet_soft_pressed,
// açık temada amber_ink ve no bir ton koyu (küçük yazıda kontrast). *_shade tokenları kitte yok; yalnızca eski ekranlarda kalan yerler için duruyor.
export const LIGHT = {
  bg: "#F2F2F5", surface: "#FFFFFF", surface_subtle: "#E9E9EF", fg: "#1B1A21",
  muted: "#5F5D6B", line: "#C9C8D3", line_strong: "#9F9DAD", control: "#858292",
  violet_shade: "#3E3193", amber_shade: "#B57618",
  violet_fill: "#5E4BC9", violet_pressed: "#4A3AAE", violet_ink: "#4A3AAE", violet_soft: "#E9E5FA", violet_soft_pressed: "#DCD5F7", violet_on: "#FFFFFF",
  amber_fill: "#E9A23B", amber_ink: "#895706", amber_soft: "#FBEFD8", amber_on: "#1B1A21",
  ok: "#167A52", ok_soft: "#DCF3E8",
  no: "#B72E48", no_soft: "#FBE1E7",
};
export const DARK: typeof LIGHT = {
  bg: "#131218", surface: "#1C1B23", surface_subtle: "#272630", fg: "#ECEBF2",
  muted: "#A09EAD", line: "#3A3946", line_strong: "#5B5A6B", control: "#747184",
  violet_shade: "#6657C4", amber_shade: "#C58C34",
  violet_fill: "#8C7CF0", violet_pressed: "#9C8DF5", violet_ink: "#B3A7FF", violet_soft: "#272443", violet_soft_pressed: "#343057", violet_on: "#131218",
  amber_fill: "#F0B45A", amber_ink: "#F4C77A", amber_soft: "#3A2D14", amber_on: "#131218",
  ok: "#4FCF93", ok_soft: "#163528",
  no: "#FF7D96", no_soft: "#3C1B25",
};
export type Token = keyof typeof LIGHT;
export type Colors = typeof LIGHT;
