"""The network receiver (producer) thread."""
import random
import time
from packet import Packet
from config import PACKET_TYPES


def producer_loop(simulation):
    while not simulation.stop_event.is_set():
        if not simulation.wait_until_running("producer"):
            break
        packet = Packet.create(simulation.next_packet_id(), random.choice(PACKET_TYPES), random.randint(64, 1400))
        simulation.statistics.increment("generated")
        simulation.log(f"Packet #{packet.packet_id} generated ({packet.packet_type})")
        if simulation.buffer.try_put(packet):
            simulation.log(f"Packet #{packet.packet_id} inserted into buffer")
        else:
            simulation.statistics.increment("dropped")
            simulation.statistics.increment("overflows")
            simulation.set_status("producer", "BUFFER FULL")
            simulation.log(f"Packet #{packet.packet_id} DROPPED — BUFFER OVERFLOW")
        simulation.interruptible_wait(lambda: 1.0 / simulation.get_rate("producer"))
