// Ayarlar (+ hesap, birleşti 2026-10-10): kimlik başlığı, hesap bölümü, takma ad, ses, titreşim, nasıl oynanır, hareket, dil, sürüm; alt menü.
import React, { useState } from "react";
import { View } from "react-native";
import { LANGS } from "@/i18n";
import { hello } from "@/net/socket";
import { useGame, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { IdentityHeader, Input, Page, Segment, SettingRow, Toggle, Txt, t } from "@/ui";
import { AccountSection } from "@/ui/account";

export default function Settings() {
  const { s } = useTheme();
  const st = useSettings();
  const [nick, setNick] = useState(st.nickname);
  const commitNick = () => {
    const v = nick.trim().slice(0, 16);
    if (v && v !== st.nickname) { st.set({ nickname: v }); if (useGame.getState().connected) hello(); }
  };
  return (
    <Page scroll gap={0} nav="settings">
      <IdentityHeader />
      <View style={{ height: s(8) }} />
      <Txt role="pageTitle">{t("menu.settings")}</Txt>
      <View style={{ height: s(16) }} />
      <AccountSection />
      <View style={{ height: s(16) }} />
      <SettingRow title={t("set.nick")}>
        <Input value={nick} onChangeText={setNick} onBlur={commitNick} onSubmitEditing={commitNick} maxLength={16} accent={false}
          accessibilityLabel={t("set.nick")} style={{ width: s(170), minHeight: s(44), fontSize: s(16), paddingVertical: s(6) }} />
      </SettingRow>
      {/* ses düzeyi kaydırıcıları oyuna ses eklenince geri gelecek (docs/TODO.md) */}
      <SettingRow title={t("set.sound")}><Toggle value={st.sound} onChange={(v) => st.set({ sound: v })} /></SettingRow>
      <SettingRow title={t("set.haptics")}><Toggle value={st.haptics} onChange={(v) => st.set({ haptics: v })} /></SettingRow>
      {/* açınca mod başına "bir daha gösterme" seçimleri de sıfırlanır: hepsi topluca yeniden açılır */}
      <SettingRow title={t("set.learn")}><Toggle value={st.learn && st.learn_off.length === 0} onChange={(v) => st.set({ learn: v, learn_off: [] })} /></SettingRow>
      <SettingRow title={t("set.reduce_motion")}><Toggle value={st.reduce_motion} onChange={(v) => st.set({ reduce_motion: v })} /></SettingRow>
      <SettingRow title={t("set.lang")}>
        <Segment values={LANGS} labels={LANGS.map((l) => l.toUpperCase())} current={st.lang} onChange={(v) => st.set({ lang: v })} />
      </SettingRow>
      <View style={{ height: s(16) }} />
      <Txt role="caption" color="muted" center>3-2-1 Kickoff v0.2 beta</Txt>
    </Page>
  );
}
