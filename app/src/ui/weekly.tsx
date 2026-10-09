// Haftanın maçı parçaları: çapraz ikiye bölünmüş kulüp renkli düğme, taraf kartı, sayı biçimi.
import { useRouter } from "expo-router";
import React from "react";
import { Pressable, View } from "react-native";
import Svg, { Polygon } from "react-native-svg";
import { getLang, t } from "../i18n";
import { Weekly, useGame } from "../store";
import { FONT, useTheme } from "../theme";
import { Text } from "react-native";
import { Chevron, Txt } from "./index";

export const num = (n: number) => Math.round(n).toLocaleString(getLang() === "tr" ? "tr-TR" : "en-US");

// Ana menüdeki düğme: sol üst yarı A kulübünün, sağ alt yarı B kulübünün rengi. Haftalık veri yoksa çizilmez.
// Slug'ı verilen etkin maç; slug yoksa ilki (tek maçlı haftalar ve eski bağlantılar)
export function useWeekly(slug?: string): Weekly | null {
  const all = useGame((g) => g.weeklies);
  return all.find((x) => x.slug === slug) ?? all[0] ?? null;
}

// Ana menü: etkin her maç için bir düğme (aynı anda birden çok maç olabilir)
export function WeeklyButtons() {
  const all = useGame((g) => g.weeklies);
  return <>{all.map((w) => <WeeklyButton key={w.slug} w={w} />)}</>;
}

export function WeeklyButton({ w }: { w: Weekly }) {
  const router = useRouter();
  const { c, s } = useTheme();
  const lead = w.a.total === w.b.total ? "" : w.a.total > w.b.total ? w.a.short : w.b.short;
  const mode = t(w.format === "career" ? "mode.career" : "weekly.mode_name");
  const label = (text: string, color: string, role: "sectionTitle" | "caption") =>
    <Txt role={role} lines={1} style={{ color }}>{text}</Txt>;
  // kit: üstte bölüm adı + mod (+ kim önde), ortada çapraz bölünmüş kulüp renklerinde adlar ve puanlar, altta açıklama + eylem. Kart tek dokunma hedefidir.
  // Kulüp arması yok (lisanslı varlık yok); renk ve ad yeter.
  return (
    <Pressable onPress={() => router.push({ pathname: "/weekly", params: { slug: w.slug } })} accessibilityRole="button"
      accessibilityLabel={`${t("weekly.title")}, ${mode}. ${w.a.short} ${t("weekly.points", num(w.a.total))}, ${w.b.short} ${t("weekly.points", num(w.b.total))}. ${t("weekly.pick")}`}
      style={({ pressed }) => ({ borderRadius: s(16), overflow: "hidden", borderWidth: 1, borderColor: pressed ? c.control : c.line, backgroundColor: c.surface })}>
      <View style={{ flexDirection: "row", alignItems: "center", paddingHorizontal: s(16), paddingVertical: s(10), gap: s(10) }}>
        <Txt role="caption" color="muted" lines={1} style={{ flexShrink: 0 }}>{t("weekly.title")}</Txt>
        <Txt role="bodyStrong" color="amber_ink" lines={1} style={{ flexShrink: 0 }}>{mode}</Txt>
        <Txt role="caption" color="muted" lines={1} style={{ flex: 1, textAlign: "right" }}>{lead ? t("weekly.lead_short", lead) : t("weekly.tied")}</Txt>
      </View>
      <View style={{ height: s(72) }}>
        <Svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute" }}>
          <Polygon points="0,0 58,0 42,100 0,100" fill={w.a.colors[0]} />
          <Polygon points="58,0 100,0 100,100 42,100" fill={w.b.colors[0]} />
        </Svg>
        <View style={{ flex: 1, flexDirection: "row", paddingHorizontal: s(16), paddingVertical: s(10) }}>
          <View style={{ flex: 1, justifyContent: "space-between" }}>
            {label(w.a.short, w.a.colors[1], "sectionTitle")}
            {label(t("weekly.points", num(w.a.total)), w.a.colors[1], "caption")}
          </View>
          <View style={{ flex: 1, justifyContent: "space-between", alignItems: "flex-end" }}>
            {label(w.b.short, w.b.colors[1], "sectionTitle")}
            {label(t("weekly.points", num(w.b.total)), w.b.colors[1], "caption")}
          </View>
        </View>
      </View>
      <View style={{ paddingHorizontal: s(16), paddingVertical: s(10), flexDirection: "row", alignItems: "center", gap: s(10) }}>
        <Txt role="caption" color="muted" lines={2} style={{ flex: 1 }}>{w.format === "career" ? t("weekly.menu_info_career") : t("weekly.menu_info")}</Txt>
        <Txt role="caption" color="violet_ink" lines={1} style={{ fontFamily: FONT[600] }}>{w.me ? t("weekly.go") : t("weekly.pick")}</Txt>
        <Chevron color="violet_ink" />
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
