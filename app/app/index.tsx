// Ana menü: oyun seçenekleri ve etkin haftalık maçlar.
import { useRouter } from "expo-router";
import React, { useEffect } from "react";
import { Pressable, View } from "react-native";
import Svg, { Path } from "react-native-svg";
import { useProfile, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { Chevron, Page, Spacer, Txt, Wordmark, t } from "@/ui";
import { WeeklyButtons } from "@/ui/weekly";

export default function Menu() {
  const router = useRouter();
  const { c, s } = useTheme();
  const nickname = useSettings((x) => x.nickname);
  const elo = useProfile((p) => p.elo);
  useEffect(() => { if (!nickname) router.push("/nickname"); }, [nickname, router]);
  return (
    <Page scroll>
      <View style={{ flexDirection: "row", alignItems: "center", gap: s(20) }}>
        <View style={{ flex: 1 }}><Wordmark /></View>
        <Pressable accessibilityRole="button" accessibilityLabel={`${t("set.account")}, ${nickname || t("guest")}`} onPress={() => router.push("/account")}
          style={({ pressed }) => ({ flexDirection: "row", alignItems: "center", gap: s(8), maxWidth: "48%", minHeight: 48, opacity: pressed ? 0.7 : 1 })}>
          <View style={{ width: s(36), height: s(36), borderRadius: s(18), backgroundColor: c.violet_soft, justifyContent: "center", alignItems: "center" }}>
            <Txt size={15} w={700} color="violet_ink">{(nickname || t("guest")).slice(0, 1).toLocaleUpperCase("tr")}</Txt>
          </View>
          <Txt size={14} w={600} style={{ flexShrink: 1 }}>{nickname || t("guest")}</Txt>
        </Pressable>
      </View>
      <Spacer h={12} flex={false} />
      <Pressable accessibilityRole="button" accessibilityLabel={`${t("menu.online")}, ${t("menu.elo", elo)}`} onPress={() => router.push("/online")}
        style={({ pressed }) => ({ backgroundColor: c.violet_fill, opacity: pressed ? 0.8 : 1, borderRadius: s(16), minHeight: Math.max(56, s(72)), padding: s(18), flexDirection: "row", alignItems: "center", gap: s(14) })}>
        <Txt size={20} w={700} color="violet_on" style={{ flex: 1 }}>{t("menu.online")}</Txt>
        <View style={{ borderLeftWidth: 1, borderColor: c.violet_on, paddingLeft: s(14), maxWidth: "40%" }}>
          <Txt size={13} w={600} color="violet_on" style={{ fontVariant: ["tabular-nums"] }}>{t("menu.elo", elo)}</Txt>
        </View>
        <Chevron color="violet_on" />
      </Pressable>
      <Pressable accessibilityRole="button" onPress={() => router.push("/single")}
        style={({ pressed }) => ({ backgroundColor: c.violet_soft, opacity: pressed ? 0.75 : 1, borderRadius: s(16), minHeight: Math.max(56, s(64)), padding: s(18), flexDirection: "row", alignItems: "center", gap: s(14) })}>
        <Txt size={20} w={700} color="violet_ink" style={{ flex: 1 }}>{t("menu.single")}</Txt>
        <Chevron color="violet_ink" />
      </Pressable>
      <WeeklyButtons />
      <Pressable accessibilityRole="button" onPress={() => router.push("/settings")}
        style={({ pressed }) => ({ backgroundColor: c.surface, borderColor: pressed ? c.violet_fill : c.line, borderWidth: 1, borderRadius: s(14), minHeight: Math.max(48, s(56)), padding: s(16), flexDirection: "row", alignItems: "center", gap: s(12) })}>
        <Svg width={s(22)} height={s(22)} viewBox="0 0 24 24">
          <Path d="M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1 1-3ZM15.5 12a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" stroke={c.fg} strokeWidth={1.7} fill="none" strokeLinejoin="round" />
        </Svg>
        <Txt size={16} w={600} style={{ flex: 1 }}>{t("menu.settings")}</Txt>
        <Chevron />
      </Pressable>
      <Spacer />
      <Txt size={11} w={600} color="muted" center>{t("menu.footer")}</Txt>
    </Page>
  );
}

