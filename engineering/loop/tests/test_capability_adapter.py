from __future__ import annotations

import unittest
import threading
import time

from engineering.loop.scripts.capability_adapter import CapabilityAdapter, CapabilitySession


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
            isolation_proof={"dependencies": True, "write_scope": True, "shared_side_effects": True, "integration_order": True},
            concurrency_limit=2,
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

    def test_parallel_verify_and_review_requires_all_isolation_proofs(self) -> None:
        class ParallelBackend(FakeBackend):
            def __init__(self) -> None:
                super().__init__()
                self.active = 0
                self.maximum = 0
                self.lock = threading.Lock()

            def wait(self, handle: str) -> dict[str, object]:
                if handle != "implement-handle":
                    with self.lock:
                        self.active += 1
                        self.maximum = max(self.maximum, self.active)
                    time.sleep(0.03)
                    with self.lock:
                        self.active -= 1
                return super().wait(handle)

        proof = {"dependencies": True, "write_scope": True, "shared_side_effects": True, "integration_order": True}
        serial_backend = ParallelBackend()
        CapabilityAdapter(serial_backend).run({"ticket": {"id": "T001"}, "attempt": 1}, concurrency_limit=2)
        self.assertEqual(serial_backend.maximum, 1)

        parallel_backend = ParallelBackend()
        result = CapabilityAdapter(parallel_backend).run({"ticket": {"id": "T001"}, "attempt": 1}, isolation_proof=proof, concurrency_limit=2)
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(parallel_backend.maximum, 2)

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
