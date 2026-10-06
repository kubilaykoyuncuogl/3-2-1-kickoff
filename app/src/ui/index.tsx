// Yapı taşları (game/scripts/ui.gd karşılığı). Tüm renkler paletten, tüm yazılar Sora'dan. Boyutlar ölçekle çarpılır (useTheme().s).
import React, { PropsWithChildren, ReactNode } from "react";
import { Pressable, ScrollView, StyleProp, Text, TextInput, TextInputProps, TextStyle, View, ViewStyle, Platform } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Svg, { Path } from "react-native-svg";
import { useRouter } from "expo-router";
import { FONT, Token, Weight, useTheme } from "../theme";
import { t } from "../i18n";

export const RADIUS = 14;
export const BORDER = 2;

// ---------- metin ----------
type TxtProps = PropsWithChildren<{ size?: number; w?: Weight; color?: Token; center?: boolean; style?: StyleProp<TextStyle>; lines?: number; upper?: boolean }>;
export function Txt({ children, size = 17, w = 500, color = "fg", center, style, lines, upper }: TxtProps) {
  const { c, s } = useTheme();
  const text = upper && typeof children === "string" ? children.toLocaleUpperCase("tr") : children;
  return (
    <Text numberOfLines={lines} style={[{ fontFamily: FONT[w], fontSize: s(size), lineHeight: s(size * 1.3), color: c[color], textAlign: center ? "center" : "left" }, style]}>
      {text}
    </Text>
  );
}
export function Eyebrow({ children, color = "muted", center, style }: TxtProps) {
  return <Txt size={12} w={700} color={color} center={center} style={[{ letterSpacing: 0.6 }, style]} upper>{children}</Txt>;
}
export function Wordmark() {
  const { s } = useTheme();
  return (
    <View>
      <Txt size={44} w={800} style={{ fontStyle: "italic", lineHeight: s(48) }}>3·2·1</Txt>
      <Eyebrow>KICKOFF</Eyebrow>
    </View>
  );
}

// ---------- ikonlar ----------
export function Chevron({ color = "muted", left, size = 18 }: { color?: Token; left?: boolean; size?: number }) {
  const { c, s } = useTheme();
  return (
    <Svg width={s(size)} height={s(size)} viewBox="0 0 24 24" style={left ? { transform: [{ scaleX: -1 }] } : undefined}>
      <Path d="M9 5l7 7-7 7" stroke={c[color]} strokeWidth={3} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </Svg>
  );
}
// Artık var olmayan kulüp (clubs.defunct): saat/geçmiş ikonu
export function DefunctIcon({ color = "muted", size = 15 }: { color?: Token; size?: number }) {
  const { c, s } = useTheme();
  return (
    <Svg width={s(size)} height={s(size)} viewBox="0 0 24 24">
      <Path d="M12 3a9 9 0 1 1-8.5 6M3 4v5h5M12 7v5l3 2" stroke={c[color]} strokeWidth={2.2} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </Svg>
  );
}
export function Globe({ color, size = 36 }: { color: Token; size?: number }) {
  const { c, s } = useTheme();
  return (
    <Svg width={s(size)} height={s(size)} viewBox="0 0 24 24">
      <Path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 0c-3 3-3 17 0 20m0-20c3 3 3 17 0 20M2 12h20M4 7h16M4 17h16" stroke={c[color]} strokeWidth={1.8} fill="none" strokeLinecap="round" />
    </Svg>
  );
}
export function Crown({ color, size = 36 }: { color: Token; size?: number }) {
  const { c, s } = useTheme();
  return (
    <Svg width={s(size)} height={s(size)} viewBox="0 0 24 24">
      <Path d="M3 18h18M3 18l-1-11 6 4 4-7 4 7 6-4-1 11" stroke={c[color]} strokeWidth={2} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </Svg>
  );
}

