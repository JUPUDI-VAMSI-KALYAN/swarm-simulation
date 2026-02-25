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

        # Aggressive behavior
        self.aggressive = False
        self.attack_priority = 0  # 0-10, higher = more aggressive
        self.attack_intensity = 1.0  # Multiplier for attack damage

        # Messaging
        self.messages = []
        self.last_message_time = 0
        self.message_cooldown = 0.1
        self.target_position = None  # Store heard target position

        # State management
        self.state_timer = 0  # Track how long in current state
        self.aggressive_timeout = 0  # How long to stay aggressive

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
                            if t.alive and t.position.distance(message.target_pos) < 10:
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
