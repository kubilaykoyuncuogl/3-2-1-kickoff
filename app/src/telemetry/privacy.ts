import type { Event } from "@sentry/react-native";

export function sanitizeEvent<T extends Event>(event: T): T {
  delete event.user;
  delete event.extra;
  delete event.message;
  delete event.logentry;
  if (event.request) {
    const { url, method } = event.request;
    event.request = { method, url: url?.split(/[?#]/)[0] };
  }
  // Exceptions may interpolate account credentials; keep types and stack locations.
  for (const exception of event.exception?.values ?? []) {
    exception.value = "[redacted]";
    for (const frame of exception.stacktrace?.frames ?? []) {
      delete frame.vars;
      delete frame.pre_context;
      delete frame.context_line;
      delete frame.post_context;
    }
  }
  for (const thread of event.threads?.values ?? []) {
    for (const frame of thread.stacktrace?.frames ?? []) {
      delete frame.vars;
      delete frame.pre_context;
      delete frame.context_line;
      delete frame.post_context;
    }
  }
  for (const span of event.spans ?? []) {
    span.data = {};
    span.description = span.op;
  }
  return event;
}