// ---------- kutular ----------
type BoxKind = "violet" | "amber" | "surface" | "";
export function Panel({ children, kind = "", style, pad = 16 }: PropsWithChildren<{ kind?: BoxKind; style?: StyleProp<ViewStyle>; pad?: number }>) {
  const { c, s } = useTheme();
  const bg = kind === "violet" ? c.violet_soft : kind === "amber" ? c.amber_soft : c.surface;
  const border = kind === "violet" || kind === "amber" ? 0 : BORDER;
  return <View style={[{ backgroundColor: bg, borderRadius: s(16), borderWidth: border, borderColor: c.line, padding: s(pad) }, style]}>{children}</View>;
}

type ChipKind = "violet" | "amber" | "ok" | "no" | "line";
export function Chip({ text, kind = "violet", style }: { text: string; kind?: ChipKind; style?: StyleProp<ViewStyle> }) {
  const { c, s } = useTheme();
  const bg = { violet: c.violet_soft, amber: c.amber_soft, ok: c.ok_soft, no: c.no_soft, line: "transparent" }[kind];
  const fg: Token = { violet: "violet_ink", amber: "amber_ink", ok: "ok", no: "no", line: "fg" }[kind] as Token;
  return (
    <View style={[{ backgroundColor: bg, borderRadius: 999, paddingHorizontal: s(10), paddingVertical: s(4), borderWidth: kind === "line" ? BORDER : 0, borderColor: c.line, alignSelf: "flex-start" }, style]}>
      <Txt size={14} w={600} color={fg} lines={1}>{text}</Txt>
    </View>
  );
}

export function Toast({ text, kind = "ok", style }: { text: string; kind?: "ok" | "no" | "muted"; style?: StyleProp<ViewStyle> }) {
  const { c, s } = useTheme();
  const bg = { ok: c.ok_soft, no: c.no_soft, muted: c.surface }[kind];
  const fg: Token = { ok: "ok", no: "no", muted: "muted" }[kind] as Token;
  return (
    <View style={[{ backgroundColor: bg, borderRadius: s(12), borderWidth: BORDER, borderColor: kind === "muted" ? c.line : c[fg], paddingHorizontal: s(16), paddingVertical: s(10) }, style]}>
      <Txt size={16} w={700} color={fg} center>{text}</Txt>
    </View>
  );
}

export function Badge({ text, kind = "muted" }: { text: string; kind?: "muted" | "violet" | "amber" | "ok" | "no" }) {
  const { c, s } = useTheme();
  const bg = { muted: c.bg, violet: c.violet_fill, amber: c.amber_fill, ok: c.ok_soft, no: c.no_soft }[kind];
  const fg: Token = { muted: "muted", violet: "violet_on", amber: "amber_on", ok: "ok", no: "no" }[kind] as Token;
  return (
    <View style={{ backgroundColor: bg, borderRadius: s(9), minWidth: s(28), height: s(28), paddingHorizontal: s(6), alignItems: "center", justifyContent: "center" }}>
      <Txt size={13} w={800} color={fg}>{text}</Txt>
    </View>
  );
}

// ---------- düğmeler ----------
type BtnKind = "violet" | "amber" | "line" | "ghost";
export function Btn({ text, kind = "violet", right, onPress, disabled, style, color }: {
  text: string; kind?: BtnKind; right?: string; onPress?: () => void; disabled?: boolean; style?: StyleProp<ViewStyle>; color?: Token;
}) {
  const { c, s } = useTheme();
  const fg: Token = color ?? ({ violet: "violet_on", amber: "amber_on", line: "fg", ghost: "muted" }[kind] as Token);
  const bg = { violet: c.violet_fill, amber: c.amber_fill, line: c.surface, ghost: "transparent" }[kind];
  const shadow = kind === "violet" ? c.violet_shade : kind === "amber" ? c.amber_shade : undefined;
  return (
    <Pressable
      onPress={onPress} disabled={disabled}
      style={({ pressed }) => [{
        backgroundColor: bg, borderRadius: s(RADIUS), minHeight: s(kind === "ghost" ? 44 : 54), paddingHorizontal: s(18),
        borderWidth: kind === "line" ? BORDER : 0, borderColor: pressed ? c.line_strong : c.line,
        flexDirection: "row", alignItems: "center", justifyContent: right ? "space-between" : "center",
        opacity: disabled ? 0.45 : 1,
        borderBottomWidth: shadow && !pressed ? 2 + (kind === "line" ? BORDER : 0) : kind === "line" ? BORDER : 0, borderBottomColor: shadow ?? c.line,
      }, style]}>
      <Txt size={16} w={kind === "ghost" ? 600 : 700} color={fg} lines={1} style={{ flexShrink: 1 }}>{text}</Txt>
      {right === ">" ? <Chevron color={fg} /> : right ? <Txt size={17} w={800} color={fg}>{right}</Txt> : null}
    </Pressable>
  );
}

