// İlk açılış: takma ad (tek alan + Devam). Her şey üstte: klavye açılınca kutu ve Devam görünür kalsın.
import { useRouter } from "expo-router";
import React, { useState } from "react";
import { KeyboardAvoidingView, Platform } from "react-native";
import { hello } from "@/net/socket";
import { useGame, useSettings } from "@/store";
import { Btn, Input, Page, Txt, Wordmark, t } from "@/ui";

export default function Nickname() {
  const router = useRouter();
  const current = useSettings((x) => x.nickname);
  const [v, setV] = useState(current);
  const ok = v.trim().length >= 2;
  const submit = () => {
    if (!ok) return;
    useSettings.getState().set({ nickname: v.trim().slice(0, 16) });
    if (useGame.getState().connected) hello();
    router.canGoBack() ? router.back() : router.replace("/");
  };
  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <Page>
        <Wordmark />
        <Txt size={22} w={800}>{t("nick.title")}</Txt>
        <Txt size={13} color="muted">{t("nick.sub")}</Txt>
        <Input value={v} onChangeText={setV} placeholder={t("nick.placeholder")} maxLength={16} autoFocus onSubmitEditing={submit} returnKeyType="done" style={{ fontFamily: "Sora_700Bold" }} />
        <Btn text={t("continue")} disabled={!ok} onPress={submit} />
        <Txt size={12} color="muted">{t("nick.hint")}</Txt>
      </Page>
    </KeyboardAvoidingView>
  );
}
