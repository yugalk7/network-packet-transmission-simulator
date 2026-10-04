"""Configuration constants for the simulator."""

DEFAULT_CAPACITY = 10
DEFAULT_PRODUCER_RATE = 5.0
DEFAULT_CONSUMER_RATE = 5.0
MAX_CAPACITY = 20
MAX_RATE = 50.0
PACKET_TYPES = (
    "PLAYER_POSITION", "ENEMY_POSITION", "SHOOT", "MOVEMENT",
    "HEALTH_UPDATE", "GAME_STATE",
)
SCENARIOS = {
    "Normal Traffic": (10, 5.0, 5.0),
    "High Network Traffic": (10, 20.0, 5.0),
    "Fast Consumer": (10, 5.0, 20.0),
    "Small Buffer": (3, 10.0, 5.0),
}
