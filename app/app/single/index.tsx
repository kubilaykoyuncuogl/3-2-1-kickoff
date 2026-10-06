// Tek oyna: beş mod kartı. Kulüp kapsamı yalnızca kulüp çifti modlarında (Klasik, Beşte Bir); dönem seçimi hepsinde.
import { useRouter } from "expo-router";
import React, { useEffect } from "react";
import { View } from "react-native";
import { connect } from "@/net/socket";
import { useGame, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { Chevron, Chip, Nav, OptionCard, Page, Spacer, Txt, t } from "@/ui";

const MODES = ["ladder", "blitz", "career", "chain", "versus"];

export default function SingleMenu() {
  const router = useRouter();
  const { s } = useTheme();
  const best = useSettings((x) => x.best);
  useEffect(() => { if (!useGame.getState().connected) connect(); }, []);
  return (
    <Page scroll>
      <Nav title={t("menu.single")} />
      <Txt size={13} color="muted">{t("single.intro")}</Txt>
      {MODES.map((m) => (
        <OptionCard key={m} kind="amber" height={92} title={t("mode." + m)} sub={t(`mode.${m}_sub`)}
          tail={<View style={{ flexDirection: "row", alignItems: "center", gap: s(8) }}>
            {(best[m] ?? 0) > 0 ? <Chip text={`${t("single.best_short")} ${best[m]}`} kind="line" style={{ alignSelf: "center" }} /> : null}
            <Chevron color="amber_ink" />
          </View>}
          onPress={() => router.push({ pathname: m === "ladder" || m === "blitz" ? "/single/scope" : "/single/era", params: { mode: m } })} />
      ))}
      <Spacer />
    </Page>
  );
}
