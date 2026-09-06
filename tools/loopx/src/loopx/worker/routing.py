from __future__ import annotations

import shutil
import os

PROVIDERS = ("codex", "claude", "kimi", "pi")


def available_providers() -> list[str]:
    return [provider for provider in PROVIDERS if shutil.which(provider)]


def runtime_provider() -> str | None:
    configured = os.environ.get("LOOPX_RUNTIME_PROVIDER")
    if configured and configured.strip().lower() not in {"0", "false", "no"}:
        if configured not in PROVIDERS:
            raise ValueError(f"Unsupported runtime provider: {configured}")
        return configured
    markers = {
        "codex": ("CODEX_THREAD_ID", "CODEX_SESSION_ID", "CODEX_CI"),
        "claude": ("CLAUDE_CODE", "CLAUDE_CODE_ENTRYPOINT"),
        "kimi": ("KIMI_SESSION_ID", "KIMI_CLI"),
        "pi": ("PI_SESSION_ID", "PI_AGENT"),
    }
    for provider, names in markers.items():
        if any(os.environ.get(name, "").strip().lower() not in {"", "0", "false", "no"} for name in names):
            return provider
    return None


def select_provider(requested: str | None = None) -> tuple[str | None, str, list[str]]:
    available = available_providers()
    if requested is not None:
        if requested not in PROVIDERS:
            raise ValueError(f"Unsupported provider: {requested}")
        if requested not in available:
            return None, f"Explicit provider is unavailable: {requested}", available
        return requested, "explicit provider override", available
    current = runtime_provider()
    if current is not None:
        if current not in available:
            return None, f"Current runtime provider is unavailable: {current}", available
        return current, f"current runtime provider: {current}", available
    if not available:
        return None, "No supported provider executable is available", available
    selected = available[0]
    return selected, f"automatic selection from supported providers: {selected}", available
