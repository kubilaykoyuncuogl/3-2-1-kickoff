// Ana menü (kit: design/SELECTED-DIRECTION.md): Online oyna (ana eylem, sağında Elo), Tek oyna (ikincil, soluk mor), haftanın maçları, Ayarlar satırı.
// Takma ad yoksa önce takma ad ekranı.
import { useRouter } from "expo-router";
import React, { useEffect } from "react";
import { Pressable, View } from "react-native";
import { useProfile, useSettings } from "@/store";
import { SIZE, useTheme } from "@/theme";
import { Btn, Chevron, EntryRow, Gear, Page, Spacer, Txt, Wordmark, t } from "@/ui";
import { WeeklyButtons } from "@/ui/weekly";

export default function Menu() {
  const router = useRouter();
  const { c, s } = useTheme();
  const nickname = useSettings((x) => x.nickname);
  const elo = useProfile((p) => p.elo);
  const nick = nickname || t("guest");
  useEffect(() => { if (!nickname) router.push("/nickname"); }, [nickname]);
  return (
    <Page scroll>
      <View style={{ flexDirection: "row", alignItems: "center" }}>
        <View style={{ flex: 1 }}><Wordmark /></View>
        <View style={{ flexDirection: "row", alignItems: "center", gap: s(8) }}>
          <View style={{ width: s(36), height: s(36), borderRadius: 999, backgroundColor: c.violet_soft, alignItems: "center", justifyContent: "center" }}>
            <Txt role="label" color="violet_ink">{nick.slice(0, 1).toLocaleLowerCase("tr")}</Txt>
          </View>
          <Txt role="bodyStrong" lines={1} style={{ maxWidth: s(120) }}>{nick}</Txt>
        </View>
      </View>
      <Spacer h={8} flex={false} />
      {/* Online oyna: tek dokunma hedefi; Elo ve ok aynı eylemin parçası */}
      <Pressable onPress={() => router.push("/online")} accessibilityRole="button" accessibilityLabel={`${t("menu.online")}, ${t("menu.elo")} ${elo}`}
        style={({ pressed }) => ({ backgroundColor: pressed ? c.violet_pressed : c.violet_fill, borderRadius: s(16), minHeight: s(68), paddingHorizontal: s(18), flexDirection: "row", alignItems: "center", gap: s(14) })}>
        <Txt role="sectionTitle" color="violet_on" lines={1} style={{ flex: 1 }}>{t("menu.online")}</Txt>
        <View style={{ width: 1, alignSelf: "stretch", marginVertical: s(14), backgroundColor: c.violet_on, opacity: 0.35 }} />
        <View>
          <Txt role="caption" color="violet_on">{t("menu.elo")}</Txt>
          <Txt role="label" color="violet_on" style={{ fontVariant: ["tabular-nums"] }}>{String(elo)}</Txt>
        </View>
        <Chevron color="violet_on" />
      </Pressable>
      <Pressable onPress={() => router.push("/single")} accessibilityRole="button" accessibilityLabel={t("menu.single")}
        style={({ pressed }) => ({ backgroundColor: pressed ? c.violet_soft_pressed : c.violet_soft, borderRadius: s(16), minHeight: s(64), paddingHorizontal: s(18), flexDirection: "row", alignItems: "center", gap: s(14) })}>
        <Txt role="sectionTitle" color="violet_ink" lines={1} style={{ flex: 1 }}>{t("menu.single")}</Txt>
        <Chevron color="violet_ink" />
      </Pressable>
      <WeeklyButtons />
      <EntryRow title={t("menu.settings")} lead={<Gear color="fg" size={SIZE.icon} />} onPress={() => router.push("/settings")} />
      <Spacer />
      <Txt role="caption" color="muted" center>{t("menu.footer")}</Txt>
    </Page>
  );
}
