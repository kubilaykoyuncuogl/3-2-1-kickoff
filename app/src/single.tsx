// Tek oyunculu modların ortak parçaları: oturum kancası (başlat, yükleme zaman aşımı, gecikmeli geçiş), üst bilgi, koşu sonu.
// single_base.gd ve single_play.gd'nin ortak kısımlarının karşılığı. Sunucu otorite: soru, süre, puan hep sunucudan.
import * as Clipboard from "expo-clipboard";
import { useRouter } from "expo-router";
import React, { ReactNode, useEffect, useRef, useState } from "react";
import { Platform, Share, View } from "react-native";
import { remaining, useNow } from "./hooks";
import { getLang, has, t } from "./i18n";
import { devSingle } from "./dev/mocks";
import { api, connect } from "./net/socket";
import { Single, useGame, useSettings } from "./store";
import { useTheme } from "./theme";
import { Btn, Chip, Eyebrow, Nav, Page, Panel, Progress, Spacer, TimerBox, Toast, Txt } from "./ui";
import { ResultCard, SITE, Section, endSections, sectionsText } from "./ui/result";

const LOAD_TIMEOUT = 8000;

// `hold(prev, next)`: yeni durum gösterilmeden önce eski ekranın kaç ms daha kalacağı (şık/sonuç gösterimi için); 0 = hemen
// `starter`: oturumu başlatan istek; verilmezse standart single_start (haftanın maçı kendi isteğini gönderir)
export function useSingle(mode: string, hold?: (prev: Single, next: Single) => number, starter?: () => void) {
  const raw = useGame((g) => g.single);
  const rawAt = useGame((g) => g.singleAt);
  const [shown, setShown] = useState<{ d: Single; at: number } | null>(null);
  const [pending, setPending] = useState<Single | null>(null);     // gösterilmeyi bekleyen durum (eski ekranda sonuç vurgulanır)
  const [failed, setFailed] = useState(false);
  const shownRef = useRef<{ d: Single; at: number } | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const loadTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const start = () => {
    setFailed(false); setShown(null); shownRef.current = null; setPending(null);
    const mock = devSingle(mode);      // yalnızca geliştirme: ?mock= ile hazır durum (ekran görüntüsü)
    if (mock) {
      if (mock !== "none") {
        const m = { d: mock, at: Date.now() }; shownRef.current = m; setShown(m);
        if ((mock as any)._pending) setPending({ ...mock, ...(mock as any)._pending });
        return;
      }
      loadTimer.current = setTimeout(() => setFailed(true), 2500); return;
    }
    useGame.getState().set({ single: null });
    if (!useGame.getState().connected) connect();
    if (starter) starter(); else api.singleStart(mode);
    if (loadTimer.current) clearTimeout(loadTimer.current);
    loadTimer.current = setTimeout(() => { if (!shownRef.current) setFailed(true); }, LOAD_TIMEOUT);
  };
  useEffect(() => {
    start();
    return () => { api.singleQuit(); if (timer.current) clearTimeout(timer.current); if (loadTimer.current) clearTimeout(loadTimer.current); };
  }, []);
  useEffect(() => {
    if (!raw || raw.mode !== mode) return;
    const next = { d: raw, at: rawAt };
    const prev = shownRef.current;
    const wait = prev && hold ? hold(prev.d, raw) : 0;
    if (timer.current) { clearTimeout(timer.current); timer.current = null; }
    if (wait > 0) {
      setPending(raw);
      timer.current = setTimeout(() => { shownRef.current = next; setShown(next); setPending(null); }, wait);
    } else { shownRef.current = next; setShown(next); setPending(null); }
  }, [raw]);
  return { d: shown?.d ?? null, at: shown?.at ?? 0, pending, failed, restart: start };
}

export function SingleLoading({ title, failed, onRetry }: { title: string; failed: boolean; onRetry: () => void }) {
  const connected = useGame((g) => g.connected);
  return (
    <Page>
      <Nav title={title} />
      {failed ? (
        <>
          <Toast text={connected ? t("net.no_reply") : t("net.failed")} kind="no" />
          <Btn text={t("retry")} onPress={onRetry} />
        </>
      ) : <Txt size={14} w={600} color="muted">{t("loading")}</Txt>}
    </Page>
  );
}

