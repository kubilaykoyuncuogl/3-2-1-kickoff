// Yalnızca geliştirme: ekran görüntüsü için hazır durumlar. `?mock=<ad>` ile yüklenir (store.ts load → applyMock).
// Maç ve tek oyunculu ekranların her halini (uyarılar, kilit, tur sonu çeşitleri, sonuç kartları) sunucuya bağlı kalmadan gösterir.
// Üretimde çağrılmaz (__DEV__ korumalı). Tam liste ve çekim: tools/all_shots.py
import { Room, Single, Weekly, useGame, useProfile } from "../store";

const P = (pid: number, nick: string, elo: number, x: Record<string, unknown> = {}) =>
  ({ pid, nick, elo, team: 0, team_name: "", picked: false, ready: false, score: 0, penalty_ms: 0, rematch: false, elo_delta: 0, away: false, ...x });
const GS = { team: 1, team_name: "Galatasaray", picked: true }; const INT = { team: 2, team_name: "Inter Milan", picked: true };
const room = (state: number, me: Record<string, unknown> = {}, opp: Record<string, unknown> = {}, x: Partial<Room> = {}): Room =>
  ({ me: 1, code: "zidane", ranked: true, scope: "all", era: 0, round_ms: 15000, state, phase_ms: 41000, last: {}, answers: [], answers_total: 0, winner: 0, used_teams: [],
     quick_picks: [], players: [P(1, "kubi", 1016, me), P(2, "arda_1907", 1004, opp)] as any, ...x });
const ANS = ["Mauro Icardi", "Nicolò Zaniolo", "Wesley Sneijder", "Alex Telles", "Lukas Podolski", "Felipe Melo", "Goran Pandev"];
const HIST = [
  { mine: "Galatasaray", theirs: "Inter Milan", type: "correct", no_common: false, by: "me", name: "Wesley Sneijder", n: 13 },
  { mine: "Real Madrid", theirs: "Juventus FC", type: "correct", no_common: false, by: "opp", name: "Zinédine Zidane", n: 15 },
  { mine: "Chelsea FC", theirs: "AC Milan", type: "timeout", no_common: false, by: null, name: null, n: 22 },
  { mine: "Liverpool FC", theirs: "FC Barcelona", type: "correct", no_common: false, by: "me", name: "Luis Suárez", n: 14 },
  { mine: "Arsenal FC", theirs: "Manchester City", type: "correct", no_common: false, by: "me", name: "Gabriel Jesus", n: 21 },
];
const QUICK = [{ id: 11, name: "Real Madrid" }, { id: 12, name: "Bayern Munich" }, { id: 13, name: "Everton FC" }, { id: 14, name: "AS Roma" }, { id: 15, name: "Ajax Amsterdam" }];

