"""Target entity that can be attacked by swarms."""

from src.core.entity import Entity
from config.settings import COLOR_TARGET


class Target(Entity):
    """Attackable target entity."""

    def __init__(self, position=None, health=100, radius=15):
        """
        Initialize a target.

        Args:
            position: Starting position (Vector2D)
            health: Initial health
            radius: Size of target
        """
        super().__init__(position=position, radius=radius)

        self.health = float(health)
        self.max_health = float(health)
        self.damage_taken_this_frame = 0
        self.threat_level = 1.0
        self.defenders = 0  # Number of swarms attacking

        # Visual feedback
        self.color = COLOR_TARGET
        self.last_damage_time = 0
        self.damage_flash_duration = 0.1

    def take_damage(self, amount):
        """
        Reduce target health.

        Args:
            amount: Damage to deal
        """
        self.health = max(0, self.health - amount)
        self.damage_taken_this_frame += amount
        self.last_damage_time = self.damage_flash_duration

        if self.health <= 0:
            self.destroy()

    def is_destroyed(self):
        """Check if target is destroyed."""
        return not self.alive or self.health <= 0

    def get_health_percentage(self):
        """Get health as percentage (0.0 to 1.0)."""
        if self.max_health <= 0:
            return 0.0
        return self.health / self.max_health

    def update(self, delta_time):
        """
        Update target state.

        Args:
            delta_time: Time since last update
        """
        super().update(delta_time)

        # Reset damage tracking
        self.damage_taken_this_frame = 0

        # Update damage flash
        if self.last_damage_time > 0:
            self.last_damage_time -= delta_time

    def get_visual_health_color(self):
        """
        Get RGB color for health bar based on current health.

        Returns:
            Tuple of (R, G, B)
        """
        health_percent = self.get_health_percentage()

        if health_percent > 0.5:
            # Green to Yellow
            r = int(255 * (1 - health_percent) * 2)
            g = 255
            b = 0
        else:
            # Yellow to Red
            r = 255
            g = int(255 * health_percent * 2)
            b = 0

        return (r, g, b)

    def __repr__(self):
        return (f"Target(id={self.id}, pos={self.position}, "
                f"health={self.health}/{self.max_health})")
