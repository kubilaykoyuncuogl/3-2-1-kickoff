const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const ts = require("typescript");

function load(file, mocks = {}, env = {}, dev = false, globals = {}) {
  const filename = path.join(__dirname, "../src", file);
  const source = ts.transpileModule(fs.readFileSync(filename, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const exports = {};
  const sandbox = {
    exports, process: { env }, __DEV__: dev, ...globals,
    require(name) {
      assert.ok(name in mocks, `Unexpected dependency: ${name}`);
      return mocks[name];
    },
  };
  vm.runInNewContext(source, sandbox, { filename });
  return exports;
}

test("invalid sample rates stay disabled", () => {
  const config = load("telemetry/config.ts");
  for (const value of ["NaN", "-1", "2", "", undefined]) assert.equal(config.sampleRate(value), 0);
  assert.equal(config.sampleRate("0.25"), 0.25);
  assert.equal(load("telemetry/config.ts", {}, {}, true).telemetryEnabled(), false);
});

test("Sentry removes account secrets while preserving exception types and stack locations", () => {
  const { sanitizeEvent } = load("telemetry/privacy.ts");
  const event = {
    user: { id: "DEVICE_SECRET" }, extra: { recovery: "RECOVERY_SECRET" },
    message: "RECOVERY_SECRET", logentry: { message: "DEVICE_SECRET" },
    request: { url: "https://example.com/acct?device=DEVICE_SECRET#RECOVERY_SECRET",
      method: "POST", headers: { Authorization: "TOKEN_SECRET" }, data: { recovery: "RECOVERY_SECRET" } },
    exception: { values: [{ type: "Error", value: "RECOVERY_SECRET",
      stacktrace: { frames: [{ filename: "socket.ts", lineno: 12, vars: { device: "DEVICE_SECRET" } }] } }] },
    spans: [{ op: "http.client", description: "DEVICE_SECRET", data: { recovery: "RECOVERY_SECRET" } }],
  };
  const result = sanitizeEvent(event);
  assert.doesNotMatch(JSON.stringify(result), /(?:DEVICE|RECOVERY|TOKEN)_SECRET/);
  assert.equal(result.exception.values[0].type, "Error");
  assert.equal(result.exception.values[0].stacktrace.frames[0].lineno, 12);
  assert.equal(result.request.url, "https://example.com/acct");
});

function nativeClarity(env, expoGo = false) {
  const calls = [];
  const mocks = {
    "expo-constants": { __esModule: true, default: { executionEnvironment: expoGo ? "storeClient" : "standalone" },
      ExecutionEnvironment: { StoreClient: "storeClient" } },
    "./config": { environment: "test", telemetryEnabled: () => true },
    "./sentry": { reportClientError: () => calls.push("error") },
    "@microsoft/react-native-clarity": {
      initialize: () => calls.push("initialize"),
      setOnSessionStartedCallback: (callback) => callback(),
      setCustomTag: async () => {}, setCurrentScreenName: async () => {},
    },
  };
  return { sdk: load("telemetry/clarity.ts", mocks, env), calls };
}

test("native recording stays off without IDs, strict masking, or in Expo Go", async () => {
  for (const [env, go] of [
    [{}, false],
    [{ EXPO_PUBLIC_CLARITY_MOBILE_PROJECT_ID: "project" }, false],
    [{ EXPO_PUBLIC_CLARITY_MOBILE_PROJECT_ID: "project", EXPO_PUBLIC_CLARITY_MOBILE_MASKING_READY: "true" }, true],
  ]) {
    const { sdk, calls } = nativeClarity(env, go);
    sdk.initializeClarity();
    await new Promise(setImmediate);
    assert.equal(calls.length, 0);
  }
});

test("native Clarity initializes once", async () => {
  const { sdk, calls } = nativeClarity({
    EXPO_PUBLIC_CLARITY_MOBILE_PROJECT_ID: "project", EXPO_PUBLIC_CLARITY_MOBILE_MASKING_READY: "true",
  });
  sdk.initializeClarity();
  sdk.initializeClarity();
  await new Promise(setImmediate);
  assert.deepEqual(calls, ["initialize"]);
});

test("web text is masked before Clarity initialization", async () => {
  const calls = [];
  const sdk = load("telemetry/clarity.web.ts", {
    "./config": { environment: "test", telemetryEnabled: () => true },
    "./sentry": { reportClientError: () => calls.push("error") },
    "@microsoft/clarity": { __esModule: true, default: { init: () => calls.push("initialize"), setTag() {}, event() {} } },
  }, { EXPO_PUBLIC_CLARITY_WEB_PROJECT_ID: "project" }, false, {
    document: { documentElement: { setAttribute: (key, value) => calls.push(`${key}=${value}`) } },
  });
  sdk.initializeClarity();
  sdk.initializeClarity();
  await new Promise(setImmediate);
  assert.deepEqual(calls, ["data-clarity-mask=true", "initialize"]);
});

test("disabled web telemetry does not load Clarity or change the document", async () => {
  const sdk = load("telemetry/clarity.web.ts", {
    "./config": { environment: "test", telemetryEnabled: () => false },
    "./sentry": { reportClientError: () => assert.fail("SDK should not load") },
  }, { EXPO_PUBLIC_CLARITY_WEB_PROJECT_ID: "project" }, false, {
    document: { documentElement: { setAttribute: () => assert.fail("Document should not change") } },
  });
  sdk.initializeClarity();
  await new Promise(setImmediate);
});

test("round countdowns do not count as new matches and socket failures exclude payloads", () => {
  const events = [], errors = [], messages = [];
  let sock;
  const state = { room: null, set(update) { Object.assign(this, update); } };
  class WebSocket {
    static OPEN = 1;
    static CONNECTING = 0;
    constructor() { sock = this; this.readyState = 0; }
    send(message) { messages.push(JSON.parse(message)); }
  }
  const dependencyMocks = {
    "expo-constants": { __esModule: true, default: { expoConfig: {} } },
    "react-native": { Platform: { OS: "android" }, AppState: { addEventListener() {} } },
    "../store": {
      State: { LOBBY: 0, PICK_TEAMS: 1, COUNTDOWN: 2, GAME_OVER: 6 },
      useGame: { getState: () => state },
      useSettings: { getState: () => ({ nickname: "Test", device_id: "DEVICE_SECRET", scope: "all", era: "all", round: 30 }) },
      useProfile: { getState: () => ({}) },
    },
    "../telemetry": { trackGameEvent: (event) => events.push(event), reportClientError: (...args) => errors.push(args) },
  };
  const socket = load("net/socket.ts", dependencyMocks, {}, false, { WebSocket });
  socket.connect();
  sock.readyState = WebSocket.OPEN;
  sock.onopen();
  assert.deepEqual(messages.map((message) => message.t), ["hello", "weekly_info"]);
  socket.api.createRoom();
  socket.api.findMatch();
  assert.equal(messages[2].round, 30);
  assert.equal(messages[3].round, 30);
  assert.deepEqual(events, ["room_create", "match_search"]);
  events.length = 0;
  sock.onmessage({ data: JSON.stringify({ t: "weekly_state", d: { title: "Weekly match" } }) });
  assert.equal(state.weekly.title, "Weekly match");
  assert.equal(events.length, 0);
  for (const roomState of [0, 1, 2, 3, 4, 5, 1, 2, 6, 6, 1]) {
    sock.onmessage({ data: JSON.stringify({ t: "room_state", d: { code: "secret-room", state: roomState } }) });
  }
  assert.deepEqual(events, ["match_start", "match_complete", "match_start"]);
  sock.onmessage({ data: JSON.stringify({ t: "room_state", secret: "DEVICE_SECRET" }) });
  assert.equal(errors.length, 1);
  assert.equal(errors[0].length, 2);
  assert.equal(errors[0][1], "socket.message");
  assert.doesNotMatch(JSON.stringify(errors), /DEVICE_SECRET/);
  assert.equal(typeof socket.connect, "function");
});