// Üst bilgi: solda adım/can, sağda puan ve sayaç; altında ince süre çubuğu
export function SingleHeader({ left, score, d, at, hotMs }: { left: ReactNode; score?: number; d: Single; at: number; hotMs: number }) {
  const { s } = useTheme();
  const now = useNow(100);
  const rem = remaining(d.remaining_ms, at, now);
  const hot = rem <= hotMs;
  return (
    <>
      <View style={{ flexDirection: "row", alignItems: "center", gap: s(8) }}>
        <View style={{ flex: 1, flexDirection: "row", alignItems: "center", gap: s(8) }}>{left}</View>
        {score !== undefined ? <Chip text={t("sp.score", score)} kind="ok" style={{ alignSelf: "center" }} /> : null}
        <TimerBox text={String(Math.ceil(rem / 1000))} hot={hot} />
      </View>
      <Progress value={rem} max={Math.max(1, d.per_ms)} hot={hot} />
    </>
  );
}

// Koşu sonu: paylaşılabilir kart (skor, seni yakan soru, biliyor muydun) + Tekrar / Paylaş.
// `note` ve `extra` kartın altına sade satır olarak eklenir (ör. "Trabzonspor hanesine +640 puan").
export function SingleOver({ mode, title, d, summary, note, extra, onAgain, chips }: { mode: string; title: string; d: Single; summary: string; note?: string; extra?: string; onAgain: () => void; chips?: string[] }) {
  const router = useRouter();
  const [copied, setCopied] = useState(false);
  const before = useRef(useSettings.getState().best[mode] ?? 0).current;
  const record = d.score > before;
  useEffect(() => { if (record) { const st = useSettings.getState(); st.set({ best: { ...st.best, [mode]: d.score } }); } }, []);
  const sections: Section[] = endSections((d as any).end);
  if (!sections.some((x) => x.kind === "burn") && note) sections.unshift({ title: t("end.burn"), lines: note.split("\n"), kind: "burn" });
  if (extra) sections.push({ title: t("end.side"), lines: [extra], kind: "plain" });
  const share = async () => {
    const text = `3-2-1 Kickoff · ${title} · ${t("sp.score", d.score)}\n${summary}\n${sectionsText(sections)}\n${SITE}`;
    try {
      if (Platform.OS === "web") {
        if (typeof navigator !== "undefined" && (navigator as any).share) await (navigator as any).share({ title: "3-2-1 Kickoff", text });
        else await Clipboard.setStringAsync(text);
      } else await Share.share({ message: text });
      setCopied(true);
    } catch {}
  };
  return (
    <Page scroll>
      <Nav title={t("sp.over")} onBack={() => (router.canGoBack() ? router.back() : router.replace("/single"))} />
      <ResultCard mode={title} chips={chips} big={String(d.score)} label={record ? t("end.record") : t("end.score_best", Math.max(before, d.score))} sub={summary} record={record} sections={sections} />
      <Spacer />
      <Btn text={t("again")} kind="amber" onPress={() => { setCopied(false); onAgain(); }} />
      <Btn text={copied ? t("shared") : t("share")} kind="ghost" onPress={share} />
    </Page>
  );
}

// Ülke adı: dil paketinde karşılığı varsa o, yoksa kaynak ad
export function country(name: unknown): string {
  if (name === null || name === undefined || String(name) === "") return "";
  const k = "country." + String(name);
  return has(k) ? t(k) : String(name);
}

// Para biçimi: 23300000 → "€23,3M", 450000 → "€450K"
export function money(v: number): string {
  if (v >= 1_000_000) {
    const m = (v / 1_000_000).toFixed(1).replace(/\.0$/, "");
    return `€${getLang() === "tr" ? m.replace(".", ",") : m}M`;
  }
  if (v >= 1000) return `€${Math.floor(v / 1000)}K`;
  return `€${v}`;
}
