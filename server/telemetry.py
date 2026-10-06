"""Optional Sentry reporting; account payloads never enter captured events."""
import asyncio
import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration


def sample_rate(value: str | None) -> float:
    try:
        rate = float(value or "0")
        return rate if 0 <= rate <= 1 else 0
    except ValueError:
        return 0


def sanitize_event(event: dict, _hint: dict | None = None) -> dict:
    for key in ("user", "extra", "message", "logentry", "breadcrumbs"):
        event.pop(key, None)
    if "request" in event:
        request = event["request"]
        event["request"] = {
            key: request[key].split("?")[0].split("#")[0] if key == "url" else request[key]
            for key in ("url", "method") if key in request
        }
    # Keep the exception type and stack, without values or captured local variables.
    for container in ("exception", "threads"):
        for value in event.get(container, {}).get("values", []):
            if container == "exception":
                value["value"] = "[redacted]"
            for frame in value.get("stacktrace", {}).get("frames", []):
                for key in ("vars", "pre_context", "context_line", "post_context"):
                    frame.pop(key, None)
    for span in event.get("spans", []):
        span.pop("data", None)
        span["description"] = span.get("op", "")
    return event


def initialize() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        release=os.getenv("SENTRY_RELEASE") or None,
        send_default_pii=False,
        include_local_variables=False,
        include_source_context=False,
        max_request_body_size="never",
        traces_sample_rate=sample_rate(os.getenv("SENTRY_TRACES_SAMPLE_RATE")),
        integrations=[FastApiIntegration(), StarletteIntegration()],
        before_send=sanitize_event,
        before_send_transaction=sanitize_event,
        before_breadcrumb=lambda _breadcrumb, _hint: None,
    )


def report_error(error: Exception, operation: str) -> None:
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("operation", operation)
        sentry_sdk.capture_exception(error)


def watch_task(task: asyncio.Task, operation: str) -> None:
    def done(completed: asyncio.Task) -> None:
        if completed.cancelled():
            return
        error = completed.exception()
        if error is not None:
            # exception() okununca asyncio kendi "never retrieved" uyarısını basmaz; Sentry kapalıyken de hata loga düşsün
            print("[task] %s failed: %r" % (operation, error), flush=True)
            report_error(error, operation)
    task.add_done_callback(done)
