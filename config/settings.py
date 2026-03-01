# Global configuration constants

from typing import Any

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
BACKGROUND_COLOR = (240, 240, 240)

# Physics
DELTA_TIME = 1.0 / FPS
FRICTION = 0.95
PIXEL_SCALE = 1.0

# Performance
MAX_ENTITIES = 1000
SPATIAL_HASH_CELL_SIZE = 50
UPDATE_NEIGHBORS_EVERY_N_FRAMES = 5
TARGET_FPS = 60
NEIGHBOR_UPDATE_INTERVAL = 0.1  # 10Hz sensing updates

# Colors
COLOR_BACKGROUND = (15, 20, 25)  # Dark Tactical HUD Background
COLOR_BOT = (50, 205, 50)        # Neon Green (Bot)
COLOR_POD = (0, 191, 255)        # Deep Water Cyan (Pod)
COLOR_DRONE = (255, 140, 0)      # Amber / Orange (Drone)
COLOR_TARGET = (255, 50, 50)     # High Alert Red
COLOR_OBSTACLE = (80, 90, 100)   # Slate Grey
COLOR_PHEROMONE = (0, 255, 0, 40) # Digital Signal Grid
COLOR_WHITE = (230, 240, 250)    # Off-white / Ice for text
COLOR_BLACK = (10, 15, 20)       # Deep Black

# Environment colors
COLOR_GROUND = (25, 30, 25)      # Dark Olive / Ground
COLOR_WATER = (10, 25, 45)       # Deep Navy / Water
COLOR_AIR = (20, 25, 35)         # Dark Air / Night Sky


# Swarm Configuration
class SwarmConfig:
    """Configuration constants for swarm agents."""

    # Base swarm agent defaults
    DEFAULT_PERCEPTION_RADIUS = 80.0
    DEFAULT_COMMUNICATION_RADIUS = 120.0
    DEFAULT_MAX_ENERGY = 100.0
    DEFAULT_MESSAGE_COOLDOWN = 0.1
    DEFAULT_AGGRESSIVE_TIMEOUT = 25.0

    # Drone (Air) configuration
    DRONE_MAX_SPEED = 350.0
    DRONE_MAX_FORCE = 180.0
    DRONE_PERCEPTION_RADIUS = 450.0
    DRONE_COMMUNICATION_RADIUS = 600.0
    DRONE_RADIUS = 6.0
    DRONE_STRIKE_COOLDOWN = 5.0
    DRONE_MAX_STRIKE_DAMAGE = 4.0
    DRONE_NORMAL_ATTACK_DAMAGE = 1.0
    DRONE_ATTACK_RANGE = 15.0
    DRONE_STRIKE_RANGE = 250.0
    DRONE_AGGRESSIVE_DAMAGE_BOOST = 1.3
    DRONE_STRIKE_DAMAGE_BOOST = 1.5
    DRONE_ALTITUDE = 100.0

    # Pod (Water) configuration
    POD_MAX_SPEED = 180.0
    POD_MAX_FORCE = 100.0
    POD_PERCEPTION_RADIUS = 350.0
    POD_COMMUNICATION_RADIUS = 500.0
    POD_RADIUS = 5.0
    POD_NORMAL_ATTACK_DAMAGE = 25.0
    POD_BARRAGE_ATTACK_DAMAGE = 80.0
    POD_ATTACK_RANGE = 250.0
    POD_BARRAGE_VOTE_THRESHOLD = 0.6  # 60% majority

    # Bot (Ground) configuration
    BOT_MAX_SPEED = 150.0
    BOT_MAX_FORCE = 80.0
    BOT_PERCEPTION_RADIUS = 250.0
    BOT_COMMUNICATION_RADIUS = 400.0
    BOT_RADIUS = 4.0
    BOT_ATTACK_RANGE = 150.0
    BOT_NORMAL_ATTACK_DAMAGE = 15.0
    BOT_RANDOM_WALK_STRENGTH = 0.4

    # Energy management
    ENERGY_DRAIN_MULTIPLIER = 5.0
    ENERGY_ATTACK_DRAIN_MULTIPLIER = 2.0
    ENERGY_RECOVERY_RATE = 10.0

    # Target detection
    TARGET_POSITION_TOLERANCE = 50.0


# Target configuration
class TargetConfig:
    """Configuration constants for targets."""
    DEFAULT_HEALTH = 100.0
    DEFAULT_RADIUS = 15.0
    DAMAGE_FLASH_DURATION = 0.1


# Environment Configuration
class EnvironmentConfig:
    """Configuration constants for environments."""

    # Air environment
    AIR_WIND_STRENGTH = 0.3
    AIR_WIND_CHANGE_SPEED = 0.5
    AIR_WIND_ANGLE_VARIANCE = 0.5

    # Water environment
    WATER_CURRENT_STRENGTH = 0.2
    WATER_CURRENT_CHANGE_SPEED = 0.3
    WATER_CURRENT_ANGLE_VARIANCE = 0.3

    # Ground environment
    GROUND_FRICTION = 0.95
    GROUND_TERRAIN_VARIANCE = 0.1
