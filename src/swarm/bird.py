"""Bird swarm implementation with flocking and diving behaviors."""

import random
import math
from src.swarm.swarm_agent import SwarmAgent
from src.intelligence.flocking import FlockingBehavior
from src.core.vector2d import Vector2D
from config.settings import COLOR_BIRD


class Bird(SwarmAgent):
    """Intelligent bird that flocks and coordinates attacks."""

    def __init__(self, position=None, flock_behavior=None):
        """
        Initialize a bird.

        Args:
            position: Starting position (Vector2D)
            flock_behavior: FlockingBehavior instance
        """
        super().__init__(position=position, swarm_type="bird", radius=6)

        # Bird-specific parameters
        self.max_speed = 4.0
        self.max_force = 1.0
        self.perception_radius = 100.0
        self.communication_radius = 150.0

        self.flock_behavior = flock_behavior or FlockingBehavior()

        # Diving attack mechanics
        self.altitude = 50  # Simulated height above target
        self.dive_cooldown = 0
        self.is_diving = False
        self.dive_target = None
        self.max_dive_damage = 3.0

        # Attack parameters
        self.normal_attack_damage = 1.0
        self.attack_range = 15

        # Color for rendering
        self.color = COLOR_BIRD

    def calculate_steering_force(self, neighbors_list, target, max_force=None):
        """
        Calculate steering force based on flocking and target seeking.

        Args:
            neighbors_list: List of (neighbor, distance) tuples
            target: Current target (if any)
            max_force: Maximum force magnitude (uses self.max_force if None)

        Returns:
            Vector2D steering force
        """
        if max_force is None:
            max_force = self.max_force

        # Use flocking behavior
        steering = self.flock_behavior.update_flock_member(
            self, neighbors_list, target,
            self.perception_radius, max_force
        )

        return steering

    def update_dive_attack(self, delta_time):
        """
        Update dive attack cooldown and state.

        Args:
            delta_time: Time since last update
        """
        if self.dive_cooldown > 0:
            self.dive_cooldown -= delta_time
        else:
            self.dive_cooldown = 0
            self.is_diving = False

    def can_dive(self):
        """Check if bird can currently dive."""
        return self.dive_cooldown <= 0 and not self.is_diving

    def initiate_dive(self, target):
        """
        Start a dive attack toward target.

        Args:
            target: Target entity to dive at
        """
        if self.can_dive():
            self.is_diving = True
            self.dive_target = target
            self.dive_cooldown = 4.0  # 4 second cooldown
            self.state = "attacking"
            return True
        return False

    def perform_dive(self, target, delta_time):
        """
        Execute dive attack movement.

        Args:
            target: Target entity
            delta_time: Time since last update
        """
        if not self.is_diving or not target.alive:
            self.is_diving = False
            self.state = "idle"
            return 0

        dist = self.distance_to(target)

        # Accelerate toward target during dive
        direction = self.get_direction_to(target)

        # High-speed dive
        dive_force = direction * self.max_force * 2
        self.apply_force(dive_force)

        # Check for hit
        if dist < target.radius + self.radius:
            self.is_diving = False
            self.state = "idle"
            return self.max_dive_damage

        return 0

    def perform_normal_attack(self, target):
        """
        Perform normal attack on target (non-dive).

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

    def update(self, delta_time, neighbors_list, target, obstacles=None):
        """
        Update bird state and physics.

        Args:
            delta_time: Time since last update
            neighbors_list: List of neighbor birds
            target: Current target (if any)
            obstacles: List of obstacles for avoidance
        """
        # Update dive state
        self.update_dive_attack(delta_time)

        # Calculate steering
        steering = self.calculate_steering_force(neighbors_list, target)
        self.apply_force(steering)

        # Parent update handles velocity and position
        super().update(delta_time)

        # Wrap around screen edges
        from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
        self.wrap_edges(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update energy
        self.update_energy(delta_time)

        # Manage state transitions
        if self.energy <= 0:
            self.state = "idle"

    def __repr__(self):
        return (f"Bird(id={self.id}, pos={self.position}, "
                f"state={self.state}, diving={self.is_diving})")
