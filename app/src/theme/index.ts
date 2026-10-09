// Tema kancası: renkler (açık/koyu) + ölçek (400 px tasarım genişliği; 0.8–1.5).
import { useColorScheme, useWindowDimensions } from "react-native";
import { DARK, LIGHT, Colors, Token } from "./palette";
import { useKeyboard } from "../keyboard";
import { useSettings } from "../store";

export const BASE_W = 400;
export const MAX_SCALE = 1.5;
export const MIN_SCALE = 0.8;
export const MIN_H = 720;            // geniş ekranda bir sayfanın sığması gereken tasarım yüksekliği
export const MAX_COL = 520;

export const FONT = { 400: "Sora_400Regular", 500: "Sora_500Medium", 600: "Sora_600SemiBold", 700: "Sora_700Bold", 800: "Sora_800ExtraBold" } as const;
export type Weight = keyof typeof FONT;

// Yazı rolleri (design/DESIGN.md "Tipografi kararları"): [boyut, satır yüksekliği, ağırlık]. Değerler 400 genişlikteki tasarım ölçüsüdür;
// ekranda useTheme().s ile ekran genişliğine orantılı ölçeklenir (ekip kararı 2026-10-09: orantılı ölçek kalır, sayfa kaymaz; kaydırma gereken yerde eleman içinde).
export const TYPE = {
  display: [40, 48, 800], countdown: [64, 72, 800], screenTitle: [28, 36, 700], navTitle: [20, 28, 600], sectionTitle: [20, 28, 700],
  score: [32, 40, 700], scoreCompact: [20, 28, 700], timer: [24, 32, 700],
  body: [16, 24, 400], bodyStrong: [16, 24, 600], label: [16, 22, 600], fieldLabel: [14, 20, 600], input: [18, 26, 400], caption: [14, 20, 500],
} as const satisfies Record<string, readonly [number, number, Weight]>;
export type TypeRole = keyof typeof TYPE;
// Ölçüler (design/tokens.json "size"): en az dokunma alanı, düğme, yazı kutusu / öneri / ayar satırı
export const SIZE = { touch: 48, button: 52, input: 56, row: 56, icon: 24 } as const;

export function useTheme() {
  const scheme = useColorScheme();
  const mode = useSettings((s) => s.theme_mode);
  const { width, height } = useWindowDimensions();
  const kb = useKeyboard((k) => k.open);      // klavye açık: ekranlar sıkı düzene geçer (başlık, geçmiş listesi gibi ikincil parçalar gizlenir)
  const dark = mode === "dark" || (mode === "system" && scheme === "dark");
  const c: Colors = dark ? DARK : LIGHT;
  // Telefonda yalnızca genişlikten (klavye açılınca yükseklik oynar, ölçek zıplamasın); 400'den dar ekranda küçülür (en az 0.8).
  // Tablet ve masaüstünde (genişlik ≥ 600) sayfa dikeyde de sığsın diye yükseklikle de sınırlanır.
  let scale = width / BASE_W;
  if (width >= 600) scale = Math.min(scale, height / MIN_H);
  scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale));
  const s = (n: number) => Math.round(n * scale);
  const col = Math.min(MAX_COL * scale, width - s(40));     // sayfa sütunu: 20 px kenar, tablet/masaüstünde ortalanır
  return { c, s, dark, scale, width, height, col, kb };
}
export type Theme = ReturnType<typeof useTheme>;
export type { Token, Colors };
