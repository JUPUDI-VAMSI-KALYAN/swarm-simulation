"""Fish swarm implementation with schooling and wave attacks."""

import random
from src.swarm.swarm_agent import SwarmAgent
from src.intelligence.schooling import SchoolingBehavior
from src.core.vector2d import Vector2D
from config.settings import COLOR_FISH


class Fish(SwarmAgent):
    """Intelligent fish that schools and performs wave attacks."""

    def __init__(self, position=None, schooling_behavior=None):
        """
        Initialize a fish.

        Args:
            position: Starting position (Vector2D)
            schooling_behavior: SchoolingBehavior instance
        """
        super().__init__(position=position, swarm_type="fish", radius=5)

        # Fish-specific parameters
        self.max_speed = 3.0
        self.max_force = 0.8
        self.perception_radius = 80.0
        self.communication_radius = 120.0

        self.schooling_behavior = schooling_behavior or SchoolingBehavior()

        # Wave attack mechanics
        self.wave_vote = None  # What target this fish wants to attack
        self.in_wave_attack = False
        self.attack_cooldown = 0
        self.normal_attack_damage = 1.5
        self.wave_attack_damage = 2.0
        self.attack_range = 12

        self.color = COLOR_FISH

    def calculate_steering_force(self, neighbors_list, target, max_force=None):
        """
        Calculate steering force based on schooling and target seeking.

        Args:
            neighbors_list: List of (neighbor, distance) tuples
            target: Current target (if any)
            max_force: Maximum force magnitude (uses self.max_force if None)

        Returns:
            Vector2D steering force
        """
        if max_force is None:
            max_force = self.max_force

        # Use schooling behavior
        steering = self.schooling_behavior.calculate_schooling_steering(
            self, neighbors_list, self.perception_radius, max_force
        )

        # Add target seeking if in wave attack
        if target and target.alive and self.in_wave_attack:
            seek = Vector2D(0, 0)
            target_dist = self.distance_to(target)
            if target_dist > 0:
                seek = (target.position - self.position).normalize() * max_force * 1.5
            steering = steering + seek

        return steering.limit(max_force)

    def vote_for_target(self, targets_list, neighbors_list):
        """
        Vote for which target the school should attack.

        Args:
            targets_list: List of available targets
            neighbors_list: List of neighbor fish
        """
        if not targets_list:
            self.wave_vote = None
            return

        # Vote for closest visible target
        closest = None
        closest_dist = float('inf')

        for target in targets_list:
            if target.alive:
                dist = self.distance_to(target)
                if dist < self.perception_radius and dist < closest_dist:
                    closest = target
                    closest_dist = dist

        self.wave_vote = closest

    def check_wave_attack_readiness(self, neighbors_list):
        """
        Check if conditions are right for a wave attack.

        Args:
            neighbors_list: List of neighbor fish

        Returns:
            Tuple (should_attack, target_to_attack) or (False, None)
        """
        if self.wave_vote is None:
            return False, None

        # Count votes
        votes_for_same_target = 1  # This fish's vote
        for neighbor, _ in neighbors_list:
            if isinstance(neighbor, Fish) and neighbor.wave_vote == self.wave_vote:
                votes_for_same_target += 1

        # Need 60% majority to attack
        total_fish = len(neighbors_list) + 1
        vote_percentage = votes_for_same_target / max(1, total_fish)

        if vote_percentage >= 0.6:
            return True, self.wave_vote

        return False, None

    def perform_attack(self, target):
        """
        Perform attack on target.

        Args:
            target: Target entity

        Returns:
            Damage dealt
        """
        if not target.alive:
            return 0

        dist = self.distance_to(target)
        if dist < self.attack_range:
            if self.in_wave_attack:
                return self.wave_attack_damage
            return self.normal_attack_damage
        return 0

    def update(self, delta_time, neighbors_list, target, targets_list=None, attacking=False):
        """
        Update fish state and physics.

        Args:
            delta_time: Time since last update
            neighbors_list: List of neighbor fish
            target: Current target (if any)
            targets_list: List of all targets (for message processing)
            attacking: Whether fish is in wave attack mode
        """
        # Process incoming messages from swarm communication
        if targets_list:
            self.process_messages(targets_list)

        self.in_wave_attack = attacking

        # Vote for targets
        all_targets = targets_list if targets_list else ([target] if target else [])
        self.vote_for_target(all_targets, neighbors_list)

        # Calculate steering
        steering = self.calculate_steering_force(neighbors_list, target)
        self.apply_force(steering)

        # Parent update
        super().update(delta_time)

        # Wrap edges
        from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
        self.wrap_edges(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update energy
        self.update_energy(delta_time)

    def __repr__(self):
        return (f"Fish(id={self.id}, pos={self.position}, "
                f"in_wave={self.in_wave_attack})")
