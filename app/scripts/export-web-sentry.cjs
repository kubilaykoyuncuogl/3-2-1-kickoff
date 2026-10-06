const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const appRoot = path.resolve(__dirname, "..");

function run(script, args, env = process.env) {
  const result = spawnSync(process.execPath, [script, ...args], {
    cwd: appRoot,
    env,
    stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}

run(require.resolve("expo/bin/cli"), ["export", "--platform", "web", "--source-maps", "--clear"]);
run(require.resolve("@sentry/cli/bin/sentry-cli"), [
  "sourcemaps", "upload", "--validate", "--wait-for", "60", "dist",
], {
  ...process.env,
  SENTRY_ORG: process.env.SENTRY_ORG ?? "grande-corpo",
  SENTRY_PROJECT: process.env.SENTRY_PROJECT ?? "kickoff-app",
});

// Archive only after a successful upload, preserving maps for local diagnostics.
const dist = path.join(appRoot, "dist");
const archive = path.join(appRoot, ".expo", "sentry-sourcemaps", new Date().toISOString().replace(/[:.]/g, "-"));
function archiveMaps(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) archiveMaps(file);
    else if (entry.name.endsWith(".map")) {
      const target = path.join(archive, path.relative(dist, file));
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.renameSync(file, target);
    }
  }
}
archiveMaps(dist);
console.log("Web export ready. Sentry maps uploaded and archived outside public dist.");
