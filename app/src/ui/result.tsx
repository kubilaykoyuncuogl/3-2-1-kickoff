// Oyun sonu kartı: ekran görüntüsü alınıp paylaşılmaya uygun, tek başına anlaşılır.
// Üst bant (oyun adı · mod), büyük skor, "seni yakan soru", "biliyor muydun", alt satır (adres · takma ad).
import React from "react";
import { Text, View } from "react-native";
import { getLang, t } from "../i18n";
import { useSettings } from "../store";
import { FONT, useTheme } from "../theme";
import { Chip, Eyebrow, Txt } from "./index";

export const SITE = "kickoff.grandecorpo.com";
const nf = (n: number) => Math.round(n).toLocaleString(getLang() === "tr" ? "tr-TR" : "en-US");
const eur = (v: number) => (v >= 1_000_000 ? `€${(v / 1_000_000).toFixed(1).replace(/\.0$/, "").replace(".", getLang() === "tr" ? "," : ".")}M` : v >= 1000 ? `€${Math.floor(v / 1000)}K` : `€${v}`);

export type Section = { title: string; lines: string[]; kind: "burn" | "fact" | "plain" };

export function ResultCard({ mode, chips = [], big, label, sub, record, sections }: {
  mode: string; chips?: string[]; big: string; label: string; sub?: string; record?: boolean; sections: Section[];
}) {
  const { c, s } = useTheme();
  const nick = useSettings((x) => x.nickname);
  return (
    <View style={{ borderRadius: s(20), borderWidth: 2, borderColor: c.violet_fill, backgroundColor: c.surface, overflow: "hidden" }}>
      <View style={{ backgroundColor: c.violet_fill, paddingHorizontal: s(16), paddingVertical: s(10), flexDirection: "row", alignItems: "center" }}>
        <Text style={{ flex: 1, fontFamily: FONT[800], fontStyle: "italic", fontSize: s(18), color: c.violet_on }}>3·2·1 <Text style={{ fontSize: s(11), fontStyle: "normal", fontFamily: FONT[700] }}>KICKOFF</Text></Text>
        <Text numberOfLines={1} style={{ fontFamily: FONT[700], fontSize: s(12), color: c.violet_on }}>{mode.toLocaleUpperCase("tr")}</Text>
      </View>
      <View style={{ padding: s(16), gap: s(10) }}>
        {chips.length ? <View style={{ flexDirection: "row", flexWrap: "wrap", gap: s(6), justifyContent: "center" }}>{chips.map((x) => <Chip key={x} text={x} kind="line" style={{ alignSelf: "center" }} />)}</View> : null}
        <View style={{ alignItems: "center" }}>
          <Eyebrow color={record ? "ok" : "muted"} center>{label}</Eyebrow>
          <Txt size={60} w={800} color="violet_ink" center style={{ lineHeight: s(66) }}>{big}</Txt>
          {sub ? <Txt size={14} w={600} color="muted" center>{sub}</Txt> : null}
        </View>
        {sections.filter((x) => x.lines.length).map((sec) => {
          const bg = sec.kind === "burn" ? c.no_soft : sec.kind === "fact" ? c.amber_soft : c.bg;
          const ink = sec.kind === "burn" ? "no" : sec.kind === "fact" ? "amber_ink" : "muted";
          return (
            <View key={sec.title} style={{ backgroundColor: bg, borderRadius: s(12), paddingHorizontal: s(12), paddingVertical: s(10), gap: s(3) }}>
              <Eyebrow color={ink as any}>{sec.title}</Eyebrow>
              {sec.lines.map((ln, i) => <Txt key={i} size={i === 0 && sec.kind !== "plain" ? 15 : 13} w={i === 0 && sec.kind !== "plain" ? 700 : 600} color="fg">{ln}</Txt>)}
            </View>
          );
        })}
        <View style={{ flexDirection: "row", alignItems: "center" }}>
          <Txt size={11} w={600} color="muted" style={{ flex: 1 }}>{SITE}</Txt>
          <Txt size={11} w={700} color="muted">{nick ? "@" + nick : ""}</Txt>
        </View>
      </View>
    </View>
  );
}

// Sunucudan gelen yapılandırılmış koşu sonu bilgisinden (end.burn / end.fact) kart satırları
export function endSections(end: any): Section[] {
  const out: Section[] = [];
  const b = end?.burn; const f = end?.fact;
  if (b) {
    const lines: string[] = [];
    if (b.kind === "pair") { lines.push(`${b.a} × ${b.b}`); if (b.tried) lines.push(t("end.yours", b.tried)); }
    else if (b.kind === "pick") { lines.push(`${b.a} × ${b.b}`); lines.push(t("end.correct", b.answer)); if (b.picked) lines.push(t("end.yours", b.picked)); }
    else if (b.kind === "who") { lines.push(t("end.correct", b.answer)); if (b.tried) lines.push(t("end.yours", b.tried)); }
    else if (b.kind === "club") { lines.push(`${b.player}: ${b.answer}`); if (b.tried) lines.push(t("end.yours", b.tried)); }
    else if (b.kind === "vs") {
      const v = (x: number) => (b.fmt === "money" ? eur(Number(x)) : nf(Number(x)));
      lines.push(t("cat." + b.cat)); lines.push(`${b.names[0]} ${v(b.values[0])}  ·  ${b.names[1]} ${v(b.values[1])}`);
      if (b.picked === 0 || b.picked === 1) lines.push(t("end.yours", b.names[b.picked]));
    }
    out.push({ title: t("end.burn"), lines, kind: "burn" });
  }
  if (f) {
    let line = "";
    if (f.kind === "pair_players") line = t("fact.pair_players", f.a, f.b, f.total, f.names.join(", ") + (f.total > f.names.length ? "…" : ""));
    else if (f.kind === "two_clubs") line = f.ay && f.by ? t("fact.two_clubs", f.name, f.a, f.ay, f.b, f.by) : t("fact.two_clubs_plain", f.name, f.a, f.b);
    else if (f.kind === "career") line = (f.apps > 0 ? (f.goals > 0 ? t("fact.career_stats", f.name, nf(f.apps), nf(f.goals)) : t("fact.career_apps", f.name, nf(f.apps))) + "\n" : "") + f.clubs.join(" → ");
    else if (f.kind === "move") line = `${f.name} · ${f.year ?? ""}: ${f.from ? f.from + " → " : ""}${f.to}` + (f.move && f.move !== "start" ? ` · ${t("kind." + f.move)}` : "") + (f.fee ? ` · ${eur(Number(f.fee))}` : "");
    else if (f.kind === "player") line = f.goals > 0 ? t("fact.player", f.name, nf(f.apps), nf(f.goals), f.n_clubs) : t("fact.player_apps", f.name, nf(f.apps), f.n_clubs);
    else if (f.kind === "club_stats") line = f.goals != null && f.assists != null ? t("fact.club_stats", f.name, f.club, nf(f.apps), nf(f.goals), nf(f.assists)) : t("fact.club_stats_apps", f.name, f.club, nf(f.apps));
    if (line) out.push({ title: t("end.fact"), lines: line.split("\n"), kind: "fact" });
  }
  return out;
}

export function sectionsText(sections: Section[]): string {
  return sections.map((x) => `${x.title}: ${x.lines.join(" · ")}`).join("\n");
}
