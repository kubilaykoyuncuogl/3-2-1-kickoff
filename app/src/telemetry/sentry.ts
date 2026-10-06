import Constants, { ExecutionEnvironment } from "expo-constants";
import { Platform } from "react-native";
import * as Sentry from "@sentry/react-native";
import { environment, sampleRate, telemetryEnabled } from "./config";
import { sanitizeEvent } from "./privacy";

const dsn = process.env.EXPO_PUBLIC_SENTRY_DSN;

Sentry.init({
  dsn,
  enabled: Boolean(dsn) && telemetryEnabled(),
  environment,
  enableNative: Platform.OS !== "web" && Constants.executionEnvironment !== ExecutionEnvironment.StoreClient,
  sendDefaultPii: false,
  tracesSampleRate: sampleRate(process.env.EXPO_PUBLIC_SENTRY_TRACES_SAMPLE_RATE),
  // Clarity owns session recording; keep Sentry replay disabled.
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,
  beforeBreadcrumb(breadcrumb) {
    // Console logs and automatic UI/network breadcrumbs can contain account codes.
    return breadcrumb.category === "game" ? breadcrumb : null;
  },
  beforeSend: sanitizeEvent,
  beforeSendTransaction: sanitizeEvent,
});

export function reportClientError(error: unknown, operation: string): void {
  if (!dsn || !telemetryEnabled()) return;
  Sentry.captureException(error, { tags: { operation } });
}

export function gameBreadcrumb(message: string): void {
  if (!dsn || !telemetryEnabled()) return;
  Sentry.addBreadcrumb({ category: "game", message, level: "info" });
}

export { Sentry };
