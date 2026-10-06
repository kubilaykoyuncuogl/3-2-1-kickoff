// Maç ekranı: PICK_TEAMS / COUNTDOWN / REVEAL / ROUND / ROUND_END (+ ortak oyuncu yok) / GAME_OVER. Sen hep üstte, rakip altta.
// Durum değişince içerik sönüp yenisi belirir; uyarılar (takım alınmış, kapsam dışı) ortada kart; rakip ayrılınca 5 sn sonra çıkılır.
import { useRouter } from "expo-router";
import React, { useEffect, useRef, useState } from "react";
import { Animated, Pressable, ScrollView, View } from "react-native";
import { remaining, useNow } from "@/hooks";
import { api } from "@/net/socket";
import { Player, Room, State, useGame, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { Btn, Chip, Eyebrow, ListCard, Nav, Page, Panel, Progress, Spacer, TimerBox, Toast, Txt, t } from "@/ui";
import { Autocomplete } from "@/ui/autocomplete";
import { eraLabel, scopeLabel } from "@/ui/pickers";
import { ResultCard, Section } from "@/ui/result";

const PICK_MS = 45000, QUICK_AT_MS = 20000, RECONNECT_MS = 10000, RETURN_MS = 5000, NOTICE_MS = 3000;

export default function Match() {
  const router = useRouter();
  const { c, s } = useTheme();
  const reduce = useSettings((x) => x.reduce_motion);
  const room = useGame((g) => g.room);
  const roomAt = useGame((g) => g.roomAt);
  const me = useGame((g) => g.pid);
  const err = useGame((g) => g.error);
  const now = useNow(100);
  const [notice, setNotice] = useState<{ text: string; at: number } | null>(null);
  const [returnAt, setReturnAt] = useState(0);
  const awaySince = useRef(0);
  const fade = useRef(new Animated.Value(1)).current;
  const lastState = useRef(-1);
  const left = useRef(false);

  // oda yoksa / çıkıldıysa geri
  useEffect(() => {
    if (!room || room.left || (room.players?.length ?? 0) < 1) { if (!left.current) { left.current = true; router.canGoBack() ? router.back() : router.replace("/online"); } }
  }, [room]);
  // durum değişince yumuşak geçiş
  useEffect(() => {
    if (!room) return;
    if (lastState.current !== -1 && lastState.current !== room.state && !reduce) {
      fade.setValue(0); Animated.timing(fade, { toValue: 1, duration: 220, useNativeDriver: true }).start();
    }
    lastState.current = room.state;
  }, [room?.state]);
  // takım seçimindeki uyarılar: ortada kart, 3 sn
  useEffect(() => {
    if (err && room?.state === State.PICK_TEAMS && Date.now() - err.at < 1000) setNotice({ text: t(err.key), at: err.at });
  }, [err]);
  useEffect(() => { if (notice && now - notice.at > NOTICE_MS) setNotice(null); }, [now]);
  // rakibin kopması
  const opp = opponentOf(room, me);
  if (opp?.away) { if (!awaySince.current) awaySince.current = Date.now(); } else awaySince.current = 0;
  // rakip ayrıldı: geri sayım, sonra çık
  useEffect(() => {
    if (room?.state === State.GAME_OVER && room.last?.type === "left") { if (!returnAt) setReturnAt(Date.now() + RETURN_MS); }
    else if (returnAt) setReturnAt(0);
  }, [room?.state, room?.last?.type]);
  useEffect(() => {
    if (returnAt && now >= returnAt && !left.current) { left.current = true; api.leave(); router.canGoBack() ? router.back() : router.replace("/online"); }
  }, [now]);

  if (!room || !room.players) return <Page />;
  const mine = meOf(room, me);
  const rem = remaining(room.phase_ms, roomAt, now);
  const awaySecs = Math.ceil(Math.max(0, RECONNECT_MS - (now - awaySince.current)) / 1000);

  return (
    <Page>
      <Animated.View style={{ flex: 1, gap: s(12), opacity: fade }}>
        {room.state === State.PICK_TEAMS && <Pick room={room} mine={mine} opp={opp} rem={rem} awaySecs={awaySecs} />}
        {room.state === State.COUNTDOWN && <Countdown room={room} mine={mine} opp={opp} rem={rem} />}
        {room.state === State.REVEAL && <Reveal mine={mine} opp={opp} />}
        {room.state === State.ROUND && <Round room={room} mine={mine} opp={opp} rem={rem} me={me} awaySecs={awaySecs} />}
        {room.state === State.ROUND_END && (room.last?.no_common ? <NoCommon room={room} mine={mine} opp={opp} rem={rem} /> : <RoundEnd room={room} mine={mine} opp={opp} me={me} />)}
        {room.state === State.GAME_OVER && <Over room={room} mine={mine} opp={opp} me={me} returnAt={returnAt} now={now} />}
      </Animated.View>
      {notice && (
        <Pressable onPress={() => setNotice(null)} style={{ position: "absolute", inset: 0, backgroundColor: c.bg + "D0", alignItems: "center", justifyContent: "center", padding: s(20) }}>
          <View style={{ width: s(300), backgroundColor: c.surface, borderRadius: s(18), borderWidth: 2, borderColor: c.no, padding: s(22), gap: s(10) }}>
            <Txt size={21} w={800} center>{notice.text}</Txt>
            <Txt size={13} color="muted" center>{t("match.back_to_pick")}</Txt>
            <Progress value={Math.max(0, NOTICE_MS - (now - notice.at))} max={NOTICE_MS} hot />
          </View>
        </Pressable>
      )}
    </Page>
  );
}

function meOf(r: Room, me: number): Player | undefined { return r.players?.find((p) => p.pid === (r.me ?? me)); }
function opponentOf(r: Room | null, me: number): Player | undefined { return r?.players?.find((p) => p.pid !== (r.me ?? me)); }

function ScoreRow({ mine, opp }: { mine?: Player; opp?: Player }) {
  const { s } = useTheme();
  return (
    <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "center", gap: s(8) }}>
      <Chip text={mine?.nick ?? ""} kind="violet" />
      <Txt size={40} w={800} style={{ lineHeight: s(46) }}>{`${mine?.score ?? 0} : ${opp?.score ?? 0}`}</Txt>
      <Chip text={opp?.nick ?? ""} kind="amber" />
    </View>
  );
}

