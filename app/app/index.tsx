// Ana sayfa (kit: references/approved-home.png): kimlik başlığı, Online oyna (lime), Tek oyna, Haftanın maçları giriş kartı, alt menü.
// Giriş kartı yalnızca Maçlar sayfasına yönlendirir; maç adları ve puanlar bu karta geri eklenmez (kit 02-screen-specs).
import { useRouter } from "expo-router";
import React, { useEffect } from "react";
import { Pressable, View } from "react-native";
import { SvgXml } from "react-native-svg";
import { useGame, useProfile, useSettings } from "@/store";
import { RADII, useTheme } from "@/theme";
import { Icon, IdentityHeader, Page, Txt, t } from "@/ui";
import { stadiumFor } from "@/ui/stadium";

export default function Menu() {
  const router = useRouter();
  const { c, s } = useTheme();
  const nickname = useSettings((x) => x.nickname);
  const elo = useProfile((p) => p.elo);
  const weeklies = useGame((g) => g.weeklies);
  useEffect(() => { if (!nickname) router.push("/nickname"); }, [nickname, router]);
  return (
    <Page scroll nav="home">
      <IdentityHeader />
      <View style={{ height: s(8) }} />
      <Pressable accessibilityRole="button" accessibilityLabel={`${t("menu.online")}, ${t("menu.elo", elo)}`} onPress={() => router.push("/online")}
        style={({ pressed }) => ({ backgroundColor: pressed ? c.primary_pressed : c.primary, borderRadius: s(RADII.action), minHeight: s(84), paddingHorizontal: s(20), paddingVertical: s(14), flexDirection: "row", alignItems: "center", gap: s(14) })}>
        <View style={{ flex: 1, gap: s(2) }}>
          <Txt role="action" color="on_primary" lines={1}>{t("menu.online")}</Txt>
          <Txt role="label" color="on_primary" style={{ fontVariant: ["tabular-nums"] }}>{t("menu.elo", elo)}</Txt>
        </View>
        <Icon name="caret_right" color="on_primary" size={28} />
      </Pressable>
      <Pressable accessibilityRole="button" onPress={() => router.push("/single")}
        style={({ pressed }) => ({ backgroundColor: pressed ? c.raised : c.surface, borderRadius: s(RADII.action), borderWidth: 1, borderColor: c.border_quiet, minHeight: s(60), paddingHorizontal: s(20), paddingVertical: s(10), flexDirection: "row", alignItems: "center", gap: s(14) })}>
        <Txt role="action" lines={1} style={{ flex: 1 }}>{t("menu.single")}</Txt>
        <Icon name="caret_right" color="text" size={28} />
      </Pressable>
      <View style={{ height: s(8) }} />
      <WeeklyEntry count={weeklies.length} slug={weeklies[0]?.slug} onPress={() => router.push("/weekly")} />
    </Page>
  );
}

// Haftanın maçları giriş kartı (kit C03 WeeklyEntry): üstte stadyum, altta opak okuma bölgesi; kartın tamamı tek yönlendirme eylemi
function WeeklyEntry({ count, slug, onPress }: { count: number; slug?: string; onPress: () => void }) {
  const { c, s, col } = useTheme();
  const countText = count === 1 ? t("weekly.count_one") : t("weekly.count", count);
  const art = Math.round(col * 0.31);
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={`${t("weekly.matches")}, ${count ? countText : t("weekly.entry_none")}. ${t("weekly.helper")}`} onPress={onPress} disabled={!count}
      style={({ pressed }) => ({ borderRadius: s(RADII.card), borderWidth: 1, borderColor: pressed ? c.border_control : c.border_quiet, backgroundColor: c.surface, overflow: "hidden" })}>
      {count ? <View style={{ height: art, backgroundColor: c.canvas }} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
        <SvgXml xml={stadiumFor(slug ?? "")} width="100%" height="100%" preserveAspectRatio="xMidYMax slice" />
      </View> : null}
      <View style={{ padding: s(16), paddingTop: s(12), gap: s(4) }}>
        <View style={{ flexDirection: "row", alignItems: "flex-end", gap: s(12), flexWrap: "wrap" }}>
          <Txt role="cardTitle" style={{ flexShrink: 1 }}>{t("weekly.matches")}</Txt>
          <Txt role="label" color="muted" style={{ marginLeft: "auto", paddingBottom: s(4) }}>{count ? countText : t("weekly.entry_none")}</Txt>
        </View>
        <View style={{ flexDirection: "row", alignItems: "center", gap: s(12) }}>
          <Txt role="body" color="muted" style={{ flex: 1 }}>{t("weekly.helper")}</Txt>
          <Icon name="caret_right" color="text" size={24} />
        </View>
      </View>
    </Pressable>
  );
}