// Seçenek kartı: [ön] başlık + açıklama ……… [arka]
export function OptionCard({ title, sub, lead, tail, selected, kind = "surface", height = 76, onPress }: {
  title: string; sub?: string; lead?: ReactNode; tail?: ReactNode; selected?: boolean; kind?: "surface" | "amber" | "violet"; height?: number; onPress?: () => void;
}) {
  const { c, s } = useTheme();
  const bg = selected ? c.violet_soft : { surface: c.surface, amber: c.amber_soft, violet: c.violet_soft }[kind];
  const edge = selected ? c.violet_fill : kind === "surface" ? c.line : "transparent";
  const ink: Token = selected ? "violet_ink" : ({ surface: "fg", amber: "amber_ink", violet: "violet_ink" }[kind] as Token);
  const subInk: Token = selected ? "violet_ink" : ({ surface: "muted", amber: "amber_ink", violet: "violet_ink" }[kind] as Token);
  return (
    <Pressable onPress={onPress} style={({ pressed }) => ({
      backgroundColor: bg, borderRadius: s(16), borderWidth: BORDER, borderColor: pressed && !selected ? c.line_strong : edge, minHeight: s(height),
      paddingHorizontal: s(14), paddingVertical: s(8), flexDirection: "row", alignItems: "center", gap: s(12),
    })}>
      {lead}
      <View style={{ flex: 1 }}>
        <Txt size={17} w={800} color={ink} lines={1}>{title}</Txt>
        {sub ? <Txt size={12} w={500} color={subInk} lines={2}>{sub}</Txt> : null}
      </View>
      {tail}
    </Pressable>
  );
}

// Segment seçici (Sistem / Açık / Koyu)
export function Segment<T extends string>({ values, labels, current, onChange }: { values: T[]; labels: string[]; current: T; onChange: (v: T) => void }) {
  const { c, s } = useTheme();
  return (
    <View style={{ flexDirection: "row", gap: s(4) }}>
      {values.map((v, i) => {
        const on = v === current;
        return (
          <Pressable key={v} onPress={() => onChange(v)} style={{ backgroundColor: on ? c.fg : "transparent", borderRadius: s(8), borderWidth: on ? 0 : BORDER, borderColor: c.line_strong, paddingHorizontal: s(10), minHeight: s(36), justifyContent: "center" }}>
            <Txt size={12} w={600} color={on ? "bg" : "fg"}>{labels[i]}</Txt>
          </Pressable>
        );
      })}
    </View>
  );
}

export function Toggle({ value, onChange }: { value: boolean; onChange: (v: boolean) => void }) {
  const { c, s } = useTheme();
  return (
    <Pressable onPress={() => onChange(!value)} hitSlop={8} style={{ width: s(44), height: s(26), borderRadius: 999, backgroundColor: value ? c.fg : c.line, padding: s(3), justifyContent: "center" }}>
      <View style={{ width: s(20), height: s(20), borderRadius: 999, backgroundColor: value ? c.bg : c.surface, alignSelf: value ? "flex-end" : "flex-start" }} />
    </Pressable>
  );
}

// Ayar satırı: başlık ……… kontrol, altı çizgili
export function SettingRow({ title, children, dim }: PropsWithChildren<{ title: string; dim?: boolean }>) {
  const { c, s } = useTheme();
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: s(12), paddingVertical: s(7), borderBottomWidth: BORDER, borderBottomColor: c.line, opacity: dim ? 0.55 : 1 }}>
      <Txt size={14} w={600} color={dim ? "muted" : "fg"} style={{ flex: 1 }} lines={1}>{title}</Txt>
      {children}
    </View>
  );
}

