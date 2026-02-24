"""Base SwarmAgent class for all swarm members."""

from src.core.entity import Entity
from src.core.vector2d import Vector2D


class SwarmAgent(Entity):
    """Base class for all swarm members."""

    def __init__(self, position=None, swarm_type="generic", radius=5.0):
        """
        Initialize a swarm agent.

        Args:
            position: Vector2D position
            swarm_type: Type of swarm (ant, fish, bird, etc.)
            radius: Collision radius
        """
        super().__init__(position=position, radius=radius)

        self.swarm_type = swarm_type
        self.perception_radius = 80.0
        self.communication_radius = 120.0

        self.target = None
        self.neighbors = []
        self.energy = 100.0
        self.max_energy = 100.0

        # State machine
        self.state = "idle"  # idle, seeking, attacking, returning

        # Messaging
        self.messages = []
        self.last_message_time = 0
        self.message_cooldown = 0.1

    def sense_environment(self, all_entities, targets_list):
        """
        Detect nearby entities (neighbors) and targets.

        Args:
            all_entities: List of all entities in simulation
            targets_list: List of targets to detect
        """
        # Clear old neighbors and find new ones
        self.neighbors = []
        for entity in all_entities:
            if entity is not self and entity.alive:
                dist = self.distance_to(entity)
                if dist < self.perception_radius and dist > 0:
                    self.neighbors.append((entity, dist))

        # Sort neighbors by distance for easier processing
        self.neighbors.sort(key=lambda x: x[1])

        # Detect nearby targets
        if self.target is None or not self.target.alive:
            self.target = self._select_target(targets_list)

    def _select_target(self, targets_list):
        """
        Select best target based on proximity and health.

        Args:
            targets_list: List of available targets

        Returns:
            Best target or None
        """
        best_score = -1
        best_target = None

        for target in targets_list:
            if target.alive:
                dist = self.distance_to(target)
                if dist < self.perception_radius:
                    # Score based on distance and health
                    dist_score = 1.0 - (dist / self.perception_radius)
                    health_ratio = target.health / target.max_health if target.max_health > 0 else 0
                    health_score = 1.0 - health_ratio  # Prefer weaker targets

                    score = dist_score * 0.6 + health_score * 0.4

                    if score > best_score:
                        best_score = score
                        best_target = target

        return best_target

    def calculate_steering_force(self, environment=None):
        """
        Calculate the steering force based on behaviors.
        Subclasses override this for specific swarm behaviors.

        Args:
            environment: Environment object (for wind/currents)

        Returns:
            Vector2D steering force
        """
        return Vector2D(0, 0)

    def communicate(self, message):
        """
        Broadcast a message to nearby agents.

        Args:
            message: Message dict with type and data
        """
        if self.messages is None:
            self.messages = []
        self.messages.append(message)

    def receive_message(self, message, sender):
        """
        Receive and process a message from another agent.

        Args:
            message: Message dict
            sender: The agent sending the message
        """
        if self.messages is None:
            self.messages = []
        self.messages.append({"type": "received", "data": message, "sender": sender})

    def update_energy(self, delta_time):
        """
        Update energy over time.

        Args:
            delta_time: Time since last update
        """
        # Energy decays based on speed
        speed = self.velocity.magnitude()
        energy_drain = speed * delta_time * 5

        # Additional drain during attacks
        if self.state == "attacking":
            energy_drain *= 2

        self.energy = max(0, self.energy - energy_drain)

        # Recover energy when idle
        if self.state == "idle":
            self.energy = min(self.max_energy, self.energy + delta_time * 10)

    def is_alive(self):
        """Check if agent is alive (has energy and alive flag)."""
        return self.alive and self.energy > 0

    def __repr__(self):
        return f"SwarmAgent(type={self.swarm_type}, state={self.state}, id={self.id})"
