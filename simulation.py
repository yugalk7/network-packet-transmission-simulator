"""Coordinator for lifecycle, shared state, and worker threads."""
import queue
import threading
import time
from buffer import BoundedPacketBuffer
from consumer import consumer_loop
from producer import producer_loop
from statistics import Statistics
from config import DEFAULT_CAPACITY, DEFAULT_CONSUMER_RATE, DEFAULT_PRODUCER_RATE


class Simulation:
    def __init__(self):
        self.events = queue.Queue()
        self.control_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.run_event = threading.Event()
        self.threads = []
        self.reset_state(DEFAULT_CAPACITY, DEFAULT_PRODUCER_RATE, DEFAULT_CONSUMER_RATE)

    def reset_state(self, capacity, producer_rate, consumer_rate):
        self.buffer = BoundedPacketBuffer(capacity)
        self.statistics = Statistics()
        self.packet_id = 0
        self.rates = {"producer": producer_rate, "consumer": consumer_rate}
        self.statuses = {"producer": "STOPPED", "consumer": "STOPPED"}

    def start(self, capacity, producer_rate, consumer_rate):
        if self.is_alive():
            self.run_event.set()
            return
        self.stop(join=True)
        self.stop_event = threading.Event()
        self.run_event.set()
        self.reset_state(capacity, producer_rate, consumer_rate)
        self.statistics.start()
        self.statuses = {"producer": "RUNNING", "consumer": "RUNNING"}
        self.threads = [threading.Thread(target=producer_loop, args=(self,), name="PacketProducer", daemon=True),
                        threading.Thread(target=consumer_loop, args=(self,), name="GameConsumer", daemon=True)]
        for thread in self.threads:
            thread.start()
        self.log("Simulation started: mutex + empty/full semaphores active")

    def pause(self):
        self.run_event.clear()
        self.set_status("producer", "PAUSED")
        self.set_status("consumer", "PAUSED")
        self.log("Simulation paused; buffer contents preserved")

    def resume(self):
        if self.is_alive():
            self.run_event.set()
            self.set_status("producer", "RUNNING")
            self.set_status("consumer", "RUNNING")
            self.log("Simulation resumed")

    def stop(self, join=True):
        self.stop_event.set()
        self.run_event.set()
        if join:
            for thread in self.threads:
                if thread.is_alive():
                    thread.join(timeout=0.5)
        self.threads = []

    def is_alive(self):
        return any(thread.is_alive() for thread in self.threads)

    def next_packet_id(self):
        with self.stats_lock:
            self.packet_id += 1
            return self.packet_id

    def get_rate(self, role):
        with self.control_lock:
            return max(0.1, self.rates[role])

    def set_rates(self, producer, consumer):
        with self.control_lock:
            self.rates.update(producer=producer, consumer=consumer)

    def set_status(self, role, status):
        with self.control_lock:
            self.statuses[role] = status

    def wait_until_running(self, role):
        while not self.stop_event.is_set() and not self.run_event.wait(0.1):
            self.set_status(role, "PAUSED")
        return not self.stop_event.is_set()

    def interruptible_wait(self, seconds_factory):
        # Only count active simulation time.  Thus Pause freezes generation
        # and processing rather than allowing an in-progress timer to finish.
        remaining = seconds_factory()
        previous = time.monotonic()
        while not self.stop_event.is_set() and remaining > 0:
            if not self.run_event.wait(0.05):
                previous = time.monotonic()
                continue
            now = time.monotonic()
            remaining -= now - previous
            previous = now

    def log(self, text):
        self.events.put((time.strftime("%H:%M:%S"), text))

    def snapshot(self):
        packets, size, locked = self.buffer.snapshot()
        data = self.statistics.snapshot(size, self.buffer.capacity)
        empty, full = self.buffer.semaphore_values()
        with self.control_lock:
            data.update(packets=packets, mutex_locked=locked, empty=empty, full=full,
                        producer_rate=self.rates["producer"], consumer_rate=self.rates["consumer"],
                        producer_status=self.statuses["producer"], consumer_status=self.statuses["consumer"])
        return data
