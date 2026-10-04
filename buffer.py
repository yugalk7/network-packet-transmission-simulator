"""Bounded FIFO queue synchronized with a mutex and counting semaphores."""
from collections import deque
import threading


class BoundedPacketBuffer:
    """A non-blocking producer and timed-blocking consumer bounded buffer.

    Producers use ``empty.acquire(False)``.  A failed acquire deliberately
    models a packet drop instead of waiting for space.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = deque()
        self.mutex = threading.Lock()
        self.empty = threading.Semaphore(capacity)
        self.full = threading.Semaphore(0)

    def try_put(self, packet):
        if not self.empty.acquire(blocking=False):
            return False
        with self.mutex:
            self.queue.append(packet)
        self.full.release()
        return True

    def try_get(self, timeout=0.1):
        if not self.full.acquire(timeout=timeout):
            return None
        with self.mutex:
            packet = self.queue.popleft()
        self.empty.release()
        return packet

    def snapshot(self):
        with self.mutex:
            return list(self.queue), len(self.queue), self.mutex.locked()

    def semaphore_values(self):
        # _value is intentionally read only for the educational display;
        # correctness relies on acquire/release, never on these values.
        return self.empty._value, self.full._value
