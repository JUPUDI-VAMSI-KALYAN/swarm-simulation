"""UI components for the tactical simulation."""

import pygame
from src.core.vector2d import Vector2D
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK,
    COLOR_DRONE, COLOR_POD, COLOR_BOT, COLOR_GROUND, COLOR_WATER, COLOR_AIR
)


class Button:
    """Clickable button UI element for tactical HUD."""

    def __init__(self, position, width, height, label, color=(30, 40, 50), text_color=COLOR_WHITE):
        """
        Initialize a HUD button.

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
        """Draw tactical button."""
        current_color = self.hover_color if self.hovered else self.color
        if self.active:
            current_color = (0, 150, 0)  # Active tactical green

        rect = self.get_rect()
        pygame.draw.rect(renderer.screen, current_color, rect, border_radius=6)
        
        # Draw stroke
        stroke_color = COLOR_WHITE if self.hovered else (100, 110, 120)
        pygame.draw.rect(renderer.screen, stroke_color, rect, 2, border_radius=6)

        # Draw text
        font = renderer.font_medium
        text_surface = font.render(self.label, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        renderer.screen.blit(text_surface, text_rect)


class UIManager:
    """Manages all HUD UI elements."""

    def __init__(self):
        """Initialize UI manager."""
        self.buttons = {}
        self.create_buttons()
        self.mouse_pos = Vector2D(0, 0)

    def create_buttons(self):
        """Create all HUD buttons."""
        # Active swarm display with switcher (top left)
        self.buttons["swarm_label"] = Button(Vector2D(45, 15), 80, 20, "UNIT:", (20, 25, 30), COLOR_WHITE)
        self.buttons["swarm_display"] = Button(Vector2D(45, 35), 80, 25, "DRONE", COLOR_DRONE, COLOR_BLACK)
        self.buttons["swarm_prev"] = Button(Vector2D(15, 35), 25, 25, "◄", (20, 25, 30))
        self.buttons["swarm_next"] = Button(Vector2D(75, 35), 25, 25, "►", (20, 25, 30))

        # Active environment display with switcher (top middle)
        self.buttons["env_label"] = Button(Vector2D(190, 15), 80, 20, "ZONE:", (20, 25, 30), COLOR_WHITE)
        self.buttons["env_display"] = Button(Vector2D(190, 35), 80, 25, "AIR", COLOR_AIR, COLOR_WHITE)
        self.buttons["env_prev"] = Button(Vector2D(160, 35), 25, 25, "◄", (20, 25, 30))
        self.buttons["env_next"] = Button(Vector2D(220, 35), 25, 25, "►", (20, 25, 30))

        # Control buttons (top right)
        self.buttons["spawn"] = Button(Vector2D(SCREEN_WIDTH - 130, 30), 100, 30, "DEPLOY x50", (30, 40, 50))
        self.buttons["pause"] = Button(Vector2D(SCREEN_WIDTH - 40, 30), 60, 30, "HOLD", (30, 40, 50))

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
        if button_name in ["drone", "pod", "bot"]:
            # Update swarm display
            label_map = {"drone": "DRONE", "pod": "POD", "bot": "BOT"}
            color_map = {"drone": COLOR_DRONE, "pod": COLOR_POD, "bot": COLOR_BOT}
            self.buttons["swarm_display"].label = label_map[button_name]
            self.buttons["swarm_display"].color = color_map[button_name]
            self.buttons["swarm_display"].text_color = COLOR_BLACK
        elif button_name in ["air", "water", "ground"]:
            # Update environment display
            label_map = {"air": "AIR", "water": "WATER", "ground": "GROUND"}
            color_map = {"air": COLOR_AIR, "water": COLOR_WATER, "ground": COLOR_GROUND}
            self.buttons["env_display"].label = label_map[button_name]
            self.buttons["env_display"].color = color_map[button_name]

    def draw(self, renderer):
        """Draw all HUD elements."""
        # Top translucent control bar
        hud_bar = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        hud_bar.fill((15, 20, 25, 200)) # Tactical dark navy with alpha
        renderer.screen.blit(hud_bar, (0, 0))
        
        # Bottom translucent stats bar
        stat_bar = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        stat_bar.fill((15, 20, 25, 200)) 
        renderer.screen.blit(stat_bar, (0, SCREEN_HEIGHT - 60))

        for button in self.buttons.values():
            button.draw(renderer)

    def draw_stats(self, renderer, stats):
        """Draw tactical telemetry on the HUD."""
        stats_text = (
            f"AIR: {stats.get('drone_count', 0):03d} | "
            f"SUB: {stats.get('pod_count', 0):03d} | "
            f"GND: {stats.get('bot_count', 0):03d} | "
            f"HOSTILES: {stats.get('targets_alive', 0):02d} | "
            f"CLEARED: {stats.get('targets_destroyed', 0):03d}"
        )
        renderer.draw_text(stats_text, (20, SCREEN_HEIGHT - 40), COLOR_WHITE, "medium")

    def draw_help(self, renderer):
        """Draw help text for command input."""
        help_text = "[L-CLK] DESIGNATE HOSTILE  |  [R-CLK] DEPLOY BARRICADE"
        renderer.draw_text(help_text, (SCREEN_WIDTH - 600, SCREEN_HEIGHT - 40), (150, 160, 170), "medium")
