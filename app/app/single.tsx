// Tek oyna (Faz 4'te yazılacak). Şimdilik yer tutucu.
import React from "react";
import { Nav, Page, Txt, t } from "@/ui";

export default function Single() {
  return (
    <Page>
      <Nav title={t("menu.single")} />
      <Txt color="muted">{t("loading")}</Txt>
    </Page>
  );
}
