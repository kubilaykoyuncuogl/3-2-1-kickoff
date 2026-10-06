import asyncio
import copy
import unittest
from unittest.mock import patch

import sentry_sdk
from fastapi import FastAPI, Request
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.transport import Transport

from server.telemetry import initialize, report_error, sample_rate, sanitize_event, watch_task


class MemoryTransport(Transport):
    def __init__(self):
        super().__init__()
        self.events = []

    def capture_envelope(self, envelope):
        for item in envelope.items:
            if item.type == "event":
                self.events.append(item.payload.json)


class TelemetryTests(unittest.TestCase):
    def test_no_dsn_does_not_initialize(self):
        with patch.dict("os.environ", {}, clear=True), patch("server.telemetry.sentry_sdk.init") as init:
            initialize()
            init.assert_not_called()

    def test_invalid_sample_rates_disabled(self):
        for value in (None, "", "nan", "inf", "-1", "2", "invalid"):
            self.assertEqual(sample_rate(value), 0)
        self.assertEqual(sample_rate("0.25"), 0.25)

    def test_scrub_account_credentials(self):
        event = {
            "user": {"id": "DEVICE_SECRET"}, "extra": {"recovery": "RECOVERY_SECRET"},
            "message": "DEVICE_SECRET", "breadcrumbs": {"values": [{"message": "DEVICE_SECRET"}]},
            "request": {"url": "https://example.com/acct?device=DEVICE_SECRET#RECOVERY_SECRET",
                        "method": "POST", "headers": {"Authorization": "TOKEN_SECRET"},
                        "cookies": "TOKEN_SECRET", "data": {"recovery": "RECOVERY_SECRET"}},
            "exception": {"values": [{"type": "ValueError", "value": "RECOVERY_SECRET",
                "stacktrace": {"frames": [{"filename": "engine.py", "lineno": 42,
                                          "vars": {"device": "DEVICE_SECRET"}}]}}]},
            "spans": [{"op": "db", "description": "DEVICE_SECRET", "data": {"device": "DEVICE_SECRET"}}],
        }
        result = sanitize_event(copy.deepcopy(event))
        self.assertNotIn("_SECRET", str(result))
        self.assertEqual(result["exception"]["values"][0]["type"], "ValueError")
        self.assertEqual(result["exception"]["values"][0]["stacktrace"]["frames"][0]["lineno"], 42)


class CaptureTests(unittest.IsolatedAsyncioTestCase):
    async def test_fastapi_exception_is_reported_without_request_credentials(self):
        transport = MemoryTransport()
        client = sentry_sdk.Client(
            dsn="https://public@example.com/1", transport=transport,
            default_integrations=False,
            integrations=[FastApiIntegration(), StarletteIntegration()],
            include_local_variables=False, before_send=sanitize_event,
            max_request_body_size="never", send_default_pii=False,
        )
        with sentry_sdk.isolation_scope() as sdk_scope:
            sdk_scope.set_client(client)
            app = FastAPI()

            @app.post("/acct")
            async def fail(request: Request):
                body = await request.json()
                raise ValueError(body["recovery"])

            async def receive():
                return {"type": "http.request", "body": b'{"recovery":"RECOVERY_SECRET"}', "more_body": False}

            async def send(_message):
                pass

            scope = {
                "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                "scheme": "http", "method": "POST", "path": "/acct", "raw_path": b"/acct",
                "query_string": b"device=DEVICE_SECRET", "root_path": "",
                "headers": [(b"content-type", b"application/json"),
                            (b"authorization", b"TOKEN_SECRET"), (b"cookie", b"device=DEVICE_SECRET")],
                "server": ("test", 80), "client": ("127.0.0.1", 1234),
            }
            with self.assertRaises(ValueError):
                await app(scope, receive, send)
            self.assertGreaterEqual(len(transport.events), 1)
            self.assertNotIn("_SECRET", str(transport.events))
            self.assertEqual(transport.events[0]["exception"]["values"][-1]["type"], "ValueError")
        client.close()

    async def test_handled_and_background_errors_reach_sentry_without_locals(self):
        transport = MemoryTransport()
        client = sentry_sdk.Client(
            dsn="https://public@example.com/1", transport=transport,
            default_integrations=False, include_local_variables=False,
            before_send=sanitize_event,
        )
        with sentry_sdk.isolation_scope() as scope:
            scope.set_client(client)
            try:
                device = "DEVICE_SECRET"
                raise ValueError(device)
            except ValueError as error:
                report_error(error, "ws.handle")

            async def fail():
                raise RuntimeError("RECOVERY_SECRET")

            task = asyncio.create_task(fail())
            watch_task(task, "engine.task")
            with self.assertRaises(RuntimeError):
                await task
            await asyncio.sleep(0)
            self.assertEqual(len(transport.events), 2)
            self.assertEqual(
                {event["tags"]["operation"] for event in transport.events},
                {"ws.handle", "engine.task"},
            )
            self.assertNotIn("_SECRET", str(transport.events))
            cancelled = asyncio.create_task(asyncio.sleep(100))
            watch_task(cancelled, "engine.task")
            cancelled.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await cancelled
            await asyncio.sleep(0)
            self.assertEqual(len(transport.events), 2)
        client.close()


if __name__ == "__main__":
    unittest.main()
