import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

const DEFAULT_INTERVAL_MS = 5000;
const MIN_PROGRESS_WRITE_INTERVAL_MS = 250;
const PHASES = new Set([
  "starting",
  "running",
  "provider_wait",
  "output",
  "tool_running",
  "tool_finished",
  "turn_finished",
  "settled",
  "stopped",
  "error",
]);

function configuredPath() {
  const value = process.env.PI_SKILLS_HEARTBEAT_FILE;
  if (!value) return null;
  if (!path.isAbsolute(value)) {
    throw new Error("PI_SKILLS_HEARTBEAT_FILE must be an absolute path");
  }
  return path.resolve(value);
}

function intervalMs() {
  const value = Number.parseInt(process.env.PI_SKILLS_HEARTBEAT_INTERVAL_MS ?? "", 10);
  return Number.isFinite(value) && value >= 250 ? value : DEFAULT_INTERVAL_MS;
}

function sessionId(ctx) {
  let sessionFile = "";
  try {
    sessionFile = ctx.sessionManager?.getSessionFile?.() ?? "";
  } catch {
    sessionFile = "";
  }
  return crypto
    .createHash("sha256")
    .update(sessionFile || `${ctx.cwd ?? process.cwd()}:${process.pid}`)
    .digest("hex")
    .slice(0, 16);
}

async function writeAtomically(file, content) {
  await fs.mkdir(path.dirname(file), { recursive: true, mode: 0o700 });
  const temp = `${file}.${process.pid}.${crypto.randomBytes(6).toString("hex")}.tmp`;
  try {
    await fs.writeFile(temp, content, { encoding: "utf8", mode: 0o600 });
    await fs.rename(temp, file);
  } finally {
    await fs.rm(temp, { force: true });
  }
}

export default function heartbeat(pi) {
  const file = configuredPath();
  if (!file) return;

  let ctx;
  let timer = null;
  let writeChain = Promise.resolve();
  let state;
  let lastProgressWriteAt = 0;
  let writeFailureReported = false;

  function reportWriteFailure(error) {
    if (writeFailureReported) return;
    writeFailureReported = true;
    process.stderr.write(`pi-skills heartbeat write failed: ${String(error?.message ?? error)}\n`);
  }

  function persist(phase, progress = true, extra = {}) {
    const nowMs = Date.now();
    const now = new Date(nowMs).toISOString();
    state = {
      ...state,
      ...extra,
      phase,
      heartbeat_at: now,
      ...(progress
        ? { seq: state.seq + 1, progress_at: now }
        : {}),
    };
    if (progress) lastProgressWriteAt = nowMs;
    const snapshot = `${JSON.stringify(state)}\n`;
    const operation = writeChain.then(() => writeAtomically(file, snapshot));
    writeChain = operation.catch((error) => {
      reportWriteFailure(error);
    });
    return operation;
  }

  function persistProgress(phase, extra = {}) {
    if (Date.now() - lastProgressWriteAt < MIN_PROGRESS_WRITE_INTERVAL_MS) {
      return Promise.resolve();
    }
    return persist(phase, true, extra);
  }

  function startTimer() {
    if (timer) return;
    timer = setInterval(() => {
      persist(state.phase, false).catch(() => {});
    }, intervalMs());
    timer.unref?.();
  }

  function stopTimer() {
    if (!timer) return;
    clearInterval(timer);
    timer = null;
  }

  pi.on("session_start", async (_event, nextCtx) => {
    stopTimer();
    ctx = nextCtx;
    const workingDirectory = path.resolve(ctx.cwd ?? process.cwd());
    if (file === workingDirectory || file.startsWith(`${workingDirectory}${path.sep}`)) {
      throw new Error("PI_SKILLS_HEARTBEAT_FILE must be outside the target repository");
    }
    state = {
      schema: 1,
      pid: process.pid,
      session: sessionId(ctx),
      seq: 0,
      heartbeat_at: new Date().toISOString(),
      progress_at: new Date().toISOString(),
      phase: "starting",
      turn: null,
    };
    await persist("starting");
  });

  pi.on("agent_start", async () => {
    startTimer();
    await persist("running");
  });

  pi.on("turn_start", async (event) => {
    startTimer();
    await persist("running", true, {
      turn: Number.isInteger(event.turnIndex) ? event.turnIndex : state.turn,
    });
  });

  pi.on("before_provider_request", async () => {
    await persist("provider_wait");
  });

  pi.on("after_provider_response", async () => {
    await persist("output");
  });

  pi.on("message_update", async () => {
    await persistProgress("output");
  });

  pi.on("tool_execution_start", async (event) => {
    await persist("tool_running", true, {
      tool: typeof event.toolName === "string" ? event.toolName : undefined,
    });
  });

  pi.on("tool_execution_update", async (event) => {
    await persistProgress("tool_running", {
      tool: typeof event.toolName === "string" ? event.toolName : state.tool,
    });
  });

  pi.on("tool_execution_end", async (event) => {
    await persist("tool_finished", true, {
      tool: typeof event.toolName === "string" ? event.toolName : state.tool,
    });
  });

  pi.on("turn_end", async (event) => {
    await persist("turn_finished", true, {
      turn: Number.isInteger(event.turnIndex) ? event.turnIndex : state.turn,
    });
  });

  pi.on("agent_settled", async () => {
    stopTimer();
    await persist("settled");
  });

  pi.on("session_shutdown", async () => {
    stopTimer();
    if (state) await persist("stopped");
  });
}

export { DEFAULT_INTERVAL_MS, PHASES };
