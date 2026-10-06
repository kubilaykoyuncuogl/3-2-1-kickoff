// Haftanın maçı oynanışı: üstte A kulübünün, altta B kulübünün oyuncusu (kulüp renklerinde). Sayısı yüksek olana dokun; ilk yanlışta biter.
// Akış tek oyunculu "o mu bu mu" ile aynı (sunucuda mode = "weekly"); puan seçilen tarafın toplamına yazılır.
import { useLocalSearchParams } from "expo-router";
import React, { useEffect, useState } from "react";
import { Pressable, Text, View } from "react-native";
import { api } from "@/net/socket";
import { Single, useGame } from "@/store";
import { SingleHeader, SingleLoading, SingleOver, useSingle } from "@/single";
import { FONT, useTheme } from "@/theme";
import { Badge, Eyebrow, Nav, Page, Txt, t } from "@/ui";
import { num } from "@/ui/weekly";

const hold = (prev: Single, next: Single) => (next.over ? (next.last?.values ? 1500 : 0) : next.idx !== prev.idx && next.last?.type === "correct" ? 900 : 0);

export default function WeeklyPlay() {
  const { side = "a" } = useLocalSearchParams<{ side?: "a" | "b" }>();
  const { c, s } = useTheme();
  const w = useGame((g) => g.weekly);
  const { d, at, pending, failed, restart } = useSingle("weekly", hold, () => api.weeklyStart(side === "b" ? "b" : "a"));
  const [pressed, setPressed] = useState(-1);
  useEffect(() => { setPressed(-1); }, [d?.idx]);
  const title = t("weekly.title");
  if (!d || !w) return <SingleLoading title={title} failed={failed} onRetry={restart} />;
  const mine = w[w.me?.side ?? (side === "b" ? "b" : "a")];
  if (d.over) return <SingleOver mode="weekly" title={title} d={d} summary={t("versus.summary", d.done ?? 0)} extra={d.score > 0 ? t("weekly.added", mine.short, num(d.score)) : undefined}
    note={d.last?.type === "timeout" ? t("sp.time_up") : undefined} onAgain={restart} />;
  const it = d.item;
  const pl = pending?.last ?? {};
  const values: unknown[] | null = pending && pl.values ? pl.values : null;
  const answer = pending ? (pl.type === "correct" ? pl.option : pl.answer ?? -1) : -1;
  const wrongPick = pending && pl.type === "wrong" ? pl.option : -1;
  return (
    <Page>
      <Nav title={title} />
      <SingleHeader d={d} at={at} hotMs={2500} score={d.score} left={<Eyebrow>{t("versus.round", d.idx + 1)}</Eyebrow>} />
      <Txt size={20} w={800} center>{t("cat." + it.cat)}</Txt>
      {(["a", "b"] as const).map((k, i) => {
        const club = w[k]; const ok = i === answer; const no = i === wrongPick;
        const tx = (text: string, size: number, weight: 600 | 800 = 800) =>
          <Text style={{ fontFamily: FONT[weight], fontSize: s(size), color: club.colors[1], textAlign: "center" }}>{text}</Text>;
        return (
          <React.Fragment key={k}>
            {i === 1 ? <View style={{ alignItems: "center" }}><Badge text="VS" /></View> : null}
            <Pressable disabled={pressed >= 0 || !!pending} onPress={() => { setPressed(i); api.singleAnswer(i); }} style={({ pressed: p }) => ({
              flex: 1, minHeight: s(110), borderRadius: s(16), borderWidth: 4, alignItems: "center", justifyContent: "center", paddingHorizontal: s(12), gap: s(2),
              backgroundColor: club.colors[0], borderColor: ok ? c.ok : no ? c.no : p || pressed === i ? c.violet_fill : c.line,
            })}>
              {tx(club.short.toLocaleUpperCase("tr"), 12, 600)}
              {tx(String(it.names[i]), 24)}
              {tx(values ? num(Number(values[i])) : "?", 30)}
            </Pressable>
          </React.Fragment>
        );
      })}
    </Page>
  );
}
