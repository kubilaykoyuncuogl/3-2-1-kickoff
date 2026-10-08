// Kulüp kapsamı ve dönem seçicileri (ui.gd scope_button / scope_picker / era_picker karşılığı). Değerler ayarlara yazılır.
import React, { useState } from "react";
import { Modal, Pressable, View } from "react-native";
import { SvgXml } from "react-native-svg";
import { has, t } from "../i18n";
import { ERAS, LEAGUES, ROUNDS, SCOPES, Scope, useSettings } from "../store";
import { Token, useTheme } from "../theme";
import { FLAGS } from "./flags";
import { BORDER, Chevron, Crown, Eyebrow, Globe, OptionCard, Txt } from "./index";

const countryName = (name: string) => (has("country." + name) ? t("country." + name) : name);

// Lig adı; aynı adı taşıyan ligler (Bundesliga: Almanya / Avusturya, Super League: Yunanistan / İsviçre) ülkesiyle ayrışır
export function scopeLabel(s: string): string {
  const lg = LEAGUES.find(([c]) => c === s);
  if (lg) return LEAGUES.filter(([, n]) => n === lg[1]).length > 1 ? `${lg[1]} · ${countryName(lg[2])}` : lg[1];
  return t(`scope.${(SCOPES as readonly string[]).includes(s) ? s : "all"}.title`);
}

// Yuvarlak ülke bayrağı (lig koduyla). Çizimler flags.ts'te; daire kırpması burada.
export function Flag({ code, size }: { code: string; size: number }) {
  const { c, s } = useTheme();
  const px = s(size);
  if (!FLAGS[code]) return <View style={{ width: px, height: px }} />;
  return (
    <View style={{ width: px, height: px, borderRadius: px / 2, overflow: "hidden", borderWidth: 1, borderColor: c.line }}>
      <SvgXml xml={`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">${FLAGS[code]}</svg>`} width="100%" height="100%" />
    </View>
  );
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

// Tek lig: dokununca 20 ülkenin en üst ligi 4×5 bayraklı ızgarada açılır; seçince kapanır, kutuda seçilen ligin bayrağı ve adı kalır.
// Başka kapsam seçilince kutu varsayılan haline döner.
function LeagueButton() {
  const { c, s, col } = useTheme();
  const scope = useSettings((x) => x.scope);
  const [open, setOpen] = useState(false);
  const cur = LEAGUES.find(([code]) => code === scope);
  const ink: Token = cur ? "violet_ink" : "fg";
  const gap = s(8); const pad = s(14);
  const tile = Math.floor((col - pad * 2 - gap * 3) / 4);      // kutu yüksekliği için; genişliği satır paylaştırır (4 sütun × 5 satır)
  return (
    <>
      <OptionCard title={cur ? cur[1] : t("scope.league.title")} sub={cur ? t("scope.league.sub_on", countryName(cur[2])) : t("scope.league.sub")} selected={!!cur} height={62}
        lead={cur ? <Flag code={cur[0]} size={30} /> : <View style={{ width: s(28), alignItems: "center" }}><Txt size={34} w={800} color={ink} style={{ lineHeight: s(36) }}>1</Txt></View>}
        tail={<Chevron color={cur ? "violet_ink" : "muted"} />} onPress={() => setOpen(true)} />
      <Modal visible={open} transparent animationType="fade" onRequestClose={() => setOpen(false)}>
        <Pressable onPress={() => setOpen(false)} style={{ flex: 1, backgroundColor: c.bg + "E6", alignItems: "center", justifyContent: "center" }}>
          <Pressable onPress={() => {}} style={{ width: col, backgroundColor: c.surface, borderRadius: s(20), borderWidth: BORDER, borderColor: c.line, padding: pad, gap: s(10) }}>
            <View style={{ flexDirection: "row", alignItems: "baseline", gap: s(8) }}>
              <Txt size={20} w={800} style={{ flex: 1 }}>{t("scope.league.pick")}</Txt>
              <Txt size={12} w={600} color="muted">{t("scope.league.pick_sub")}</Txt>
            </View>
            {[0, 4, 8, 12, 16].map((r) => <View key={r} style={{ flexDirection: "row", gap }}>
              {LEAGUES.slice(r, r + 4).map(([code, , country]) => {
                const on = code === scope;
                return (
                  <Pressable key={code} accessibilityRole="button" accessibilityLabel={scopeLabel(code)} onPress={() => { useSettings.getState().set({ scope: code }); setOpen(false); }}
                    style={({ pressed }) => ({ flex: 1, height: tile + s(6), borderRadius: s(14), borderWidth: BORDER, alignItems: "center", justifyContent: "center", gap: s(5), paddingHorizontal: s(2),
                      backgroundColor: on ? c.violet_soft : c.bg, borderColor: on ? c.violet_fill : pressed ? c.line_strong : c.line })}>
                    <Flag code={code} size={Math.min(40, (tile / s(1)) * 0.48)} />
                    <Txt size={11} w={700} color={on ? "violet_ink" : "fg"} center lines={1}>{countryName(country)}</Txt>
                  </Pressable>
                );
              })}
            </View>)}
          </Pressable>
        </Pressable>
      </Modal>
    </>
  );
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

// Çok oyunculuda tur süresi: 10 / 15 / 30 sn (ayarlara yazılır; Ara ve Oda kur bununla gider)
export function RoundPicker() {
  const { c, s } = useTheme();
  const round = useSettings((x) => x.round);
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: s(8) }}>
      <Eyebrow style={{ flex: 1 }}>{t("online.round")}</Eyebrow>
      {ROUNDS.map((v) => {
        const on = v === round;
        return (
          <Pressable key={v} onPress={() => useSettings.getState().set({ round: v })} style={{
            minWidth: s(64), minHeight: s(38), borderRadius: s(12), borderWidth: BORDER, alignItems: "center", justifyContent: "center",
            backgroundColor: on ? c.violet_soft : c.surface, borderColor: on ? c.violet_fill : c.line,
          }}>
            <Txt size={13} w={700} color={on ? "violet_ink" : "fg"}>{t("online.round_fmt", v)}</Txt>
          </Pressable>
        );
      })}
    </View>
  );
}

// Koşu sonu kartındaki çipler: seçili kapsam ve (varsa) dönem
export function runChips(): string[] {
  const st = useSettings.getState();
  return [scopeLabel(st.scope), ...(st.era ? [eraLabel(st.era)] : [])];
}
