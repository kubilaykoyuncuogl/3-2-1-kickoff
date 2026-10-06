// "Öğrenmeyi açık tut" (Ayarlar) açıkken bir moda girerken çıkan kısa açıklama kartı. Anladım ile kapanır; "Bir daha gösterme" ayarı kapatır.
import React, { useState } from "react";
import { View } from "react-native";
import { t } from "../i18n";
import { useSettings } from "../store";
import { useTheme } from "../theme";
import { Btn, Eyebrow, Txt } from "./index";

export function LearnCard({ id, title }: { id: string; title: string }) {
  const { c, s } = useTheme();
  const learn = useSettings((x) => x.learn);
  const [open, setOpen] = useState(true);
  if (!learn || !open) return null;
  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: c.bg + "E6", alignItems: "center", justifyContent: "center", padding: s(20) }}>
      <View style={{ width: "100%", maxWidth: s(360), backgroundColor: c.surface, borderRadius: s(18), borderWidth: 2, borderColor: c.violet_fill, padding: s(20), gap: s(10) }}>
        <Eyebrow color="violet_ink">{t("learn.header")}</Eyebrow>
        <Txt size={22} w={800}>{title}</Txt>
        <Txt size={15} w={500} style={{ lineHeight: s(22) }}>{t("learn." + id)}</Txt>
        <Btn text={t("learn.ok")} onPress={() => setOpen(false)} />
        <Btn text={t("learn.never")} kind="ghost" onPress={() => { useSettings.getState().set({ learn: false }); setOpen(false); }} />
      </View>
    </View>
  );
}