// Liste satırı: [rozet] başlık (+ alt satır) ……… [sağ]
export function Row({ index, title, sub, right, state = "", defunct }: { index: string; title: string; sub?: string; right?: ReactNode; state?: "" | "new" | "hidden"; defunct?: boolean }) {
  const { c, s } = useTheme();
  const bg = state === "new" ? c.violet_soft : state === "hidden" ? "transparent" : c.surface;
  const edge = state === "new" ? c.violet_fill : c.line;
  const ink: Token = state === "new" ? "violet_ink" : state === "hidden" ? "muted" : "fg";
  return (
    <View style={{ backgroundColor: bg, borderRadius: s(12), borderWidth: BORDER, borderColor: edge, paddingLeft: s(10), paddingRight: s(12), paddingVertical: s(8), minHeight: s(48), flexDirection: "row", alignItems: "center", gap: s(10) }}>
      <Badge text={index} kind={state === "new" ? "violet" : "muted"} />
      {defunct ? <DefunctIcon color={state === "new" ? "violet_ink" : "muted"} /> : null}
      <View style={{ flex: 1 }}>
        <Txt size={16} w={700} color={ink} lines={1}>{title}</Txt>
        {sub ? <Txt size={12} w={500} color={state === "new" ? "violet_ink" : "muted"} lines={1}>{sub}</Txt> : null}
      </View>
      {right}
    </View>
  );
}

// Başlıklı sade liste kartı: satırlar ince çizgiyle ayrılır, altta isteğe bağlı not
export function ListCard({ title, items, footer }: { title?: string; items: string[]; footer?: string }) {
  const { c, s } = useTheme();
  return (
    <View style={{ backgroundColor: c.surface, borderRadius: s(12), borderWidth: BORDER, borderColor: c.line, paddingVertical: s(6) }}>
      {title ? <Txt size={11} w={700} color="muted" upper style={{ paddingHorizontal: s(12), paddingVertical: s(4) }}>{title}</Txt> : null}
      {items.map((it, i) => (
        <View key={i} style={{ borderTopWidth: BORDER, borderTopColor: c.line, paddingHorizontal: s(12), paddingVertical: s(5), flexDirection: "row", alignItems: "center", gap: s(10) }}>
          <Badge text={String(i + 1)} />
          <Txt size={15} w={600} lines={1} style={{ flex: 1 }}>{it}</Txt>
        </View>
      ))}
      {footer ? <Txt size={13} w={600} color="muted" style={{ borderTopWidth: BORDER, borderTopColor: c.line, paddingHorizontal: s(12), paddingTop: s(6), paddingBottom: s(2) }}>{footer}</Txt> : null}
    </View>
  );
}

// İpucu karosu: küçük başlık + değer
export function Kv({ k, v, kind = "violet" }: { k: string; v: string; kind?: "violet" | "amber" }) {
  const { c, s } = useTheme();
  return (
    <View style={{ backgroundColor: c.surface, borderRadius: s(10), paddingHorizontal: s(12), paddingVertical: s(8) }}>
      <Txt size={10} w={700} color="muted" upper>{k}</Txt>
      <Txt size={17} w={800} color={kind === "violet" ? "violet_ink" : "amber_ink"} lines={1}>{v}</Txt>
    </View>
  );
}

// Yazı kutusu
export const Input = React.forwardRef<TextInput, TextInputProps & { big?: boolean; accent?: boolean }>(function Input(props, ref) {
  const { c, s } = useTheme();
  const { big, accent = true, style, ...rest } = props;
  return (
    <TextInput ref={ref}
      placeholderTextColor={c.muted} selectionColor={c.violet_fill} autoCorrect={false} autoCapitalize="none"
      style={[{
        backgroundColor: c.surface, borderRadius: s(big ? 14 : 12), borderWidth: BORDER, borderColor: accent ? c.violet_fill : c.line_strong,
        minHeight: s(big ? 64 : 56), paddingHorizontal: s(16), color: c.fg, fontFamily: FONT[big ? 800 : 600], fontSize: s(big ? 28 : 20),
        textAlign: big ? "center" : "left", ...(Platform.OS === "web" ? ({ outlineStyle: "none" } as any) : {}),
      }, style]}
      {...rest}
    />
  );
});

