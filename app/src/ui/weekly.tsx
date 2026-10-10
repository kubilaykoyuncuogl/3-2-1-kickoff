// Haftanın maçı parçaları: çapraz ikiye bölünmüş kulüp renkli düğme, taraf kartı, sayı biçimi.
import { useRouter } from "expo-router";
import React from "react";
import { Pressable, Text, View } from "react-native";
import { SvgXml } from "react-native-svg";
import { getLang, t } from "../i18n";
import { Weekly, useGame } from "../store";
import { FONT, useTheme } from "../theme";
import { Chevron } from "./index";
import { STADIUM, STADIUM_RATIO } from "./stadium";

export const num = (n: number) => Math.round(n).toLocaleString(getLang() === "tr" ? "tr-TR" : "en-US");

// Stadyum çizimi: sol tribün A, sağ tribün B kulübünün renklerinde (tools/weekly_art.py)
export const stadiumXml = (w: Weekly) => STADIUM.replace("__A0__", w.a.colors[0]).replace("__A1__", w.a.colors[1]).replace("__B0__", w.b.colors[0]).replace("__B1__", w.b.colors[1]);

// Ana menüdeki düğme: tribünleri kulüp renkli stadyum, isimler ve puanlar çimin üstünde. Haftalık veri yoksa çizilmez.
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
  const status = lead ? t("weekly.lead_short", lead) : t("weekly.tied");
  const action = w.me ? t("weekly.play_for", w[w.me.side].short) : t("weekly.pick");
  const info = t(w.format === "career" ? "weekly.menu_info_career" : "weekly.menu_info");
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={`${t("weekly.title")}. ${mode}. ${w.a.short}, ${t("weekly.points", num(w.a.total))}. ${w.b.short}, ${t("weekly.points", num(w.b.total))}. ${status}. ${action}.`}
      onPress={() => router.push({ pathname: "/weekly", params: { slug: w.slug } })}
      style={({ pressed }) => ({ borderRadius: s(16), overflow: "hidden", borderWidth: 1, borderColor: pressed ? c.violet_fill : c.line, backgroundColor: c.surface, opacity: pressed ? 0.85 : 1 })}>
      <View style={{ padding: s(16), gap: s(12) }}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", gap: s(12) }}>
          <Text style={{ flex: 1, fontFamily: FONT[600], fontSize: s(12), lineHeight: s(16), color: c.muted }}>{t("weekly.title")}</Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: s(5), maxWidth: "60%", minHeight: s(32), paddingVertical: s(6) }}>
            <Text style={{ flexShrink: 1, fontFamily: FONT[700], fontSize: s(12), lineHeight: s(17), color: c.violet_ink }}>{action}</Text>
            <Chevron color="violet_ink" size={14} />
          </View>
        </View>

      </View>
      <View style={{ aspectRatio: 1 / STADIUM_RATIO, justifyContent: "flex-end" }}>
        <SvgXml xml={stadiumXml(w)} width="100%" height="100%" style={{ position: "absolute" }} />
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end", paddingHorizontal: s(16), paddingBottom: s(12) }}>
          {(["a", "b"] as const).map((side) => (
            <View key={side} style={{ width: "46%", gap: s(2), alignItems: side === "b" ? "flex-end" : "flex-start" }}>
              <Text numberOfLines={1} style={{ fontFamily: FONT[600], fontSize: s(14), lineHeight: s(19), color: "#F2F2F5" }}>{w[side].short}</Text>
              <Text style={{ fontFamily: FONT[800], fontSize: s(20), lineHeight: s(26), color: "#FFFFFF", fontVariant: ["tabular-nums"] }}>{t("weekly.points", num(w[side].total))}</Text>
              <Text style={{ fontFamily: FONT[500], fontSize: s(11), lineHeight: s(15), color: "#DCEBDF" }}>{t("weekly.runs", w[side].runs)}</Text>
            </View>
          ))}
        </View>
      </View>
      <View style={{ padding: s(16), gap: s(14) }}>
        <View style={{ alignSelf: "flex-start", borderLeftWidth: s(4), borderColor: c.violet_fill, paddingLeft: s(10), paddingVertical: s(2) }}>
          <Text style={{ fontFamily: FONT[800], fontSize: s(21), lineHeight: s(28), color: c.violet_ink }}>{mode}</Text>
        </View>
        <View style={{ alignSelf: "flex-start", flexDirection: "row", alignItems: "center", gap: s(5), backgroundColor: c.bg, borderRadius: s(6), paddingHorizontal: s(8), paddingVertical: s(4) }}>
          {lead ? <Text style={{ fontFamily: FONT[800], fontSize: s(13), color: c.violet_ink }}>↗</Text> : null}
          <Text style={{ fontFamily: FONT[700], fontSize: s(12), lineHeight: s(17), color: c.fg }}>{status}</Text>
        </View>
        <Text style={{ fontFamily: FONT[500], fontSize: s(13), lineHeight: s(19), color: c.muted }}>{info}</Text>
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