function Side({ p, side, children, flex, ratio }: { p?: Player; side: "violet" | "amber"; children?: React.ReactNode; flex?: boolean; ratio?: number }) {
  const ink = side === "violet" ? "violet_ink" : "amber_ink";
  // içerik (cevap + liste) varsa panel en az içeriği kadar yer alır ve büzülmez; boş taraf kalan yeri paylaşır
  const grow = children ? { flexGrow: ratio ?? 1, flexShrink: 0, flexBasis: "auto" as const } : { flex: ratio ?? 1, minHeight: 0 };
  return (
    <Panel kind={side} style={flex ? grow : undefined}>
      <Eyebrow color={ink}>{(side === "violet" ? t("you") : t("opponent")) + " · " + (p?.nick ?? "")}</Eyebrow>
      <Txt size={26} w={800} color={ink} lines={2}>{p?.team_name || "—"}</Txt>
      {children}
    </Panel>
  );
}

// ---------- takım seçimi ----------
function Pick({ room, mine, opp, rem, awaySecs }: { room: Room; mine?: Player; opp?: Player; rem: number; awaySecs: number }) {
  const { s } = useTheme();
  const router = useRouter();
  const secs = Math.ceil(rem / 1000);
  const showQuick = rem <= PICK_MS - QUICK_AT_MS && !mine?.team && (room.quick_picks?.length ?? 0) > 0;
  const oppText = opp?.away ? t("match.away_short", awaySecs) : opp?.ready ? t("match.opp_ready") : opp?.picked ? t("match.opp_picked") : t("match.opp_thinking");
  return (
    <>
      <Nav title={t("match.pick_title", scopeLabel(room.scope ?? "all"), room.code ?? "")} onBack={() => { api.leave(); router.canGoBack() ? router.back() : router.replace("/online"); }}
        right={<Txt size={20} w={800} color={rem <= 10000 ? "no" : "muted"}>{String(secs)}</Txt>} />
      <ScoreRow mine={mine} opp={opp} />
      <Panel kind="violet" style={{ flex: 1, gap: s(8) }}>
        <Eyebrow color="violet_ink">{t("you") + " · " + (mine?.nick ?? "")}</Eyebrow>
        {mine?.ready ? (
          <>
            <Txt size={26} w={800} color="violet_ink">{mine.team_name}</Txt>
            <Chip text={t("ready")} kind="ok" />
            <Txt size={12} color="violet_ink">{t("match.waiting_opp")}</Txt>
          </>
        ) : mine?.team ? (
          <>
            <Txt size={26} w={800} color="violet_ink">{mine.team_name}</Txt>
            <View style={{ flexDirection: "row", gap: s(8) }}>
              <Btn text={t("change")} kind="line" style={{ flex: 1 }} onPress={() => api.pickTeam(0, "")} />
              <Btn text={t("ready_btn")} style={{ flex: 1 }} onPress={() => api.ready()} />
            </View>
          </>
        ) : (
          <>
            <Autocomplete kind="team" onPick={(id, name) => api.pickTeam(id, name)} />
            {showQuick && (
              <View style={{ gap: s(6) }}>
                <Txt size={13} w={600} color="violet_ink">{t("match.quick")}</Txt>
                <View style={{ flexDirection: "row", flexWrap: "wrap", gap: s(6) }}>
                  {room.quick_picks!.map((q) => <Btn key={q.id} text={q.name} kind="line" style={{ minHeight: s(40) }} onPress={() => api.pickTeam(q.id, q.name)} />)}
                </View>
              </View>
            )}
          </>
        )}
      </Panel>
      <Panel kind="amber">
        <Eyebrow color="amber_ink">{t("opponent") + " · " + (opp?.nick ?? "?")}</Eyebrow>
        <Txt size={24} w={800} color="amber_ink">{oppText}</Txt>
      </Panel>
    </>
  );
}

