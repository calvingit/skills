"""Provider-neutral capability adapter for one Loop ticket."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable, Protocol
from uuid import uuid4
import threading

from .graph.execution_graph.contracts import WORKER_RECEIPT_VERSION

CAPABILITIES = ("implement", "verify", "review")
OUTCOMES = {"completed", "blocked", "failed", "interrupted"}


class Backend(Protocol):
    def create(self, capability: str, bundle: dict[str, Any]) -> Any: ...

    def send(self, handle: Any, bundle: dict[str, Any]) -> None: ...

    def wait(self, handle: Any) -> dict[str, Any]: ...

    def interrupt(self, handle: Any) -> None: ...

    def close(self, handle: Any) -> None: ...


@dataclass(frozen=True)
class CapabilityResult:
    capability: str
    ticket_id: str
    attempt: int
    agent_instance_id: str
    outcome: str
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "ticket_id": self.ticket_id,
            "current_attempt": self.attempt,
            "agent_instance_id": self.agent_instance_id,
            "outcome": self.outcome,
            "payload": self.payload,
        }


@dataclass
class CapabilitySession:
    """In-memory handles for one ticket's multi-round execution."""

    implement_handle: Any | None = None


class CapabilityAdapter:
    """Run implement, verify and review serially through one backend."""

    def __init__(self, backend: Backend):
        self._backend = backend
        self._handles: set[Any] = set()
        self._handles_lock = threading.Lock()

    def interrupt(self) -> None:
        with self._handles_lock:
            handles = list(self._handles)
        for handle in handles:
            self._backend.interrupt(handle)

    def close_session(self, session: CapabilitySession) -> None:
        handle = session.implement_handle
        session.implement_handle = None
        if handle is not None:
            with self._handles_lock:
                self._handles.discard(handle)
            self._backend.close(handle)

    def run(
        self,
        bundle: dict[str, Any],
        *,
        after_capability: Callable[[CapabilityResult], None] | None = None,
        on_event: Callable[[dict[str, Any]], None] | None = None,
        session: CapabilitySession | None = None,
        keep_session: bool = False,
    ) -> dict[str, Any]:
        ticket = bundle.get("ticket")
        if not isinstance(ticket, dict) or not isinstance(ticket.get("id"), str):
            raise ValueError("bundle.ticket.id is required")
        attempt = bundle.get("attempt")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            raise ValueError("bundle.attempt must be a positive integer")

        session = session or CapabilitySession()
        implement, implement_handle = self._run_one(
            "implement",
            bundle,
            ticket["id"],
            attempt,
            after_capability,
            on_event,
            handle=session.implement_handle,
            keep_open=keep_session,
        )
        session.implement_handle = implement_handle if keep_session else None
        results: list[CapabilityResult] = [implement]
        if implement.outcome != "completed":
            return self._aggregate(results)
        implementation_bundle = self._with_handoff(bundle, implement)
        verify, _ = self._run_one("verify", implementation_bundle, ticket["id"], attempt, after_capability, on_event, keep_open=False)
        results.append(verify)
        if verify.outcome == "completed":
            review_bundle = self._with_handoff(implementation_bundle, verify)
            review, _ = self._run_one("review", review_bundle, ticket["id"], attempt, after_capability, on_event, keep_open=False)
            results.append(review)
        return self._aggregate(results)

    @staticmethod
    def _with_handoff(bundle: dict[str, Any], result: CapabilityResult) -> dict[str, Any]:
        handoff = copy.deepcopy(bundle)
        prior = handoff.setdefault("capability_receipts", {})
        if not isinstance(prior, dict):
            raise ValueError("bundle.capability_receipts must be an object")
        prior[result.capability] = result.as_dict()
        return handoff

    def _run_one(
        self,
        capability: str,
        bundle: dict[str, Any],
        ticket_id: str,
        attempt: int,
        after_capability: Callable[[CapabilityResult], None] | None,
        on_event: Callable[[dict[str, Any]], None] | None,
        *,
        handle: Any | None = None,
        keep_open: bool = False,
    ) -> tuple[CapabilityResult, Any]:
        capability_bundle = copy.deepcopy(bundle)
        capability_bundle["capability"] = capability
        capability_bundle["allowed_write_scope"] = bundle.get("allowed_write_scope", []) if capability == "implement" else []
        capability_bundle["temporary_write_scope"] = bundle.get("temporary_write_scope", []) if capability != "implement" else []
        if handle is None:
            handle = self._backend.create(capability, capability_bundle)
        with self._handles_lock:
            self._handles.add(handle)
        if on_event is not None:
            on_event({"type": "started", "capability": capability, "ticket_id": ticket_id, "attempt": attempt})
        try:
            self._backend.send(handle, capability_bundle)
            raw = self._backend.wait(handle)
            result = self._result(capability, ticket_id, attempt, handle, raw)
            if after_capability is not None:
                after_capability(result)
            if on_event is not None:
                on_event({"type": "completed", "capability": capability, "outcome": result.outcome})
            return result, handle
        except Exception:
            if on_event is not None:
                on_event({"type": "failed", "capability": capability})
            self._backend.interrupt(handle)
            self._backend.close(handle)
            raise
        finally:
            with self._handles_lock:
                self._handles.discard(handle)
            if not keep_open:
                self._backend.close(handle)

    @staticmethod
    def _result(capability: str, ticket_id: str, attempt: int, handle: Any, raw: dict[str, Any]) -> CapabilityResult:
        if not isinstance(raw, dict):
            raise ValueError("backend result must be an object")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            raise ValueError("backend result has an unsupported outcome")
        payload = raw.get("payload", {})
        if not isinstance(payload, dict):
            raise ValueError("backend result payload must be an object")
        instance_id = getattr(handle, "agent_instance_id", None) or uuid4().hex
        return CapabilityResult(capability, ticket_id, attempt, instance_id, outcome, payload)

    @staticmethod
    def _aggregate(results: list[CapabilityResult]) -> dict[str, Any]:
        completed = all(result.outcome == "completed" for result in results)
        failure = next((result.outcome for result in results if result.outcome != "completed"), None)
        payloads = {result.capability: result.payload for result in results}
        implement = payloads.get("implement", {})
        verify = payloads.get("verify", {})
        review = payloads.get("review", {})
        unverified_scope = []
        acceptance_protocol_gaps = []
        blocking_findings = []
        non_blocking_findings = []
        for payload in payloads.values():
            if isinstance(payload, dict):
                for key, target in (("unverified_scope", unverified_scope), ("acceptance_protocol_gaps", acceptance_protocol_gaps), ("blocking_findings", blocking_findings), ("non_blocking_findings", non_blocking_findings)):
                    value = payload.get(key, [])
                    if not isinstance(value, list):
                        raise ValueError(f"{key} must be an array")
                    target.extend(value)
                if not isinstance(payload.get("unverified", []), list) or any(not isinstance(value, str) for value in payload.get("unverified", [])):
                    raise ValueError("unverified must be a string array")
        receipt = {
            "schema_version": WORKER_RECEIPT_VERSION,
            "outcome": "completed" if completed and len(results) == len(CAPABILITIES) else (failure or results[-1].outcome),
            "ticket_id": results[0].ticket_id,
            "current_attempt": results[0].attempt,
            "landed_changes": implement.get("landed_changes", []),
            "acceptance_evidence": verify.get("acceptance_evidence", []),
            "verification": verify.get("verification", []),
            "simplification": implement.get("simplification", {"result": "blocked"}),
            "review": review.get("review", {"contract": "failed", "change_surface": "failed", "exploratory": "failed", "protocol_health": "not_triggered"}),
            "blocking_findings": blocking_findings,
            "non_blocking_findings": non_blocking_findings,
            "acceptance_protocol_gaps": acceptance_protocol_gaps,
            "unverified_scope": unverified_scope,
            "blocker": next((payload["blocker"] for payload in payloads.values() if payload.get("blocker") is not None), None),
            "unverified": list(dict.fromkeys(value for payload in payloads.values() if isinstance(payload, dict) for value in payload.get("unverified", []) if isinstance(value, str))),
        }
        return {
            "outcome": receipt["outcome"],
            "capabilities": [result.as_dict() for result in results],
            "receipt": receipt,
        }
