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
SPATIAL_HASH_CELL_SIZE = 100  # 100m cells for realistic scale
UPDATE_NEIGHBORS_EVERY_N_FRAMES = 5
TARGET_FPS = 60
NEIGHBOR_UPDATE_INTERVAL = 0.2  # 5Hz sensing updates (realistic for most sensors)

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

# Map colors
COLOR_MAP_LAND = (40, 50, 40)     # Dark green land
COLOR_MAP_WATER = (10, 30, 60)    # Deep blue ocean
COLOR_MAP_BORDER = (100, 120, 100) # Border outline
COLOR_MAP_CITY = (255, 80, 80)    # City marker
COLOR_MAP_PORT = (255, 150, 50)   # Port marker


# Swarm Configuration
class SwarmConfig:
    """Configuration constants for swarm agents."""

    # Base swarm agent defaults
    DEFAULT_PERCEPTION_RADIUS = 100.0
    DEFAULT_COMMUNICATION_RADIUS = 150.0
    DEFAULT_MAX_ENERGY = 100.0
    DEFAULT_MESSAGE_COOLDOWN = 0.1
    DEFAULT_AGGRESSIVE_TIMEOUT = 30.0

    # Drone (Air) configuration - Realistic quadcopter parameters
    # Max speed ~25 m/s (90 km/h), typical reconnaissance drone
    DRONE_MAX_SPEED = 90.0
    DRONE_MAX_FORCE = 45.0
    # Lidar/sensor range ~200m in good conditions
    DRONE_PERCEPTION_RADIUS = 200.0
    # Mesh network communication range ~300m
    DRONE_COMMUNICATION_RADIUS = 300.0
    DRONE_RADIUS = 0.3  # ~30cm wingspan
    DRONE_STRIKE_COOLDOWN = 10.0  # 10 seconds between strikes
    DRONE_MAX_STRIKE_DAMAGE = 5.0  # Light explosive payload
    DRONE_NORMAL_ATTACK_DAMAGE = 0.5  # Small arms / sensor jamming
    DRONE_ATTACK_RANGE = 15.0
    DRONE_STRIKE_RANGE = 50.0  # Must get close for strike
    DRONE_AGGRESSIVE_DAMAGE_BOOST = 1.3
    DRONE_STRIKE_DAMAGE_BOOST = 1.5
    DRONE_ALTITUDE = 100.0

    # Pod (Water) configuration - Realistic UUV (Unmanned Underwater Vehicle)
    # Typical UUV speed ~2-4 knots (1-2 m/s), some can do 6 knots
    POD_MAX_SPEED = 3.0
    POD_MAX_FORCE = 1.5
    # Underwater sonar range ~500m in good conditions
    POD_PERCEPTION_RADIUS = 150.0
    # Acoustic modem range ~1km
    POD_COMMUNICATION_RADIUS = 200.0
    POD_RADIUS = 0.2  # ~20cm diameter
    POD_NORMAL_ATTACK_DAMAGE = 1.0  # Light torpedo
    POD_BARRAGE_ATTACK_DAMAGE = 3.0  # Full torpedo
    POD_ATTACK_RANGE = 30.0
    POD_BARRAGE_VOTE_THRESHOLD = 0.6  # 60% majority

    # Bot (Ground) configuration - Realistic UGV (Unmanned Ground Vehicle)
    # Typical patrol speed ~1-2 m/s
    BOT_MAX_SPEED = 2.0
    BOT_MAX_FORCE = 1.0
    # Ground robot sensor range ~50-100m
    BOT_PERCEPTION_RADIUS = 80.0
    # Ground mesh network ~100m
    BOT_COMMUNICATION_RADIUS = 100.0
    BOT_RADIUS = 0.3  # ~60cm footprint
    BOT_ATTACK_RANGE = 20.0
    BOT_NORMAL_ATTACK_DAMAGE = 0.8
    BOT_RANDOM_WALK_STRENGTH = 0.3

    # Energy management - Realistic battery life
    ENERGY_DRAIN_MULTIPLIER = 2.0  # Lower drain rate
    ENERGY_ATTACK_DRAIN_MULTIPLIER = 1.5
    ENERGY_RECOVERY_RATE = 5.0  # Solar/charging

    # Target detection
    TARGET_POSITION_TOLERANCE = 20.0


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
