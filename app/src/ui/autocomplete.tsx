// Yazı kutusu + öneri listesi. Öneriler sunucudan (store.suggestions) gelir; öneriye dokunmak = seçmek.
import React, { useEffect, useRef, useState } from "react";
import { Pressable, TextInput, View } from "react-native";
import { t } from "../i18n";
import { api } from "../net/socket";
import { Suggestion, useGame } from "../store";
import { useTheme } from "../theme";
import { BORDER, DefunctIcon, Input, Txt } from "./index";

export function Autocomplete({ kind, locked, lockedText, onPick, autoFocus = true, clearKey }: {
  kind: "team" | "player"; locked?: boolean; lockedText?: string; onPick: (id: number, name: string) => void; autoFocus?: boolean; clearKey?: unknown;
}) {
  const { c, s } = useTheme();
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

  return (
    <View style={{ gap: s(6) }}>
      <Input ref={input} value={locked ? "" : q} onChangeText={onText} editable={!locked} autoFocus={autoFocus}
        placeholder={locked ? lockedText : t(kind === "player" ? "ph.player" : "ph.team")} accent={!locked}
        style={locked ? { backgroundColor: c.no_soft, borderColor: c.no, fontSize: s(20) } : { fontSize: s(20) }} />
      {!locked && items.map((it) => {
        const used = !!it.used || it.in_scope === false;
        const label = it.name + (kind === "player" && it.born ? `  ·  ${it.born}` : "") + (used ? (it.used ? t("ac.used") : t("ac.out_of_scope")) : "");
        return (
          <Pressable key={it.id} disabled={used} onPress={() => onPick(it.id, it.name)} style={({ pressed }) => ({
            backgroundColor: pressed ? c.violet_soft : used ? "transparent" : c.surface, borderRadius: s(12), borderWidth: BORDER, borderColor: pressed ? c.violet_fill : c.line,
            minHeight: s(48), paddingHorizontal: s(14), flexDirection: "row", alignItems: "center", gap: s(8),
          })}>
            <Txt size={16} w={600} color={used ? "muted" : "fg"} lines={1} style={{ flex: 1 }}>{label}</Txt>
            {it.defunct ? <DefunctIcon /> : null}
          </Pressable>
        );
      })}
    </View>
  );
}
