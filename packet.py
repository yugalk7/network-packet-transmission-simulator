"""Packet data model."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Packet:
    packet_id: int
    packet_type: str
    timestamp: str
    size: int

    @classmethod
    def create(cls, packet_id, packet_type, size):
        return cls(packet_id, packet_type, datetime.now().strftime("%H:%M:%S.%f")[:-3], size)
