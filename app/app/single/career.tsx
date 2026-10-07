// Kariyer yolu (tek oyunculu mod). Oynanış: src/career.tsx
import React from "react";
import { CareerPlay } from "@/career";
import { t } from "@/ui";

export default function Career() {
  return <CareerPlay mode="career" title={t("mode.career")} />;
}
