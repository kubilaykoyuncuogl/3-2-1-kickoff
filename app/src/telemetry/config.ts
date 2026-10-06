export function telemetryEnabled(): boolean {
  return !__DEV__ || process.env.EXPO_PUBLIC_TELEMETRY_IN_DEV === "true";
}

export function sampleRate(value: string | undefined, fallback = 0): number {
  if (!value?.trim()) return fallback;
  const rate = Number(value);
  return Number.isFinite(rate) && rate >= 0 && rate <= 1 ? rate : fallback;
}

export const environment =
  process.env.EXPO_PUBLIC_TELEMETRY_ENVIRONMENT || (__DEV__ ? "development" : "production");