const ROOMS: Record<string, () => Room> = {
  online_search: () => ({ me: 1, state: 0, searching: true, band: 125, elo: 1016, waiting: 3, cross_in_ms: 21000 }),
  online_room: () => ({ ...room(0), ranked: false, players: [P(1, "kubi", 1016)] as any }),
  pick_empty: () => room(1),
  pick_quick: () => room(1, {}, { picked: true }, { phase_ms: 22000, quick_picks: QUICK }),
  pick_chosen: () => room(1, GS, { picked: true }, { phase_ms: 33000 }),
  pick_ready: () => room(1, { ...GS, ready: true }, {}, { phase_ms: 30000 }),
  pick_oppready: () => room(1, {}, { picked: true, ready: true }, { phase_ms: 28000 }),
  pick_late: () => room(1, {}, { picked: true, ready: true }, { phase_ms: 8000, quick_picks: QUICK }),
  pick_away: () => room(1, GS, { away: true }, { phase_ms: 26000 }),
  countdown: () => room(2, { ...GS, ready: true }, { ...INT, ready: true }, { phase_ms: 2400 }),
  reveal: () => room(3, GS, INT, { phase_ms: 1500 }),
  round: () => room(4, { ...GS, score: 1 }, INT, { phase_ms: 12400 }),
  round_hot: () => room(4, { ...GS, score: 1 }, { ...INT, score: 2 }, { phase_ms: 3800 }),
  round_wrong_me: () => room(4, { ...GS, penalty_ms: 4300 }, INT, { phase_ms: 9000, last: { type: "wrong", pid: 1, name: "Lukas Hernandez" } }),
  round_wrong_opp: () => room(4, GS, { ...INT, penalty_ms: 3600 }, { phase_ms: 8200, last: { type: "wrong", pid: 2, name: "Mesut Özil" } }),
  round_away: () => room(4, GS, { ...INT, away: true }, { phase_ms: 7000 }),
  round_30: () => room(4, GS, INT, { phase_ms: 26000, round_ms: 30000, scope: "TR1", era: 6 }),
  end_me: () => room(5, { ...GS, score: 1 }, INT, { phase_ms: 3500, last: { type: "correct", pid: 1, name: "Wesley Sneijder" }, answers: ANS, answers_total: 13 }),
  end_opp: () => room(5, GS, { ...INT, score: 1 }, { phase_ms: 3500, last: { type: "correct", pid: 2, name: "Mauro Icardi" }, answers: ANS, answers_total: 13 }),
  end_nobody: () => room(5, GS, INT, { phase_ms: 3500, last: { type: "timeout" }, answers: ANS, answers_total: 13 }),
  end_pick_win: () => room(5, { ...GS, score: 1 }, {}, { phase_ms: 3500, last: { type: "pick_timeout", pid: 2 } }),
  end_pick_lose: () => room(5, {}, { ...INT, score: 1 }, { phase_ms: 3500, last: { type: "pick_timeout", pid: 1 } }),
  no_common: () => room(5, { team: 3, team_name: "Genclerbirligi Ankara", picked: true }, { team: 4, team_name: "FC Copenhagen", picked: true }, { phase_ms: 2400, last: { type: "timeout", no_common: true } }),
  over_win: () => room(6, { score: 3, elo_delta: 16 }, { score: 1, elo_delta: -16 }, { winner: 1, last: { type: "correct", pid: 1, name: "Gabriel Jesus" }, answers: ["Gabriel Jesus", "Oleksandr Zinchenko", "Kolo Touré", "Bacary Sagna", "Samir Nasri", "Gaël Clichy"], answers_total: 21, history: HIST } as any),
  over_lose: () => room(6, { score: 1, elo_delta: -14 }, { score: 3, elo_delta: 14 }, { winner: 2, last: { type: "correct", pid: 2, name: "Zinédine Zidane" }, answers: ["Zinédine Zidane", "Cristiano Ronaldo", "Gonzalo Higuaín", "Álvaro Morata", "Sami Khedira"], answers_total: 15,
    history: HIST.slice(0, 4).map((h) => ({ ...h, by: h.by === "me" ? "opp" : h.by === "opp" ? "me" : null })) } as any),
  over_draw: () => room(6, { score: 1 }, { score: 1 }, { winner: 0, ranked: false, last: { type: "timeout", no_common: true, draw: true },
    history: [HIST[0], HIST[1], ...[1, 2, 3].map(() => ({ mine: "Genclerbirligi Ankara", theirs: "FC Copenhagen", type: "timeout", no_common: true, by: null, name: null, n: 0 }))] } as any),
  over_left: () => ({ ...room(6, { score: 2, elo_delta: 12 }, {}, { winner: 1, last: { type: "left" } }), players: [P(1, "kubi", 1016, { score: 2, elo_delta: 12 })] as any }),
  over_rematch_wait: () => room(6, { score: 3, elo_delta: 16, rematch: true }, { score: 1, elo_delta: -16 }, { winner: 1, last: { type: "correct", pid: 1, name: "Gabriel Jesus" }, answers: ["Gabriel Jesus", "Kolo Touré"], answers_total: 21, history: HIST } as any),
  over_opp_rematch: () => room(6, { score: 1, elo_delta: -14 }, { score: 3, elo_delta: 14, rematch: true }, { winner: 2, last: { type: "correct", pid: 2, name: "Zinédine Zidane" }, answers: ["Zinédine Zidane", "Sami Khedira"], answers_total: 15, history: HIST.slice(0, 4) } as any),
};
// takım seçiminde ortada çıkan uyarılar: oda + hata anahtarı
const NOTICES: Record<string, string> = { pick_clash: "err.team_clash", pick_used: "err.team_used", pick_scope: "err.out_of_scope" };

