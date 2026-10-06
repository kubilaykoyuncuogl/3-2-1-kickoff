// Sıradaki kulüp: oyuncu verilir; önce ilk profesyonel kulübü, sonra her transferin hedefi tahmin edilir.
// İpuçları karo olarak: yıl, tür, bedel, gittiği ülke, lig.
import React, { useState } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, View } from "react-native";
import { api } from "@/net/socket";
import { SingleHeader, SingleLoading, SingleOver, country, money, useSingle } from "@/single";
import { useTheme } from "@/theme";
import { Eyebrow, Kv, Lives, Nav, Page, Panel, Row, Toast, Txt, t } from "@/ui";
import { Autocomplete } from "@/ui/autocomplete";

function moveText(st: any): string {
  const parts: string[] = [];
  if (st.year != null) parts.push(String(st.year));
  if (st.kind !== "start") parts.push(t("kind." + st.kind));
  if (st.fee != null) parts.push(money(Number(st.fee)));
  return parts.join(" · ");
}

export default function Chain() {
  const { s } = useTheme();
  const { d, at, failed, restart } = useSingle("chain");
  const [clearKey, setClearKey] = useState(0);
  const title = t("mode.chain");
  if (!d) return <SingleLoading title={title} failed={failed} onRetry={restart} />;
  const last = d.last ?? {};
  if (d.over) return <SingleOver mode="chain" title={title} d={d} summary={t("chain.summary", d.done ?? 0)} note={last.answer ? t("chain.was", last.answer) : undefined} onAgain={restart} />;
  const it = d.item; const hint = it.hint ?? {}; const first = it.step === 0; const hist: any[] = it.history ?? [];
  const sub: string[] = [];
  if (it.born != null) sub.push(t("chain.born", it.born));
  if (it.pos != null) sub.push(String(it.pos));
  sub.push(t("chain.step_n", Math.min(it.step + 1, it.steps_total), it.steps_total));
  const toast = last.type === "correct" ? { text: `${last.name ?? ""}  +${last.gained ?? 0}`, kind: "ok" as const }
    : last.type === "wrong" ? { text: t("chain.wrong", last.name ?? "", last.answer ?? ""), kind: "no" as const }
    : last.type === "timeout" ? { text: t("chain.timeout", last.answer ?? ""), kind: "no" as const } : null;
  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <Page>
        <Nav title={title} />
        <SingleHeader d={d} at={at} hotMs={5000} score={d.score} left={<><Eyebrow>{t("career.player_n", d.idx + 1)}</Eyebrow><Lives n={d.lives} /></>} />
        <View>
          <Txt size={26} w={800} lines={1}>{String(it.name)}</Txt>
          <Txt size={13} w={600} color="muted">{sub.join("  ·  ")}</Txt>
        </View>
        {toast ? <Toast text={toast.text} kind={toast.kind} /> : null}
        <Panel kind="violet" style={{ gap: s(8) }}>
          <Txt size={18} w={800} color="violet_ink">{first ? t("chain.first_q") : t("chain.next_q")}</Txt>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: s(6) }}>
            {hint.year != null ? <Kv k={t("chain.k_year")} v={String(hint.year)} /> : null}
            {!first ? <Kv k={t("chain.k_type")} v={t("kind." + (hint.kind ?? "free"))} /> : null}
            {hint.fee != null ? <Kv k={t("chain.k_fee")} v={money(Number(hint.fee))} /> : null}
            {hint.country != null ? <Kv k={first ? t("chain.k_country") : t("chain.to_country")} v={country(hint.country)} /> : null}
            {hint.league != null ? <Kv k={t("chain.league")} v={String(hint.league)} /> : null}
          </View>
        </Panel>
        <Autocomplete kind="team" clearKey={`${d.idx}-${it.step}-${clearKey}`} onPick={(id, name) => { api.singleTeam(id, name); setClearKey((k) => k + 1); }} />
        <ScrollView style={{ flex: 1 }} contentContainerStyle={{ gap: s(6) }} keyboardShouldPersistTaps="handled">
          {hist.map((st, i) => ({ st, i })).reverse().map(({ st, i }) => {
            const mt = moveText(st);
            return <Row key={i} index={String(i + 1)} title={String(st.club)} sub={country(st.country)} state={i === hist.length - 1 ? "new" : ""} defunct={!!st.defunct}
              right={mt ? <Txt size={12} w={600} color="muted">{mt}</Txt> : undefined} />;
          })}
        </ScrollView>
      </Page>
    </KeyboardAvoidingView>
  );
}