function Countdown({ mine, opp, rem }: { room: Room; mine?: Player; opp?: Player; rem: number }) {
  const { s } = useTheme();
  return (
    <>
      <Spacer />
      <Panel kind="violet"><Eyebrow color="violet_ink">{t("you") + " · " + (mine?.nick ?? "")}</Eyebrow><Txt size={22} w={800} color="violet_ink">{t("ready")}</Txt></Panel>
      <Txt size={140} w={800} center style={{ fontStyle: "italic", lineHeight: s(150) }}>{String(Math.max(1, Math.ceil(rem / 1000)))}</Txt>
      <Panel kind="amber"><Eyebrow color="amber_ink">{t("opponent") + " · " + (opp?.nick ?? "")}</Eyebrow><Txt size={22} w={800} color="amber_ink">{t("ready")}</Txt></Panel>
      <Spacer />
    </>
  );
}

function Reveal({ mine, opp }: { mine?: Player; opp?: Player }) {
  return (
    <>
      <Spacer />
      <Panel kind="violet"><Eyebrow color="violet_ink">{t("you") + " · " + (mine?.nick ?? "")}</Eyebrow><Txt size={34} w={800} color="violet_ink">{mine?.team_name ?? ""}</Txt></Panel>
      <Txt size={56} w={800} color="muted" center>×</Txt>
      <Panel kind="amber"><Eyebrow color="amber_ink">{t("opponent") + " · " + (opp?.nick ?? "")}</Eyebrow><Txt size={34} w={800} color="amber_ink">{opp?.team_name ?? ""}</Txt></Panel>
      <Spacer />
    </>
  );
}

