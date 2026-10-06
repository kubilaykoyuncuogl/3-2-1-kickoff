import { clarityEvent, initializeClarity, setClarityScreen } from "./clarity";
import { gameBreadcrumb, Sentry } from "./sentry";

export { reportClientError } from "./sentry";

export type GameEvent =
  | "match_search"
  | "room_create"
  | "room_join"
  | "match_start"
  | "match_complete"
  | "rematch_request"
  | "single_start"
  | "single_complete";

export function trackGameEvent(event: GameEvent): void {
  gameBreadcrumb(event);
  clarityEvent(event);
}

export function trackScreen(screen: string): void {
  Sentry.setTag("screen", screen);
  setClarityScreen(screen);
}

// Re-export the SDK wrapper without coupling telemetry to game stores.
export { Sentry, initializeClarity };
