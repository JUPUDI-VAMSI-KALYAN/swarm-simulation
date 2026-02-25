"""Ant swarm implementation with pheromone communication."""

import random
import math
from src.swarm.swarm_agent import SwarmAgent
from src.core.vector2d import Vector2D
from config.settings import COLOR_ANT


class Ant(SwarmAgent):
    """Intelligent ant that uses pheromones for communication."""

    def __init__(self, position=None, pheromone_map=None):
        """
        Initialize an ant.

        Args:
            position: Starting position (Vector2D)
            pheromone_map: PheromoneMap instance
        """
        super().__init__(position=position, swarm_type="ant", radius=3)

        # Ant-specific parameters
        self.max_speed = 2.0
        self.max_force = 0.5
        self.perception_radius = 60.0
        self.communication_radius = 100.0

        self.pheromone_map = pheromone_map

        # Ant behavior states
        self.carrying_food = False
        self.pheromone_trail = []
        self.random_walk_strength = 0.3
        self.wander_angle = random.uniform(0, 2 * math.pi)

        self.normal_attack_damage = 1.0
        self.attack_range = 8

        self.color = COLOR_ANT

    def calculate_steering_force(self, target, neighbors_list, max_force=None):
        """
        Calculate steering force based on pheromones and target.

        Args:
            target: Current target (if any)
            neighbors_list: List of neighbor ants
            max_force: Maximum force magnitude

        Returns:
            Vector2D steering force
        """
        if max_force is None:
            max_force = self.max_force

        forces = []

        # 1. Follow food pheromones if not carrying
        if not self.carrying_food and self.pheromone_map:
            pheromone_gradient = self.pheromone_map.get_food_gradient(self.position)
            if pheromone_gradient.magnitude() > 0:
                forces.append(pheromone_gradient.normalize() * max_force * 0.8)

        # 2. Seek target if in range
        if target and target.alive:
            target_dist = self.distance_to(target)
            if target_dist < self.perception_radius:
                seek = (target.position - self.position).normalize() * max_force
                forces.append(seek * 1.5)

        # 3. Random walk for exploration
        wander, self.wander_angle = self._wander(max_force)
        forces.append(wander * self.random_walk_strength)

        # Combine forces
        total = Vector2D(0, 0)
        for f in forces:
            total = total + f

        return total.limit(max_force)

    def _wander(self, max_force):
        """
        Random walk behavior.

        Args:
            max_force: Maximum force magnitude

        Returns:
            Tuple (steering_force, new_wander_angle)
        """
        # Update wander angle randomly
        change = random.uniform(-math.pi / 8, math.pi / 8)
        self.wander_angle += change

        # Calculate wander direction
        wander_x = math.cos(self.wander_angle)
        wander_y = math.sin(self.wander_angle)

        wander_force = Vector2D(wander_x, wander_y).normalize() * max_force
        return wander_force, self.wander_angle

    def deposit_pheromone(self, target_found=False):
        """
        Deposit pheromone trails.

        Args:
            target_found: Whether target was found
        """
        if not self.pheromone_map:
            return

        if self.carrying_food or target_found:
            # Deposit strong food pheromone
            self.pheromone_map.deposit_food_pheromone(self.position, 1.5)
        else:
            # Deposit weak exploratory pheromone
            self.pheromone_map.deposit_food_pheromone(self.position, 0.3)

    def pick_up_food(self, target):
        """Pick up food from target."""
        self.carrying_food = True
        self.state = "returning"

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
            return self.normal_attack_damage
        return 0

    def update(self, delta_time, target, neighbors_list, targets_list=None):
        """
        Update ant state and physics.

        Args:
            delta_time: Time since last update
            target: Current target (if any)
            neighbors_list: List of neighbor ants
            targets_list: List of all targets (for message processing)
        """
        # Process incoming messages from swarm communication
        if targets_list:
            self.process_messages(targets_list)

        # Deposit pheromone as we move
        target_found = target is not None and target.alive
        self.deposit_pheromone(target_found)

        # Pick up food when reaching target
        if target and target.alive and self.distance_to(target) < 15:
            self.pick_up_food(target)

        # Calculate steering
        steering = self.calculate_steering_force(target, neighbors_list)
        self.apply_force(steering)

        # Parent update
        super().update(delta_time)

        # Wrap edges
        from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
        self.wrap_edges(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update energy
        self.update_energy(delta_time)

    def __repr__(self):
        return (f"Ant(id={self.id}, pos={self.position}, "
                f"carrying={'yes' if self.carrying_food else 'no'})")
