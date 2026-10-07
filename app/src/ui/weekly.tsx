// Haftanın maçı parçaları: çapraz ikiye bölünmüş kulüp renkli düğme, taraf kartı, sayı biçimi.
import { useRouter } from "expo-router";
import React from "react";
import { Pressable, View } from "react-native";
import Svg, { Polygon } from "react-native-svg";
import { getLang, t } from "../i18n";
import { Weekly, useGame } from "../store";
import { FONT, useTheme } from "../theme";
import { Text } from "react-native";
import { Chevron } from "./index";

export const num = (n: number) => Math.round(n).toLocaleString(getLang() === "tr" ? "tr-TR" : "en-US");

// Ana menüdeki düğme: sol üst yarı A kulübünün, sağ alt yarı B kulübünün rengi. Haftalık veri yoksa çizilmez.
export function WeeklyButton() {
  const router = useRouter();
  const { c, s } = useTheme();
  const w = useGame((g) => g.weekly);
  if (!w) return null;
  const lead = w.a.total === w.b.total ? "" : w.a.total > w.b.total ? w.a.short : w.b.short;
  const label = (text: string, color: string, size: number, weight: 600 | 700 | 800 = 800) =>
    <Text numberOfLines={1} style={{ fontFamily: FONT[weight], fontSize: s(size), color }}>{text}</Text>;
  // üst satır: solda "Haftanın maçı", ortada oyun modu (amber, büyük harf), sağda kim önde · orta: çapraz bölünmüş kulüp renklerinde adlar ve puanlar · alt: mod açıklaması
  return (
    <Pressable onPress={() => router.push("/weekly")} style={({ pressed }) => ({ borderRadius: s(14), overflow: "hidden", borderWidth: 2, borderColor: pressed ? c.line_strong : c.line, backgroundColor: c.surface })}>
      <View style={{ flexDirection: "row", alignItems: "center", paddingHorizontal: s(14), paddingVertical: s(8), gap: s(6) }}>
        <Text numberOfLines={2} style={{ flex: 1, fontFamily: FONT[700], fontSize: s(9.5), lineHeight: s(12), color: c.muted }}>{t("weekly.title").toLocaleUpperCase("tr")}</Text>
        <Text numberOfLines={1} style={{ fontFamily: FONT[800], fontSize: s(14), color: c.amber_ink }}>{t(w.format === "career" ? "mode.career" : "weekly.mode_name").toLocaleUpperCase("tr")}</Text>
        <Text numberOfLines={2} style={{ flex: 1, textAlign: "right", fontFamily: FONT[700], fontSize: s(9.5), lineHeight: s(12), color: c.muted }}>{(lead ? t("weekly.lead_short", lead) : t("weekly.tied")).toLocaleUpperCase("tr")}</Text>
      </View>
      <View style={{ height: s(66) }}>
        <Svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute" }}>
          <Polygon points="0,0 58,0 42,100 0,100" fill={w.a.colors[0]} />
          <Polygon points="58,0 100,0 100,100 42,100" fill={w.b.colors[0]} />
        </Svg>
        <View style={{ flex: 1, flexDirection: "row", paddingHorizontal: s(14), paddingVertical: s(9) }}>
          <View style={{ flex: 1, justifyContent: "space-between" }}>
            {label(w.a.short, w.a.colors[1], 20)}
            {label(t("weekly.points", num(w.a.total)), w.a.colors[1], 13, 700)}
          </View>
          <View style={{ flex: 1, justifyContent: "space-between", alignItems: "flex-end" }}>
            {label(w.b.short, w.b.colors[1], 20)}
            {label(t("weekly.points", num(w.b.total)), w.b.colors[1], 13, 700)}
          </View>
        </View>
      </View>
      <View style={{ paddingHorizontal: s(14), paddingVertical: s(8), flexDirection: "row", alignItems: "center", gap: s(8) }}>
        <Text numberOfLines={2} style={{ flex: 1, fontFamily: FONT[600], fontSize: s(12), lineHeight: s(16), color: c.muted }}>{w.format === "career" ? t("weekly.menu_info_career") : t("weekly.menu_info")}</Text>
        <Chevron color="muted" />
      </View>
    </Pressable>
  );
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
