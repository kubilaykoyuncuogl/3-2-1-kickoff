// Tema kancası: renkler (açık/koyu) + ölçek. Ölçek Godot'daki gibi yalnızca genişlikten: 400 px tasarım genişliği, en fazla 1.5.
import { useColorScheme, useWindowDimensions } from "react-native";
import { DARK, LIGHT, Colors, Token } from "./palette";
import { useSettings } from "../store";

export const BASE_W = 400;
export const MAX_SCALE = 1.5;
export const MAX_COL = 520;

export const FONT = { 500: "Sora_500Medium", 600: "Sora_600SemiBold", 700: "Sora_700Bold", 800: "Sora_800ExtraBold" } as const;
export type Weight = keyof typeof FONT;

export function useTheme() {
  const scheme = useColorScheme();
  const mode = useSettings((s) => s.theme_mode);
  const { width, height } = useWindowDimensions();
  const dark = mode === "dark" || (mode === "system" && scheme === "dark");
  const c: Colors = dark ? DARK : LIGHT;
  const scale = Math.min(MAX_SCALE, Math.max(1, width / BASE_W));
  const s = (n: number) => Math.round(n * scale);
  const col = Math.min(MAX_COL * scale, width - s(40));     // sayfa sütunu: 20 px kenar, tablet/masaüstünde ortalanır
  return { c, s, dark, scale, width, height, col };
}
export type Theme = ReturnType<typeof useTheme>;
export type { Token, Colors };
