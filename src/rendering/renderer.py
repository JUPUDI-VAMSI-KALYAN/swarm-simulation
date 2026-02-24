"""Pygame-based rendering engine for the simulation."""

import pygame
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR,
    COLOR_WHITE, COLOR_BLACK
)


class Renderer:
    """Handles all Pygame rendering."""

    def __init__(self, title="Swarm Simulation"):
        """Initialize Pygame and create display."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)

    def clear(self):
        """Clear screen with background color."""
        self.screen.fill(BACKGROUND_COLOR)

    def draw_circle(self, position, radius, color, filled=True):
        """Draw a circle."""
        x, y = int(position.x), int(position.y)
        if filled:
            pygame.draw.circle(self.screen, color, (x, y), int(radius))
        else:
            pygame.draw.circle(self.screen, color, (x, y), int(radius), 2)

    def draw_rectangle(self, position, width, height, color, filled=True):
        """Draw a rectangle."""
        x, y = int(position.x), int(position.y)
        rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 2)

    def draw_line(self, start_pos, end_pos, color, width=1):
        """Draw a line."""
        x1, y1 = int(start_pos.x), int(start_pos.y)
        x2, y2 = int(end_pos.x), int(end_pos.y)
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

    def draw_polygon(self, points, color, filled=True):
        """Draw a polygon given list of points."""
        int_points = [(int(p[0]), int(p[1])) for p in points]
        if filled:
            pygame.draw.polygon(self.screen, color, int_points)
        else:
            pygame.draw.polygon(self.screen, color, int_points, 2)

    def draw_text(self, text, position, color=COLOR_BLACK, size="small"):
        """Draw text on screen."""
        font = self.font_small if size == "small" else self.font_large
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (int(position[0]), int(position[1])))

    def draw_health_bar(self, position, width, height, current_health, max_health, bg_color=(200, 200, 200)):
        """Draw a health bar."""
        x, y = int(position.x), int(position.y)

        # Background
        pygame.draw.rect(self.screen, bg_color, (x - width // 2, y - height // 2, width, height))

        # Health bar (gradient from green to red)
        health_percent = max(0, min(1, current_health / max_health))
        if health_percent > 0.5:
            color = (int(255 * (1 - health_percent) * 2), 255, 0)  # Green to Yellow
        else:
            color = (255, int(255 * health_percent * 2), 0)  # Yellow to Red

        health_width = int(width * health_percent)
        pygame.draw.rect(self.screen, color, (x - width // 2, y - height // 2, health_width, height))

        # Border
        pygame.draw.rect(self.screen, (50, 50, 50), (x - width // 2, y - height // 2, width, height), 1)

    def display_fps(self):
        """Display current FPS in top-left corner."""
        fps = self.clock.get_fps()
        fps_text = f"FPS: {fps:.1f}"
        self.draw_text(fps_text, (10, 10), COLOR_WHITE, "small")

    def flip(self):
        """Update the display."""
        pygame.display.flip()

    def tick(self, fps=FPS):
        """Cap framerate and return delta time."""
        return self.clock.tick(fps) / 1000.0  # Convert milliseconds to seconds

    def get_mouse_pos(self):
        """Get current mouse position."""
        return pygame.mouse.get_pos()

    def quit(self):
        """Clean up Pygame."""
        pygame.quit()
