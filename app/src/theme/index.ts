// Tema kancası: renkler (tek tema, Forest Lime) + ölçek (400 px tasarım genişliği; 0.8–1.5).
import { useWindowDimensions } from "react-native";
import { DARK, Colors, Token } from "./palette";
import { useKeyboard } from "../keyboard";

export const BASE_W = 400;
export const MAX_SCALE = 1.5;
export const MIN_SCALE = 0.8;
export const MIN_H = 720;            // geniş ekranda bir sayfanın sığması gereken tasarım yüksekliği
export const MAX_COL = 520;

// İki yazı ailesi (design/forest-lime/docs/01-design-system.md): Barlow Condensed = eylem, başlık, takım, puan; Inter = gövde, etiket, menü.
// Barlow Condensed yalnızca Latin: Kiril / Yunan dillerinde (ru, uk, el) başlıklar Inter'e düşer (displayFamily). CJK gelirse aynı yuvaya bölgesel Noto Sans CJK girer
// (Tolga'nın eşlemesi 2026-10-10: CJK gövde Regular–Medium, başlık Bold–Black; JP / KR / SC / TC sürümü dile göre).
export const FONT = { 400: "Inter_400Regular", 500: "Inter_500Medium", 600: "Inter_600SemiBold", 700: "Inter_700Bold", 800: "Inter_800ExtraBold" } as const;
export const BARLOW = { 400: "BarlowCondensed_500Medium", 500: "BarlowCondensed_500Medium", 600: "BarlowCondensed_600SemiBold", 700: "BarlowCondensed_700Bold", 800: "BarlowCondensed_800ExtraBold" } as const;
export type Weight = keyof typeof FONT;
const LATIN_ONLY_DISPLAY = new Set(["ru", "uk", "el"]);      // bu dillerde başlık ailesi = gövde ailesi
export const displayFamily = (lang: string) => (LATIN_ONLY_DISPLAY.has(lang) ? FONT : BARLOW);
export const DISPLAY = BARLOW;

// Yazı rolleri: [boyut, satır yüksekliği, ağırlık, aile]. Değerler 400 genişlikteki tasarım ölçüsüdür; ekranda useTheme().s ile orantılı ölçeklenir
// (ekip kararı 2026-10-09, 2026-10-10'da yinelendi: orantılı ölçek kalır, sayfa kaymaz; kaydırma gereken yerde eleman içinde).
export const TYPE = {
  // kit rolleri
  action: [32, 36, 800, "display"], pageTitle: [30, 34, 700, "display"], cardTitle: [28, 32, 700, "display"], team: [20, 24, 700, "display"], points: [34, 38, 700, "display"],
  body: [16, 24, 400, "text"], bodyStrong: [16, 24, 600, "text"], label: [16, 22, 600, "text"], fieldLabel: [14, 20, 600, "text"], caption: [14, 20, 500, "text"], nav: [12, 16, 600, "text"],
  // önceki kitten kalan roller, aynı ailelere eşlendi
  display: [40, 48, 800, "display"], countdown: [64, 72, 800, "display"], screenTitle: [30, 34, 700, "display"], navTitle: [22, 28, 600, "display"], sectionTitle: [22, 28, 700, "display"],
  score: [34, 38, 700, "display"], scoreCompact: [22, 28, 700, "display"], timer: [26, 32, 700, "display"], input: [18, 26, 400, "text"],
} as const satisfies Record<string, readonly [number, number, Weight, "display" | "text"]>;
export type TypeRole = keyof typeof TYPE;
export const family = (w: Weight, kind: "display" | "text" = "text", lang = "tr") => (kind === "display" ? displayFamily(lang) : FONT)[w];
// Ölçüler: en az dokunma alanı, düğme, yazı kutusu / öneri / ayar satırı, ikon, alt menü
export const SIZE = { touch: 48, button: 52, input: 56, row: 56, icon: 24, nav: 72, navItem: 56 } as const;
export const RADII = { action: 10, card: 12, sheet: 24 } as const;

export function useTheme() {
  const { width, height } = useWindowDimensions();
  const kb = useKeyboard((k) => k.open);      // klavye açık: ekranlar sıkı düzene geçer (başlık, geçmiş listesi gibi ikincil parçalar gizlenir)
  const c: Colors = DARK;
  const dark = true;
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
