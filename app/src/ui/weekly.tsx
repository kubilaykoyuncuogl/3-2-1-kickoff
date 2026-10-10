// Haftanın maçı parçaları: etkin maç seçimi, taraf kartı (oyun içi), sayı biçimi. Menü kartları app/app/weekly/index.tsx'te.
import React from "react";
import { Pressable, Text } from "react-native";
import { getLang, t } from "../i18n";
import { Weekly, useGame } from "../store";
import { FONT, useTheme } from "../theme";

export const num = (n: number) => Math.round(n).toLocaleString(getLang() === "tr" ? "tr-TR" : "en-US");

// Slug'ı verilen etkin maç; slug yoksa ilki (tek maçlı haftalar ve eski bağlantılar)
export function useWeekly(slug?: string): Weekly | null {
  const all = useGame((g) => g.weeklies);
  return all.find((x) => x.slug === slug) ?? all[0] ?? null;
}

// Taraf kartı: kulüp renginde; toplam puan ve koşu sayısı. selected: çerçeve vurgusu.
export function SideCard({ w, side, selected, dim, onPress }: { w: Weekly; side: "a" | "b"; selected?: boolean; dim?: boolean; onPress?: () => void }) {
  const { c, s } = useTheme();
  const d = w[side];
  const tx = (text: string, size: number, weight: 600 | 700 | 800 = 800) =>
    <Text numberOfLines={1} adjustsFontSizeToFit style={{ fontFamily: FONT[weight], fontSize: s(size), color: d.colors[1], textAlign: "center" }}>{text}</Text>;
  return (
    <Pressable disabled={!onPress} onPress={onPress} style={{ flex: 1, backgroundColor: d.colors[0], borderRadius: s(16), borderWidth: 3, borderColor: selected ? c.violet_fill : c.line,
      paddingVertical: s(16), paddingHorizontal: s(8), gap: s(4), opacity: dim ? 0.45 : 1 }}>
      {tx(d.short, 18)}
      {tx(num(d.total), 32)}
      {tx(t("weekly.runs", d.runs), 12, 600)}
    </Pressable>
  );
}







