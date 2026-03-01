"""Drone swarm implementation with tactical formation and strike behaviors."""

import logging
import math
import random
from typing import Any, Optional

from src.swarm.swarm_agent import SwarmAgent
from src.intelligence.tactical_formation import TacticalFormationBehavior
from src.core.vector2d import Vector2D
from config.settings import COLOR_DRONE, SwarmConfig

logger = logging.getLogger(__name__)


class Drone(SwarmAgent):
    """Intelligent combat drone that aligns in formation and coordinates payload strikes."""

    def __init__(
        self,
        position: Optional[Vector2D] = None,
        formation_behavior: Optional[TacticalFormationBehavior] = None
    ) -> None:
        """
        Initialize a drone.

        Args:
            position: Starting position (Vector2D)
            formation_behavior: TacticalFormationBehavior instance
        """
        super().__init__(position=position, swarm_type="drone", radius=SwarmConfig.DRONE_RADIUS)

        self.max_speed = SwarmConfig.DRONE_MAX_SPEED
        self.max_force = SwarmConfig.DRONE_MAX_FORCE
        self.perception_radius = SwarmConfig.DRONE_PERCEPTION_RADIUS
        self.communication_radius = SwarmConfig.DRONE_COMMUNICATION_RADIUS

        self.formation_behavior = formation_behavior or TacticalFormationBehavior()

        self.altitude = SwarmConfig.DRONE_ALTITUDE
        self.strike_cooldown = 0.0
        self.is_striking = False
        self.strike_target = None
        self.max_strike_damage = SwarmConfig.DRONE_MAX_STRIKE_DAMAGE

        self.normal_attack_damage = SwarmConfig.DRONE_NORMAL_ATTACK_DAMAGE
        self.attack_range = SwarmConfig.DRONE_ATTACK_RANGE

        self.color = COLOR_DRONE

    def calculate_steering_force(
        self,
        neighbors: list[tuple[Any, float]],
        target: Optional[Any],
        max_force: Optional[float] = None
    ) -> Vector2D:
        """
        Calculate steering force based on tactical formation and target seeking.

        Args:
            neighbors_list: List of (neighbor, distance) tuples
            target: Current target (if any)
            max_force: Maximum force magnitude (uses self.max_force if None)

        Returns:
            Vector2D steering force
        """
        if max_force is None:
            max_force = self.max_force

        # Use tactical grid formation behavior
        steering = self.formation_behavior.update_formation_member(
            self, neighbors, target,
            self.perception_radius, max_force
        )

        if math.isnan(steering.x) or math.isnan(steering.y):
            logger.warning(f"Drone {self.id} generated NaN steering force, using fallback")
            return Vector2D(0, 0)

        return steering

    def update_strike_attack(self, delta_time):
        """
        Update strike attack cooldown and state.

        Args:
            delta_time: Time since last update
        """
        if self.strike_cooldown > 0:
            self.strike_cooldown -= delta_time
        else:
            self.strike_cooldown = 0
            self.is_striking = False

    def can_strike(self):
        """Check if drone can currently initiate a strike."""
        return self.strike_cooldown <= 0 and not self.is_striking

    def initiate_strike(self, target):
        """
        Start a kamikaze/payload strike toward target.

        Args:
            target: Target entity to strike
        """
        if self.can_strike():
            self.is_striking = True
            self.strike_target = target
            self.strike_cooldown = 5.0  # 5 second cooldown
            self.state = "attacking"
            return True
        return False

    def perform_strike(self, target, delta_time):
        """
        Execute strike attack movement.

        Args:
            target: Target entity
            delta_time: Time since last update
        """
        if not self.is_striking or not target.alive:
            self.is_striking = False
            self.state = "idle"
            return 0

        dist = self.distance_to(target)

        # Accelerate toward target during strike
        if dist > 0:
            direction = self.get_direction_to(target)
            strike_force = direction * self.max_force * 2.5
            self.apply_force(strike_force)

        # Check for hit
        if dist < target.radius + self.radius:
            self.is_striking = False
            self.state = "idle"
            # Apply aggressive damage multiplier to strike attacks
            strike_damage = self.max_strike_damage * self.attack_intensity
            if self.aggressive:
                strike_damage *= 1.3  # 30% damage boost when aggressive
            return strike_damage

        return 0

    def perform_normal_attack(self, target):
        """
        Perform normal payload logic on target.

        Args:
            target: Target entity

        Returns:
            Damage dealt (0 if out of range)
        """
        dist = self.distance_to(target)
        if dist < self.attack_range:
            # Aggressive behavior - increased damage when aggressive
            damage = self.normal_attack_damage * self.attack_intensity
            if self.aggressive:
                damage *= 1.5  # 50% more damage when aggressive
                self.state = "attacking"
            return damage
        return 0

    def update(
        self,
        delta_time: float,
        neighbors: list[tuple[Any, float]],
        target: Optional[Any],
        targets_list: Optional[list[Any]] = None,
        obstacles: Optional[list[Any]] = None
    ) -> None:
        """
        Update drone state and physics.

        Args:
            delta_time: Time since last update
            neighbors: List of neighbor drones
            target: Current target (if any)
            targets_list: List of all targets (for message processing)
            obstacles: List of obstacles for avoidance
        """
        # Process incoming messages from swarm communication with targets list
        self.process_messages(targets_list)

        # Update strike state
        self.update_strike_attack(delta_time)

        # Calculate steering
        steering = self.calculate_steering_force(neighbors, target)
        self.apply_force(steering)

        import math
        # Prevent physics explosion on self.acceleration
        if math.isnan(self.acceleration.x) or math.isnan(self.acceleration.y):
            self.acceleration = Vector2D(0, 0)

        # Parent update handles velocity and position
        super().update(delta_time)
        
        # Prevent physics explosion on self.velocity
        if math.isnan(self.velocity.x) or math.isnan(self.velocity.y):
            self.velocity = Vector2D(0, 0)
        # Prevent physics explosion on self.position
        if math.isnan(self.position.x) or math.isnan(self.position.y):
            self.position = Vector2D(100, 100) # Reset on screen

        # Wrap around screen edges
        from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
        self.wrap_edges(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update energy and manage state timeouts
        self.update_energy(delta_time)

        # Manage state transitions
        if self.energy <= 0:
            self.state = "idle"

    def __repr__(self):
        return (f"Drone(id={self.id}, pos={self.position}, "
                f"state={self.state}, striking={self.is_striking})")