// ---------- tur ----------
function Round({ room, mine, opp, rem, me, awaySecs }: { room: Room; mine?: Player; opp?: Player; rem: number; me: number; awaySecs: number }) {
  const { s } = useTheme();
  const hot = rem <= 5000;
  const pen = mine?.penalty_ms ?? 0;
  const penaltyAt = useRef(0); const penAt = useGame((g) => g.roomAt);
  const penRem = Math.max(0, pen - (Date.now() - penAt));
  const last = room.last ?? {};
  const [clearKey, setClearKey] = useState(0);
  let toast: { text: string; kind: "no" | "muted" } | null = null;
  if (opp?.away) toast = { text: t("match.opp_away", awaySecs), kind: "muted" };
  else if (last.type === "wrong") toast = last.pid === (room.me ?? me) ? { text: t("match.wrong_me", last.name), kind: "no" } : { text: t("match.wrong_opp", last.name, Math.ceil((opp?.penalty_ms ?? 0) / 1000)), kind: "muted" };
  void penaltyAt;
  return (
    <>
      <View style={{ flexDirection: "row", alignItems: "center", gap: s(8) }}>
        <View style={{ flex: 1, gap: s(4) }}>
          <Chip text={mine?.team_name ?? ""} kind="violet" style={{ maxWidth: s(250) }} />
          <Chip text={opp?.team_name ?? ""} kind="amber" style={{ maxWidth: s(250) }} />
        </View>
        <TimerBox text={String(Math.ceil(rem / 1000))} hot={hot} />
      </View>
      <Progress value={rem} max={room.round_ms ?? 15000} hot={hot} />
      <View style={{ flex: 1 }}>
        <Autocomplete kind="player" locked={penRem > 0} lockedText={t("locked_fmt", Math.ceil(penRem / 1000))} clearKey={clearKey}
          onPick={(id, name) => { api.guess(id, name); setClearKey((k) => k + 1); }} />
      </View>
      {toast ? <Toast text={toast.text} kind={toast.kind} /> : null}
      <ScoreRow mine={mine} opp={opp} />
    </>
  );
}

function RoundEnd({ room, mine, opp, me }: { room: Room; mine?: Player; opp?: Player; me: number }) {
  const { s } = useTheme();
  const last = room.last ?? {}; const my = room.me ?? me; const tp = last.type;
  const iWon = (tp === "correct" && last.pid === my) || (tp === "pick_timeout" && last.pid !== my);
  const theyWon = (tp === "correct" && last.pid !== my) || (tp === "pick_timeout" && last.pid === my);
  const ans = room.answers ?? []; const total = room.answers_total ?? 0; const answerName = String(last.name ?? "");
  const others = ans.filter((n) => n !== answerName).slice(0, 5);
  const rest = Math.max(0, total - others.length - (answerName ? 1 : 0));
  const sub = (
    <View style={{ gap: s(8), marginTop: s(8) }}>
      {tp === "pick_timeout" ? <Toast text={iWon ? t("match.pick_to_win") : t("match.pick_to_lose")} kind={iWon ? "ok" : "no"} />
        : tp === "correct" ? <Toast text={`${answerName}  +1`} kind={iWon ? "ok" : "no"} />
        : <Toast text={last.no_common ? t("match.no_common") : t("match.nobody")} kind="no" />}
      {others.length > 0 && <ListCard title={(tp === "correct" ? t("match.others") : t("match.possible")).trim().replace(/:$/, "")} items={others}
        footer={rest > 0 ? t("match.more", rest).trim().replace(/^…/, "").trim() : undefined} />}
    </View>
  );
  const topW = iWon ? 1.6 : theyWon ? 0.6 : 1; const botW = theyWon ? 1.6 : iWon ? 0.6 : 1;
  return (
    <>
      <Side p={mine} side="violet" flex ratio={topW}>{iWon || !theyWon ? sub : null}</Side>
      <ScoreRow mine={mine} opp={opp} />
      <Side p={opp} side="amber" flex ratio={botW}>{theyWon ? sub : null}</Side>
    </>
  );
}

