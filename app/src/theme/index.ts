// Tema kancası: renkler (açık/koyu) + ölçek (400 px tasarım genişliği; 0.8–1.5).
import { useColorScheme, useWindowDimensions } from "react-native";
import { DARK, LIGHT, Colors, Token } from "./palette";
import { useSettings } from "../store";

export const BASE_W = 400;
export const MAX_SCALE = 1.5;
export const MIN_SCALE = 0.8;
export const MIN_H = 720;            // geniş ekranda bir sayfanın sığması gereken tasarım yüksekliği
export const MAX_COL = 520;

export const FONT = { 500: "Sora_500Medium", 600: "Sora_600SemiBold", 700: "Sora_700Bold", 800: "Sora_800ExtraBold" } as const;
export type Weight = keyof typeof FONT;

export function useTheme() {
  const scheme = useColorScheme();
  const mode = useSettings((s) => s.theme_mode);
  const { width, height } = useWindowDimensions();
  const dark = mode === "dark" || (mode === "system" && scheme === "dark");
  const c: Colors = dark ? DARK : LIGHT;
  // Telefonda yalnızca genişlikten (klavye açılınca yükseklik oynar, ölçek zıplamasın); 400'den dar ekranda küçülür (en az 0.8).
  // Tablet ve masaüstünde (genişlik ≥ 600) sayfa dikeyde de sığsın diye yükseklikle de sınırlanır.
  let scale = width / BASE_W;
  if (width >= 600) scale = Math.min(scale, height / MIN_H);
  scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale));
  const s = (n: number) => Math.round(n * scale);
  const col = Math.min(MAX_COL * scale, width - s(40));     // sayfa sütunu: 20 px kenar, tablet/masaüstünde ortalanır
  return { c, s, dark, scale, width, height, col };
}
export type Theme = ReturnType<typeof useTheme>;
export type { Token, Colors };
