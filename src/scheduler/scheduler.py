"""Concurrent job scheduler with priority queue."""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Any, Callable

from .job import Job, Priority
from .worker_pool import WorkerPool


@dataclass
class SchedulerConfig:
    """Configuration for the job scheduler."""

    num_workers: int = 4


class Scheduler:
    """
    Job scheduler with priority queue and worker pool.
    Higher priority jobs run before lower priority.
    """

    def __init__(self, config: SchedulerConfig | None = None) -> None:
        cfg = config or SchedulerConfig()
        self._job_queue: queue.PriorityQueue[tuple[int, int, Job]] = queue.PriorityQueue()
        self._pool = WorkerPool(cfg.num_workers, self._job_queue)
        self._submit_counter = 0
        self._counter_lock = threading.Lock()
        self._started = False

    def start(self) -> None:
        """Start the worker pool."""
        self._pool.start()
        self._started = True

    def shutdown(self) -> None:
        """Gracefully shutdown: drain queue, wait for in-flight jobs."""
        self._pool.stop()
        self._started = False

    def submit(
        self,
        func: Callable[..., Any],
        *args: Any,
        priority: int | Priority = Priority.MEDIUM,
        **kwargs: Any,
    ) -> None:
        """Submit a job. Higher priority runs first."""
        if not self._started:
            raise RuntimeError("Scheduler not started; call start() first")
        p = int(priority)
        with self._counter_lock:
            c = self._submit_counter
            self._submit_counter += 1
        job = Job(priority=p, func=func, args=args, kwargs=kwargs, _id=c)
        self._job_queue.put((-p, c, job))
