// Kariyer yolu: kulüpler ilk kulüpten başlayarak tek tek açılır; oyuncuyu ne kadar erken bilirsen o kadar puan.
// Liste en yeni kulüp üstte (klavye açıkken görünür kalsın).
import { runChips } from "@/ui/pickers";
import React, { useState } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, View } from "react-native";
import { api } from "@/net/socket";
import { SingleHeader, SingleLoading, SingleOver, country, useSingle } from "@/single";
import { useTheme } from "@/theme";
import { Chip, Eyebrow, Lives, Nav, Page, Row, Toast, Txt, t } from "@/ui";
import { Autocomplete } from "@/ui/autocomplete";

export default function Career() {
  const { s, kb } = useTheme();
  const { d, at, failed, restart } = useSingle("career");
  const [clearKey, setClearKey] = useState(0);
  const title = t("mode.career");
  if (!d) return <SingleLoading title={title} failed={failed} onRetry={restart} />;
  const last = d.last ?? {};
  if (d.over) return <SingleOver mode="career" title={title} d={d} summary={t("career.summary", d.done ?? 0)} note={last.answer ? t("career.was", last.answer) : undefined} onAgain={restart} chips={runChips()} />;
  const clubs: any[] = d.item.clubs ?? []; const total: number = d.item.total ?? clubs.length;
  const toast = last.type === "correct" ? { text: `${last.name ?? ""}  +${last.gained ?? 0}`, kind: "ok" as const }
    : last.type === "wrong" ? { text: t("career.wrong", last.name ?? ""), kind: "no" as const }
    : last.type === "timeout" ? { text: t("career.timeout", last.answer ?? ""), kind: "no" as const } : null;
  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <Page>
        <Nav title={title} />
        <SingleHeader d={d} at={at} hotMs={0} score={d.score} left={<><Eyebrow>{t("career.player_n", d.idx + 1)}</Eyebrow><Lives n={d.lives} /></>} />
        {kb ? null : <Txt size={20} w={800}>{t("career.prompt")}</Txt>}
        {toast && !kb ? <Toast text={toast.text} kind={toast.kind} /> : null}
        {/* klavye açıkken en çok 3 öneri: kulüp listesi (sorunun kendisi) görünür kalsın */}
        <Autocomplete kind="player" max={kb ? 3 : 6} clearKey={`${d.idx}-${clearKey}`} onPick={(id, name) => { api.singleGuess(id, name); setClearKey((k) => k + 1); }}
          below={kb && toast ? <Toast text={toast.text} kind={toast.kind} /> : undefined} />
        <ScrollView style={{ flex: 1 }} contentContainerStyle={{ gap: s(6) }} keyboardShouldPersistTaps="handled">
          {total > clubs.length ? <Row index="?" title={t("career.more", total - clubs.length)} state="hidden" /> : null}
          {clubs.map((c, i) => ({ c, i })).reverse().map(({ c, i }) => (
            <Row key={i} index={String(i + 1)} title={String(c.club)} sub={country(c.country)} state={i === clubs.length - 1 ? "new" : ""} defunct={!!c.defunct}
              right={<View style={{ flexDirection: "row", alignItems: "center", gap: s(6) }}>
                {c.kind === "loan" ? <Chip text={t("kind.loan")} kind="amber" style={{ alignSelf: "center" }} /> : null}
                {c.year != null ? <Txt size={15} w={800} color={i === clubs.length - 1 ? "violet_ink" : "muted"}>{String(c.year)}</Txt> : null}
              </View>} />
          ))}
        </ScrollView>
      </Page>
    </KeyboardAvoidingView>
  );
}
