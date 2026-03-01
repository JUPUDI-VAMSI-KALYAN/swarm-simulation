"""Pod swarm implementation with sonar search and torpedo barrage attacks."""

import random
from typing import Any, Optional

from src.swarm.swarm_agent import SwarmAgent
from src.intelligence.sonar_sweeps import SonarSweepBehavior
from src.core.vector2d import Vector2D
from config.settings import COLOR_POD, SwarmConfig


class Pod(SwarmAgent):
    """Intelligent unmanned underwater vehicle (Pod) that sweeps with sonar and performs torpedo barrages."""

    def __init__(
        self,
        position: Optional[Vector2D] = None,
        sweep_behavior: Optional[SonarSweepBehavior] = None
    ) -> None:
        """
        Initialize a pod.

        Args:
            position: Starting position (Vector2D)
            sweep_behavior: SonarSweepBehavior instance
        """
        super().__init__(position=position, swarm_type="pod", radius=SwarmConfig.POD_RADIUS)

        self.max_speed = SwarmConfig.POD_MAX_SPEED
        self.max_force = SwarmConfig.POD_MAX_FORCE
        self.perception_radius = SwarmConfig.POD_PERCEPTION_RADIUS
        self.communication_radius = SwarmConfig.POD_COMMUNICATION_RADIUS

        self.sweep_behavior = sweep_behavior or SonarSweepBehavior()
        self.sweep_angle = random.uniform(0, 6.28)

        self.barrage_vote: Optional[Any] = None
        self.in_barrage_attack = False
        self.attack_cooldown = 0.0
        self.normal_attack_damage = SwarmConfig.POD_NORMAL_ATTACK_DAMAGE
        self.barrage_attack_damage = SwarmConfig.POD_BARRAGE_ATTACK_DAMAGE
        self.attack_range = SwarmConfig.POD_ATTACK_RANGE

        self.color = COLOR_POD

    def calculate_steering_force(
        self,
        neighbors: list[tuple[Any, float]],
        target: Optional[Any],
        max_force: Optional[float] = None
    ) -> Vector2D:
        """
        Calculate steering force based on sonar sweep and target seeking.

        Args:
            neighbors: List of (neighbor, distance) tuples
            target: Current target (if any)
            max_force: Maximum force magnitude (uses self.max_force if None)

        Returns:
            Vector2D steering force
        """
        if max_force is None:
            max_force = self.max_force

        steering, self.sweep_angle = self.sweep_behavior.calculate_sweep_steering(
            self, self.sweep_angle, neighbors, self.perception_radius, max_force
        )

        if target and target.alive:
            target_dist = self.distance_to(target)
            if target_dist > 0:
                return (self.get_direction_to(target) * max_force * 2.0).limit(max_force)

        return steering.limit(max_force)

    def vote_for_target(self, targets_list: list[Any], neighbors_list: list[tuple[Any, float]]) -> None:
        """
        Vote for which target the fleet should attack via torpedo barrage.

        Args:
            targets_list: List of available targets
            neighbors_list: List of neighbor pods
        """
        # Always vote for our currently assigned mesh target if it's alive
        if self.target and self.target.alive:
            self.barrage_vote = self.target
            return

        if not targets_list:
            self.barrage_vote = None
            return

        # Otherwise vote for closest visible target via sonar/acoustics
        closest = None
        closest_dist = float('inf')

        for target in targets_list:
            if target.alive:
                dist = self.distance_to(target)
                if dist < self.perception_radius and dist < closest_dist:
                    closest = target
                    closest_dist = dist

        self.barrage_vote = closest

    def check_barrage_attack_readiness(self, neighbors_list):
        """
        Check if conditions are right for a torpedo barrage.

        Args:
            neighbors_list: List of neighbor pods

        Returns:
            Tuple (should_attack, target_to_attack) or (False, None)
        """
        if self.barrage_vote is None:
            return False, None

        # Count votes on mesh network
        votes_for_same_target = 1  # This pod's vote
        for neighbor, _ in neighbors_list:
            if isinstance(neighbor, Pod) and neighbor.barrage_vote == self.barrage_vote:
                votes_for_same_target += 1

        # Need 60% majority to authorize barrage
        total_pods = len(neighbors_list) + 1
        vote_percentage = votes_for_same_target / max(1, total_pods)

        if vote_percentage >= 0.6:
            return True, self.barrage_vote

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
        actual_dist = max(0, dist - getattr(target, 'radius', 15) - self.radius)
        if actual_dist < self.attack_range:
            if self.in_barrage_attack:
                return self.barrage_attack_damage
            return self.normal_attack_damage
        return 0

    def update(
        self,
        delta_time: float,
        neighbors: list[tuple[Any, float]],
        target: Optional[Any],
        targets_list: Optional[list[Any]] = None,
        attacking: bool = False
    ) -> None:
        """
        Update pod state and physics.

        Args:
            delta_time: Time since last update
            neighbors: List of neighbor pods
            target: Current target (if any)
            targets_list: List of all targets (for message processing)
            attacking: Whether pod is in torpedo barrage mode
        """
        if targets_list:
            self.process_messages(targets_list)

        self.in_barrage_attack = attacking

        all_targets = targets_list if targets_list else ([target] if target else [])
        self.vote_for_target(all_targets, neighbors)

        steering = self.calculate_steering_force(neighbors, self.target)
        self.apply_force(steering)

        # Parent update
        super().update(delta_time)

        # Wrap edges
        from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
        self.wrap_edges(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update energy
        self.update_energy(delta_time)

    def __repr__(self):
        return (f"Pod(id={self.id}, pos={self.position}, "
                f"in_barrage={self.in_barrage_attack})")
