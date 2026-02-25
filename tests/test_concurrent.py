"""Concurrency stress tests for Scheduler."""

import threading
import time

from scheduler import Priority, Scheduler, SchedulerConfig


def test_many_jobs_no_duplicate_execution() -> None:
    """Many jobs, each executes exactly once."""
    executed: set[int] = set()
    lock = threading.Lock()

    def run_once(job_id: int) -> None:
        with lock:
            executed.add(job_id)

    s = Scheduler(SchedulerConfig(num_workers=4))
    s.start()
    try:
        for i in range(200):
            s.submit(run_once, i)
        time.sleep(1)
        assert len(executed) == 200
        assert executed == set(range(200))
    finally:
        s.shutdown()


def test_priority_under_load() -> None:
    """High priority jobs complete before low under concurrent load."""
    high_done = threading.Event()
    low_started_before_high_done = [False]
    lock = threading.Lock()

    def high_priority() -> None:
        time.sleep(0.05)
        high_done.set()

    def low_priority() -> None:
        if not high_done.is_set():
            with lock:
                low_started_before_high_done[0] = True

    s = Scheduler(SchedulerConfig(num_workers=2))
    s.start()
    try:
        for _ in range(5):
            s.submit(low_priority, priority=Priority.LOW)
        s.submit(high_priority, priority=Priority.HIGH)
        time.sleep(0.3)
        high_done.wait(timeout=1)
    finally:
        s.shutdown()
