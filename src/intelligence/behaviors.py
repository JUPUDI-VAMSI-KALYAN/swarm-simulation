"""Steering behaviors for swarm agents."""

import math
from src.core.vector2d import Vector2D


class SteeringBehaviors:
    """Collection of steering behavior functions."""

    @staticmethod
    def seek(position, target_position, max_speed=300.0):
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
    def flee(position, threat_position, max_speed=300.0):
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
    def arrive(position, velocity, target_position, slow_radius=100, max_speed=300.0):
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
    def grid_alignment(velocity, neighbors, perception_radius=80, max_force=1.0):
        """
        Grid Alignment - Steer agents so they all perfectly align to a specific tactical heading
        (e.g., straight up, down, left, right relative to swarm center).
        
        Args:
            velocity: Current velocity (Vector2D)
            neighbors: List of neighbor entities
            perception_radius: Distance to consider neighbors
            max_force: Maximum force magnitude

        Returns:
            Steering force (Vector2D)
        """
        import math
        steering = Vector2D(0, 0)
        count = 0

        for neighbor, distance in neighbors:
            if distance < perception_radius:
                steering = steering + neighbor.velocity
                count += 1

        if count > 0:
            steering = steering / count
            
            # Snap steering to standard block angles (0, 90, 180, 270)
            if steering.magnitude() > 0:
                angle = math.atan2(steering.y, steering.x)
                # Round to nearest 90 degrees (pi/2 radians)
                snapped_angle = round(angle / (math.pi/2)) * (math.pi/2)
                
                rigid_dir = Vector2D(math.cos(snapped_angle), math.sin(snapped_angle))
                steering = rigid_dir * velocity.magnitude() - velocity
                
        if steering.magnitude() > 0:
            steering = steering.normalize() * max_force

        return steering

    @staticmethod
    def sonar_sweep(position, velocity, sweep_angle, sweep_radius=40, max_force=1.0):
        """
        Sonar Sweep - Methodical searching pattern (like a scanning arc).
        
        Args:
            position: Current position (Vector2D)
            velocity: Current velocity (Vector2D)
            sweep_angle: Current sweeping angle in radians (must be updated externally)
            sweep_radius: Radius of sweep circle
            max_force: Max steering force
            
        Returns:
            Tuple of (steering_force, new_sweep_angle)
        """
        import math
        
        # Methodical sweep (oscillating between -45 and 45 degrees)
        # Assuming sweep_angle increases constantly
        sweep_angle += 0.05
        
        # Calculate offset using sine to sweep back and forth
        offset = math.sin(sweep_angle) * (math.pi / 4) # 45 degree arc
        
        if velocity.magnitude() > 0:
            current_heading = math.atan2(velocity.y, velocity.x)
            target_angle = current_heading + offset
        else:
            target_angle = offset
            
        target_dir = Vector2D(math.cos(target_angle), math.sin(target_angle))
        
        steering = target_dir * max_force
        
        return steering, sweep_angle

    @staticmethod
    def precision_patrol(velocity, patrol_timer, patrol_state, max_force=1.0):
        """
        Precision Patrol - Terrestrial bots move in perfect straight lines, 
        stop, rotate 90 degrees, and continue driving the grid.
        
        Args:
            velocity: Current velocity (Vector2D)
            patrol_timer: Time spent on current leg
            patrol_state: Direction state (0, 1, 2, 3) mapped to NSEW
            max_force: Maximum steering force
            
        Returns:
            Tuple (steering, new_timer, new_state)
        """
        import math
        
        patrol_timer -= 1
        
        if patrol_timer <= 0:
            # Time to turn 90 degrees (switch state)
            patrol_state = (patrol_state + 1) % 4
            patrol_timer = 60 # wait 60 frames on new leg
            
        # Direction mapping (0: E, 1: S, 2: W, 3: N)
        angles = [0, math.pi/2, math.pi, -math.pi/2]
        target_angle = angles[patrol_state]
        
        target_dir = Vector2D(math.cos(target_angle), math.sin(target_angle))
        
        if velocity.magnitude() == 0:
            steering = target_dir * max_force
        else:
            steering = (target_dir * velocity.magnitude()) - velocity
            
        if steering.magnitude() > 0:
            steering = steering.normalize() * max_force
            
        return steering, patrol_timer, patrol_state
