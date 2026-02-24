"""Steering behaviors for swarm agents."""

import math
from src.core.vector2d import Vector2D


class SteeringBehaviors:
    """Collection of steering behavior functions."""

    @staticmethod
    def seek(position, target_position, max_speed=5.0):
        """
        Seek behavior - steer toward target.

        Args:
            position: Current position (Vector2D)
            target_position: Target position (Vector2D)
            max_speed: Maximum speed magnitude

        Returns:
            Steering force (Vector2D)
        """
        desired = target_position - position
        distance = desired.magnitude()

        if distance == 0:
            return Vector2D(0, 0)

        desired = desired.normalize()
        desired = desired * max_speed

        return desired

    @staticmethod
    def flee(position, threat_position, max_speed=5.0):
        """
        Flee behavior - steer away from threat.

        Args:
            position: Current position (Vector2D)
            threat_position: Threat position (Vector2D)
            max_speed: Maximum speed magnitude

        Returns:
            Steering force (Vector2D)
        """
        desired = position - threat_position
        distance = desired.magnitude()

        if distance == 0:
            return Vector2D(0, 0)

        desired = desired.normalize()
        desired = desired * max_speed

        return desired

    @staticmethod
    def arrive(position, velocity, target_position, slow_radius=100, max_speed=5.0):
        """
        Arrive behavior - steer toward target and slow down nearby.

        Args:
            position: Current position (Vector2D)
            velocity: Current velocity (Vector2D)
            target_position: Target position (Vector2D)
            slow_radius: Distance to start slowing down
            max_speed: Maximum speed magnitude

        Returns:
            Steering force (Vector2D)
        """
        desired = target_position - position
        distance = desired.magnitude()

        if distance == 0:
            return Vector2D(0, 0) - velocity

        if distance < slow_radius:
            speed = max_speed * (distance / slow_radius)
        else:
            speed = max_speed

        desired = desired.normalize() * speed

        steering = desired - velocity
        return steering

    @staticmethod
    def separation(position, neighbors, perception_radius=80, max_force=1.0):
        """
        Separation behavior - avoid crowding neighbors.

        Args:
            position: Current position (Vector2D)
            neighbors: List of neighbor entities
            perception_radius: Distance to consider neighbors
            max_force: Maximum force magnitude

        Returns:
            Steering force (Vector2D)
        """
        steer = Vector2D(0, 0)
        count = 0

        for neighbor, distance in neighbors:
            if distance > 0 and distance < perception_radius:
                # Calculate repulsion force (inverse of distance)
                diff = position - neighbor.position
                diff = diff.normalize()
                diff = diff / (distance + 0.1)  # Avoid division by zero
                steer = steer + diff
                count += 1

        if count > 0:
            steer = steer / count

        if steer.magnitude() > 0:
            steer = steer.normalize() * max_force

        return steer

    @staticmethod
    def cohesion(position, neighbors, perception_radius=80, max_force=1.0):
        """
        Cohesion behavior - steer toward average position of neighbors.

        Args:
            position: Current position (Vector2D)
            neighbors: List of neighbor entities
            perception_radius: Distance to consider neighbors
            max_force: Maximum force magnitude

        Returns:
            Steering force (Vector2D)
        """
        steering = Vector2D(0, 0)
        count = 0

        for neighbor, distance in neighbors:
            if distance < perception_radius:
                steering = steering + neighbor.position
                count += 1

        if count > 0:
            steering = steering / count  # Average position
            steering = steering - position  # Direction to average

        if steering.magnitude() > 0:
            steering = steering.normalize() * max_force

        return steering

    @staticmethod
    def alignment(velocity, neighbors, perception_radius=80, max_force=1.0):
        """
        Alignment behavior - steer toward average heading of neighbors.

        Args:
            velocity: Current velocity (Vector2D)
            neighbors: List of neighbor entities
            perception_radius: Distance to consider neighbors
            max_force: Maximum force magnitude

        Returns:
            Steering force (Vector2D)
        """
        steering = Vector2D(0, 0)
        count = 0

        for neighbor, distance in neighbors:
            if distance < perception_radius:
                steering = steering + neighbor.velocity
                count += 1

        if count > 0:
            steering = steering / count
            steering = steering - velocity

        if steering.magnitude() > 0:
            steering = steering.normalize() * max_force

        return steering

    @staticmethod
    def obstacle_avoidance(position, velocity, obstacles, lookahead_distance=50, max_force=1.0):
        """
        Obstacle avoidance - steer away from obstacles in path.

        Args:
            position: Current position (Vector2D)
            velocity: Current velocity (Vector2D)
            obstacles: List of obstacle entities
            lookahead_distance: How far ahead to look
            max_force: Maximum force magnitude

        Returns:
            Steering force (Vector2D)
        """
        if velocity.magnitude() == 0:
            return Vector2D(0, 0)

        # Predict future position
        future_pos = position + velocity.normalize() * lookahead_distance

        steer = Vector2D(0, 0)

        for obstacle in obstacles:
            dist = obstacle.position.distance(future_pos)

            # Check if on collision course
            if dist < obstacle.radius + 5:
                # Steer perpendicular to obstacle
                normal = (position - obstacle.position).normalize()
                steer = normal * max_force
                break

        return steer

    @staticmethod
    def wander(velocity, wander_angle, wander_radius=20, max_force=1.0):
        """
        Wander behavior - explore space with random direction changes.

        Args:
            velocity: Current velocity (Vector2D)
            wander_angle: Current wander angle (radians) - update this value
            wander_radius: Radius of wander circle
            max_force: Maximum force magnitude

        Returns:
            Tuple of (steering_force, new_wander_angle)
        """
        import random

        # Update wander angle randomly
        change = random.uniform(-math.pi / 8, math.pi / 8)
        wander_angle += change

        # Calculate wander circle position
        if velocity.magnitude() > 0:
            direction = velocity.normalize()
            wander_center = direction * wander_radius
        else:
            wander_center = Vector2D(wander_radius, 0)

        # Add point on wander circle
        wander_pos = Vector2D(
            wander_center.x + math.cos(wander_angle) * wander_radius,
            wander_center.y + math.sin(wander_angle) * wander_radius
        )

        # Steer toward wander position
        steering = wander_pos.normalize() * max_force

        return steering, wander_angle
