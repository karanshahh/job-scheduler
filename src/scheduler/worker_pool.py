"""Worker pool that consumes jobs from a priority queue."""

from __future__ import annotations

import queue
import threading
from typing import Any

from .job import Job


class WorkerPool:
    """
    Pool of worker threads that pull jobs from a priority queue.
    Uses (-priority, id) so higher priority runs first.
    """

    def __init__(self, num_workers: int, job_queue: queue.PriorityQueue[tuple[int, int, Job]]) -> None:
        if num_workers < 1:
            raise ValueError("num_workers must be >= 1")
        self._num_workers = num_workers
        self._queue = job_queue
        self._workers: list[threading.Thread] = []
        self._shutdown = threading.Event()
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        """Start worker threads."""
        with self._lock:
            if self._running:
                return
            self._shutdown.clear()
            self._running = True
            for i in range(self._num_workers):
                t = threading.Thread(target=self._worker, name=f"worker-{i}", daemon=True)
                self._workers.append(t)
                t.start()

    def stop(self) -> None:
        """Signal workers to stop. Workers finish current job, then exit on next empty get."""
        self._shutdown.set()
        with self._lock:
            for t in self._workers:
                t.join(timeout=5)
            self._workers.clear()
            self._running = False

    def _worker(self) -> None:
        while True:
            if self._shutdown.is_set():
                return
            try:
                _, _, job = self._queue.get(timeout=0.1)
                job.run()
            except queue.Empty:
                continue
