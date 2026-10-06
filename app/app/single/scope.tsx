// Tek oyna, 2. adım (Klasik ve Beşte Bir): kulüp kapsamı. Dokununca seçilir ve dönem adımına geçilir.
import { useLocalSearchParams, useRouter } from "expo-router";
import React from "react";
import { SCOPES, useSettings } from "@/store";
import { Nav, Page, Spacer, Txt, t } from "@/ui";
import { ScopeButton } from "@/ui/pickers";

export default function SingleScope() {
  const router = useRouter();
  const { mode = "ladder" } = useLocalSearchParams<{ mode?: string }>();
  const scope = useSettings((x) => x.scope);
  const best = useSettings((x) => x.best[mode] ?? 0);
  return (
    <Page>
      <Nav title={t("mode." + mode)} />
      <Txt size={22} w={800}>{t("scope.title_q")}</Txt>
      <Txt size={13} color="muted">{t("scope.best", best)}</Txt>
      {SCOPES.map((sc) => <ScopeButton key={sc} scope={sc} selected={scope === sc} onPress={(v) => { useSettings.getState().set({ scope: v }); router.push({ pathname: "/single/era", params: { mode } }); }} />)}
      <Spacer />
    </Page>
  );
}
