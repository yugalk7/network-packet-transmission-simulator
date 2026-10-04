# Viva Preparation

1. **What is Producer–Consumer?** A synchronization problem where producers add items to a shared buffer and consumers remove them safely.
2. **What is a producer?** A thread that creates data; here it is the network packet receiver.
3. **What is a consumer?** A thread that takes data for processing; here it is the game engine.
4. **What is a bounded buffer?** A shared queue with a fixed maximum capacity.
5. **Why is synchronization required?** Both threads access the same queue, so access must be coordinated to avoid races.
6. **What is a mutex?** A mutual-exclusion lock allowing only one thread into a critical section at a time.
7. **What is a semaphore?** A synchronization counter used to manage access to limited resources.
8. **What are `empty` and `full`?** `empty` counts free slots; `full` counts packets ready to consume.
9. **What is buffer overflow?** A packet arrives when all buffer slots are occupied.
10. **What is packet loss?** Generated packets that cannot be queued and are dropped.
11. **How is packet loss calculated?** `(dropped / generated) × 100`.
12. **What if Producer speed is greater than Consumer speed?** The queue fills and eventually packets are dropped.
13. **What if Consumer speed is greater than Producer speed?** The queue remains mostly empty and the consumer waits for packets.
14. **What is a race condition?** An incorrect result caused by timing-dependent unsynchronized concurrent access.
15. **What is a deadlock?** Threads wait forever for resources held by each other.
16. **How are races prevented here?** A mutex protects queue operations and semaphores control empty/full availability.
17. **Why are threads used?** Packet arrival and game processing happen independently and concurrently.
18. **How does this represent online gaming?** It models incoming player/state updates waiting for the game engine.
19. **How can packet loss be reduced?** Increase consumer throughput, increase buffer capacity for bursts, or reduce incoming load.
20. **Why does a bigger buffer affect loss?** It can hold more temporary backlog before it becomes full, though it cannot solve a permanent rate mismatch.
