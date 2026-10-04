# Network Packet Transmission Simulator

A Python/Tkinter Operating Systems mini-project that demonstrates the bounded-buffer Producer–Consumer problem through network packet reception in an online competitive game.

## Objective

The simulator shows a network receiver (Producer) generating game packets, a finite receive queue (shared buffer), and the game engine (Consumer) processing packets concurrently. It makes buffer saturation, overflow, and packet loss visible in real time.

## Real-world mapping

| Operating-system concept | Game-networking model |
|---|---|
| Producer thread | Network packet receiver |
| Bounded shared buffer | Finite packet queue / receive buffer |
| Consumer thread | Game engine networking processor |
| Produced item | Movement, shoot, health, or game-state packet |
| Full buffer | Receive-buffer overflow |
| Dropped item | Lost network packet |

## Architecture

`main.py` starts the Tkinter interface. `Simulation` owns one real Producer `threading.Thread` and one real Consumer `threading.Thread`. `BoundedPacketBuffer` contains a FIFO queue, a mutex, and `empty` / `full` counting semaphores. Worker threads send event strings to a thread-safe `queue.Queue`; Tkinter’s main thread reads this queue via `after()`, so worker threads never touch widgets.

## Synchronization algorithm

The buffer begins with `empty = capacity` and `full = 0`.

**Producer:** create packet → attempt `empty.acquire(False)` → if successful, lock mutex and append → unlock mutex → `full.release()`. If the non-blocking acquire fails, the buffer is full: the packet is dropped, instead of waiting. This intentional change models packet loss at a finite receive buffer.

**Consumer:** wait (with a short timeout, so shutdown is responsive) for `full.acquire()` → lock mutex and remove the oldest packet → unlock mutex → `empty.release()` → spend the configured processing time on it.

The mutex prevents concurrent buffer mutation. Semaphores prevent removing from an empty queue or inserting beyond capacity. Statistics have their own lock. Threads are stopped with an event and joined during Reset/window close, preventing uncontrolled duplicate threads.

## Calculations

`Packet Loss % = Dropped Packets / Generated Packets × 100`

`Buffer Utilization % = Current Buffer Size / Buffer Capacity × 100`

`Throughput = Processed Packets / Simulation Time`

## Run

Requirements: Python 3.9+ with Tkinter (standard library). No internet connection or third-party package is required.

```bash
cd network_packet_simulator
python3 main.py
```

## Controls and scenarios

Start creates exactly one Producer thread and one Consumer thread. Pause freezes both, retaining queued packets; Resume continues them. Reset terminates threads safely, empties the queue, clears graph/history/log/statistics, and restores defaults. Rates can be edited while running.

| Preset | Buffer | Producer | Consumer | Expected result |
|---|---:|---:|---:|---|
| Normal Traffic | 10 | 5/s | 5/s | Stable queue, little or no loss |
| High Network Traffic | 10 | 20/s | 5/s | Queue fills, overflow, loss rises |
| Fast Consumer | 10 | 5/s | 20/s | Mostly empty queue, no overflow |
| Small Buffer | 3 | 10/s | 5/s | Frequent overflow and higher loss |

## Educational takeaway

A higher producer rate fills a limited buffer faster than a consumer can drain it. Increasing buffer capacity can absorb bursts, but it is not a replacement for adequate consumer throughput; a sustained rate mismatch still causes drops. Synchronization is essential because unsynchronized queue access can produce races, corrupted data, or incorrect counters.