const S = (mode: string, x: Partial<Single>): Single =>
  ({ mode, idx: 0, total: 27, lives: 3, score: 0, combo: 1, done: 0, best_combo: 1, remaining_ms: 16000, per_ms: 20000, over: false, item: {}, last: {}, era: 0, ...x });
const PAIR = { a_name: "Real Madrid", b_name: "Juventus FC", a: 1, b: 2, a_defunct: false, b_defunct: false };
const CLUBS = [
  { club: "Sporting CP", year: 2002, kind: "start", country: "Portugal", defunct: false }, { club: "Manchester United", year: 2003, kind: "sale", country: "England", defunct: false },
  { club: "Real Madrid", year: 2009, kind: "sale", country: "Spain", defunct: false }, { club: "Juventus FC", year: 2018, kind: "sale", country: "Italy", defunct: false },
  { club: "Manchester United", year: 2021, kind: "sale", country: "England", defunct: false }, { club: "Al-Nassr FC", year: 2023, kind: "free", country: "Saudi Arabia", defunct: false },
];
const CHAIN = { name: "Wesley Sneijder", born: 1984, pos: "AM", steps_total: 6 };
const VS = { cat: "goals", fmt: "int", names: ["Hakan Şükür", "Burak Yılmaz"], born: [1971, 1985], shown: [null, null], new_cat: false };
const W = { cat: "w_goals", fmt: "int", names: ["Fatih Tekke", "Cenk Tosun"], born: [1977, 1991], shown: [null, null], new_cat: false };

