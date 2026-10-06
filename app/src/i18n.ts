// Dil paketi: lang/<kod>.json (anahtar → metin). t("menu.online"), t("sp.step", 3). Eksik anahtar Türkçeye, o da yoksa anahtara düşer.
// Yer tutucular printf biçimi (%s %d %.1f %%): Godot sürümüyle aynı dosyalar paylaşılır, tools/check_lang.py iki konumu da kontrol eder.
import tr from "../lang/tr.json";
import en from "../lang/en.json";

type Dict = Record<string, string>;
const PACKS: Record<string, Dict> = { tr: tr as Dict, en: en as Dict };
export const LANGS = Object.keys(PACKS).sort((a, b) => (a === "tr" ? -1 : b === "tr" ? 1 : a.localeCompare(b)));
let current = "tr";

export function setLang(code: string) { current = PACKS[code] ? code : "tr"; }
export function getLang() { return current; }

export function fmt(s: string, ...args: (string | number)[]): string {
  let i = 0;
  return s.replace(/%(\.\d+)?([sdf%])/g, (m, prec, kind) => {
    if (kind === "%") return "%";
    const v = args[i++];
    if (v === undefined) return m;
    if (kind === "d") return String(Math.trunc(Number(v)));
    if (kind === "f") return Number(v).toFixed(prec ? parseInt(prec.slice(1), 10) : 6);
    return String(v);
  });
}

export function t(key: string, ...args: (string | number)[]): string {
  const s = PACKS[current]?.[key] ?? PACKS.tr[key] ?? key;
  return args.length ? fmt(s, ...args) : s;
}

export function has(key: string): boolean { return key in (PACKS[current] ?? {}) || key in PACKS.tr; }
