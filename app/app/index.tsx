// Ana menü: dört madde (docs/screens.md 0a). Takma ad yoksa önce takma ad ekranı.
import { useRouter } from "expo-router";
import React, { useEffect } from "react";
import { View } from "react-native";
import { useProfile, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { Btn, Chip, Page, Spacer, Txt, Wordmark, t } from "@/ui";
import { WeeklyButtons } from "@/ui/weekly";

export default function Menu() {
  const router = useRouter();
  const { s } = useTheme();
  const nickname = useSettings((x) => x.nickname);
  const elo = useProfile((p) => p.elo);
  useEffect(() => { if (!nickname) router.push("/nickname"); }, [nickname]);
  return (
    <Page scroll>
      <View style={{ flexDirection: "row", alignItems: "flex-start" }}>
        <View style={{ flex: 1 }}><Wordmark /></View>
        <View style={{ gap: s(6), alignItems: "flex-end" }}>
          <Chip text="BETA" kind="amber" />
          <Chip text={nickname || t("guest")} kind="line" />
        </View>
      </View>
      <Spacer h={16} flex={false} />
      <Btn text={t("menu.online")} kind="violet" right={String(elo)} onPress={() => router.push("/online")} />
      <Btn text={t("menu.single")} kind="amber" right=">" onPress={() => router.push("/single")} />
      <WeeklyButtons />
      <Btn text={t("menu.settings")} kind="line" onPress={() => router.push("/settings")} />
      <Spacer />
      <Txt size={11} w={600} color="muted" center>{t("menu.footer")}</Txt>
    </Page>
  );
}
