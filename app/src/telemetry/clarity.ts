import Constants, { ExecutionEnvironment } from "expo-constants";
import { environment, telemetryEnabled } from "./config";
import { reportClientError } from "./sentry";

type ClaritySdk = typeof import("@microsoft/react-native-clarity");
let sdk: ClaritySdk | undefined;
let started = false;
let currentScreen = "home";

export function initializeClarity(): void {
  const projectId = process.env.EXPO_PUBLIC_CLARITY_MOBILE_PROJECT_ID;
  if (started || !projectId || !telemetryEnabled()) return;
  if (Constants.executionEnvironment === ExecutionEnvironment.StoreClient) return;
  // Enable only after the mobile project's masking mode is set to Strict.
  if (process.env.EXPO_PUBLIC_CLARITY_MOBILE_MASKING_READY !== "true") return;
  started = true;
  // Expo Go must not evaluate the native module at import time.
  void import("@microsoft/react-native-clarity")
    .then((clarity) => {
      sdk = clarity;
      sdk.setOnSessionStartedCallback(() => {
        void sdk?.setCustomTag("environment", environment).catch(() => {});
        void sdk?.setCurrentScreenName(currentScreen).catch(() => {});
      });
      sdk.initialize(projectId);
    })
    .catch((error: unknown) => {
      sdk = undefined;
      reportClientError(error, "clarity.initialize");
    });
}

export function setClarityScreen(screen: string): void {
  currentScreen = screen;
  void sdk?.setCurrentScreenName(screen).catch(() => {});
}

export function clarityEvent(name: string): void {
  void sdk?.sendCustomEvent(name).catch(() => {});
}
