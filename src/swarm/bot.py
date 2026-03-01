"""Bot swarm implementation with digital signal network communication."""

import random
import math
from src.swarm.swarm_agent import SwarmAgent
from src.intelligence.behaviors import SteeringBehaviors
from src.core.vector2d import Vector2D
from config.settings import COLOR_BOT


class Bot(SwarmAgent):
    """Intelligent terrestrial bot that uses digital signals (mesh network) for communication."""

    def __init__(self, position=None, signal_map=None):
        """
        Initialize a terrestrial bot.

        Args:
            position: Starting position (Vector2D)
            signal_map: SignalNetworkMap instance
        """
        super().__init__(position=position, swarm_type="bot", radius=4)

        # Bot-specific parameters (ground traversal)
        self.max_speed = 150.0
        self.max_force = 80.0
        self.perception_radius = 250.0
        self.communication_radius = 400.0

        self.signal_map = signal_map

        # Bot behavior states
        self.carrying_payload = False
        self.signal_trail = []
        self.attack_range = 150.0 # Standard engagement range
        self.normal_attack_damage = 15.0 # Damage per second (kinetic/electronic)
        self.random_walk_strength = 0.4
        
        # Precision patrol state
        self.patrol_timer = random.randint(10, 60)
        self.patrol_state = random.randint(0, 3) # N/E/S/W

        self.attack_range = 10

        self.color = COLOR_BOT

    def calculate_steering_force(self, target, neighbors_list, max_force=None):
        """
        Calculate steering force based on signal grid and target.

        Args:
            target: Current target (if any)
            neighbors_list: List of neighbor bots
            max_force: Maximum force magnitude

        Returns:
            Vector2D steering force
        """
        if max_force is None:
            max_force = self.max_force

        forces = []

        # 1. Follow digital signals if not carrying
        if not self.carrying_payload and self.signal_map:
            signal_gradient = self.signal_map.get_signal_gradient(self.position)
            if signal_gradient.magnitude() > 0:
                forces.append(signal_gradient.normalize() * max_force * 0.85)

        # 2. Seek target if one is assigned (either via lidar or mesh network)
        if target and target.alive:
            target_dist = self.distance_to(target)
            if 0 < target_dist:
                seek = self.get_direction_to(target) * max_force
                forces.append(seek * 1.5)

        # 3. Precision patrol (rigid 90 degree movements for robotic sweep)
        patrol, self.patrol_timer, self.patrol_state = SteeringBehaviors.precision_patrol(
            self.velocity, self.patrol_timer, self.patrol_state, max_force
        )
        forces.append(patrol * self.random_walk_strength)
        
        # 4. Light separation to not crowd completely
        sep = SteeringBehaviors.separation(
            self.position, neighbors_list, self.perception_radius * 0.4, max_force
        )
        forces.append(sep * 0.5)

        # Combine forces
        total = Vector2D(0, 0)
        for f in forces:
            total = total + f

        return total.limit(max_force)

    def emit_digital_signal(self, target_found=False):
        """
        Emit a digital mesh signal (breadcrumbs) on the network map.

        Args:
            target_found: Whether target was found
        """
        if not self.signal_map:
            return

        if self.carrying_payload or target_found:
            # Emit strong path signal
            self.signal_map.emit_signal(self.position, 1.5)
        else:
            # Emit weak scouting signal
            self.signal_map.emit_signal(self.position, 0.3)

    def pick_up_payload(self, target):
        """Pick up digital or physical payload from target."""
        self.carrying_payload = True
        self.state = "returning"

    def perform_attack(self, target):
        """
        Perform kinetic/electronic attack on target.

        Args:
            target: Target entity

        Returns:
            Damage dealt
        """
        if not target.alive:
            return 0

        dist = self.distance_to(target)
        actual_dist = max(0, dist - target.radius - self.radius)
        print(f"[DEBUG] Bot Actual Dist: {actual_dist} (Attack Range: {self.attack_range})")
        if actual_dist < self.attack_range:
            print("[DEBUG] Bot hitting target!")
            return self.normal_attack_damage
        return 0

    def update(self, delta_time, target, neighbors_list, targets_list=None):
        """
        Update bot state and physics.

        Args:
            delta_time: Time since last update
            target: Current target (if any)
            neighbors_list: List of neighbor bots
            targets_list: List of all targets (for message processing)
        """
        # Process incoming messages from swarm communication
        if targets_list:
            self.process_messages(targets_list)

        # Emit mesh networking signal
        target_found = target is not None and target.alive
        self.emit_digital_signal(target_found)

        # Engage with target when close
        if target and target.alive:
            actual_dist = max(0, self.distance_to(target) - getattr(target, 'radius', 15) - self.radius)
            if actual_dist < 15:
                self.pick_up_payload(target)

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
        return (f"Bot(id={self.id}, pos={self.position}, "
                f"payload={'yes' if self.carrying_payload else 'no'})")
