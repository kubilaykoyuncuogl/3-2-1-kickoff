// Online oyna: Elo kartı, kapsam ve dönem seçici, Ara / Oda kur / Odaya katıl. Arama ve oda bekleme de bu sayfada (mode).
// Oda 2 kişi olunca /match açılır. ?oda=<kod> ile gelince doğrudan katılma denenir (web linki ve kickoff:// şeması).
import * as Clipboard from "expo-clipboard";
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useEffect, useRef, useState } from "react";
import { Platform, Share, View } from "react-native";
import { useNow, useServerError } from "@/hooks";
import { api, connect } from "@/net/socket";
import { State, useGame, useProfile, useSettings } from "@/store";
import { useTheme } from "@/theme";
import { Btn, Chip, Eyebrow, Input, Nav, Page, Panel, Spacer, Txt, t } from "@/ui";
import { EraPicker, ScopePicker, eraLabel, scopeLabel } from "@/ui/pickers";

type Mode = "menu" | "searching" | "room" | "join";
const PROD_WEB = "https://kickoff.grandecorpo.com";

export default function Online() {
  const router = useRouter();
  const { s } = useTheme();
  const params = useLocalSearchParams<{ oda?: string }>();
  const connected = useGame((g) => g.connected);
  const room = useGame((g) => g.room);
  const profile = useProfile();
  const settings = useSettings();
  const errText = useServerError();
  const [mode, setMode] = useState<Mode>("menu");
  const [code, setCode] = useState("");
  const [since, setSince] = useState(0);
  const [copied, setCopied] = useState(false); const [shared, setShared] = useState(false);
  const now = useNow(500);
  const autoJoined = useRef(false);

  useEffect(() => { if (!connected) connect(); }, []);
  useEffect(() => {      // oda linkiyle gelindi: bağlanınca katıl
    if (params.oda && connected && !autoJoined.current) { autoJoined.current = true; api.joinRoom(String(params.oda)); }
  }, [params.oda, connected]);
  useEffect(() => {
    if (!room) return;
    if (room.left) { setMode("menu"); return; }
    if (room.searching) { setMode("searching"); return; }
    if ((room.players?.length ?? 0) >= 2 && room.state !== State.LOBBY) { router.push("/match"); return; }
    setMode("room"); setCopied(false); setShared(false);
  }, [room]);

  const back = () => {
    if (mode === "searching") { api.cancelFind(); setMode("menu"); }
    else if (mode === "room") { api.leave(); setMode("menu"); }
    else if (mode === "join") setMode("menu");
    else router.canGoBack() ? router.back() : router.replace("/");
  };
  const roomLink = (c: string) => {
    if (Platform.OS === "web" && typeof location !== "undefined") return `${location.origin}${location.pathname}?oda=${c}`;
    return `${PROD_WEB}/?oda=${c}`;
  };

  return (
    <Page scroll>
      <Nav title={t("menu.online")} onBack={back} />
      {mode === "menu" && (
        <>
          <Panel pad={16}>
            <View style={{ flexDirection: "row", alignItems: "center" }}>
              <Txt size={15} w={700} style={{ flex: 1 }}>{settings.nickname}</Txt>
              <Txt size={32} w={800}>{String(profile.elo)}</Txt>
            </View>
            <Txt size={11} color="muted">{t("online.elo_note")}</Txt>
          </Panel>
          <ScopePicker />
          <EraPicker />
          <Btn text={t("online.find")} right=">" disabled={!connected} onPress={() => { setSince(Date.now()); api.findMatch(); }} />
          <View style={{ flexDirection: "row", gap: s(8) }}>
            <Btn text={t("online.create")} kind="line" disabled={!connected} onPress={() => api.createRoom()} style={{ flex: 1 }} />
            <Btn text={t("online.join")} kind="line" disabled={!connected} onPress={() => setMode("join")} style={{ flex: 1 }} />
          </View>
          <Txt size={11} color="muted" center>{t("online.room_note")}</Txt>
          <Txt size={12} w={600} color="no" center>{errText || (connected ? "" : t("net.connecting"))}</Txt>
        </>
      )}
      {mode === "searching" && (
        <>
          <Spacer />
          <Txt size={22} w={800} center>{t("online.searching")}</Txt>
          <Txt size={13} w={600} color="muted" center>{searchLine(room, profile.elo, since, now, settings.scope, settings.era)}</Txt>
          <View style={{ flexDirection: "row", gap: s(6), justifyContent: "center" }}>
            <Chip text={profile.verified ? t("online.pool_verified") : t("online.pool_general")} kind={profile.verified ? "ok" : "line"} />
            <Chip text={scopeLabel(settings.scope)} kind="violet" />
            {settings.era ? <Chip text={eraLabel(settings.era)} kind="amber" /> : null}
          </View>
          <Spacer />
          <Btn text={t("cancel")} kind="ghost" onPress={back} />
        </>
      )}
      {mode === "room" && room && (
        <>
          <Panel kind="violet"><Eyebrow color="violet_ink">{t("you")}</Eyebrow><Txt size={20} w={800} color="violet_ink">{settings.nickname}</Txt></Panel>
          <Spacer />
          <Eyebrow center>{t("room.code")}</Eyebrow>
          <Txt size={44} w={800} center>{room.code ?? "----"}</Txt>
          <Txt size={12} color="muted" center>{roomLink(room.code ?? "")}</Txt>
          <View style={{ flexDirection: "row", gap: s(6), justifyContent: "center" }}>
            <Chip text={scopeLabel(room.scope ?? "all")} kind="violet" />
            {room.era ? <Chip text={eraLabel(room.era)} kind="amber" /> : null}
          </View>
          <View style={{ flexDirection: "row", gap: s(8), justifyContent: "center" }}>
            <Btn text={copied ? t("copied_caps") : t("room.copy")} kind="line" style={{ minWidth: s(150) }} onPress={() => { Clipboard.setStringAsync(room.code ?? ""); setCopied(true); }} />
            <Btn text={shared ? t("shared_caps") : t("room.share")} style={{ minWidth: s(150) }} onPress={async () => {
              const l = roomLink(room.code ?? "");
              try {
                if (Platform.OS === "web" && typeof navigator !== "undefined" && (navigator as any).share) await (navigator as any).share({ title: "3-2-1 Kickoff", text: t("room.share_text"), url: l });
                else if (Platform.OS === "web") await Clipboard.setStringAsync(l);
                else await Share.share({ message: t("room.share_text") + l });
                setShared(true);
              } catch {}
            }} />
          </View>
          <Spacer />
          <Panel kind="amber" style={{ opacity: 0.65 }}><Eyebrow color="amber_ink">{t("opponent")}</Eyebrow><Txt size={20} w={800} color="amber_ink">{t("room.waiting")}</Txt></Panel>
          <Txt size={12} w={600} color="no">{errText}</Txt>
        </>
      )}
      {mode === "join" && (
        <>
          <Eyebrow center>{t("room.friend_code")}</Eyebrow>
          <Input big value={code} onChangeText={setCode} placeholder="zidane" maxLength={14} autoFocus returnKeyType="go"
            onSubmitEditing={() => code.trim().length >= 3 && api.joinRoom(code.trim())} />
          <Txt size={12} w={600} color={errText ? "no" : "muted"} center>{errText || t("room.code_hint")}</Txt>
          <Btn text={t("join")} onPress={() => code.trim().length >= 3 && api.joinRoom(code.trim())} />
          <Spacer />
        </>
      )}
    </Page>
  );
}

function searchLine(room: any, elo: number, since: number, now: number, scope: string, era: number): string {
  const band = room?.band ?? 75; const e = room?.elo ?? elo; const waiting = room?.waiting ?? 1;
  const cross = Math.ceil((room?.cross_in_ms ?? 0) / 1000);
  let line = t("online.search_line", e - band, e + band, Math.floor((now - since) / 1000), waiting);
  if (scope !== "all" || era !== 0) line += "\n" + (cross > 0 ? t("online.cross_in", cross) : t("online.cross_done"));
  return line;
}
