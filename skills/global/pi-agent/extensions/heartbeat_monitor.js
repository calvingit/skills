import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_HEARTBEAT_TIMEOUT_MS = 15_000;
const DEFAULT_PROGRESS_TIMEOUT_MS = 120_000;

function asTimestamp(value, field) {
  if (typeof value !== "string") throw new Error(`${field} must be an ISO timestamp`);
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) throw new Error(`${field} must be an ISO timestamp`);
  return timestamp;
}

export function validateHeartbeat(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("heartbeat must be a JSON object");
  }
  if (value.schema !== 1) throw new Error("unsupported heartbeat schema");
  if (!Number.isInteger(value.pid) || value.pid <= 0) {
    throw new Error("heartbeat pid must be a positive integer");
  }
  if (typeof value.session !== "string" || !/^[a-f0-9]{16}$/u.test(value.session)) {
    throw new Error("heartbeat session must be a 16-character hash");
  }
  if (!Number.isInteger(value.seq) || value.seq < 0) {
    throw new Error("heartbeat seq must be a non-negative integer");
  }
  asTimestamp(value.heartbeat_at, "heartbeat_at");
  asTimestamp(value.progress_at, "progress_at");
  if (typeof value.phase !== "string" || value.phase.length === 0) {
    throw new Error("heartbeat phase must be a non-empty string");
  }
  return value;
}

export async function readHeartbeat(file) {
  const content = await fs.readFile(file, "utf8");
  return validateHeartbeat(JSON.parse(content));
}

export function processIsAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error?.code === "EPERM";
  }
}

export function classifyHeartbeat(
  heartbeat,
  {
    now = Date.now(),
    processAlive = true,
    heartbeatTimeoutMs = DEFAULT_HEARTBEAT_TIMEOUT_MS,
    progressTimeoutMs = DEFAULT_PROGRESS_TIMEOUT_MS,
  } = {},
) {
  validateHeartbeat(heartbeat);
  const heartbeatAgeMs = Math.max(0, now - Date.parse(heartbeat.heartbeat_at));
  const progressAgeMs = Math.max(0, now - Date.parse(heartbeat.progress_at));
  const terminal = heartbeat.phase === "settled" || heartbeat.phase === "stopped";

  let status;
  if (!processAlive) {
    status = terminal ? "exited" : "timeout";
  } else if (heartbeatAgeMs > heartbeatTimeoutMs) {
    status = "timeout";
  } else if (terminal) {
    status = "settled";
  } else if (progressAgeMs > progressTimeoutMs) {
    status = "waiting";
  } else if (heartbeat.seq === 0) {
    status = "alive";
  } else {
    status = "progressing";
  }

  return {
    status,
    pid: heartbeat.pid,
    session: heartbeat.session,
    phase: heartbeat.phase,
    seq: heartbeat.seq,
    heartbeat_age_ms: heartbeatAgeMs,
    progress_age_ms: progressAgeMs,
  };
}

export async function inspectHeartbeat(
  file,
  { processAlive = processIsAlive, ...options } = {},
) {
  let heartbeat;
  try {
    heartbeat = await readHeartbeat(file);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return { status: "missing", file };
    }
    return { status: "invalid", file, reason: error.message };
  }
  return classifyHeartbeat(heartbeat, {
    ...options,
    processAlive: processAlive(heartbeat.pid),
  });
}

async function main() {
  const file = process.argv[2];
  if (!file || !path.isAbsolute(file)) {
    throw new Error("usage: node heartbeat_monitor.js /absolute/path/heartbeat.json");
  }
  const heartbeatTimeoutMs = process.argv[3] ? Number(process.argv[3]) : undefined;
  const progressTimeoutMs = process.argv[4] ? Number(process.argv[4]) : undefined;
  for (const value of [heartbeatTimeoutMs, progressTimeoutMs]) {
    if (value !== undefined && (!Number.isFinite(value) || value < 0)) {
      throw new Error("timeout arguments must be non-negative numbers");
    }
  }
  process.stdout.write(`${JSON.stringify(await inspectHeartbeat(file, {
    heartbeatTimeoutMs,
    progressTimeoutMs,
  }))}\n`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`pi-skills heartbeat monitor: ${error.message}\n`);
    process.exitCode = 1;
  });
}

export {
  DEFAULT_HEARTBEAT_TIMEOUT_MS,
  DEFAULT_PROGRESS_TIMEOUT_MS,
};
