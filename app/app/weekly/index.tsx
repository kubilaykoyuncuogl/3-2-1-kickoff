// Haftanın maçları (kit: references/approved-weekly.png): kimlik başlığı, başlık + karşılaşma sayısı, maç kartları, alt menü.
// Kart: mod adı + kalan süre rozeti, stadyum (mock, slug'a göre), iki takım + puan, "Tarafını seç" → alt sayfa; taraf hafta boyunca değişmez
// (kitteki "Değiştir" yok, karar 2026-10-10). Seçim onaylanınca kart altı "X için oyna" olur, oyun oradan başlar; taraf sunucuda ilk koşuyla kilitlenir.
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import { Pressable, View } from "react-native";
import { SvgXml } from "react-native-svg";
import { api, connect } from "@/net/socket";
import { Weekly, useGame } from "@/store";
import { RADII, useTheme } from "@/theme";
import { Btn, Icon, IdentityHeader, Page, Txt, t } from "@/ui";
import { LearnSteps } from "@/ui/learn";
import { ChoiceRow, Sheet } from "@/ui/sheet";
import { stadiumFor } from "@/ui/stadium";
import { num } from "@/ui/weekly";

export default function Matches() {
  const router = useRouter();
  const { s } = useTheme();
  const { slug } = useLocalSearchParams<{ slug?: string }>();
  const all = useGame((g) => g.weeklies);
  const connected = useGame((g) => g.connected);
  const [chosen, setChosen] = useState<Record<string, "a" | "b">>({});
  const [sheet, setSheet] = useState<Weekly | null>(null);
  const [pick, setPick] = useState<"a" | "b" | null>(null);
  useEffect(() => { if (!useGame.getState().connected) connect(); else api.weeklyInfo(); }, [connected]);
  const list = slug ? [...all].sort((x, y) => (x.slug === slug ? -1 : y.slug === slug ? 1 : 0)) : all;      // bağlantıyla gelen maç en üstte
  const countText = all.length === 1 ? t("weekly.count_one") : t("weekly.count", all.length);
  const open = (w: Weekly) => { setPick(chosen[w.slug] ?? null); setSheet(w); };
  const confirm = () => { if (sheet && pick) { setChosen({ ...chosen, [sheet.slug]: pick }); setSheet(null); } };
  return (
    <>
      <Page scroll nav="matches">
        <IdentityHeader />
        <View style={{ height: s(8) }} />
        <View style={{ flexDirection: "row", alignItems: "flex-end", gap: s(12), flexWrap: "wrap" }}>
          <Txt role="pageTitle" style={{ flexShrink: 1 }}>{t("weekly.matches")}</Txt>
          {all.length ? <Txt role="label" color="muted" style={{ marginLeft: "auto", paddingBottom: s(4) }}>{countText}</Txt> : null}
        </View>
        <Txt role="body" color="muted">{all.length ? t("weekly.helper") : connected ? t("weekly.none") : t("net.connecting")}</Txt>
        {list.map((w) => <MatchCard key={w.slug} w={w} side={w.me?.side ?? chosen[w.slug] ?? null} locked={!!w.me}
          onPick={() => open(w)} onPlay={(side) => router.push({ pathname: "/weekly/play", params: { side, slug: w.slug } })} />)}
      </Page>
      <Sheet open={!!sheet} title={t("weekly.sheet_title")} sub={sheet ? `${sheet.a.short} – ${sheet.b.short}` : undefined} onClose={() => setSheet(null)}>
        {sheet ? (["a", "b"] as const).map((k) => <ChoiceRow key={k} title={sheet[k].short} selected={pick === k} onPress={() => setPick(k)} />) : null}
        <Btn text={t("weekly.confirm")} onPress={confirm} disabled={!pick} />
        <Txt role="caption" color="muted" center>{t("weekly.pick_note")}</Txt>
      </Sheet>
      {all[0] ? <LearnSteps id={all[0].format === "career" ? "weekly_career" : "weekly"} title={t("weekly.matches")} /> : null}
    </>
  );
}

