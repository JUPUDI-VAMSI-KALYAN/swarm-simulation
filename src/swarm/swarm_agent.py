"""Base SwarmAgent class for all swarm members."""

from typing import Any, Optional
from src.core.entity import Entity
from src.core.vector2d import Vector2D
from config.settings import SwarmConfig


class SwarmAgent(Entity):
    """Base class for all swarm members."""

    def __init__(
        self,
        position: Optional[Vector2D] = None,
        swarm_type: str = "generic",
        radius: float = 5.0
    ) -> None:
        """
        Initialize a swarm agent.

        Args:
            position: Vector2D position
            swarm_type: Type of swarm (ant, fish, bird, etc.)
            radius: Collision radius
        """
        super().__init__(position=position, radius=radius)

        self.swarm_type = swarm_type
        self.perception_radius = SwarmConfig.DEFAULT_PERCEPTION_RADIUS
        self.communication_radius = SwarmConfig.DEFAULT_COMMUNICATION_RADIUS

        self.target: Optional[Any] = None
        self.neighbors: list[tuple[Any, float]] = []
        self.energy = SwarmConfig.DEFAULT_MAX_ENERGY
        self.max_energy = SwarmConfig.DEFAULT_MAX_ENERGY

        self.state: str = "idle"

        self.aggressive = False
        self.attack_priority = 0
        self.attack_intensity = 1.0

        self.messages: list[Any] = []
        self.last_message_time = 0.0
        self.message_cooldown = SwarmConfig.DEFAULT_MESSAGE_COOLDOWN
        self.target_position: Optional[Vector2D] = None

        self.state_timer = 0.0
        self.aggressive_timeout = 0.0

    def sense_environment(
        self,
        all_entities: list[Any],
        targets_list: list[Any]
    ) -> None:
        """
        Detect nearby entities (neighbors) and targets.

        Args:
            all_entities: List of all entities in simulation
            targets_list: List of targets to detect
        """
        if not all_entities:
            return
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

    def calculate_steering_force(
        self,
        neighbors: list[tuple[Any, float]],
        target: Optional[Any],
        max_force: Optional[float] = None
    ) -> Vector2D:
        """
        Calculate the steering force based on behaviors.
        Subclasses override this for specific swarm behaviors.

        Args:
            neighbors: List of (neighbor_entity, distance) tuples
            target: Current target entity (if any)
            max_force: Maximum force magnitude

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

    def receive_message(self, message):
        """
        Queue a message for processing.

        Args:
            message: Message object or dict
        """
        if self.messages is None:
            self.messages = []
        self.messages.append(message)

    def process_messages(self, targets_list=None):
        """
        Process queued messages and update agent state.
        This is the critical integration point for swarm communication.

        Args:
            targets_list: List of targets (for resolving target positions)
        """
        if not self.messages:
            return

        for message in self.messages[:]:  # Copy list to avoid modification during iteration
            # Handle TARGET_FOUND messages
            if hasattr(message, 'msg_type'):
                msg_type_str = message.msg_type.value if hasattr(message.msg_type, 'value') else str(message.msg_type)
            else:
                msg_type_str = message.get('type', '')

            # Message types: target_found, target_location, under_attack, target_destroyed, attack_now
            if 'target' in msg_type_str.lower() or 'location' in msg_type_str.lower():
                # Adopt the target from the message
                if hasattr(message, 'target_pos') and targets_list:
                    self.target_position = message.target_pos
                    # Find actual target by position (may be sent as reference in Message)
                    if hasattr(message, 'target') and message.target:
                        self.target = message.target
                    else:
                        # Search for target at position
                        for t in targets_list:
                            # Allow a much larger tolerance (50px) for position matching via mesh
                            if t.alive and t.position.distance(message.target_pos) < 50:
                                self.target = t
                                break
                    # If we got target, become aggressive and set timeout
                    if self.target is not None:
                        self.aggressive = True
                        self.aggressive_timeout = 25  # Stay aggressive for 25 seconds
                        self.attack_priority = 8
                        self.state = "attacking"  # Go straight to attacking to broadcast message

            # Handle ATTACK_NOW messages - increase aggression
            elif 'attack' in msg_type_str.lower():
                self.aggressive = True
                self.attack_priority = max(self.attack_priority, 9)
                self.state = "attacking"

            # Remove processed message
            self.messages.remove(message)

    def broadcast_to_neighbors(self, neighbors_list, message):
        """
        Broadcast a message to neighboring agents.

        Args:
            neighbors_list: List of (neighbor, distance) tuples
            message: Message to broadcast
        """
        for neighbor, _ in neighbors_list:
            if neighbor.alive:
                neighbor.receive_message(message)

    def update_energy(self, delta_time):
        """
        Update energy over time and manage state transitions.

        Args:
            delta_time: Time since last update
        """
        # Update state timers
        self.state_timer += delta_time

        # Manage aggressive timeout
        if self.aggressive_timeout > 0:
            self.aggressive_timeout -= delta_time
        else:
            # Timeout aggressive state if no target
            if self.aggressive and self.target is None:
                self.aggressive = False
                self.attack_priority = 0
                self.state = "idle"
                self.state_timer = 0

        # Energy decays based on speed
        speed = self.velocity.magnitude()
        # Normalize speed relative to max_speed (0 to 1) so scaling up physics doesn't instantly drain energy
        normalized_speed = speed / max(1.0, float(getattr(self, 'max_speed', 150.0)))
        energy_drain = normalized_speed * delta_time * 5.0

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