const SINGLES: Record<string, () => Single> = {
  ladder_play: () => S("ladder", { idx: 3, score: 345, item: PAIR }),
  ladder_wrong: () => S("ladder", { idx: 3, score: 345, lives: 2, item: PAIR, last: { type: "wrong", name: "Luka Modrić" } }),
  ladder_timeout: () => S("ladder", { idx: 4, score: 345, lives: 1, item: { ...PAIR, a_name: "Valencia CF", b_name: "Atalanta BC" }, last: { type: "timeout" }, remaining_ms: 18000, per_ms: 18000 }),
  ladder_over: () => S("ladder", { idx: 5, score: 600, lives: 0, over: true, item: { ...PAIR, a_name: "Valencia CF", b_name: "Atalanta BC" }, last: { type: "wrong", name: "Rodrigo" },
    end: { burn: { kind: "pair", a: "Valencia CF", b: "Atalanta BC", tried: "Rodrigo" }, fact: { kind: "pair_players", a: "Valencia CF", b: "Atalanta BC", total: 3, names: ["Yunus Musah", "Cristiano Lucarelli", "Cristiano Piccini"] } } } as any),
  ladder_over_many: () => S("ladder", { idx: 9, score: 1180, lives: 0, over: true, item: { ...PAIR, a_name: "CA River Plate", b_name: "Inter Milan" }, last: { type: "timeout" },
    end: { burn: { kind: "pair", a: "CA River Plate", b: "Inter Milan", tried: null }, fact: { kind: "pair_players", a: "CA River Plate", b: "Inter Milan", total: 20, names: ["Alexis Sánchez", "Esteban Cambiasso", "Hernán Crespo", "Julio Cruz", "Santiago Solari"] } } } as any),
  blitz_play: () => S("blitz", { idx: 4, total: 40, lives: 1, score: 460, combo: 1.4, best_combo: 1.4, remaining_ms: 6200, per_ms: 8000, item: { ...PAIR, a_name: "Chelsea FC", b_name: "AC Milan", options: ["Didier Drogba", "Andriy Shevchenko", "Kaká", "Frank Lampard", "Paolo Maldini"] } }),
  blitz_over: () => S("blitz", { idx: 5, total: 40, lives: 1, score: 610, combo: 1.5, best_combo: 1.5, over: true, item: { ...PAIR, a_name: "Arsenal FC", b_name: "Liverpool FC", options: ["Piero Hincapié", "Jermaine Pennant", "Thierry Henry", "Steven Gerrard", "Bukayo Saka"] }, last: { type: "wrong", option: 0, answer: 1 },
    end: { burn: { kind: "pick", a: "Arsenal FC", b: "Liverpool FC", answer: "Jermaine Pennant", picked: "Piero Hincapié" }, fact: { kind: "two_clubs", name: "Jermaine Pennant", spells: [{ club: "Arsenal FC", spans: [[2001, 2005]] }, { club: "Liverpool FC", spans: [[2006, 2009]] }] } } } as any),
  // cevaptan hemen sonraki an: şık / kart yeşil-kırmızı yanar (gösterilen durum + bekleyen sonuç)
  blitz_ok: () => ({ ...SINGLES.blitz_play(), _pending: { last: { type: "correct", option: 1 } } } as any),
  blitz_no: () => ({ ...SINGLES.blitz_play(), _pending: { over: true, last: { type: "wrong", option: 3, answer: 1 } } } as any),
  career_first: () => S("career", { total: 30, remaining_ms: 6500, per_ms: 8000, item: { clubs: CLUBS.slice(0, 1), total: 6, revealed: 1 } }),
  career_mid: () => S("career", { idx: 2, total: 30, score: 520, done: 2, remaining_ms: 5200, per_ms: 8000, item: { clubs: CLUBS.slice(0, 4), total: 6, revealed: 4 } }),
  career_wrong: () => S("career", { idx: 2, total: 30, score: 520, done: 2, lives: 2, remaining_ms: 4100, per_ms: 8000, item: { clubs: CLUBS.slice(0, 3), total: 6, revealed: 3 }, last: { type: "wrong", name: "Luís Figo" } }),
  career_right: () => S("career", { idx: 3, total: 30, score: 880, done: 3, remaining_ms: 7600, per_ms: 8000, item: { clubs: [{ club: "FC Barcelona", year: 2004, kind: "start", country: "Spain", defunct: false }], total: 4, revealed: 1 }, last: { type: "correct", name: "Cristiano Ronaldo", gained: 280 } }),
  career_over: () => S("career", { idx: 4, total: 30, score: 880, done: 3, lives: 0, over: true, item: { clubs: CLUBS, total: 6, revealed: 6 }, last: { type: "wrong", name: "Luís Figo", answer: "Cristiano Ronaldo" },
    end: { burn: { kind: "who", answer: "Cristiano Ronaldo", tried: "Luís Figo", first: "Sporting CP" }, fact: { kind: "career", name: "Cristiano Ronaldo", clubs: CLUBS.map((c) => c.club), apps: 1358, goals: 985 } } } as any),
  chain_first: () => S("chain", { total: 15, item: { ...CHAIN, step: 0, history: [], hint: { year: 2002, kind: "start", fee: null, country: "Netherlands", league: "Eredivisie" } } }),
  chain_mid: () => S("chain", { total: 15, score: 310, remaining_ms: 13000, item: { ...CHAIN, step: 2, hint: { year: 2009, kind: "sale", fee: 15000000, country: "Italy", league: "Serie A" },
    history: [{ club: "Ajax Amsterdam", year: 2002, kind: "start", fee: null, country: "Netherlands", defunct: false }, { club: "Real Madrid", year: 2007, kind: "sale", fee: 27000000, country: "Spain", defunct: false }] }, last: { type: "correct", name: "Real Madrid", gained: 165 } }),
  chain_wrong: () => S("chain", { total: 15, score: 310, lives: 2, remaining_ms: 19000, item: { ...CHAIN, step: 3, hint: { year: 2013, kind: "sale", fee: 7500000, country: "Türkiye", league: "Süper Lig" },
    history: [{ club: "Ajax Amsterdam", year: 2002, kind: "start", fee: null, country: "Netherlands", defunct: false }, { club: "Real Madrid", year: 2007, kind: "sale", fee: 27000000, country: "Spain", defunct: false }, { club: "Inter Milan", year: 2009, kind: "sale", fee: 15000000, country: "Italy", defunct: false }] },
    last: { type: "wrong", name: "AC Milan", answer: "Inter Milan" } }),
  chain_over: () => S("chain", { idx: 2, total: 15, score: 640, done: 2, lives: 0, over: true, item: { name: "Andrea Belotti", born: 1993, pos: "CF", step: 2, steps_total: 6, history: [] }, last: { type: "wrong", name: "AC Milan", answer: "Torino FC" },
    end: { burn: { kind: "club", player: "Andrea Belotti", answer: "Torino FC", tried: "AC Milan" }, fact: { kind: "move", name: "Andrea Belotti", year: 2015, from: "Palermo FC", to: "Torino FC", move: "sale", fee: 8400000 } } } as any),
  versus_play: () => S("versus", { total: 80, lives: 1, remaining_ms: 7400, per_ms: 9000, item: VS }),
  versus_shown: () => S("versus", { idx: 3, total: 80, lives: 1, score: 548, done: 3, remaining_ms: 6100, per_ms: 9000, item: { ...VS, cat: "apps", names: ["Kaká", "Peter Crouch"], born: [1982, 1981], shown: [712, null] } }),
  versus_newcat: () => S("versus", { idx: 6, total: 80, lives: 1, score: 1120, done: 6, remaining_ms: 8000, per_ms: 8500, item: { ...VS, cat: "assists", names: ["Kevin De Bruyne", "Mesut Özil"], born: [1991, 1988], new_cat: true } }),
  versus_over: () => S("versus", { idx: 7, total: 80, lives: 1, score: 1304, done: 7, over: true, item: { ...VS, cat: "apps", names: ["Roberto Baggio", "Roy Makaay"], born: [1967, 1975] }, last: { type: "wrong", option: 0, answer: 1, values: [692, 731] },
    end: { burn: { kind: "vs", cat: "apps", fmt: "int", names: ["Roberto Baggio", "Roy Makaay"], values: [692, 731], picked: 0 }, fact: { kind: "player", name: "Roy Makaay", apps: 731, goals: 337, n_clubs: 5 } } } as any),
  versus_ok: () => ({ ...SINGLES.versus_play(), _pending: { last: { type: "correct", option: 0, values: [383, 291] } } } as any),
  versus_no: () => ({ ...SINGLES.versus_play(), _pending: { over: true, last: { type: "wrong", option: 1, answer: 0, values: [383, 291] } } } as any),
  weekly_no: () => ({ ...SINGLES.weekly_play(), _pending: { over: true, last: { type: "wrong", option: 0, answer: 1, values: [31, 64] } } } as any),
  wcareer_play: () => S("weekly_career", { idx: 2, total: 40, score: 440, done: 2, remaining_ms: 5200, per_ms: 8000, item: { clubs: [{ club: "FC Groningen", year: 2005, kind: "start", country: "Netherlands", defunct: false }, { club: "Ajax Amsterdam", year: 2007, kind: "sale", country: "Netherlands", defunct: false }, { club: "Liverpool FC", year: 2011, kind: "sale", country: "England", defunct: false }], total: 6, revealed: 3 } }),
  wcareer_over: () => S("weekly_career", { idx: 4, total: 40, score: 880, done: 3, lives: 0, over: true, item: { clubs: CLUBS.slice(0, 3), total: 5, revealed: 3 }, last: { type: "wrong", name: "Dirk Kuyt", answer: "Luis Suárez" },
    end: { burn: { kind: "who", answer: "Luis Suárez", tried: "Dirk Kuyt", first: "Club Nacional" }, fact: { kind: "career", name: "Luis Suárez", clubs: ["Club Nacional", "FC Groningen", "Ajax Amsterdam", "Liverpool FC", "FC Barcelona", "Atlético de Madrid"], apps: 987, goals: 588 } } } as any),
  weekly_play: () => S("weekly", { idx: 2, total: 60, lives: 1, score: 372, done: 2, remaining_ms: 7000, per_ms: 9000, item: W }),
  weekly_over: () => S("weekly", { idx: 5, total: 60, lives: 1, score: 930, done: 5, over: true, item: { ...W, cat: "w_assists", names: ["Hamdi Aslan", "Olcay Şahan"] }, last: { type: "wrong", option: 0, answer: 1, values: [22, 34] },
    end: { burn: { kind: "vs", cat: "w_assists", fmt: "int", names: ["Hamdi Aslan", "Olcay Şahan"], values: [22, 34], picked: 0 }, fact: { kind: "club_stats", name: "Olcay Şahan", club: "Beşiktaş", apps: 183, goals: 37, assists: 34, seasons: 5 } } } as any),
};
const WEEK = (me: Weekly["me"]): Weekly => ({ slug: "ts-bjk", date: "2026-10-10", me,
  a: { name: "Trabzonspor", short: "Trabzonspor", colors: ["#7A1230", "#8FD0F5"], total: 12480, runs: 31 }, b: { name: "Beşiktaş JK", short: "Beşiktaş", colors: ["#111111", "#FFFFFF"], total: 13920, runs: 36 } });
