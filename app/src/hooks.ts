// Ortak kancalar: saniyelik saat, sunucu aşamasının yerel bitişi, hata anahtarını çeviren uyarı.
import { useEffect, useRef, useState } from "react";
import { t } from "./i18n";
import { useGame } from "./store";

// Her `ms` milisaniyede yeniden çizdirir (sayaçlar için)
export function useNow(ms = 250): number {
  const [now, setNow] = useState(Date.now());
  useEffect(() => { const id = setInterval(() => setNow(Date.now()), ms); return () => clearInterval(id); }, [ms]);
  return now;
}

// Sunucudan gelen kalan süre (phase_ms / remaining_ms) + geldiği an → şu an kalan ms
export function remaining(ms: number | undefined, at: number, now: number): number {
  return Math.max(0, (ms ?? 0) - (now - at));
}

// Sunucu hatası (err.* anahtarı) geldiğinde çevrilmiş metni verir; `ttl` ms sonra silinir
export function useServerError(ttl = 4000): string {
  const err = useGame((g) => g.error);
  const now = useNow(500);
  if (!err || now - err.at > ttl) return "";
  return t(err.key);
}

// Bir değer değiştiğinde çalışır ama ilk çizimde çalışmaz
export function useChanged<T>(value: T, fn: (v: T) => void) {
  const first = useRef(true);
  useEffect(() => { if (first.current) { first.current = false; return; } fn(value); }, [value]);
}
