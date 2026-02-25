"""UI components for the simulation."""

import pygame
from src.core.vector2d import Vector2D
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK,
    COLOR_BIRD, COLOR_FISH, COLOR_ANT, COLOR_GROUND, COLOR_WATER, COLOR_AIR
)


class Button:
    """Clickable button UI element."""

    def __init__(self, position, width, height, label, color=(100, 100, 100), text_color=COLOR_WHITE):
        """
        Initialize a button.

        Args:
            position: Vector2D position
            width: Button width
            height: Button height
            label: Button text
            color: Button background color
            text_color: Text color
        """
        self.position = position
        self.width = width
        self.height = height
        self.label = label
        self.color = color
        self.text_color = text_color
        self.hover_color = tuple(min(255, c + 30) for c in color)
        self.hovered = False
        self.active = False

    def get_rect(self):
        """Get button rectangle."""
        return pygame.Rect(
            self.position.x - self.width // 2,
            self.position.y - self.height // 2,
            self.width,
            self.height
        )

    def is_clicked(self, mouse_pos):
        """Check if button is clicked."""
        rect = self.get_rect()
        return rect.collidepoint(int(mouse_pos.x), int(mouse_pos.y))

    def update_hover(self, mouse_pos):
        """Update hover state."""
        self.hovered = self.get_rect().collidepoint(int(mouse_pos.x), int(mouse_pos.y))

    def draw(self, renderer):
        """Draw button."""
        current_color = self.hover_color if self.hovered else self.color
        if self.active:
            current_color = (0, 200, 0)

        rect = self.get_rect()
        pygame.draw.rect(renderer.screen, current_color, rect)
        pygame.draw.rect(renderer.screen, COLOR_BLACK, rect, 2)

        # Draw text
        font = renderer.font_small
        text_surface = font.render(self.label, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        renderer.screen.blit(text_surface, text_rect)


class UIManager:
    """Manages all UI elements."""

    def __init__(self):
        """Initialize UI manager."""
        self.buttons = {}
        self.create_buttons()
        self.mouse_pos = Vector2D(0, 0)

    def create_buttons(self):
        """Create all UI buttons."""
        # Active swarm display with switcher (top left)
        self.buttons["swarm_label"] = Button(Vector2D(40, 15), 70, 20, "SWARM:", (50, 50, 50), COLOR_WHITE)
        self.buttons["swarm_display"] = Button(Vector2D(40, 35), 70, 25, "BIRD", COLOR_BIRD)
        self.buttons["swarm_prev"] = Button(Vector2D(15, 35), 25, 25, "◄")
        self.buttons["swarm_next"] = Button(Vector2D(65, 35), 25, 25, "►")

        # Active environment display with switcher (top middle)
        self.buttons["env_label"] = Button(Vector2D(180, 15), 70, 20, "ENV:", (50, 50, 50), COLOR_WHITE)
        self.buttons["env_display"] = Button(Vector2D(180, 35), 70, 25, "AIR", COLOR_AIR)
        self.buttons["env_prev"] = Button(Vector2D(155, 35), 25, 25, "◄")
        self.buttons["env_next"] = Button(Vector2D(205, 35), 25, 25, "►")

        # Control buttons (top right)
        self.buttons["spawn"] = Button(Vector2D(SCREEN_WIDTH - 120, 30), 80, 30, "SPAWN x50")
        self.buttons["pause"] = Button(Vector2D(SCREEN_WIDTH - 30, 30), 50, 30, "PAUSE")

    def update(self, mouse_pos):
        """Update UI state."""
        self.mouse_pos = mouse_pos
        for button in self.buttons.values():
            button.update_hover(mouse_pos)

    def handle_click(self, mouse_pos):
        """
        Handle button clicks including environment/swarm switching.

        Args:
            mouse_pos: Mouse position (Vector2D)

        Returns:
            Action dict with clicked button info
        """
        action = {}

        for button_name, button in self.buttons.items():
            if button.is_clicked(mouse_pos):
                # Handle switcher arrows
                if button_name == "swarm_next":
                    action["clicked_button"] = "swarm_cycle_next"
                elif button_name == "swarm_prev":
                    action["clicked_button"] = "swarm_cycle_prev"
                elif button_name == "env_next":
                    action["clicked_button"] = "env_cycle_next"
                elif button_name == "env_prev":
                    action["clicked_button"] = "env_cycle_prev"
                else:
                    action["clicked_button"] = button_name
                return action

        return action

    def set_active_button(self, button_name):
        """Update active swarm type or environment display."""
        if button_name in ["bird", "fish", "ant"]:
            # Update swarm display
            label_map = {"bird": "BIRD", "fish": "FISH", "ant": "ANT"}
            color_map = {"bird": COLOR_BIRD, "fish": COLOR_FISH, "ant": COLOR_ANT}
            self.buttons["swarm_display"].label = label_map[button_name]
            self.buttons["swarm_display"].color = color_map[button_name]
        elif button_name in ["air", "water", "ground"]:
            # Update environment display
            label_map = {"air": "AIR", "water": "WATER", "ground": "GROUND"}
            color_map = {"air": COLOR_AIR, "water": COLOR_WATER, "ground": COLOR_GROUND}
            self.buttons["env_display"].label = label_map[button_name]
            self.buttons["env_display"].color = color_map[button_name]

    def draw(self, renderer):
        """Draw all UI elements."""
        for button in self.buttons.values():
            button.draw(renderer)

    def draw_stats(self, renderer, stats):
        """Draw simulation statistics."""
        stats_text = (
            f"Birds: {stats.get('bird_count', 0)} | "
            f"Fish: {stats.get('fish_count', 0)} | "
            f"Ants: {stats.get('ant_count', 0)} | "
            f"Targets: {stats.get('targets_alive', 0)} | "
            f"Destroyed: {stats.get('targets_destroyed', 0)}"
        )
        renderer.draw_text(stats_text, (10, SCREEN_HEIGHT - 25), COLOR_BLACK, "small")

    def draw_help(self, renderer):
        """Draw help text."""
        help_text = "Left Click: Place Target | Right Click: Place Obstacle | R: Reset"
        renderer.draw_text(help_text, (10, SCREEN_HEIGHT - 50), COLOR_BLACK, "small")
