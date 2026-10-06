// Hesap: misafir → hesap oluştur / var olan hesaba bağlan; hesaplı → cihaz ekle, çıkış, silme. (Google/Apple girişi: docs/TODO.md)
import * as Clipboard from "expo-clipboard";
import { useRouter } from "expo-router";
import React, { useEffect, useRef, useState } from "react";
import { View } from "react-native";
import { api, connect } from "@/net/socket";
import { useGame, useProfile, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { Btn, Chip, Input, Nav, Page, Panel, Row, Segment, Spacer, Toast, Txt, t } from "@/ui";

type View_ = "main" | "recovery" | "have" | "code" | "confirm_delete";

export default function Account() {
  const router = useRouter();
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
  const back = () => {
    if (view === "have" || view === "code" || view === "confirm_delete") { setView("main"); setMsg(null); }
    else if (view === "recovery") return;      // kod kaydedilmeden çıkılmasın: "Kaydettim" ile kapanır
    else router.canGoBack() ? router.back() : router.replace("/");
  };
  const rem = Math.max(0, Math.floor((codeUntil - now) / 1000));

  return (
    <Page>
      <Nav title={t("acct.title")} onBack={back} />
      {msg ? <Toast text={msg.text} kind={msg.kind} /> : null}
      {view === "main" && (prof.linked ? (
        <>
          <Panel kind="violet">
            <Txt size={24} w={800} color="violet_ink">{st.nickname}</Txt>
            <View style={{ flexDirection: "row", gap: s(6), marginTop: s(6) }}>
              <Chip text={prof.verified ? t("verified") : t("acct.linked_chip")} kind="ok" />
              <Chip text={t("acct.devices", prof.devices)} kind="line" />
            </View>
            <Txt size={14} w={700} color="violet_ink" style={{ marginTop: s(6) }}>{`Elo ${prof.elo}`}</Txt>
          </Panel>
          <Btn text={t("acct.add_device")} right=">" onPress={() => send("link_code")} />
          <Txt size={12} color="muted">{t("acct.providers")}</Txt>
          <Spacer />
          <Btn text={t("acct.logout")} kind="line" onPress={() => send("logout")} />
          <Btn text={t("acct.delete")} kind="ghost" color="no" onPress={() => { setView("confirm_delete"); setMsg(null); }} />
        </>
      ) : (
        <>
          <Panel>
            <Txt size={18} w={800}>{t("acct.guest_title")}</Txt>
            <Txt size={13} color="muted">{t("acct.guest_body")}</Txt>
          </Panel>
          <Row index="@" title={st.nickname || t("guest")} sub={t("set.nick")} right={<Txt size={14} w={800} color="muted">{`Elo ${prof.elo}`}</Txt>} />
          <Btn text={t("acct.create")} right=">" onPress={() => send("create")} />
          <Btn text={t("acct.have")} kind="line" right=">" onPress={() => { setView("have"); setMsg(null); }} />
          <Txt size={12} color="muted">{t("acct.providers")}</Txt>
          <Spacer />
        </>
      ))}
      {view === "recovery" && (
        <>
          <Txt size={20} w={800}>{t("acct.recovery_title")}</Txt>
          <Panel kind="amber"><Txt size={22} w={800} color="amber_ink" center>{recovery}</Txt></Panel>
          <Txt size={13} color="muted">{t("acct.recovery_body")}</Txt>
          <Btn text={copied ? t("copied") : t("acct.copy")} kind="line" onPress={() => { Clipboard.setStringAsync(recovery); setCopied(true); }} />
          <Spacer />
          <Btn text={t("acct.saved")} onPress={() => { setRecovery(""); setCopied(false); setView("main"); }} />
        </>
      )}
      {view === "code" && (
        <>
          <Txt size={20} w={800}>{t("acct.code_title")}</Txt>
          <Panel kind="violet">
            <Txt size={44} w={800} color="violet_ink" center>{linkCode.slice(0, 3) + " " + linkCode.slice(3)}</Txt>
            <Txt size={14} w={700} color="violet_ink" center>{`${Math.floor(rem / 60)}:${String(rem % 60).padStart(2, "0")}`}</Txt>
          </Panel>
          <Txt size={13} color="muted">{t("acct.code_body")}</Txt>
          <Spacer />
        </>
      )}
      {view === "have" && (
        <>
          <Segment values={["code", "recovery"] as const} labels={[t("acct.tab_code"), t("acct.tab_recovery")]} current={tab} onChange={(v) => { setTab(v); setMsg(null); }} />
          {tab === "code" ? (
            <>
              <Txt size={13} w={600} color="muted">{t("acct.enter_code")}</Txt>
              <Input big value={inCode} onChangeText={setInCode} placeholder="000000" maxLength={6} keyboardType="number-pad" autoFocus onSubmitEditing={() => inCode.trim().length >= 6 && send("link", inCode.trim())} />
              <Btn text={t("acct.link")} onPress={() => inCode.trim().length >= 6 && send("link", inCode.trim())} />
            </>
          ) : (
            <>
              <Input value={inNick} onChangeText={setInNick} placeholder={t("acct.enter_nick")} maxLength={16} autoFocus style={{ fontSize: s(17) }} />
              <Input value={inRec} onChangeText={setInRec} placeholder={t("acct.enter_recovery")} maxLength={60} style={{ fontSize: s(17) }} onSubmitEditing={() => inNick.trim() && inRec.trim() && send("recover", inNick.trim(), inRec.trim())} />
              <Btn text={t("acct.link")} onPress={() => inNick.trim() && inRec.trim() && send("recover", inNick.trim(), inRec.trim())} />
            </>
          )}
          <Spacer />
        </>
      )}
      {view === "confirm_delete" && (
        <>
          <Txt size={20} w={800}>{t("acct.delete")}</Txt>
          <Toast text={t("acct.delete_confirm")} kind="no" />
          <Spacer />
          <Btn text={t("acct.delete_yes")} kind="line" color="no" onPress={() => send("delete")} />
          <Btn text={t("acct.cancel")} onPress={() => setView("main")} />
        </>
      )}
    </Page>
  );
}
