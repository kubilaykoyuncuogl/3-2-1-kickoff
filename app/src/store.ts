// Uygulama durumu (zustand). Üç dilim: kalıcı ayarlar, sunucudan gelen profil, canlı oyun durumu (oda / tek oyunculu / öneriler).
// Godot'daki App (ayarlar) + Game (sinyaller) karşılığı. Sunucu sözlükleri olduğu gibi saklanır (alan adları game.gd ile aynı).
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Platform } from "react-native";
import { create } from "zustand";
import { setLang } from "./i18n";
import { applyMock } from "./dev/mocks";      // döngüsel içe aktarma: iki taraf da birbirini yalnızca fonksiyon içinde kullanır

export const SCOPES = ["all", "top", "big5"] as const;      // genel kapsamlar
// Tek lig kapsamı: değer lig kodu (server/game/consts.py LEAGUES ile aynı sıra). Adlar özel isim, çevrilmez.
export const LEAGUES: [string, string][] = [["GB1", "Premier League"], ["ES1", "La Liga"], ["IT1", "Serie A"], ["L1", "Bundesliga"], ["FR1", "Ligue 1"],
  ["TR1", "Süper Lig"], ["NL1", "Eredivisie"], ["PO1", "Liga Portugal"]];
export const leagueName = (code: string) => LEAGUES.find(([c]) => c === code)?.[1] ?? "";
export type Scope = string;
export const ROUNDS = [10, 15, 30];      // çok oyunculuda tur süresi seçenekleri (sn); sunucudaki ROUND_CHOICES ile aynı
export const ERAS: [string, number][] = [["80", 1], ["90", 2], ["00", 4], ["10", 8], ["20", 16]];
export type ThemeMode = "system" | "light" | "dark";

export type Settings = {
  nickname: string; theme_mode: ThemeMode; lang: string; sound: boolean; haptics: boolean; reduce_motion: boolean; learn: boolean; learn_off: string[]; round: number;
  scope: Scope; era: number; best: Record<string, number>; elo: number; device_id: string;
};
const DEFAULTS: Settings = { nickname: "", theme_mode: "system", lang: "tr", sound: true, haptics: true, reduce_motion: false, learn: true, learn_off: [], round: 15,
  scope: "all", era: 0, best: {}, elo: 1000, device_id: "" };

type SettingsStore = Settings & {
  loaded: boolean;
  set: (patch: Partial<Settings>) => void;
  eraToggle: (bit: number) => void;
  load: () => Promise<void>;
};

const KEY = "kickoff.settings";
let saveTimer: ReturnType<typeof setTimeout> | null = null;
function persist(s: Settings) {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(() => { AsyncStorage.setItem(KEY, JSON.stringify(s)).catch(() => {}); }, 150);
}
function pick(s: SettingsStore): Settings {
  const { nickname, theme_mode, lang, sound, haptics, reduce_motion, learn, learn_off, round, scope, era, best, elo, device_id } = s;
  return { nickname, theme_mode, lang, sound, haptics, reduce_motion, learn, learn_off, round, scope, era, best, elo, device_id };
}
function randomId(): string {
  let out = "";
  for (let i = 0; i < 32; i++) out += Math.floor(Math.random() * 16).toString(16);
  return out;
}

export const useSettings = create<SettingsStore>((set, get) => ({
  ...DEFAULTS, loaded: false,
  set: (patch) => { set(patch); if (patch.lang) setLang(patch.lang); persist(pick(get())); },
  // Dönem düğmesi: Tümü tek başına; Tümü seçiliyken bir on yıla basınca yalnız o; sonra aç/kapa; hiçbiri kalmazsa Tümü
  eraToggle: (bit) => { const e = get().era; get().set({ era: bit === 0 ? 0 : e === 0 ? bit : e ^ bit }); },
  load: async () => {
    try {
      const raw = await AsyncStorage.getItem(KEY);
      if (raw) { const v = JSON.parse(raw); set({ ...DEFAULTS, ...v }); }
    } catch {}
    let dev = get().device_id;
    if (!dev) {      // cihaz kimliği: hesabın anahtarı, ekranda gösterilmez; yerelde (web'de localStorage, telefonda SecureStore) kalır
      dev = await loadDeviceId();
      if (!dev) { dev = randomId(); await saveDeviceId(dev); }
      set({ device_id: dev });
    }
    if (__DEV__ && Platform.OS === "web" && typeof location !== "undefined") {   // ekran görüntüsü aracı: ?nick=…&theme=dark&lang=en&scope=TR1&era=6 (yalnızca geliştirme)
      const q = new URLSearchParams(location.search);
      const patch: Partial<Settings> = {};
      if (q.get("nick")) patch.nickname = q.get("nick")!;
      if (q.get("theme")) patch.theme_mode = q.get("theme") as ThemeMode;
      if (q.get("lang")) patch.lang = q.get("lang")!;
      if (q.get("scope")) patch.scope = q.get("scope")!;
      if (q.get("era")) patch.era = Number(q.get("era")) & 31;
      if (q.get("learn") === "0") patch.learn = false;
      if (q.get("learn") === "1") { patch.learn = true; patch.learn_off = []; }
      if (q.get("round")) patch.round = Number(q.get("round"));
      if (q.get("best")) { const b = Number(q.get("best")); patch.best = { ladder: b, blitz: b, career: b, chain: b, versus: b, weekly: b }; }
      const mock = q.get("mock");      // hazır ekran durumları (src/dev/mocks.ts; tools/all_shots.py)
      if (mock) applyMock(mock);      // eşzamanlı: ekranlar ilk çizimde hazır durumu görsün
      set(patch);
    }
    setLang(get().lang);
    set({ loaded: true }); persist(pick(get()));
  },
}));

