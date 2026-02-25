# Job Scheduler

**Concurrent job scheduler with priority queue and worker pool. Demonstrates multi-threading, locks, and race condition handling.**

---

## Overview

Submits jobs (callables) to a priority queue; worker threads pull and execute. Higher priority runs first. Protects shared state with locks.
Graceful shutdown: workers finish current job, then exit on empty queue.

---

## Installation & Usage

```bash
pip install -e .
```

```python
from scheduler import Scheduler, SchedulerConfig, Priority

s = Scheduler(SchedulerConfig(num_workers=4))
s.start()
s.submit(my_func, arg1, priority=Priority.HIGH)
s.submit(other_func, priority=Priority.LOW)
s.shutdown()
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest -v
pytest --cov=src --cov-report=term-missing
```

| Test Suite | Purpose |
|------------|---------|
| `test_scheduler.py` | Priority order (HIGH before MEDIUM before LOW), all jobs execute, submit-before-start raises |
| `test_concurrent.py` | 200 jobs each executes once; priority under load; race condition (10 jobs × 100 increments with lock = 1000) |

**What each validates:** `test_scheduler` — 1 worker runs HIGH before MEDIUM before LOW, 50 jobs all run, submit without start raises. `test_race_condition_counter` — lock prevents lost increments. `test_concurrent` — no duplicate execution, priority ordering under load.

**Coverage: 97%**

---

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **`PriorityQueue` with (-priority, id)** | Python's heap is min-heap; negating priority makes higher values pop first. `id` breaks ties. |
| **Single lock for shared counter in tests** | Demonstrates correct synchronization; without lock, increments are lost. |
| **`get(timeout=0.1)` in workers** | Allows workers to check shutdown flag periodically instead of blocking forever. |
| **Daemon threads** | Process exit kills workers; acceptable for library use. |

---

## Data Flow

```
submit(func, *args, priority) → queue.put((-priority, id, Job))
Worker → queue.get() → job.run()
Shutdown → set event → workers exit on next empty get
```
