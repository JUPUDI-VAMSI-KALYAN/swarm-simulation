"""Pod swarm implementation with sonar search and torpedo barrage attacks."""

import random
from src.swarm.swarm_agent import SwarmAgent
from src.intelligence.sonar_sweeps import SonarSweepBehavior
from src.core.vector2d import Vector2D
from config.settings import COLOR_POD


class Pod(SwarmAgent):
    """Intelligent unmanned underwater vehicle (Pod) that sweeps with sonar and performs torpedo barrages."""

    def __init__(self, position=None, sweep_behavior=None):
        """
        Initialize a pod.

        Args:
            position: Starting position (Vector2D)
            sweep_behavior: SonarSweepBehavior instance
        """
        super().__init__(position=position, swarm_type="pod", radius=5)

        # Pod-specific parameters, slightly slower due to water resistance
        self.max_speed = 180.0
        self.max_force = 100.0
        self.perception_radius = 350.0
        self.communication_radius = 500.0

        self.sweep_behavior = sweep_behavior or SonarSweepBehavior()
        self.sweep_angle = random.uniform(0, 6.28) # Initialize sweep angle

        # Torpedo barrage mechanics
        self.barrage_vote = None  # What target this pod wants to attack
        self.in_barrage_attack = False
        self.attack_cooldown = 0
        self.normal_attack_damage = 25.0 # Normal damage per second
        self.barrage_attack_damage = 80.0 # Barrage damage per second
        self.attack_range = 250.0 # Torpedo standoff distance

        self.color = COLOR_POD

    def calculate_steering_force(self, neighbors_list, target, max_force=None):
        """
        Calculate steering force based on sonar sweep and target seeking.

        Args:
            neighbors_list: List of (neighbor, distance) tuples
            target: Current target (if any)
            max_force: Maximum force magnitude (uses self.max_force if None)

        Returns:
            Vector2D steering force
        """
        if max_force is None:
            max_force = self.max_force

        # Use sonar sweep behavior
        steering, self.sweep_angle = self.sweep_behavior.calculate_sweep_steering(
            self, self.sweep_angle, neighbors_list, self.perception_radius, max_force
        )

        # Add target seeking if one is assigned
        if target and target.alive:
            # Prioritize seeking over sweeping when a target is found
            target_dist = self.distance_to(target)
            if target_dist > 0:
                # Overpower the sweep behavior when engaging
                return (self.get_direction_to(target) * max_force * 2.0).limit(max_force)

        return steering.limit(max_force)

    def vote_for_target(self, targets_list, neighbors_list):
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

    def update(self, delta_time, neighbors_list, target, targets_list=None, attacking=False):
        """
        Update pod state and physics.

        Args:
            delta_time: Time since last update
            neighbors_list: List of neighbor pods
            target: Current target (if any)
            targets_list: List of all targets (for message processing)
            attacking: Whether pod is in torpedo barrage mode
        """
        # Process incoming messages from swarm communication
        if targets_list:
            self.process_messages(targets_list)

        self.in_barrage_attack = attacking

        # Vote for targets via underwater acoustics
        all_targets = targets_list if targets_list else ([target] if target else [])
        self.vote_for_target(all_targets, neighbors_list)

        # Calculate steering
        steering = self.calculate_steering_force(neighbors_list, self.target)
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
