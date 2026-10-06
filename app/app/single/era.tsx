// Tek oyna, son adım: dönem. Tümü ya da bir / birkaç on yıl; havuz o on yıllarda en az bir maça çıkmış oyunculardan kurulur.
import { useLocalSearchParams, useRouter } from "expo-router";
import React from "react";
import { useGame, useSettings } from "@/store";
import { connect } from "@/net/socket";
import { Btn, Nav, Page, Spacer, Txt, t } from "@/ui";
import { EraPicker, eraLabel } from "@/ui/pickers";

export default function SingleEra() {
  const router = useRouter();
  const { mode = "ladder" } = useLocalSearchParams<{ mode?: string }>();
  const era = useSettings((x) => x.era);
  const start = () => {
    if (!useGame.getState().connected) connect();
    const path = mode === "ladder" || mode === "blitz" ? "/single/play" : `/single/${mode}`;
    router.push({ pathname: path as any, params: { mode } });
  };
  return (
    <Page scroll>
      <Nav title={t("mode." + mode)} />
      <Txt size={22} w={800}>{t("era.title_q")}</Txt>
      <Txt size={13} color="muted">{t("era.sub")}</Txt>
      <EraPicker big />
      <Txt size={14} w={700} color="violet_ink" center>{eraLabel(era)}</Txt>
      <Btn text={t("era.start")} right=">" onPress={start} />
      <Spacer />
    </Page>
  );
}