// Ortak oyuncusu olmayan çift: iki takım, ortada uyarı kartı, süre çubuğu; sunucu 3 sn sonra seçime döndürür
function NoCommon({ mine, opp, rem }: { room: Room; mine?: Player; opp?: Player; rem: number }) {
  const { c, s } = useTheme();
  return (
    <>
      <ScoreRow mine={mine} opp={opp} />
      <Spacer />
      <Panel kind="violet"><Txt size={24} w={800} color="violet_ink" center>{mine?.team_name || "—"}</Txt></Panel>
      <Txt size={34} w={800} color="muted" center>×</Txt>
      <Panel kind="amber"><Txt size={24} w={800} color="amber_ink" center>{opp?.team_name || "—"}</Txt></Panel>
      <View style={{ height: s(10) }} />
      <View style={{ backgroundColor: c.surface, borderRadius: s(18), borderWidth: 2, borderColor: c.no, padding: s(20), gap: s(10) }}>
        <Txt size={21} w={800} center>{t("match.no_common")}</Txt>
        <Txt size={13} color="muted" center>{t("match.back_to_pick")}</Txt>
        <Progress value={rem} max={NOTICE_MS} hot />
      </View>
      <Spacer />
    </>
  );
}

function Over({ room, mine, opp, me, returnAt, now }: { room: Room; mine?: Player; opp?: Player; me: number; returnAt: number; now: number }) {
  const router = useRouter();
  const elo = useSettings((x) => x.elo);
  const last = room.last ?? {}; const my = room.me ?? me; const winner = room.winner ?? 0;
  let title = winner === 0 ? t("draw") : winner === my ? t("won") : t("lost");
  if (last.type === "left") title = t("match.opp_left");
  const de = mine?.elo_delta ?? 0;
  // tur tur özet (sunucudan izleyene göre gelir) ve maçı bitiren çiftin diğer cevapları
  const hist: any[] = (room as any).history ?? [];
  const rounds = hist.slice(-6).map((h) => {
    const pair = `${h.mine || "—"} × ${h.theirs || "—"}`;
    const res = h.no_common ? t("end.round_nocommon") : h.type === "pick_timeout" ? t("end.round_pick") : h.type === "correct" ? (h.by === "me" ? t("end.round_me", h.name) : t("end.round_opp", h.name)) : t("end.round_none");
    return `${pair}  ·  ${res}`;
  });
  const answerName = last.type === "correct" ? String(last.name ?? "") : "";
  const others = last.type === "left" ? [] : (room.answers ?? []).filter((n) => n !== answerName).slice(0, 4);
  const lastRound = hist[hist.length - 1];
  const sections: Section[] = [];
  if (rounds.length) sections.push({ title: t("end.rounds"), lines: rounds, kind: "plain" });
  if (others.length && lastRound) sections.push({ title: t("end.fact"), lines: [t("fact.pair_players", lastRound.mine, lastRound.theirs, room.answers_total ?? others.length, [answerName, ...others].filter(Boolean).slice(0, 4).join(", ") + ((room.answers_total ?? 0) > 4 ? "…" : ""))], kind: "fact" });
  const leave = () => { api.leave(); router.canGoBack() ? router.back() : router.replace("/online"); };
  const chips = [scopeLabel(room.scope ?? "all"), ...(room.era ? [eraLabel(room.era)] : []), t("online.round_fmt", Math.round((room.round_ms ?? 15000) / 1000))];
  return (
    <ScrollView style={{ flex: 1 }} contentContainerStyle={{ flexGrow: 1, gap: 12 }} keyboardShouldPersistTaps="handled">
      <ResultCard mode={t("menu.online")} chips={chips} big={`${mine?.score ?? 0} : ${opp?.score ?? 0}`} label={title} record={winner === my}
        sub={`${mine?.nick ?? ""} – ${opp?.nick ?? ""}` + (room.ranked && de !== 0 ? `  ·  Elo ${elo} (${de > 0 ? "+" : ""}${de})` : "")} sections={sections} />
      <View style={{ flex: 1 }} />
      {last.type === "left" ? (
        <Txt size={14} w={600} color="muted" center>{t("match.returning", Math.ceil(Math.max(0, returnAt - now) / 1000))}</Txt>
      ) : (
        <>
          <Txt size={13} w={700} color="amber_ink" center>{opp?.rematch ? `${opp?.nick ?? ""}: ${t("match.wants_rematch")}` : ""}</Txt>
          <Btn text={t("rematch") + (mine?.rematch ? t("match.waiting_paren") : "")} disabled={!!mine?.rematch} onPress={() => api.rematch()} />
        </>
      )}
      <Btn text={t("leave")} kind="ghost" onPress={leave} />
    </ScrollView>
  );
}
