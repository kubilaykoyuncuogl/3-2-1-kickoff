// Kulüp kapsamı ve dönem seçicileri (ui.gd scope_button / scope_picker / era_picker karşılığı). Değerler ayarlara yazılır.
import React from "react";
import { Pressable, View } from "react-native";
import { t } from "../i18n";
import { ERAS, LEAGUES, SCOPES, Scope, leagueName, useSettings } from "../store";
import { Token, useTheme } from "../theme";
import { BORDER, Chevron, Chip, Crown, Eyebrow, Globe, OptionCard, Txt } from "./index";

export function scopeLabel(s: string): string {
  const lg = leagueName(s);
  return lg || t(`scope.${(SCOPES as readonly string[]).includes(s) ? s : "all"}.title`);
}

export function eraLabel(era: number): string {
  const e = era & 31;
  if (e === 0 || e === 31) return t("era.all_long");
  return ERAS.filter(([, bit]) => e & bit).map(([k]) => t("era.short." + k)).join(" · ");
}

function ScopeIcon({ scope, ink, compact }: { scope: Scope; ink: Token; compact?: boolean }) {
  const { s } = useTheme();
  const size = compact ? 28 : 36;
  if (scope === "all") return <Globe color={ink} size={size} />;
  if (scope === "top") return <Crown color={ink} size={size} />;
  return <View style={{ width: s(size), alignItems: "center" }}><Txt size={size * 1.2} w={800} color={ink} style={{ lineHeight: s(size * 1.2) }}>5</Txt></View>;
}

// compact: Online'da seçim (seçili işaretli); değilse Tek oyna'da ileri oklu
export function ScopeButton({ scope, selected, onPress, compact }: { scope: Scope; selected: boolean; onPress: (s: Scope) => void; compact?: boolean }) {
  const ink: Token = selected ? "violet_ink" : "fg";
  const tail = !compact ? <Chevron color={selected ? "violet_ink" : "muted"} /> : null;      // sıkı düzende seçim renkten belli; etiket alt yazıyı kesiyordu
  return <OptionCard title={t(`scope.${scope}.title`)} sub={t(`scope.${scope}.sub`)} lead={<ScopeIcon scope={scope} ink={ink} compact={compact} />} tail={tail} selected={selected} height={compact ? 62 : 76} onPress={() => onPress(scope)} />;
}

// Tek lig: dokundukça ligler sırayla değişir (Premier League → La Liga → …). Başka kapsam seçilince varsayılan haline döner.
function LeagueButton() {
  const { s } = useTheme();
  const scope = useSettings((x) => x.scope);
  const i = LEAGUES.findIndex(([c]) => c === scope);
  const on = i >= 0;
  const ink: Token = on ? "violet_ink" : "fg";
  return <OptionCard title={on ? LEAGUES[i][1] : t("scope.league.title")} sub={on ? t("scope.league.sub_on") : t("scope.league.sub")} selected={on} height={62}
    lead={<View style={{ width: s(28), alignItems: "center" }}><Txt size={34} w={800} color={ink} style={{ lineHeight: s(36) }}>1</Txt></View>}
    tail={on ? <Chip text={`${i + 1} / ${LEAGUES.length}`} kind="violet" style={{ minWidth: s(58), alignItems: "center" }} /> : null}
    onPress={() => useSettings.getState().set({ scope: LEAGUES[on ? (i + 1) % LEAGUES.length : 0][0] })} />;
}

export function ScopePicker() {
  const { s } = useTheme();
  const scope = useSettings((x) => x.scope);
  return (
    <View style={{ gap: s(6) }}>
      <Eyebrow>{t("scope.header")}</Eyebrow>
      {SCOPES.map((sc) => <ScopeButton key={sc} scope={sc} selected={scope === sc} compact onPress={(v) => useSettings.getState().set({ scope: v })} />)}
      <LeagueButton />
    </View>
  );
}

// Tümü + beş on yıl, çoklu seçim (mantık store.eraToggle). big: ayrı ekranda üçlü ızgara, değilse tek satır çip
export function EraPicker({ big }: { big?: boolean }) {
  const { c, s } = useTheme();
  const era = useSettings((x) => x.era);
  const items: [string, number][] = [["all", 0], ...ERAS];
  const btn = ([k, bit]: [string, number]) => {
    const on = bit === 0 ? era === 0 : (era & bit) !== 0;
    return (
      <Pressable key={k} onPress={() => useSettings.getState().eraToggle(bit)} style={{
        flexBasis: big ? "31%" : undefined, flexGrow: 1, minHeight: s(big ? 64 : 40), borderRadius: s(12), borderWidth: BORDER, paddingHorizontal: s(4),
        backgroundColor: on ? c.violet_soft : c.surface, borderColor: on ? c.violet_fill : c.line, alignItems: "center", justifyContent: "center",
      }}>
        <Txt size={big ? 17 : 13} w={700} color={on ? "violet_ink" : "fg"} lines={1}>{t(big || bit === 0 ? "era." + k : "era.short." + k)}</Txt>
      </Pressable>
    );
  };
  const wrap = <View style={{ flexDirection: "row", flexWrap: big ? "wrap" : "nowrap", gap: s(big ? 8 : 4) }}>{items.map(btn)}</View>;
  if (big) return wrap;
  return <View style={{ gap: s(6) }}><Eyebrow>{t("era.header")}</Eyebrow>{wrap}</View>;
}