// Kalan süre: hafta dosyasındaki `date` günün sonu sayılır; SS:DD:SN (saat 24'ü aşabilir). Tarih yoksa "Bu hafta", geçtiyse "Sona erdi".
function useCountdown(date: string) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => { if (!date) return; const id = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(id); }, [date]);
  if (!date) return t("weekly.this_week");
  const end = new Date(`${date}T23:59:59`).getTime();
  const left = Math.floor((end - now) / 1000);
  if (!Number.isFinite(left)) return t("weekly.this_week");
  if (left <= 0) return t("weekly.ended");
  const h = Math.floor(left / 3600), m = Math.floor((left % 3600) / 60), sec = left % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

// Maç kartı (kit C04): başlık satırı, stadyum, takımlar ve puanlar (VS ortada), ayırıcı, alt eylem satırı
function MatchCard({ w, side, locked, onPick, onPlay }: { w: Weekly; side: "a" | "b" | null; locked: boolean; onPick: () => void; onPlay: (side: "a" | "b") => void }) {
  const { c, s, col } = useTheme();
  const mode = t(w.format === "career" ? "mode.career" : "weekly.mode_name");
  const timeLeft = useCountdown(w.date);
  const art = Math.round((col - 2) / 3);
  const action = side ? t("weekly.play_for", w[side].short) : t("weekly.pick");
  const onAction = side ? () => onPlay(side) : onPick;
  return (
    <View style={{ borderRadius: s(RADII.card), borderWidth: 1, borderColor: c.border_quiet, backgroundColor: c.surface, overflow: "hidden" }}
      accessible accessibilityLabel={`${mode}. ${timeLeft}. ${w.a.short}, ${t("weekly.points", num(w.a.total))}. ${w.b.short}, ${t("weekly.points", num(w.b.total))}.`}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: s(12), paddingHorizontal: s(16), paddingTop: s(12), paddingBottom: s(6) }}>
        <Txt role="cardTitle" lines={1} style={{ flex: 1 }}>{mode}</Txt>
        <View style={{ borderRadius: 999, borderWidth: 1, borderColor: c.border_control, paddingHorizontal: s(12), paddingVertical: s(5) }}>
          <Txt role="caption" style={{ fontVariant: ["tabular-nums"] }}>{timeLeft}</Txt>
        </View>
      </View>
      <View style={{ height: art, backgroundColor: c.canvas }} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
        <SvgXml xml={stadiumFor(w.slug)} width="100%" height="100%" preserveAspectRatio="xMidYMid slice" />
      </View>
      <View style={{ flexDirection: "row", alignItems: "flex-end", paddingHorizontal: s(16), paddingTop: s(10), paddingBottom: s(12), gap: s(8) }}>
        {(["a", "b"] as const).map((k, i) => (
          <React.Fragment key={k}>
            {i === 1 ? <Txt role="team" color="muted" style={{ paddingBottom: s(6) }}>{t("weekly.vs")}</Txt> : null}
            <View style={{ flex: 1, alignItems: k === "b" ? "flex-end" : "flex-start", gap: s(2) }}>
              <Txt role="team" lines={2} style={{ textAlign: k === "b" ? "right" : "left" }}>{w[k].short}</Txt>
              <View style={{ flexDirection: "row", alignItems: "baseline", gap: s(6), flexWrap: "wrap", justifyContent: k === "b" ? "flex-end" : "flex-start" }}>
                <Txt role="points" style={{ fontVariant: ["tabular-nums"] }}>{num(w[k].total)}</Txt>
                <Txt role="label" color="muted">{t("weekly.points_unit")}</Txt>
              </View>
            </View>
          </React.Fragment>
        ))}
      </View>
      <View style={{ height: 1, backgroundColor: c.border_quiet, marginHorizontal: s(16) }} />
      <Pressable accessibilityRole="button" accessibilityLabel={action} onPress={onAction}
        style={({ pressed }) => ({ minHeight: s(56), paddingHorizontal: s(16), flexDirection: "row", alignItems: "center", gap: s(12), backgroundColor: pressed ? c.raised : "transparent" })}>
        {locked ? <Icon name="check_circle" color="primary" size={22} /> : null}
        <Txt role="team" color={side ? "primary" : "text"} lines={1} style={{ flex: 1 }}>{action}</Txt>
        <Icon name="arrow_right" color={side ? "primary" : "text"} size={24} />
      </Pressable>
    </View>
  );
}
