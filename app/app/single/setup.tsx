// Tek oyna, 2. adım: kulüp kapsamı ve dönem tek ekranda (Online sayfasındaki gibi), sonra Başla.
// Klasik ve Beşte Bir'de kapsam kulüpleri belirler; Kariyer yolu, Sıradaki kulüp ve O mu bu mu'da kariyeri o kapsama en az bir kez uğramış oyuncuları.
import { useLocalSearchParams, useRouter } from "expo-router";
import React from "react";
import { connect } from "@/net/socket";
import { useGame, useSettings } from "@/store";
import { Btn, Nav, Page, Spacer, Txt, t } from "@/ui";
import { LearnCard } from "@/ui/learn";
import { EraPicker, ScopePicker, eraLabel, scopeLabel } from "@/ui/pickers";

export default function SingleSetup() {
  const router = useRouter();
  const { mode = "ladder" } = useLocalSearchParams<{ mode?: string }>();
  const era = useSettings((x) => x.era);
  const scope = useSettings((x) => x.scope);
  const best = useSettings((x) => x.best[mode] ?? 0);
  const pairs = mode === "ladder" || mode === "blitz";
  const start = () => {
    if (!useGame.getState().connected) connect();
    router.push({ pathname: (pairs ? "/single/play" : `/single/${mode}`) as any, params: { mode } });
  };
  return (
    <>
    <Page scroll>
      <Nav title={t("mode." + mode)} />
      <ScopePicker />
      <EraPicker />
      {!pairs ? <Txt size={12} color="muted" center>{t("scope.path_note")}</Txt> : null}
      <Txt size={13} w={700} color="violet_ink" center>{scopeLabel(scope) + "  ·  " + eraLabel(era) + (best > 0 ? "  ·  " + t("scope.best", best) : "")}</Txt>
      <Btn text={t("era.start")} right=">" onPress={start} />
      <Spacer />
    </Page>
    <LearnCard id={mode} title={t("mode." + mode)} />
    </>
  );
}
