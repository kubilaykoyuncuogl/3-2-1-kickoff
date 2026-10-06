// O mu bu mu: iki futbolcu, bir kategori. Değeri büyük olana dokun; doğruysa sürer, ilk yanlışta biter.
import { runChips } from "@/ui/pickers";
import React, { useEffect, useState } from "react";
import { Pressable, View } from "react-native";
import { api } from "@/net/socket";
import { Single } from "@/store";
import { SingleHeader, SingleLoading, SingleOver, money, useSingle } from "@/single";
import { useTheme } from "@/theme";
import { Badge, Eyebrow, Nav, Page, Toast, Txt, t } from "@/ui";

// sonuç gösterimi: doğruysa 0,9 sn, koşu bitiyorsa 1,5 sn değerler açık kalır
const hold = (prev: Single, next: Single) => (next.over ? (next.last?.values ? 1500 : 0) : next.idx !== prev.idx && next.last?.type === "correct" ? 900 : 0);

// Koşuyu bitiren sorunun dökümü: soru, iki oyuncu ve sayıları
function lastLine(d: Single, fmt: string): string | undefined {
  const v = d.last?.values; const it = d.item;
  if (!v || !it?.names) return d.last?.type === "timeout" ? t("sp.time_up") : undefined;
  const f = (x: unknown) => (fmt === "money" ? money(Number(x)) : String(Math.trunc(Number(x))));
  return `${d.last?.type === "timeout" ? t("sp.time_up") + "  ·  " : ""}${t("cat." + it.cat)}\n${it.names[0]} ${f(v[0])}  ·  ${it.names[1]} ${f(v[1])}`;
}

export default function Versus() {
  const { c, s } = useTheme();
  const { d, at, pending, failed, restart } = useSingle("versus", hold);
  const [pressed, setPressed] = useState(-1);
  useEffect(() => { setPressed(-1); }, [d?.idx]);
  const title = t("mode.versus");
  if (!d) return <SingleLoading title={title} failed={failed} onRetry={restart} />;
  if (d.over) return <SingleOver mode="versus" title={title} d={d} summary={t("versus.summary", d.done ?? 0)} note={lastLine(d, String(d.item?.fmt ?? "int"))} onAgain={restart} chips={runChips()} />;
  const it = d.item; const fmt = String(it.fmt ?? "int");
  const val = (v: unknown) => (v === null || v === undefined ? "?" : fmt === "money" ? money(Number(v)) : String(Math.trunc(Number(v))));
  const pl = pending?.last ?? {};
  const values: unknown[] | null = pending && pl.values ? pl.values : null;
  const answer = pending ? (pl.type === "correct" ? pl.option : pl.answer ?? -1) : -1;
  const wrongPick = pending && pl.type === "wrong" ? pl.option : -1;
  return (
    <Page>
      <Nav title={title} />
      <SingleHeader d={d} at={at} hotMs={2500} score={d.score} left={<Eyebrow>{t("versus.round", d.idx + 1)}</Eyebrow>} />
      {it.new_cat ? <Toast text={t("versus.new_cat")} kind="ok" /> : null}
      <Txt size={20} w={800} center>{t("cat." + it.cat)}</Txt>
      {[0, 1].map((i) => {
        const side = i === 0 ? "violet" : "amber"; const ink = i === 0 ? "violet_ink" : "amber_ink";
        const ok = i === answer; const no = i === wrongPick;
        const born = it.born?.[i];
        return (
          <React.Fragment key={i}>
            {i === 1 ? <View style={{ alignItems: "center" }}><Badge text="VS" /></View> : null}
            <Pressable disabled={pressed >= 0 || !!pending} onPress={() => { setPressed(i); api.singleAnswer(i); }} style={({ pressed: p }) => ({
              flex: 1, minHeight: s(110), borderRadius: s(16), borderWidth: 2, alignItems: "center", justifyContent: "center", paddingHorizontal: s(12),
              backgroundColor: ok ? c.ok_soft : no ? c.no_soft : side === "violet" ? c.violet_soft : c.amber_soft,
              borderColor: ok ? c.ok : no ? c.no : p || pressed === i ? (side === "violet" ? c.violet_fill : c.amber_fill) : "transparent",
            })}>
              <Txt size={24} w={800} color={ink} center>{String(it.names[i])}</Txt>
              <Txt size={12} color={ink} center>{born != null ? t("chain.born", born) : ""}</Txt>
              <Txt size={30} w={800} color={ink} center>{val(values ? values[i] : it.shown?.[i])}</Txt>
            </Pressable>
          </React.Fragment>
        );
      })}
    </Page>
  );
}
