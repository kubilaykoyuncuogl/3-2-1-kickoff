// Yazı kutusu + öneri listesi. Öneriler sunucudan (store.suggestions) gelir; öneriye dokunmak = seçmek.
import React, { ReactNode, useEffect, useRef, useState } from "react";
import { Pressable, ScrollView, TextInput, View } from "react-native";
import { has, t } from "../i18n";
import { api } from "../net/socket";
import { Suggestion, useGame } from "../store";
import { useTheme } from "../theme";
import { BORDER, DefunctIcon, Input, Txt } from "./index";

// `fill`: kalan yeri doldurur, öneriler sığmazsa kendi içinde kayar (dar alanda taşıp alttaki parçaların üstüne binmez)
// `out`: elenen adlar (öneride soluk ve dokunulmaz çıkar). `max`: en çok kaç öneri; `below`: öneri yokken kutunun altında gösterilecek parça (klavye açıkken sonuç bildirimi)
// Ülke adı: dil paketinde karşılığı varsa o, yoksa kaynak ad (single.tsx'teki country ile aynı; oradan alınırsa döngüsel içe aktarma olur)
const country = (name: string) => (has("country." + name) ? t("country." + name) : name);

export function Autocomplete({ kind, locked, lockedText, onPick, autoFocus = true, clearKey, fill, max = 6, below, out, label }: {
  kind: "team" | "player"; locked?: boolean; lockedText?: string; onPick: (id: number, name: string) => void; autoFocus?: boolean; clearKey?: unknown;
  fill?: boolean; max?: number; below?: ReactNode; out?: string[]; label?: boolean;
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
        const gone = !!out?.includes(it.name);      // elenen isim: daha önce yanlış denendi
        const used = !!it.used || it.in_scope === false || gone;
        // kit: ad solda (bodyStrong), ikincil bilgi sağda (caption): doğum yılı · milliyet, ya da neden seçilemediği
        const note = gone ? t("ac.out").replace(/^[\s·]+/, "") : used ? (it.used ? t("ac.used") : t("ac.out_of_scope")).replace(/^[\s·]+/, "") : "";
        const meta = note || (kind === "player" ? [it.born, it.nat ? country(it.nat) : ""].filter(Boolean).join(" · ") : "");
        return (
          <Pressable key={it.id} disabled={used} onPress={() => onPick(it.id, it.name)} accessibilityRole="button" accessibilityLabel={[it.name, meta].filter(Boolean).join(", ")} accessibilityState={{ disabled: used }}
            style={({ pressed }) => ({
              backgroundColor: pressed ? c.violet_soft : used ? "transparent" : c.surface, borderRadius: s(12), borderWidth: BORDER, borderColor: pressed ? c.violet_fill : c.control,
              minHeight: s(kb ? 50 : 56), paddingHorizontal: s(16), flexDirection: "row", alignItems: "center", gap: s(10),
            })}>
            <Txt role="bodyStrong" color={used ? "muted" : "fg"} lines={1} style={{ flex: 1 }}>{it.name}</Txt>
            {it.defunct ? <DefunctIcon /> : null}
            {meta ? <Txt role="caption" color="muted" lines={1} style={{ flexShrink: 0, maxWidth: "50%" }}>{meta}</Txt> : null}
          </Pressable>
        );
  });
  return (
    <View style={[{ gap: s(8) }, fill ? { flex: 1, minHeight: 0 } : null]}>
      {label ? <Txt role="fieldLabel" color="muted" style={{ marginBottom: -s(2) }}>{t(kind === "player" ? "field.player" : "field.team")}</Txt> : null}
      <Input accessibilityLabel={t(kind === "player" ? "field.player" : "field.team")} ref={input} value={locked ? "" : q} onChangeText={onText} editable={!locked} autoFocus={autoFocus}
        placeholder={locked ? lockedText : t(kind === "player" ? "ph.player" : "ph.team")} accent={!locked}
        style={locked ? { backgroundColor: c.surface_subtle, borderColor: c.control, borderWidth: BORDER } : undefined} />
      {shown.length === 0 ? below : fill
        ? <ScrollView style={{ flex: 1 }} contentContainerStyle={{ gap: s(8) }} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>{rows}</ScrollView>
        : rows}
    </View>
  );
}
