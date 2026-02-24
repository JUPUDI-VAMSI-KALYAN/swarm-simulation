"""Handle mouse and keyboard input."""

import pygame
from src.core.vector2d import Vector2D


class InputHandler:
    """Manages user input events."""

    def __init__(self):
        """Initialize input handler."""
        self.mouse_pos = Vector2D(0, 0)
        self.mouse_clicked = False
        self.mouse_clicked_right = False
        self.keys_pressed = {}

    def handle_events(self, event):
        """
        Process a Pygame event.

        Args:
            event: Pygame event object

        Returns:
            Dictionary of input actions
        """
        actions = {
            "quit": False,
            "pause": False,
            "spawn_swarm": False,
            "place_target": False,
            "place_obstacle": False,
            "reset": False,
            "mouse_pos": self.mouse_pos,
            "active_key": None
        }

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                actions["quit"] = True
            elif event.key == pygame.K_SPACE:
                actions["pause"] = True
            elif event.key == pygame.K_r:
                actions["reset"] = True
            elif event.key == pygame.K_s:
                actions["spawn_swarm"] = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_pos = Vector2D(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            actions["mouse_pos"] = self.mouse_pos

            if event.button == 1:  # Left click
                actions["place_target"] = True
            elif event.button == 3:  # Right click
                actions["place_obstacle"] = True

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = Vector2D(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            actions["mouse_pos"] = self.mouse_pos

        return actions
