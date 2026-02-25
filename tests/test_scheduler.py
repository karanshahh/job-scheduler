"""Tests for Scheduler."""

import threading
import time

import pytest

from scheduler import Priority, Scheduler, SchedulerConfig


def test_priority_order() -> None:
    """Higher priority jobs run before lower priority."""
    results: list[int] = []
    lock = threading.Lock()

    def record(val: int) -> None:
        with lock:
            results.append(val)

    s = Scheduler(SchedulerConfig(num_workers=1))
    s.start()
    try:
        s.submit(record, 1, priority=Priority.LOW)
        s.submit(record, 2, priority=Priority.HIGH)
        s.submit(record, 3, priority=Priority.MEDIUM)
        time.sleep(0.5)
        assert results == [2, 3, 1]
    finally:
        s.shutdown()


def test_jobs_execute() -> None:
    """All submitted jobs execute."""
    counter = [0]
    lock = threading.Lock()

    def inc() -> None:
        with lock:
            counter[0] += 1

    s = Scheduler(SchedulerConfig(num_workers=4))
    s.start()
    try:
        for _ in range(50):
            s.submit(inc)
        time.sleep(0.5)
        assert counter[0] == 50
    finally:
        s.shutdown()


def test_submit_before_start_raises() -> None:
    s = Scheduler()
    with pytest.raises(RuntimeError):
        s.submit(lambda: None)


def test_race_condition_counter() -> None:
    """Shared counter increment - no lost updates with lock."""
    counter = [0]
    lock = threading.Lock()

    def inc() -> None:
        for _ in range(100):
            with lock:
                counter[0] += 1

    s = Scheduler(SchedulerConfig(num_workers=4))
    s.start()
    try:
        for _ in range(10):
            s.submit(inc)
        time.sleep(1)
        assert counter[0] == 10 * 100
    finally:
        s.shutdown()
