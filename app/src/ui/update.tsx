// Sunucu farklı bir sözleşme sürümüyle konuşuyor: tüm ekranı kapatan "yeni sürüm" kartı.
// Expo Updates açıkken önce güncelleme çekilir; web'de sayfa yenilenir; aksi halde mağazaya yönlendirir.
import * as Updates from "expo-updates";
import React, { useEffect, useState } from "react";
import { Platform, View } from "react-native";
import { useGame } from "../store";
import { useTheme } from "../theme";
import { Btn, Txt, t } from "./index";

export function UpdateCard() {
  const needed = useGame((g) => g.updateNeeded);
  const { c, s } = useTheme();
  const [busy, setBusy] = useState(false);
  const web = Platform.OS === "web";
  useEffect(() => {
    if (!needed || web || !Updates.isEnabled) return;
    setBusy(true);
    Updates.fetchUpdateAsync().then((r) => { if (r.isNew) Updates.reloadAsync(); }).catch(() => {}).finally(() => setBusy(false));
  }, [needed]);
  if (!needed) return null;
  return (
    <View style={{ position: "absolute", inset: 0, backgroundColor: c.bg + "F0", alignItems: "center", justifyContent: "center", padding: s(20) }}>
      <View style={{ width: s(310), backgroundColor: c.surface, borderRadius: s(18), borderWidth: 2, borderColor: c.violet_fill, padding: s(22), gap: s(12) }}>
        <Txt size={22} w={800} center>{t("update.title")}</Txt>
        <Txt size={14} color="muted" center>{busy ? t("loading") : web ? t("update.web") : t("update.app")}</Txt>
        {web ? <Btn text={t("update.reload")} onPress={() => { if (typeof location !== "undefined") location.reload(); }} /> : null}
      </View>
    </View>
  );
}
