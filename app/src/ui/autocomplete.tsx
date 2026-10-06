// Yazı kutusu + öneri listesi. Öneriler sunucudan (store.suggestions) gelir; öneriye dokunmak = seçmek.
import React, { ReactNode, useEffect, useRef, useState } from "react";
import { Pressable, ScrollView, TextInput, View } from "react-native";
import { t } from "../i18n";
import { api } from "../net/socket";
import { Suggestion, useGame } from "../store";
import { useTheme } from "../theme";
import { BORDER, DefunctIcon, Input, Txt } from "./index";

// `fill`: kalan yeri doldurur, öneriler sığmazsa kendi içinde kayar (dar alanda taşıp alttaki parçaların üstüne binmez)
// `max`: en çok kaç öneri; `below`: öneri yokken kutunun altında gösterilecek parça (klavye açıkken sonuç bildirimi)
export function Autocomplete({ kind, locked, lockedText, onPick, autoFocus = true, clearKey, fill, max = 6, below }: {
  kind: "team" | "player"; locked?: boolean; lockedText?: string; onPick: (id: number, name: string) => void; autoFocus?: boolean; clearKey?: unknown;
  fill?: boolean; max?: number; below?: ReactNode;
}) {
  const { c, s, kb } = useTheme();
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Suggestion[]>([]);
  const lastQ = useRef("");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const input = useRef<TextInput>(null);
  const sugg = useGame((g) => g.suggestions);

  useEffect(() => { setQ(""); setItems([]); lastQ.current = ""; }, [clearKey]);
  useEffect(() => {
    if (!sugg || sugg.kind !== kind || sugg.q !== lastQ.current) return;   // başka kutunun ya da eski sorgunun cevabı
    setItems(sugg.list.slice(0, 6));
  }, [sugg]);
  useEffect(() => { if (!locked && autoFocus) setTimeout(() => input.current?.focus(), 50); }, [locked]);

  const onText = (text: string) => {
    setQ(text);
    const v = text.trim();
    if (v.length < 2) { setItems([]); lastQ.current = ""; return; }
    lastQ.current = v;
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => { if (!locked && lastQ.current === v) api.suggest(kind, v); }, 120);   // yazma bitince tek istek
  };

  const shown = locked ? [] : items.slice(0, max);
  const rows = shown.map((it) => {
        const used = !!it.used || it.in_scope === false;
        const label = it.name + (kind === "player" && it.born ? `  ·  ${it.born}` : "") + (used ? (it.used ? t("ac.used") : t("ac.out_of_scope")) : "");
        return (
          <Pressable key={it.id} disabled={used} onPress={() => onPick(it.id, it.name)} style={({ pressed }) => ({
            backgroundColor: pressed ? c.violet_soft : used ? "transparent" : c.surface, borderRadius: s(12), borderWidth: BORDER, borderColor: pressed ? c.violet_fill : c.line,
            minHeight: s(kb ? 44 : 48), paddingHorizontal: s(14), flexDirection: "row", alignItems: "center", gap: s(8),
          })}>
            <Txt size={16} w={600} color={used ? "muted" : "fg"} lines={1} style={{ flex: 1 }}>{label}</Txt>
            {it.defunct ? <DefunctIcon /> : null}
          </Pressable>
        );
  });
  return (
    <View style={[{ gap: s(6) }, fill ? { flex: 1, minHeight: 0 } : null]}>
      <Input ref={input} value={locked ? "" : q} onChangeText={onText} editable={!locked} autoFocus={autoFocus}
        placeholder={locked ? lockedText : t(kind === "player" ? "ph.player" : "ph.team")} accent={!locked}
        style={locked ? { backgroundColor: c.no_soft, borderColor: c.no, fontSize: s(20) } : { fontSize: s(20) }} />
      {shown.length === 0 ? below : fill
        ? <ScrollView style={{ flex: 1 }} contentContainerStyle={{ gap: s(6) }} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>{rows}</ScrollView>
        : rows}
    </View>
  );
}
