// Online oyna (Faz 3'te yazılacak). Şimdilik yer tutucu.
import React from "react";
import { Nav, Page, Txt, t } from "@/ui";

export default function Online() {
  return (
    <Page>
      <Nav title={t("menu.online")} />
      <Txt color="muted">{t("loading")}</Txt>
    </Page>
  );
}
