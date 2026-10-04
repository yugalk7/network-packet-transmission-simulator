"""The game engine (consumer) thread."""
from packet import Packet


def consumer_loop(simulation):
    while not simulation.stop_event.is_set():
        if not simulation.wait_until_running("consumer"):
            break
        simulation.set_status("consumer", "WAITING")
        packet = simulation.buffer.try_get(timeout=0.15)
        if packet is None:
            simulation.set_status("consumer", "BUFFER EMPTY")
            continue
        simulation.set_status("consumer", "RUNNING")
        simulation.interruptible_wait(lambda: 1.0 / simulation.get_rate("consumer"))
        if simulation.stop_event.is_set():
            break
        simulation.statistics.increment("processed")
        simulation.log(f"Packet #{packet.packet_id} processed by game engine")
