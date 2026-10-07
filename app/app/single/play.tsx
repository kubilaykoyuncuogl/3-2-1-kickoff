// Klasik merdiven ve Beşte Bir: oynanış + koşu sonu.
import { useLocalSearchParams } from "expo-router";
import { runChips } from "@/ui/pickers";
import React, { useEffect, useRef, useState } from "react";
import { KeyboardAvoidingView, Platform, Pressable, View } from "react-native";
import { api } from "@/net/socket";
import { Single } from "@/store";
import { MARK, SingleHeader, SingleLoading, SingleOver, useSingle } from "@/single";
import { useTheme } from "@/theme";
import { BORDER, Chip, DefunctIcon, Eyebrow, Lives, Nav, Page, Panel, Row, Toast, Txt, t } from "@/ui";
import { Autocomplete } from "@/ui/autocomplete";

type Hist = { name: string; gained: number; bonus: number; idx: number };

export default function SinglePlay() {
  const { mode = "ladder" } = useLocalSearchParams<{ mode?: string }>();
  const { c, s, kb } = useTheme();
  const blitz = mode === "blitz";
  // Beşte Bir: sonraki soruya / koşu sonuna geçmeden önce şıklar kısa süre renklenir
  const hold = (prev: Single, next: Single) => {
    if (!blitz) return 0;
    const tp = next.last?.type;
    if (next.over) return tp === "wrong" ? MARK.quick.wrong : tp === "timeout" ? MARK.quick.timeout : 0;
    return next.idx !== prev.idx && tp === "correct" ? MARK.quick.ok : 0;
  };
  const { d, at, pending, failed, restart } = useSingle(mode, hold);
  const [clearKey, setClearKey] = useState(0);
  const [pressed, setPressed] = useState(-1);
  const prevScore = useRef(0);
  const history = useRef<Hist[]>([]);
  const [toast, setToast] = useState<{ text: string; kind: "ok" | "no" } | null>(null);
  const title = t("mode." + mode);

  useEffect(() => { setPressed(-1); }, [d?.idx]);
  useEffect(() => {
    if (!d) return;
    const last = d.last ?? {}; const gained = d.score - prevScore.current;
    if (last.type === "correct") {
      const bonus = Math.max(0, gained - 100);
      let text = blitz ? t("sp.correct_combo", gained, d.combo) : `${last.name ?? t("correct")}  +${gained}`;
      if (!blitz && bonus > 0) text += t("sp.speed_bonus", bonus);
      setToast({ text, kind: "ok" });
      if (!blitz && gained > 0 && history.current[0]?.idx !== d.idx - 1) history.current.unshift({ name: String(last.name ?? ""), gained, bonus, idx: d.idx - 1 });
    } else if (last.type === "wrong") setToast({ text: t("sp.wrong", last.name ?? ""), kind: "no" });
    else if (last.type === "timeout") setToast({ text: t("sp.timeout"), kind: "no" });
    else setToast(null);
    prevScore.current = d.score;
  }, [d]);

  if (!d) return <SingleLoading title={title} failed={failed} onRetry={restart} />;
  if (d.over) {
    const last = d.last ?? {};
    return <SingleOver mode={mode} title={blitz ? t("mode.blitz") : t("mode.ladder_short")} d={d}
      summary={blitz ? t("sp.blitz_summary", d.idx, d.best_combo) : t("sp.ladder_summary", d.idx)}
      onAgain={() => { prevScore.current = 0; history.current = []; setToast(null); restart(); }} chips={runChips()} />;
  }
  const it = d.item;
  // şık vurgusu: bekleyen (henüz gösterilmeyen) durumun sonucuna göre
  const pl = pending?.last ?? {};
  const answer = pending ? (pl.type === "correct" ? pl.option : pl.answer ?? -1) : -1;
  const wrongPick = pending && pl.type === "wrong" ? pl.option : -1;
  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <Page>
        <Nav title={title} />
        <SingleHeader d={d} at={at} hotMs={blitz ? 2000 : 5000} score={d.score} frozen={blitz && (pressed >= 0 || !!pending)}
          left={blitz ? <><Eyebrow>{t("sp.question", d.idx + 1)}</Eyebrow><Chip text={`×${d.combo.toFixed(1)}`} kind="ok" style={{ alignSelf: "center" }} /></>
            : <><Eyebrow>{t("sp.step", d.idx + 1)}</Eyebrow><Lives n={d.lives} /></>} />
        <Panel pad={kb ? 10 : 16}>
          {it.a_defunct ? <View style={{ alignItems: "center" }}><DefunctIcon color="violet_ink" /></View> : null}
          <Txt size={kb ? 18 : 22} w={800} color="violet_ink" center lines={kb ? 1 : undefined}>{it.a_name}</Txt>
          <Txt size={kb ? 11 : 14} w={700} color="muted" center>×</Txt>
          <Txt size={kb ? 18 : 22} w={800} color="amber_ink" center lines={kb ? 1 : undefined}>{it.b_name}</Txt>
          {it.b_defunct ? <View style={{ alignItems: "center" }}><DefunctIcon color="amber_ink" /></View> : null}
        </Panel>
        {toast && !(kb && !blitz) ? <Toast text={toast.text} kind={toast.kind} /> : null}
        {blitz ? (
          <View style={{ flex: 1, justifyContent: "center", gap: s(8) }}>
            {(it.options as string[]).map((o, i) => {
              const ok = i === answer; const no = i === wrongPick; const busy = pressed >= 0 || !!pending;
              return (
                <Pressable key={i} disabled={busy} onPress={() => { setPressed(i); api.singleAnswer(i); }} style={({ pressed: p }) => ({
                  minHeight: s(58), borderRadius: s(14), borderWidth: ok || no ? MARK.border : BORDER, alignItems: "center", justifyContent: "center", paddingHorizontal: s(16),
                  backgroundColor: ok ? c.ok_soft : no ? c.no_soft : c.surface, borderColor: ok ? c.ok : no ? c.no : p || pressed === i ? c.line_strong : c.line,
                })}>
                  <Txt size={16} w={700} color={ok ? "ok" : no ? "no" : "fg"} lines={1}>{o}</Txt>
                </Pressable>
              );
            })}
          </View>
        ) : (
          <>
            {/* klavye açıkken: sonuç bildirimi kutunun altında (öneri gelince çekilir), "Bildiklerin" gizli */}
            <View style={{ flex: 1, minHeight: 0 }}>
              <Autocomplete kind="player" fill clearKey={`${d.idx}-${clearKey}`} onPick={(id, name) => { api.singleGuess(id, name); setClearKey((k) => k + 1); }}
                below={kb && toast ? <Toast text={toast.text} kind={toast.kind} /> : undefined} />
            </View>
            {!kb && history.current.length > 0 && (
              <View style={{ gap: s(6) }}>
                <Eyebrow>{t("sp.history")}</Eyebrow>
                {history.current.slice(0, 4).map((h, i) => (
                  <Row key={h.idx} index={String(h.idx + 1)} title={h.name} sub={h.bonus > 0 ? t("sp.speed_short", h.bonus).trim() : undefined}
                    right={<Txt size={15} w={800} color="ok">{`+${h.gained}`}</Txt>} state={i === 0 ? "new" : ""} />
                ))}
              </View>
            )}
          </>
        )}
      </Page>
    </KeyboardAvoidingView>
  );
}
