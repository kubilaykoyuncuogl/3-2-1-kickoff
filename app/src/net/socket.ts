// Tek WebSocket: bağlan, hello gönder, mesajları store'a yaz, kopunca artan aralıkla yeniden bağlan.
// Mesaj sözleşmesi: docs/expo-plan.md §2 (server/game/engine.py ile aynı alan adları).
import Constants from "expo-constants";
import { AppState, Platform } from "react-native";
import { State, useGame, useProfile, useSettings } from "../store";
import { reportClientError, trackGameEvent } from "../telemetry";

export const PROTO = 4;
export const PROD_URL = "wss://kickoff.grandecorpo.com/ws";
const DEV_PORT = 9081;

let ws: WebSocket | null = null;
let retry = 0;
let timer: ReturnType<typeof setTimeout> | null = null;
let wanted = false;

export function serverUrl(): string {
  if (Platform.OS === "web" && typeof location !== "undefined") {
    if (location.protocol === "https:") return `wss://${location.host}/ws`;      // canlı web: sayfayı sunan adresin /ws'si (Caddy yönlendirir)
    if (!__DEV__) return `ws://${location.host}/ws`;                              // yerelde konteyner denemesi (http)
    return `ws://${location.hostname}:${DEV_PORT}/ws`;                            // expo start --web: oyun sunucusu aynı makinede 9081'de
  }
  if (!__DEV__) return PROD_URL;
  const host = (Constants.expoConfig?.hostUri ?? "127.0.0.1:8081").split(":")[0];   // Expo dev sunucusunun makinesi = oyun sunucusu
  return `ws://${host}:${DEV_PORT}/ws`;
}

export function send(msg: Record<string, unknown>) {
  if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg));
}

export function hello() {
  const s = useSettings.getState();
  send({ t: "hello", nick: s.nickname, device: s.device_id, proto: PROTO });
}

export function connect() {
  wanted = true;
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;
  if (timer) { clearTimeout(timer); timer = null; }
  const url = serverUrl();
  try { ws = new WebSocket(url); } catch { schedule(); return; }
  const sock = ws;
  sock.onopen = () => { retry = 0; useGame.getState().set({ connected: true }); hello(); send({ t: "weekly_info" }); };
  sock.onmessage = (ev) => {
    let message: any;
    try { message = JSON.parse(String(ev.data)); } catch { return; }
    try { handle(message); } catch (error) { reportClientError(error, "socket.message"); }
  };
  sock.onerror = () => {};
  sock.onclose = () => {
    if (ws !== sock) return;
    ws = null; useGame.getState().set({ connected: false });
    if (wanted) schedule();
  };
}

export function disconnect() {
  wanted = false;
  if (timer) { clearTimeout(timer); timer = null; }
  ws?.close(); ws = null;
}

function schedule() {
  const delay = Math.min(10000, 1000 * 2 ** retry++);
  timer = setTimeout(connect, delay);
}

// Uygulama öne gelince hemen yeniden dene (arka planda bağlantı kopmuş olabilir)
AppState.addEventListener("change", (st) => { if (st === "active" && wanted) { retry = 0; connect(); } });

function handle(m: any) {
  const g = useGame.getState();
  switch (m.t) {
    case "welcome": g.set({ pid: m.pid }); break;
    case "room_state":
      if (m.d.state === State.PICK_TEAMS &&
          (!g.room || g.room.code !== m.d.code || g.room.state === State.LOBBY || g.room.state === State.GAME_OVER)) {
        trackGameEvent("match_start");
      }
      if (m.d.state === State.GAME_OVER &&
          (g.room?.code !== m.d.code || g.room?.state !== State.GAME_OVER)) trackGameEvent("match_complete");
      g.set({ room: m.d, roomAt: Date.now() }); break;
    case "single_state":
      if (m.d.over && !g.single?.over) trackGameEvent("single_complete");
      g.set({ single: m.d, singleAt: Date.now() }); break;
    case "suggest_result": g.set({ suggestions: { kind: m.kind, q: m.q, list: m.list } }); break;
    case "profile_state":
      useProfile.getState().apply(m.d);
      if (m.d.proto !== undefined && m.d.proto !== PROTO) g.set({ updateNeeded: true });
      break;
    case "weekly_state": g.set({ weekly: m.d ?? null }); break;
    case "acct_result": g.set({ acctResult: { ...m.d, at: Date.now() } }); break;
    case "err":
      if (m.key === "err.proto") g.set({ updateNeeded: true });
      g.set({ error: { key: m.key, at: Date.now() } });
      break;
  }
}

// ---------- istemci yardımcıları (Godot c_* karşılığı) ----------
export const api = {
  createRoom: () => { const s = useSettings.getState(); trackGameEvent("room_create"); send({ t: "create_room", scope: s.scope, era: s.era, round: s.round }); },
  joinRoom: (code: string) => { trackGameEvent("room_join"); send({ t: "join_room", code }); },
  findMatch: () => { const s = useSettings.getState(); trackGameEvent("match_search"); send({ t: "find_match", scope: s.scope, era: s.era, round: s.round }); },
  cancelFind: () => send({ t: "cancel_find" }),
  leave: () => send({ t: "leave_room" }),
  pickTeam: (team_id: number, team_name: string) => send({ t: "pick_team", team_id, team_name }),
  ready: () => send({ t: "set_ready" }),
  guess: (player_id: number, name: string) => send({ t: "guess", player_id, name }),
  suggest: (kind: "team" | "player", q: string) => send({ t: "suggest", kind, q }),
  rematch: () => { trackGameEvent("rematch_request"); send({ t: "rematch" }); },
  singleStart: (mode: string) => { const s = useSettings.getState(); trackGameEvent("single_start"); send({ t: "single_start", mode, scope: s.scope, era: s.era }); },
  singleGuess: (player_id: number, name: string) => send({ t: "single_guess", player_id, name }),
  singleAnswer: (option: number) => send({ t: "single_answer", option }),
  singleTeam: (team_id: number, name: string) => send({ t: "single_team", team_id, name }),
  singleQuit: () => send({ t: "single_quit" }),
  acct: (op: string, a = "", b = "") => send({ t: "acct", op, a, b }),
  weeklyInfo: () => send({ t: "weekly_info" }),
  weeklyStart: (side: "a" | "b") => send({ t: "weekly_start", side }),
};
