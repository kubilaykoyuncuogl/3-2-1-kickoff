// Ayarlar: hesap, takma ad, ses, titreşim, tema, hareket, dil, nasıl oynanır; tek ekran, kaydırmasız.
import { useRouter } from "expo-router";
import React, { useState } from "react";
import { View } from "react-native";
import { LANGS } from "@/i18n";
import { hello } from "@/net/socket";
import { ThemeMode, useGame, useProfile, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { Btn, Chevron, Input, Nav, OptionCard, Page, Segment, SettingRow, Spacer, Toggle, Txt, t } from "@/ui";

export default function Settings() {
  const router = useRouter();
  const { s } = useTheme();
  const st = useSettings();
  const prof = useProfile();
  const [nick, setNick] = useState(st.nickname);
  const commitNick = () => {
    const v = nick.trim().slice(0, 16);
    if (v && v !== st.nickname) { st.set({ nickname: v }); if (useGame.getState().connected) hello(); }
  };
  return (
    <Page gap={0}>
      <Nav title={t("menu.settings")} />
      <View style={{ height: s(12) }} />
      <OptionCard
        title={prof.linked ? st.nickname : t("acct.guest_title")}
        sub={prof.linked ? (prof.verified ? t("verified") : t("acct.linked_chip")) : t("acct.create")}
        tail={<Chevron color={prof.linked ? "violet_ink" : "muted"} />} selected={prof.linked} height={60}
        onPress={() => router.push("/account")}
      />
      <SettingRow title={t("set.nick")}>
        <Input value={nick} onChangeText={setNick} onBlur={commitNick} onSubmitEditing={commitNick} maxLength={16} accent={false}
          style={{ width: s(160), minHeight: s(40), fontSize: s(14), paddingVertical: s(6) }} />
      </SettingRow>
      {/* ses düzeyi kaydırıcıları oyuna ses eklenince geri gelecek (docs/TODO.md) */}
      <SettingRow title={t("set.sound")}><Toggle value={st.sound} onChange={(v) => st.set({ sound: v })} /></SettingRow>
      <SettingRow title={t("set.haptics")}><Toggle value={st.haptics} onChange={(v) => st.set({ haptics: v })} /></SettingRow>
      <SettingRow title={t("set.theme")}>
        <Segment<ThemeMode> values={["system", "light", "dark"]} labels={[t("theme.system"), t("theme.light"), t("theme.dark")]} current={st.theme_mode} onChange={(v) => st.set({ theme_mode: v })} />
      </SettingRow>
      <SettingRow title={t("set.reduce_motion")}><Toggle value={st.reduce_motion} onChange={(v) => st.set({ reduce_motion: v })} /></SettingRow>
      <SettingRow title={t("set.lang")}>
        <Segment values={LANGS} labels={LANGS.map((l) => l.toUpperCase())} current={st.lang} onChange={(v) => st.set({ lang: v })} />
      </SettingRow>
      <View style={{ height: s(12) }} />
      <Btn text={t("menu.howto")} kind="line" onPress={() => router.push("/howto")} />
      <View style={{ height: s(10) }} />
      <Txt size={11} color="muted" center>3-2-1 Kickoff v0.2 beta</Txt>
      <Spacer />
    </Page>
  );
}
