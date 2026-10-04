"""Thread-safe counters and snapshots used by the user interface."""
import threading
import time


class Statistics:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        with self.lock:
            self.generated = self.processed = self.dropped = self.overflows = 0
            self.started_at = None

    def start(self):
        with self.lock:
            if self.started_at is None:
                self.started_at = time.monotonic()

    def increment(self, name):
        with self.lock:
            setattr(self, name, getattr(self, name) + 1)

    def snapshot(self, buffer_size, capacity):
        with self.lock:
            elapsed = max(0.0, time.monotonic() - self.started_at) if self.started_at else 0.0
            return {
                "generated": self.generated, "processed": self.processed,
                "dropped": self.dropped, "overflows": self.overflows,
                "buffer_size": buffer_size, "capacity": capacity,
                "utilization": (buffer_size / capacity * 100) if capacity else 0,
                "loss": (self.dropped / self.generated * 100) if self.generated else 0,
                "throughput": (self.processed / elapsed) if elapsed else 0,
                "elapsed": elapsed,
            }