async function loadDeviceId(): Promise<string> {
  try {
    if (Platform.OS === "web") return (await AsyncStorage.getItem("kickoff.device")) ?? "";
    const SecureStore = await import("expo-secure-store");
    return (await SecureStore.getItemAsync("kickoff.device")) ?? "";
  } catch { return ""; }
}
async function saveDeviceId(v: string) {
  try {
    if (Platform.OS === "web") { await AsyncStorage.setItem("kickoff.device", v); return; }
    const SecureStore = await import("expo-secure-store");
    await SecureStore.setItemAsync("kickoff.device", v);
  } catch {}
}

// ---------- sunucudan gelen profil ----------
export type Profile = { elo: number; games: number; nick: string; linked: boolean; verified: boolean; bests: Record<string, number>; devices: number; proto: number };
type ProfileStore = { elo: number; linked: boolean; verified: boolean; devices: number; apply: (p: Profile) => void };
export const useProfile = create<ProfileStore>((set) => ({
  elo: 1000, linked: false, verified: false, devices: 1,
  apply: (p) => {
    set({ elo: p.elo, linked: p.linked, verified: p.verified, devices: p.devices });
    const st = useSettings.getState();
    const best = { ...st.best };
    for (const m of Object.keys(p.bests ?? {})) best[m] = Math.max(best[m] ?? 0, p.bests[m]);
    const patch: Partial<Settings> = { elo: p.elo, best };
    if (p.linked && p.nick) patch.nickname = p.nick;      // hesabın adı cihazdakinin önüne geçer
    st.set(patch);
  },
}));

// ---------- canlı oyun durumu ----------
export type Player = { pid: number; nick: string; elo: number; team: number; team_name: string; picked: boolean; ready: boolean; score: number;
  penalty_ms: number; rematch: boolean; elo_delta: number; away: boolean };
export type Room = { me?: number; code?: string; ranked?: boolean; scope?: Scope; era?: number; round_ms?: number; state: number; players?: Player[]; phase_ms?: number;
  last?: Record<string, any>; answers?: string[]; answers_total?: number; winner?: number; used_teams?: number[]; quick_picks?: { id: number; name: string }[];
  searching?: boolean; left?: boolean; band?: number; elo?: number; waiting?: number; cross_in_ms?: number };
export type Single = { mode: string; idx: number; total: number; lives: number; score: number; combo: number; done: number; best_combo: number;
  remaining_ms: number; per_ms: number; over: boolean; item: Record<string, any>; last: Record<string, any>; era: number };
export type Suggestion = { id: number; name: string; born?: number; used?: boolean; in_scope?: boolean; defunct?: boolean };

// Haftanın maçı: iki taraf (ad, kısa ad, [zemin, yazı] renkleri, toplam puan, koşu sayısı) ve oyuncunun seçtiği taraf
export type WeeklySide = { name: string; short: string; colors: [string, string]; total: number; runs: number };
export type Weekly = { slug: string; date: string; format?: "versus" | "career"; years?: [number, number] | null; a: WeeklySide; b: WeeklySide; me: { side: "a" | "b"; points: number; runs: number } | null };

type GameStore = {
  connected: boolean; pid: number; updateNeeded: boolean; weekly: Weekly | null;
  room: Room | null; roomAt: number;          // roomAt: son oda durumunun geldiği an (phase_ms'i yerel saate bağlamak için)
  single: Single | null; singleAt: number;
  suggestions: { kind: string; q: string; list: Suggestion[] } | null;
  error: { key: string; at: number } | null;
  acctResult: Record<string, any> | null;
  set: (patch: Partial<Omit<GameStore, "set">>) => void;
};
export const useGame = create<GameStore>((set) => ({
  connected: false, pid: 0, updateNeeded: false, weekly: null, room: null, roomAt: 0, single: null, singleAt: 0, suggestions: null, error: null, acctResult: null,
  set: (patch) => set(patch),
}));

export const State = { LOBBY: 0, PICK_TEAMS: 1, COUNTDOWN: 2, REVEAL: 3, ROUND: 4, ROUND_END: 5, GAME_OVER: 6 } as const;
