from __future__ import annotations
import json
import shutil
from pathlib import Path
from typing import Any
from .contracts import envelope, problem, validate_shape, validate_string_list
from .store import acquire_write_lock, release_lock, validated_snapshot, atomic_copy

def recover_transaction(
    task_dir: Path, mode: str
) -> tuple[dict[str, object], int]:
    descriptor, _, lock_problems = acquire_write_lock(task_dir)
    if lock_problems:
        return envelope("recover", ok=False, problems=lock_problems), 1
    transaction = task_dir / ".ticket-graph-transaction"
    try:
        manifest_path = transaction / "manifest.json"
        if not manifest_path.is_file():
            problems = [problem("recovery", "missing_transaction", "No recoverable graph transaction exists.")]
            return envelope("recover", ok=False, problems=problems), 1
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            problems = [problem("recovery", "invalid_transaction_manifest", str(exc), path=manifest_path.name)]
            return envelope("recover", ok=False, problems=problems), 1
        manifest_problems = validate_shape(
            manifest,
            {"operation", "state", "original_files", "target_files"},
            path=manifest_path.name,
            ticket_id=None,
            field="",
        )
        original_files = manifest.get("original_files")
        target_files = manifest.get("target_files")
        if (
            manifest_problems
            or manifest.get("state") not in {"prepared", "switching"}
            or not validate_string_list(original_files)
            or not validate_string_list(target_files, require_items=True)
            or any(
                not relative.startswith("tickets/") or ".." in Path(relative).parts
                for relative in [*original_files, *target_files]
            )
        ):
            if not manifest_problems:
                manifest_problems.append(problem("recovery", "invalid_transaction_manifest", "Transaction manifest fields are invalid."))
            return envelope("recover", ok=False, problems=manifest_problems), 1

        if mode == "commit":
            staging = transaction / "staging"
            _, _, staging_problems = validated_snapshot(staging, allow_transaction=True)
            if staging_problems:
                return envelope("recover", ok=False, problems=staging_problems), 1
            for relative in target_files:
                atomic_copy(staging / relative, task_dir / relative)
        elif mode == "rollback":
            original_set = set(original_files)
            for relative in target_files:
                if relative not in original_set:
                    try:
                        (task_dir / relative).unlink()
                    except FileNotFoundError:
                        pass
            for relative in original_files:
                atomic_copy(transaction / "backup" / relative, task_dir / relative)
        else:
            problems = [problem("contract", "invalid_recovery_mode", "Recovery mode must be rollback or commit.")]
            return envelope("recover", ok=False, problems=problems), 1

        _, graph, committed_problems = validated_snapshot(task_dir, allow_transaction=True)
        if committed_problems:
            return envelope("recover", ok=False, graph=graph, problems=committed_problems), 1
        shutil.rmtree(transaction)
        return envelope("recover", ok=True, result={"mode": mode}, graph=graph), 0
    except OSError as exc:
        problems = [problem("recovery", "recovery_failed", str(exc), path=transaction.name)]
        return envelope("recover", ok=False, problems=problems), 1
    finally:
        release_lock(descriptor)
