// Hesap bölümü (Ayarlar sayfasının üstü; hesap ve ayarlar birleşti, karar 2026-10-10): misafir → hesap oluştur / var olan hesaba bağlan;
// hesaplı → cihaz ekle, çıkış, silme. (Google/Apple girişi: docs/TODO.md)
import * as Clipboard from "expo-clipboard";
import React, { useEffect, useRef, useState } from "react";
import { View } from "react-native";
import { api, connect } from "../net/socket";
import { useGame, useProfile, useSettings } from "../store";
import { useTheme } from "../theme";
import { Btn, Chip, Feedback, Field, Input, Panel, Row, Segment, Txt, t } from "./index";

type View_ = "main" | "recovery" | "have" | "code" | "confirm_delete";

export function AccountSection() {
  const { s } = useTheme();
  const st = useSettings();
  const prof = useProfile();
  const connected = useGame((g) => g.connected);
  const result = useGame((g) => g.acctResult);
  const [view, setView] = useState<View_>("main");
  const [tab, setTab] = useState<"code" | "recovery">("code");
  const [msg, setMsg] = useState<{ text: string; kind: "ok" | "no" } | null>(null);
  const [recovery, setRecovery] = useState("");
  const [linkCode, setLinkCode] = useState("");
  const [codeUntil, setCodeUntil] = useState(0);
  const [now, setNow] = useState(Date.now());
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [inCode, setInCode] = useState(""); const [inNick, setInNick] = useState(""); const [inRec, setInRec] = useState("");
  const seen = useRef(0);

  useEffect(() => { if (!connected) connect(); }, []);
  useEffect(() => { const id = setInterval(() => setNow(Date.now()), 500); return () => clearInterval(id); }, []);
  useEffect(() => {
    if (!result || result.at === seen.current) return;
    seen.current = result.at; setBusy(false);
    if (!result.ok) { setMsg({ text: t("err." + (result.error || "server")), kind: "no" }); return; }
    setMsg(null);
    switch (result.op) {
      case "create": setRecovery(String(result.recovery ?? "")); setView("recovery"); break;
      case "link_code": setLinkCode(String(result.code ?? "")); setCodeUntil(Date.now() + Number(result.ttl ?? 600) * 1000); setView("code"); break;
      case "link": case "recover": setView("main"); setMsg({ text: t("acct.done_link"), kind: "ok" }); break;
      case "logout": setView("main"); setMsg({ text: t("acct.done_logout"), kind: "ok" }); break;
      case "delete": setView("main"); setMsg({ text: t("acct.done_delete"), kind: "ok" }); break;
    }
  }, [result]);
  useEffect(() => { if (view === "code" && codeUntil && now >= codeUntil) setView("main"); }, [now]);

  const send = (op: string, a = "", b = "") => {
    if (busy) return;
    if (!useGame.getState().connected) { setMsg({ text: t("acct.need_conn"), kind: "no" }); connect(); return; }
    setBusy(true); api.acct(op, a, b);
  };
  const back = () => { setView("main"); setMsg(null); };      // kurtarma kodu görünümünde geri yok: "Kaydettim" ile kapanır
  const rem = Math.max(0, Math.floor((codeUntil - now) / 1000));

  return (
    <View style={{ gap: s(12) }}>
      <Txt role="sectionTitle">{t("acct.title")}</Txt>
      {msg ? <Feedback title={msg.text} kind={msg.kind} /> : null}
      {view === "main" && (prof.linked ? (
        <>
          <Panel kind="violet">
            <Txt role="sectionTitle" color="violet_ink">{st.nickname}</Txt>
            <View style={{ flexDirection: "row", gap: s(6), marginTop: s(6) }}>
              <Chip text={prof.verified ? t("verified") : t("acct.linked_chip")} kind="ok" />
              <Chip text={t("acct.devices", prof.devices)} kind="line" />
            </View>
            <Txt role="caption" color="violet_ink" style={{ marginTop: s(6) }}>{`Elo ${prof.elo}`}</Txt>
          </Panel>
          <Btn text={t("acct.add_device")} right=">" onPress={() => send("link_code")} />
          <Txt role="caption" color="muted">{t("acct.providers")}</Txt>
                    <Btn text={t("acct.logout")} kind="line" onPress={() => send("logout")} />
          <Btn text={t("acct.delete")} kind="ghost" color="no" onPress={() => { setView("confirm_delete"); setMsg(null); }} />
        </>
      ) : (
        <>
          <Panel>
            <Txt role="sectionTitle">{t("acct.guest_title")}</Txt>
            <Txt role="caption" color="muted" style={{ marginTop: s(4) }}>{t("acct.guest_body")}</Txt>
          </Panel>
          <Row index="@" title={st.nickname || t("guest")} sub={t("set.nick")} right={<Txt role="caption" color="muted">{`Elo ${prof.elo}`}</Txt>} />
          <Btn text={t("acct.create")} right=">" onPress={() => send("create")} />
          <Btn text={t("acct.have")} kind="soft" right=">" onPress={() => { setView("have"); setMsg(null); }} />
          <Txt role="caption" color="muted">{t("acct.providers")}</Txt>
                  </>
      ))}
      {view === "recovery" && (
        <>
          <Txt role="sectionTitle">{t("acct.recovery_title")}</Txt>
          {/* amber rakibin rengi: kurtarma kodu nötr yüzeyde, kalın yazıyla */}
          <Panel><Txt role="sectionTitle" center style={{ fontVariant: ["tabular-nums"] }}>{recovery}</Txt></Panel>
          <Txt role="caption" color="muted">{t("acct.recovery_body")}</Txt>
          <Btn text={copied ? t("copied") : t("acct.copy")} kind="line" onPress={() => { Clipboard.setStringAsync(recovery); setCopied(true); }} />
                    <Btn text={t("acct.saved")} onPress={() => { setRecovery(""); setCopied(false); setView("main"); }} />
        </>
      )}
      {view === "code" && (
        <>
          <Txt role="sectionTitle">{t("acct.code_title")}</Txt>
          <Panel kind="violet">
            <Txt role="display" color="violet_ink" center style={{ fontVariant: ["tabular-nums"] }}>{linkCode.slice(0, 3) + " " + linkCode.slice(3)}</Txt>
            <Txt role="caption" color="violet_ink" center>{`${Math.floor(rem / 60)}:${String(rem % 60).padStart(2, "0")}`}</Txt>
          </Panel>
          <Txt role="caption" color="muted">{t("acct.code_body")}</Txt>
          <Btn text={t("back")} kind="ghost" onPress={back} />
                  </>
      )}
      {view === "have" && (
        <>
          <Segment values={["code", "recovery"] as const} labels={[t("acct.tab_code"), t("acct.tab_recovery")]} current={tab} onChange={(v) => { setTab(v); setMsg(null); }} />
          {tab === "code" ? (
            <>
              <Field label={t("acct.enter_code")}>
                <Input big value={inCode} onChangeText={setInCode} placeholder="000000" maxLength={6} keyboardType="number-pad" autoFocus accessibilityLabel={t("acct.enter_code")} onSubmitEditing={() => inCode.trim().length >= 6 && send("link", inCode.trim())} />
              </Field>
              <Btn text={t("acct.link")} onPress={() => inCode.trim().length >= 6 && send("link", inCode.trim())} />
            </>
          ) : (
            <>
              <Field label={t("acct.enter_nick")}>
                <Input value={inNick} onChangeText={setInNick} maxLength={16} autoFocus accessibilityLabel={t("acct.enter_nick")} />
              </Field>
              <Field label={t("acct.enter_recovery")}>
                <Input value={inRec} onChangeText={setInRec} maxLength={60} accent={false} accessibilityLabel={t("acct.enter_recovery")} onSubmitEditing={() => inNick.trim() && inRec.trim() && send("recover", inNick.trim(), inRec.trim())} />
              </Field>
              <Btn text={t("acct.link")} onPress={() => inNick.trim() && inRec.trim() && send("recover", inNick.trim(), inRec.trim())} />
            </>
          )}
          <Btn text={t("back")} kind="ghost" onPress={back} />
                  </>
      )}
      {view === "confirm_delete" && (
        <>
          <Txt role="sectionTitle">{t("acct.delete")}</Txt>
          <Feedback title={t("acct.delete_confirm")} kind="no" />
                    <Btn text={t("acct.delete_yes")} kind="line" color="no" onPress={() => send("delete")} />
          <Btn text={t("acct.cancel")} onPress={() => setView("main")} />
        </>
      )}
    </View>
  );
}
