// Nasıl oynanır: online maç (5 adım) + her tek oyunculu mod için birer adım; ipucu balonu + örnek kart.
import { useRouter } from "expo-router";
import React, { useState } from "react";
import { View } from "react-native";
import { useTheme } from "@/theme";
import { Btn, Eyebrow, Nav, Page, Panel, Txt, t } from "@/ui";

// [grup, başlık, metin, üst etiket, üst yazı, alt etiket, alt yazı]; etiket ve yazılar dil anahtarıysa çevrilir, değilse aynen yazılır
const STEPS: [string, string, string, string, string, string, string][] = [
  ["menu.online", "howto.1.title", "howto.1.body", "you", "Galatasaray", "coach", "Inter Milan"],
  ["menu.online", "howto.2.title", "howto.2.body", "you", "Galatasaray", "coach", "Inter Milan"],
  ["menu.online", "howto.3.title", "howto.3.body", "you", "Snei", "coach", "Wesley Sneijder"],
  ["menu.online", "howto.4.title", "howto.4.body", "you", "howto.4.a", "coach", "howto.4.b"],
  ["menu.online", "howto.5.title", "howto.5.body", "you", "3 : 1", "coach", "won"],
  ["menu.single", "mode.ladder", "howto.ladder", "howto.ex.clubs", "Real Madrid × Juventus", "howto.ex.answer", "Zinédine Zidane"],
  ["menu.single", "mode.blitz", "howto.blitz", "howto.ex.clubs", "Chelsea × AC Milan", "howto.ex.one_of_five", "Andriy Shevchenko"],
  ["menu.single", "mode.career", "howto.career", "howto.ex.path", "Sporting → Man United → Real Madrid", "howto.ex.answer", "Cristiano Ronaldo"],
  ["menu.single", "mode.chain", "howto.chain", "howto.ex.player", "Wesley Sneijder", "howto.ex.next_club", "Ajax → Real Madrid → ?"],
  ["menu.single", "mode.versus", "howto.versus", "howto.ex.more_goals", "Hakan Şükür", "howto.ex.or", "Burak Yılmaz"],
];

export default function HowTo() {
  const router = useRouter();
  const { c, s } = useTheme();
  const [i, setI] = useState(0);
  const st = STEPS[i]; const last = i === STEPS.length - 1;
  return (
    <Page scroll>
      <Nav title={t("menu.howto")} />
      <View style={{ backgroundColor: c.fg, borderRadius: s(12), padding: s(14) }}>
        <Txt size={14} w={600} color="bg">{t(st[2])}</Txt>
      </View>
      <Txt size={13} w={700} color="muted">{`${t(st[0]).toLocaleUpperCase("tr")}  ·  ${i + 1} / ${STEPS.length}  ·  ${t(st[1])}`}</Txt>
      <Panel kind="violet" style={{ flex: 1 }}>
        <Eyebrow color="violet_ink">{t(st[3])}</Eyebrow>
        <Txt size={22} w={800} color="violet_ink">{t(st[4])}</Txt>
      </Panel>
      {i === 1 ? <Txt size={72} w={800} center style={{ fontStyle: "italic", lineHeight: s(80) }}>3</Txt> : null}
      <Panel kind="amber" style={{ flex: 1 }}>
        <Eyebrow color="amber_ink">{t(st[5])}</Eyebrow>
        <Txt size={22} w={800} color="amber_ink">{t(st[6])}</Txt>
      </Panel>
      <View style={{ flexDirection: "row", gap: s(8) }}>
        <Btn text={t("back")} kind="line" disabled={i === 0} onPress={() => setI(i - 1)} style={{ flex: 1 }} />
        <Btn text={last ? t("menu.single") : t("next")} onPress={() => (last ? router.replace("/single") : setI(i + 1))} style={{ flex: 1 }} />
      </View>
    </Page>
  );
}