const WEEK_C = (me: Weekly["me"]): Weekly => ({ slug: "mci-liv", date: "", format: "career", years: [2000, 2026], me,
  a: { name: "Manchester City", short: "Man City", colors: ["#6CABDD", "#1C2C5B"], total: 8640, runs: 22 }, b: { name: "Liverpool FC", short: "Liverpool", colors: ["#C8102E", "#FFFFFF"], total: 9120, runs: 25 } });
const WEEKLIES: Record<string, () => Weekly | null> = { wcareer_fresh: () => WEEK_C(null), wcareer_locked: () => WEEK_C({ side: "b", points: 1320, runs: 3 }), weekly_fresh: () => WEEK(null), weekly_locked: () => WEEK({ side: "b", points: 1860, runs: 4 }), weekly_none: () => null };

let current = "";
export function mockName(): string { return current; }

// Tek oyunculu ekran için hazır durum: mod tutuyorsa döner. "single_fail" = hiç cevap gelmemiş gibi (yükleme → "sunucudan cevap gelmedi").
export function devSingle(mode: string): Single | "none" | null {
  if (!__DEV__ || !current) return null;
  if (current === "single_fail") return "none";
  const f = SINGLES[current];
  if (!f) return null;
  const s = f();
  return s.mode === mode ? s : null;
}

