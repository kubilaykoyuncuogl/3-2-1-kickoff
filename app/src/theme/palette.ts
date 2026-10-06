// Renk tokenları. docs/palette.md ve game/scripts/palette.gd ile aynı hex'ler.
export const LIGHT = {
  bg: "#F2F2F5", surface: "#FFFFFF", fg: "#1B1A21",
  muted: "#5F5D6B", line: "#C9C8D3", line_strong: "#9F9DAD",
  violet_shade: "#3E3193", amber_shade: "#B57618",
  violet_fill: "#5E4BC9", violet_ink: "#4A3AAE", violet_soft: "#E9E5FA", violet_on: "#FFFFFF",
  amber_fill: "#E9A23B", amber_ink: "#9A6207", amber_soft: "#FBEFD8", amber_on: "#1B1A21",
  ok: "#167A52", ok_soft: "#DCF3E8",
  no: "#C2334F", no_soft: "#FBE1E7",
};
export const DARK: typeof LIGHT = {
  bg: "#131218", surface: "#1C1B23", fg: "#ECEBF2",
  muted: "#A09EAD", line: "#3A3946", line_strong: "#5B5A6B",
  violet_shade: "#6657C4", amber_shade: "#C58C34",
  violet_fill: "#8C7CF0", violet_ink: "#B3A7FF", violet_soft: "#272443", violet_on: "#131218",
  amber_fill: "#F0B45A", amber_ink: "#F4C77A", amber_soft: "#3A2D14", amber_on: "#131218",
  ok: "#4FCF93", ok_soft: "#163528",
  no: "#FF7D96", no_soft: "#3C1B25",
};
export type Token = keyof typeof LIGHT;
export type Colors = typeof LIGHT;