// Can göstergesi: dolu daireler kalan, boş daireler giden
export function Lives({ n, total = 3 }: { n: number; total?: number }) {
  const { c, s } = useTheme();
  return (
    <View style={{ flexDirection: "row", gap: s(6), justifyContent: "center" }}>
      {Array.from({ length: total }, (_, i) => {
        const alive = i < n;
        return <View key={i} style={{ width: s(16), height: s(16), borderRadius: 999, backgroundColor: alive ? (n >= 2 ? c.ok : c.no) : "transparent", borderWidth: alive ? 0 : 2, borderColor: c.line_strong }} />;
      })}
    </View>
  );
}

export function Progress({ value, max, hot }: { value: number; max: number; hot?: boolean }) {
  const { c, s } = useTheme();
  const pct = max > 0 ? Math.max(0, Math.min(1, value / max)) : 0;
  return (
    <View style={{ height: s(6), borderRadius: 999, backgroundColor: c.line, overflow: "hidden" }}>
      <View style={{ width: `${pct * 100}%`, height: "100%", backgroundColor: hot ? c.no : c.fg, borderRadius: 999 }} />
    </View>
  );
}

export function TimerBox({ text, hot }: { text: string; hot?: boolean }) {
  const { c, s } = useTheme();
  return (
    <View style={{ backgroundColor: c.surface, borderRadius: s(12), borderWidth: BORDER, borderColor: c.line, minWidth: s(56), height: s(40), alignItems: "center", justifyContent: "center", paddingHorizontal: s(10) }}>
      <Txt size={22} w={800} color={hot ? "no" : "fg"}>{text}</Txt>
    </View>
  );
}

export function Spacer({ h, flex = true }: { h?: number; flex?: boolean }) {
  const { s } = useTheme();
  return <View style={{ flex: flex ? 1 : 0, minHeight: h ? s(h) : 0 }} />;
}

export function HLine() {
  const { c } = useTheme();
  return <View style={{ height: BORDER, backgroundColor: c.line }} />;
}

// ---------- sayfa iskeleti ----------
export function Nav({ title, onBack, right }: { title: string; onBack?: () => void; right?: ReactNode }) {
  const { c, s } = useTheme();
  const router = useRouter();
  const back = onBack ?? (() => (router.canGoBack() ? router.back() : router.replace("/")));
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: s(8) }}>
      <Pressable onPress={back} hitSlop={8} style={({ pressed }) => ({ width: s(40), height: s(40), borderRadius: s(12), backgroundColor: c.surface, borderWidth: BORDER, borderColor: pressed ? c.line_strong : c.line, alignItems: "center", justifyContent: "center" })}>
        <Chevron color="fg" left />
      </Pressable>
      <Eyebrow center style={{ flex: 1 }}>{title}</Eyebrow>
      <View style={{ width: s(40), alignItems: "flex-end" }}>{right}</View>
    </View>
  );
}

// Güvenli alan + 20 px kenar + ortalanmış sütun; gap 12. scroll: içerik ekrandan uzunsa kaydırılır (varsayılan kapalı: ekranlar tek sayfaya sığar)
export function Page({ children, scroll, gap = 12, style }: PropsWithChildren<{ scroll?: boolean; gap?: number; style?: StyleProp<ViewStyle> }>) {
  const { c, s, col } = useTheme();
  const insets = useSafeAreaInsets();
  const inner = { width: col, alignSelf: "center" as const, gap: s(gap), flex: 1, paddingTop: Math.max(insets.top, s(16)), paddingBottom: Math.max(insets.bottom, s(16)) };
  if (scroll) {
    return (
      <ScrollView style={{ flex: 1, backgroundColor: c.bg }} contentContainerStyle={[{ flexGrow: 1 }]} keyboardShouldPersistTaps="handled">
        <View style={[inner, style]}>{children}</View>
      </ScrollView>
    );
  }
  return <View style={{ flex: 1, backgroundColor: c.bg }}><View style={[inner, style]}>{children}</View></View>;
}

export { t };
