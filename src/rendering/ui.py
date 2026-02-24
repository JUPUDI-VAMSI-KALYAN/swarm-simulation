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
        # Swarm type buttons (top left)
        self.buttons["bird"] = Button(Vector2D(50, 30), 50, 30, "BIRD", COLOR_BIRD)
        self.buttons["fish"] = Button(Vector2D(120, 30), 50, 30, "FISH", COLOR_FISH)
        self.buttons["ant"] = Button(Vector2D(190, 30), 50, 30, "ANT", COLOR_ANT)

        # Environment buttons (top middle)
        self.buttons["ground"] = Button(Vector2D(280, 30), 60, 30, "GROUND", COLOR_GROUND)
        self.buttons["water"] = Button(Vector2D(360, 30), 50, 30, "WATER", COLOR_WATER)
        self.buttons["air"] = Button(Vector2D(420, 30), 40, 30, "AIR", COLOR_AIR)

        # Control buttons (top right)
        self.buttons["spawn"] = Button(Vector2D(SCREEN_WIDTH - 150, 30), 80, 30, "SPAWN x50")
        self.buttons["pause"] = Button(Vector2D(SCREEN_WIDTH - 60, 30), 50, 30, "PAUSE")

    def update(self, mouse_pos):
        """Update UI state."""
        self.mouse_pos = mouse_pos
        for button in self.buttons.values():
            button.update_hover(mouse_pos)

    def handle_click(self, mouse_pos):
        """
        Handle button clicks.

        Args:
            mouse_pos: Mouse position (Vector2D)

        Returns:
            Action dict with clicked button info
        """
        action = {}

        for button_name, button in self.buttons.items():
            if button.is_clicked(mouse_pos):
                action["clicked_button"] = button_name
                return action

        return action

    def set_active_button(self, button_name):
        """Set a button as active (highlighted)."""
        for name, button in self.buttons.items():
            button.active = (name == button_name)

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
