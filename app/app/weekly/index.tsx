// Haftanın maçı: iki tarafın toplam puanı, taraf seçimi (hafta boyunca sabit) ve Oyna.
import { useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import { View } from "react-native";
import { api, connect } from "@/net/socket";
import { useGame } from "@/store";
import { useTheme } from "@/theme";
import { Btn, Nav, Page, Spacer, Txt, t } from "@/ui";
import { LearnSteps } from "@/ui/learn";
import { SideCard, num } from "@/ui/weekly";

export default function WeeklyHome() {
  const router = useRouter();
  const { c, s } = useTheme();
  const w = useGame((g) => g.weekly);
  const connected = useGame((g) => g.connected);
  const [pick, setPick] = useState<"a" | "b" | null>(null);
  useEffect(() => { if (!useGame.getState().connected) connect(); else api.weeklyInfo(); }, [connected]);
  if (!w) return <Page><Nav title={t("weekly.title")} /><Txt size={14} w={600} color="muted">{connected ? t("weekly.none") : t("net.connecting")}</Txt></Page>;
  const locked = w.me?.side ?? null;
  const side = locked ?? pick;
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
        <Txt size={14} w={700} color="violet_ink" center>{locked ? t("weekly.your", w[locked].short, num(w.me!.points)) : side ? t("weekly.pick_note") : t("weekly.pick")}</Txt>
        <Btn text={side ? t("weekly.play_for", w[side].short) : t("weekly.pick")} right=">" disabled={!side || !connected}
          onPress={() => side && router.push({ pathname: "/weekly/play", params: { side } })} />
        <Spacer />
      </Page>
      <LearnSteps id={w.format === "career" ? "weekly_career" : "weekly"} title={t("weekly.title")} />
    </>
  );
}
