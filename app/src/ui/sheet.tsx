// Alt sayfa (kit C14 TeamChoiceSheet'in iskeleti): karartma + alttan açılan panel, üst köşeler 24, tutamaç, başlık + kapat düğmesi.
// Kapatmak (karartma, X, sistem geri) seçimi kaydetmez; onay yalnızca içerikteki düğmeyle verilir. Klavye açıksa önce kapatılır (çağıran taraf).
import React, { PropsWithChildren } from "react";
import { Modal, Pressable, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { RADII, useTheme } from "../theme";
import { Icon, Txt, t } from "./index";

export function Sheet({ open, title, sub, onClose, children }: PropsWithChildren<{ open: boolean; title: string; sub?: string; onClose: () => void }>) {
  const { c, s, col } = useTheme();
  const insets = useSafeAreaInsets();
  return (
    <Modal visible={open} transparent animationType="slide" onRequestClose={onClose} statusBarTranslucent>
      <View style={{ flex: 1, justifyContent: "flex-end" }}>
        <Pressable accessibilityRole="button" accessibilityLabel={t("close")} onPress={onClose} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: c.scrim }} />
        <View accessibilityViewIsModal style={{ backgroundColor: c.surface, borderTopLeftRadius: s(RADII.sheet), borderTopRightRadius: s(RADII.sheet), borderWidth: 1, borderBottomWidth: 0, borderColor: c.border_quiet,
          paddingHorizontal: s(20), paddingTop: s(10), paddingBottom: Math.max(insets.bottom, s(16)) + s(8), gap: s(12), alignSelf: "center", width: "100%", maxWidth: col + s(40) }}>
          <View style={{ alignSelf: "center", width: s(40), height: s(4), borderRadius: 999, backgroundColor: c.border_control, opacity: 0.6, marginBottom: s(6) }} />
          <View style={{ flexDirection: "row", alignItems: "flex-start", gap: s(12) }}>
            <View style={{ flex: 1, gap: s(2) }}>
              <Txt role="pageTitle" lines={2}>{title}</Txt>
              {sub ? <Txt role="body" color="muted">{sub}</Txt> : null}
            </View>
            <Pressable onPress={onClose} accessibilityRole="button" accessibilityLabel={t("close")} hitSlop={6}
              style={({ pressed }) => ({ width: s(48), height: s(48), borderRadius: 999, borderWidth: 1, borderColor: c.primary, backgroundColor: pressed ? c.raised : "transparent", alignItems: "center", justifyContent: "center" })}>
              <Icon name="x" color="primary" size={22} />
            </Pressable>
          </View>
          {children}
        </View>
      </View>
    </Modal>
  );
}

// Seçenek satırı (kit C13 ChoiceRow): yalnız bir seçim; seçili: aktif yeşil zemin + lime kenar + onay işareti
export function ChoiceRow({ title, selected, onPress, disabled }: { title: string; selected: boolean; onPress: () => void; disabled?: boolean }) {
  const { c, s } = useTheme();
  return (
    <Pressable onPress={onPress} disabled={disabled} accessibilityRole="radio" accessibilityState={{ selected, disabled: !!disabled }}
      style={({ pressed }) => ({ minHeight: s(56), borderRadius: s(RADII.action), borderWidth: 1, borderColor: selected ? c.primary : c.border_control, backgroundColor: selected ? c.active_surface : pressed ? c.raised : "transparent",
        paddingHorizontal: s(16), flexDirection: "row", alignItems: "center", gap: s(12), opacity: disabled ? 0.5 : 1 })}>
      <Txt role="team" color={selected ? "primary" : "text"} lines={1} style={{ flex: 1 }}>{title}</Txt>
      {selected ? <Icon name="check" color="primary" size={22} /> : null}
    </Pressable>
  );
}
