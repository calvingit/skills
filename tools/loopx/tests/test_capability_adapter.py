from __future__ import annotations

import unittest
import threading
import time

from loopx.capability_adapter import CapabilityAdapter, CapabilitySession


class FakeBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, object]]] = []
        self.closed: list[str] = []

    def create(self, capability: str, bundle: dict[str, object]) -> str:
        handle = f"{capability}-handle"
        self.calls.append(("create", capability, bundle))
        return handle

    def send(self, handle: str, bundle: dict[str, object]) -> None:
        self.calls.append(("send", str(bundle["capability"]), bundle))

    def wait(self, handle: str) -> dict[str, object]:
        return {"outcome": "completed", "payload": {"handle": handle}}

    def interrupt(self, handle: str) -> None:
        self.calls.append(("interrupt", handle, {}))

    def close(self, handle: str) -> None:
        self.closed.append(handle)


class CapabilityAdapterTests(unittest.TestCase):
    def test_implement_handle_can_be_reused_across_attempts(self) -> None:
        backend = FakeBackend()
        adapter = CapabilityAdapter(backend)
        session = CapabilitySession()
        bundle = {"ticket": {"id": "T001"}, "attempt": 1}

        adapter.run(bundle, session=session, keep_session=True)
        adapter.run({**bundle, "attempt": 2}, session=session, keep_session=True)

        self.assertEqual([item[1] for item in backend.calls if item[0] == "create"], ["implement", "verify", "review", "verify", "review"])
        self.assertEqual(backend.closed, ["verify-handle", "review-handle", "verify-handle", "review-handle"])
        adapter.close_session(session)
        self.assertEqual(backend.closed[-1], "implement-handle")

    def test_capability_bundles_do_not_share_nested_mutations(self) -> None:
        class MutatingBackend(FakeBackend):
            def send(self, handle: str, bundle: dict[str, object]) -> None:
                super().send(handle, bundle)
                if handle == "verify-handle":
                    bundle["ticket"]["changed_by"] = "verify"  # type: ignore[index]

        backend = MutatingBackend()
        CapabilityAdapter(backend).run(
            {"ticket": {"id": "T001"}, "attempt": 1},
        )

        review_bundle = next(bundle for name, capability, bundle in backend.calls if name == "send" and capability == "review")
        self.assertNotIn("changed_by", review_bundle["ticket"])

    def test_runs_three_capabilities_with_shared_snapshot_and_scoped_writes(self) -> None:
        backend = FakeBackend()
        bundle = {
            "ticket": {"id": "T001"},
            "attempt": 1,
            "snapshot": {"diff": "same"},
            "allowed_write_scope": ["src/"],
        }

        result = CapabilityAdapter(backend).run(bundle)

        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["receipt"]["schema_version"], 1)
        self.assertEqual(result["receipt"]["ticket_id"], "T001")
        self.assertEqual([item[1] for item in backend.calls if item[0] == "create"], ["implement", "verify", "review"])
        self.assertEqual([item["capability"] for item in result["capabilities"]], ["implement", "verify", "review"])
        self.assertEqual(backend.calls[3][2]["snapshot"], backend.calls[5][2]["snapshot"])
        self.assertEqual(backend.calls[1][2]["allowed_write_scope"], ["src/"])
        self.assertEqual(backend.calls[3][2]["allowed_write_scope"], [])
        self.assertEqual(len(backend.closed), 3)

    def test_serial_capabilities_receive_prior_capability_receipts(self) -> None:
        backend = FakeBackend()

        CapabilityAdapter(backend).run({"ticket": {"id": "T001"}, "attempt": 1})

        verify_bundle = next(bundle for name, capability, bundle in backend.calls if name == "send" and capability == "verify")
        review_bundle = next(bundle for name, capability, bundle in backend.calls if name == "send" and capability == "review")
        self.assertEqual(verify_bundle["capability_receipts"]["implement"]["payload"], {"handle": "implement-handle"})
        self.assertEqual(review_bundle["capability_receipts"]["verify"]["payload"], {"handle": "verify-handle"})

    def test_stops_after_a_failed_capability_and_closes_context(self) -> None:
        class FailingBackend(FakeBackend):
            def wait(self, handle: str) -> dict[str, object]:
                if handle == "verify-handle":
                    return {"outcome": "failed", "payload": {"reason": "bad"}}
                return super().wait(handle)

        backend = FailingBackend()
        result = CapabilityAdapter(backend).run({"ticket": {"id": "T001"}, "attempt": 1})

        self.assertEqual(result["outcome"], "failed")
        self.assertEqual([item[1] for item in backend.calls if item[0] == "create"], ["implement", "verify"])
        self.assertEqual(backend.closed, ["implement-handle", "verify-handle"])

    def test_review_waits_for_verification_result(self) -> None:
        class EvidenceBackend(FakeBackend):
            def wait(self, handle):
                if handle == "verify-handle":
                    return {"outcome": "completed", "payload": {"verification": [{"command": "check", "exit_code": 1, "summary": "failure"}]}}
                return super().wait(handle)
        backend = EvidenceBackend()
        CapabilityAdapter(backend).run({"ticket": {"id": "T001"}, "attempt": 1})
        bundle = next(item[2] for item in backend.calls if item[:2] == ("send", "review"))
        self.assertEqual(bundle["capability_receipts"]["verify"]["payload"]["verification"][0]["exit_code"], 1)

    def test_interrupt_cancels_active_handles(self) -> None:
        backend = FakeBackend()
        adapter = CapabilityAdapter(backend)
        handle = backend.create("verify", {})
        with adapter._handles_lock:
            adapter._handles.add(handle)
        adapter.interrupt()
        self.assertIn(("interrupt", "verify-handle", {}), backend.calls)

    def test_emits_lifecycle_events(self) -> None:
        events: list[str] = []
        backend = FakeBackend()
        CapabilityAdapter(backend).run({"ticket": {"id": "T001"}, "attempt": 1}, on_event=lambda event: events.append(event["type"]))
        self.assertEqual(events, ["started", "completed", "started", "completed", "started", "completed"])


if __name__ == "__main__":
    unittest.main()
