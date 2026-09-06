import fs from "node:fs";
import path from "node:path";

const FILE_TOOLS = new Set(["read", "grep", "find", "ls", "edit", "write"]);
const DANGEROUS_BASH = [
  ["privilege escalation", /\b(?:sudo|doas)\b/i],
  ["recursive deletion", /\brm\b[^\n;&|]*(?:--recursive|-[a-z]*r[a-z]*)/i],
  ["deletion outside worktree", /\brm\b[^\n;&|]*(?:\s\/|\s~\/|\s\.\.\/)/i],
  ["find -delete", /\bfind\b[^\n;&|]*\s-delete\b/i],
  [
    "Git state mutation",
    /\bgit\b(?:\s+(?:(?:-C|-c|--git-dir|--work-tree)\s+\S+|--\S+))*\s+(?:add|commit|push|reset|clean|checkout|restore|switch|branch|tag|rebase|merge|cherry-pick|revert|stash|worktree|config|pull|fetch|remote|gc)\b/i,
  ],
  ["disk or system control", /\b(?:diskutil|mkfs(?:\.\w+)?|fdisk|shutdown|reboot|halt|launchctl)\b/i],
  ["broad process termination", /\b(?:killall|pkill)\b|\bkill\s+-9\b/i],
  ["ownership or recursive permission change", /\bchown\b|\bchmod\b[^\n;&|]*(?:\s-R\b|\b777\b)/i],
  [
    "secondary shell or eval",
    /\b(?:bash|sh|zsh)\s+-c\b|\b(?:python\d*|node|ruby|perl)\s+(?:-c|-e)\b|\beval\b|\bsource\b|\|\s*(?:bash|sh|zsh)\b/i,
  ],
  ["redirection outside worktree", /(?:^|\s)(?:\d?>|\d?>>)\s*(?:\/|~\/|\.\.\/)/i],
];

function isInside(root, target) {
  const relative = path.relative(root, target);
  return relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== "..");
}

function realExistingParent(target) {
  let current = target;
  while (!fs.existsSync(current)) {
    const parent = path.dirname(current);
    if (parent === current) return current;
    current = parent;
  }
  return fs.realpathSync(current);
}

function allowedPaths(root) {
  let values;
  try {
    values = JSON.parse(process.env.PI_SKILLS_ALLOWED_PATHS ?? "[]");
  } catch (error) {
    throw new Error(`PI_SKILLS_ALLOWED_PATHS must contain valid JSON: ${error.message}`);
  }
  if (!Array.isArray(values) || values.length === 0) {
    throw new Error("PI_SKILLS_ALLOWED_PATHS must be a non-empty JSON array");
  }
  return values.map((item) => {
    if (typeof item !== "string" || !item || path.isAbsolute(item)) {
      throw new Error("PI_SKILLS_ALLOWED_PATHS entries must be non-empty relative paths");
    }
    const target = path.resolve(root, item);
    if (!isInside(root, target) || item.split(/[\\/]/).includes(".git")) {
      throw new Error(`PI_SKILLS_ALLOWED_PATHS entry escapes the worktree: ${item}`);
    }
    return target;
  });
}

export default function worktreeGuard(pi) {
  const configuredRoot = process.env.PI_SKILLS_WORKTREE;
  if (!configuredRoot) throw new Error("PI_SKILLS_WORKTREE is required");
  const root = fs.realpathSync(path.resolve(configuredRoot));
  const gitMetadata = path.resolve(root, ".git");
  if (!fs.lstatSync(gitMetadata).isFile()) {
    throw new Error("PI_SKILLS_WORKTREE must be a linked Git worktree whose .git is a file");
  }
  const allowed = allowedPaths(root);

  pi.on("tool_call", (event) => {
    if (event.toolName === "bash") {
      const command = event.input?.command;
      if (typeof command !== "string") {
        return { block: true, reason: "pi-skills: bash requires a command" };
      }
      const blocked = DANGEROUS_BASH.find(([, pattern]) => pattern.test(command));
      if (blocked) {
        return { block: true, reason: `pi-skills: blocked high-risk command (${blocked[0]})` };
      }
      return;
    }
    if (!FILE_TOOLS.has(event.toolName)) return;
    const rawPath = event.input?.path ?? event.input?.file_path;
    const mutates = event.toolName === "edit" || event.toolName === "write";
    if (rawPath === undefined && !mutates) return;
    if (typeof rawPath !== "string") {
      return { block: true, reason: `pi-skills: ${event.toolName} requires a path` };
    }
    const target = path.resolve(root, rawPath.replace(/^@/, ""));
    if (
      !isInside(root, target) ||
      !isInside(root, realExistingParent(target)) ||
      isInside(gitMetadata, target) ||
      (mutates && !allowed.some((entry) => isInside(entry, target)))
    ) {
      return { block: true, reason: `pi-skills: disallowed ${event.toolName} path: ${rawPath}` };
    }
  });
}
