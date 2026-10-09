// Haftanın maçı: iki tarafın toplam puanı, taraf seçimi (hafta boyunca sabit) ve Oyna.
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import { Pressable, View } from "react-native";
import Svg, { Circle, Path } from "react-native-svg";
import { api, connect } from "@/net/socket";
import { useGame } from "@/store";
import { useTheme } from "@/theme";
import { Nav, Page, Spacer, Txt, t } from "@/ui";
import { LearnSteps } from "@/ui/learn";
import { SideCard, num, useWeekly } from "@/ui/weekly";

export default function WeeklyHome() {
  const router = useRouter();
  const { c, s } = useTheme();
  const { slug } = useLocalSearchParams<{ slug?: string }>();
  const w = useWeekly(slug);
  const connected = useGame((g) => g.connected);
  const [pick, setPick] = useState<"a" | "b" | null>(null);
  useEffect(() => { if (!useGame.getState().connected) connect(); else api.weeklyInfo(); }, [connected]);
  if (!w) return <Page><Nav title={t("weekly.title")} /><Txt size={14} w={600} color="muted">{connected ? t("weekly.none") : t("net.connecting")}</Txt></Page>;
  const locked = w.me?.side ?? null;
  const side = locked ?? pick;
  const disabled = !side || !connected;
  const diff = Math.abs(w.a.total - w.b.total);
  const lead = w.a.total === w.b.total ? t("weekly.tied") : t("weekly.lead", w.a.total > w.b.total ? w.a.short : w.b.short, num(diff));
  const sum = w.a.total + w.b.total;
  return (
    <>
      <Page scroll>
        <Nav title={t("weekly.title")} />
        <Txt size={24} w={800} center>{`${w.a.short} – ${w.b.short}`}</Txt>
        <Txt size={13} w={600} color="muted" center>{lead}</Txt>
        <View style={{ flexDirection: "row", gap: s(10) }}>
          <SideCard w={w} side="a" selected={side === "a"} dim={!!side && side !== "a"} onPress={locked ? undefined : () => setPick("a")} />
          <SideCard w={w} side="b" selected={side === "b"} dim={!!side && side !== "b"} onPress={locked ? undefined : () => setPick("b")} />
        </View>
        <View style={{ flexDirection: "row", height: s(10), borderRadius: 999, overflow: "hidden", backgroundColor: c.line, borderWidth: 1, borderColor: c.line }}>
          <View style={{ flex: sum ? w.a.total : 1, backgroundColor: w.a.colors[0] }} />
          <View style={{ flex: sum ? w.b.total : 1, backgroundColor: w.b.colors[0] }} />
        </View>
        <Txt size={13} color="muted" center>{w.format === "career" ? t("weekly.note_career", w.years?.[0] ?? 2000) : t("weekly.note")}</Txt>
        {locked ? <Txt size={14} w={700} color="violet_ink" center>{t("weekly.your", w[locked].short, num(w.me!.points))}</Txt> : !side ? <Txt size={14} w={700} color="violet_ink" center>{t("weekly.pick")}</Txt> : null}
        {side ? <View style={{ flexDirection: "row", alignItems: "center", gap: s(10), padding: s(14), backgroundColor: c.violet_soft, borderRadius: s(10), borderLeftWidth: s(3), borderLeftColor: c.violet_fill }}>
          <Svg width={s(20)} height={s(20)} viewBox="0 0 24 24">
            <Circle cx={12} cy={12} r={9} stroke={c.violet_ink} strokeWidth={1.8} fill="none" />
            <Path d="M12 7v6m0 3v1" stroke={c.violet_ink} strokeWidth={2} strokeLinecap="round" />
          </Svg>
          <Txt size={13} w={600} color="violet_ink" style={{ flex: 1 }}>{t("weekly.pick_note")}</Txt>
        </View> : null}
        <Pressable accessibilityRole="button" accessibilityState={{ disabled }} disabled={disabled}
          onPress={() => side && router.push({ pathname: "/weekly/play", params: { side, slug: w.slug } })}
          style={({ pressed }) => ({ backgroundColor: disabled ? c.line : w[side!].colors[0], borderRadius: s(14), minHeight: Math.max(56, s(56)), paddingHorizontal: s(18), paddingVertical: s(14), flexDirection: "row", alignItems: "center", gap: s(12), opacity: pressed ? 0.8 : 1 })}>
          <Txt size={17} w={700} color={disabled ? "muted" : "violet_on"} style={{ flex: 1, color: disabled ? c.muted : w[side!].colors[1] }}>{side ? t("weekly.play_for", w[side].short) : t("weekly.pick")}</Txt>
          {!disabled ? <Svg width={s(20)} height={s(20)} viewBox="0 0 24 24"><Path d="m9 5 7 7-7 7" stroke={w[side!].colors[1]} strokeWidth={2.2} fill="none" strokeLinecap="round" strokeLinejoin="round" /></Svg> : null}
        </Pressable>
        {!connected ? <View accessibilityLiveRegion="polite"><Txt size={12} color="muted" center>{t("net.connecting")}</Txt></View> : null}
        <Spacer />
      </Page>
      <LearnSteps id={w.format === "career" ? "weekly_career" : "weekly"} title={t("weekly.title")} />
    </>
  );
}