export function applyMock(names: string) {
  if (!__DEV__) return;
  const g = useGame.getState();
  for (const name of names.split(",")) {
    current = SINGLES[name] || name === "single_fail" ? name : current;
    const base = NOTICES[name] ? "pick_empty" : name;
    if (ROOMS[base]) g.set({ room: ROOMS[base](), roomAt: Date.now(), pid: 1 });
    if (NOTICES[name]) setTimeout(() => useGame.getState().set({ error: { key: NOTICES[name], at: Date.now() } }), 1400);
    if (name === "update") g.set({ updateNeeded: true });
    // sunucudan gelen gerçek profil / haftalık durum sonradan üstüne yazmasın diye gecikmeli ve iki kez
    if (WEEKLIES[name]) for (const ms of [300, 1600, 2600]) setTimeout(() => useGame.getState().set({ weekly: WEEKLIES[name]() }), ms);
    if (name === "linked") for (const ms of [1500, 2500]) setTimeout(() => useProfile.setState({ linked: true, verified: false, devices: 2, elo: 1042 }), ms);
    if (name === "acct_recovery") setTimeout(() => useGame.getState().set({ acctResult: { op: "create", ok: true, error: "", recovery: "zidane-pirlo-xavi-4821", at: Date.now() } }), 1600);
    if (name === "acct_code") setTimeout(() => useGame.getState().set({ acctResult: { op: "link_code", ok: true, error: "", code: "482913", ttl: 600, at: Date.now() } }), 1600);
    if (name === "acct_error") setTimeout(() => useGame.getState().set({ acctResult: { op: "link", ok: false, error: "bad_code", at: Date.now() } }), 2600);
    if (name === "join_error") setTimeout(() => useGame.getState().set({ error: { key: "err.room_not_found", at: Date.now() } }), 2600);
  }
}
