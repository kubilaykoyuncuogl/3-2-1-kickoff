import { environment, telemetryEnabled } from "./config";
import { reportClientError } from "./sentry";

type ClaritySdk = typeof import("@microsoft/clarity").default;
let sdk: ClaritySdk | undefined;
let started = false;
let currentScreen = "home";

export function initializeClarity(): void {
  const projectId = process.env.EXPO_PUBLIC_CLARITY_WEB_PROJECT_ID;
  if (started || !projectId || !telemetryEnabled() || typeof document === "undefined") return;
  started = true;
  // Mask rendered account/recovery text before Clarity can take its first snapshot.
  document.documentElement.setAttribute("data-clarity-mask", "true");
  void import("@microsoft/clarity")
    .then(({ default: clarity }) => {
      sdk = clarity;
      sdk.init(projectId);
      sdk.setTag("environment", environment);
      sdk.setTag("screen", currentScreen);
    })
    .catch((error: unknown) => {
      sdk = undefined;
      reportClientError(error, "clarity.initialize");
    });
}

export function setClarityScreen(screen: string): void {
  currentScreen = screen;
  sdk?.setTag("screen", screen);
}

export function clarityEvent(name: string): void {
  sdk?.event(name);
}
