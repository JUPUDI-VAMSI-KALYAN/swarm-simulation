"""Main simulation loop."""

import pygame
import random
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_BIRD, COLOR_TARGET,
    COLOR_WHITE, COLOR_GROUND, COLOR_WATER, COLOR_AIR
)
from src.core.vector2d import Vector2D
from src.rendering.renderer import Renderer
from src.rendering.ui import UIManager
from src.swarm.swarm_controller import SwarmController
from src.entities.target import Target
from src.entities.obstacle import Obstacle
from src.simulation.input_handler import InputHandler
from src.environment.environment import Environment
from src.environment.air import AirEnvironment
from src.environment.water import WaterEnvironment
from src.environment.terrain import TerrainEnvironment
from src.intelligence.communication import CommunicationSystem


class Simulation:
    """Main simulation controller."""

    def __init__(self):
        """Initialize the simulation."""
        self.renderer = Renderer("Swarm Simulation - Full v1")
        self.ui_manager = UIManager()
        self.swarm_controller = SwarmController()
        self.input_handler = InputHandler()

        self.targets = []
        self.obstacles = []

        self.running = False
        self.paused = False
        self.total_damage_dealt = 0
        self.targets_destroyed = 0

        # Communication system
        self.communication = CommunicationSystem()

        # Environment management
        self.current_environment_type = "air"
        self.environments = {
            "air": AirEnvironment(),
            "water": WaterEnvironment(),
            "ground": TerrainEnvironment()
        }
        self.current_environment = self.environments["air"]

    def spawn_swarm(self, swarm_type, count=50, position=None):
        """
        Spawn a swarm of the specified type.

        Args:
            swarm_type: Type of swarm ("bird", "fish", "ant")
            count: Number of agents
            position: Center position (Vector2D)
        """
        if position is None:
            position = Vector2D(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        self.swarm_controller.spawn_swarm(swarm_type, count, position)
        self.swarm_controller.active_swarm_type = swarm_type
        self.ui_manager.set_active_button(swarm_type)

    def place_target(self, position):
        """
        Place a target at the given position.
        Broadcasts to nearest swarm member, then swarm communicates.

        Args:
            position: Vector2D position
        """
        target = Target(position=position, health=100)
        self.targets.append(target)

        # Find nearest agent and tell it
        all_agents = self.swarm_controller.get_all_agents()
        if all_agents:
            nearest_agent = min(all_agents, key=lambda a: a.position.distance(position))
            # Set target on nearest agent (first scout)
            nearest_agent.target = target
            nearest_agent.aggressive = True
            nearest_agent.attack_priority = 10
            nearest_agent.state = "attacking"

    def place_obstacle(self, position):
        """
        Place an obstacle at the given position.

        Args:
            position: Vector2D position
        """
        obstacle = Obstacle(position=position, width=30, height=30)
        self.obstacles.append(obstacle)
        self.current_environment.add_obstacle(obstacle)

    def switch_environment(self, env_type):
        """
        Switch to a different environment.

        Args:
            env_type: Environment type ("air", "water", "ground")
        """
        if env_type in self.environments:
            self.current_environment_type = env_type
            self.current_environment = self.environments[env_type]
            self.ui_manager.set_active_button(env_type)

            # Clear incompatible swarms
            if env_type == "air":
                self.swarm_controller.swarms["fish"].clear()
                self.swarm_controller.swarms["ant"].clear()
                if not self.swarm_controller.swarms["bird"]:
                    self.spawn_swarm("bird", 50)
            elif env_type == "water":
                self.swarm_controller.swarms["bird"].clear()
                self.swarm_controller.swarms["ant"].clear()
                if not self.swarm_controller.swarms["fish"]:
                    self.spawn_swarm("fish", 50)
            elif env_type == "ground":
                self.swarm_controller.swarms["bird"].clear()
                self.swarm_controller.swarms["fish"].clear()
                if not self.swarm_controller.swarms["ant"]:
                    self.spawn_swarm("ant", 50)

    def update(self, delta_time):
        """Update simulation state."""
        if self.paused:
            return

        # Update environment
        self.current_environment.update(delta_time)

        # Update swarms
        self.swarm_controller.update_swarms(delta_time, self.targets, self.obstacles)

        # Propagate target information through swarm
        all_agents = self.swarm_controller.get_all_agents()
        self.communication.propagate_target_info(all_agents, 120)  # Communication radius 120

        # Update targets
        for target in self.targets:
            if target.alive:
                target.update(delta_time)

            # Track damage and destruction
            if target.is_destroyed():
                self.targets_destroyed += 1

        # Remove dead targets
        self.targets = [t for t in self.targets if t.alive]

        # Clean up dead agents
        self.swarm_controller.remove_dead_agents()

    def render(self):
        """Render the simulation."""
        # Draw environment background
        self.renderer.screen.fill(self.current_environment.color)

        # Draw obstacles
        for obstacle in self.obstacles:
            self.renderer.draw_rectangle(
                obstacle.position,
                obstacle.width,
                obstacle.height,
                obstacle.color
            )

        # Draw all targets
        for target in self.targets:
            if target.alive:
                self.renderer.draw_rectangle(
                    target.position,
                    target.radius * 2,
                    target.radius * 2,
                    COLOR_TARGET
                )

                # Draw health bar
                health_bar_width = 40
                health_bar_height = 5
                bar_pos = Vector2D(target.position.x, target.position.y - target.radius - 10)
                self.renderer.draw_health_bar(
                    bar_pos, health_bar_width, health_bar_height,
                    target.health, target.max_health
                )

        # Draw all agents
        agents = self.swarm_controller.get_all_agents()
        for agent in agents:
            if agent.alive:
                self.renderer.draw_circle(agent.position, agent.radius, agent.color)

        # Draw UI
        self.ui_manager.update(Vector2D(*pygame.mouse.get_pos()))
        self.ui_manager.draw(self.renderer)

        # Draw stats
        stats = self.swarm_controller.get_swarm_stats()
        stats["targets_alive"] = len([t for t in self.targets if t.alive])
        stats["targets_destroyed"] = self.targets_destroyed
        self.ui_manager.draw_stats(self.renderer, stats)
        self.ui_manager.draw_help(self.renderer)

        # Draw FPS
        self.renderer.display_fps()

        self.renderer.flip()

    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            actions = self.input_handler.handle_events(event)

            if actions["quit"]:
                self.running = False
            elif actions["pause"]:
                self.paused = not self.paused
            elif actions["reset"]:
                self.reset_simulation()
            elif actions["place_target"]:
                self.place_target(actions["mouse_pos"])
            elif actions["place_obstacle"]:
                self.place_obstacle(actions["mouse_pos"])
            elif actions["spawn_swarm"]:
                swarm_type = self.swarm_controller.active_swarm_type
                self.spawn_swarm(swarm_type, 50)

            # Handle UI button clicks
            button_action = self.ui_manager.handle_click(actions["mouse_pos"])
            if "clicked_button" in button_action:
                button_name = button_action["clicked_button"]

                # Swarm type buttons
                if button_name in ["bird", "fish", "ant"]:
                    swarm_type = button_name
                    if not self.swarm_controller.swarms[swarm_type]:
                        self.spawn_swarm(swarm_type, 50)
                    else:
                        self.swarm_controller.active_swarm_type = swarm_type
                        self.ui_manager.set_active_button(swarm_type)

                # Environment buttons
                elif button_name in ["ground", "water", "air"]:
                    self.switch_environment(button_name)

                # Control buttons
                elif button_name == "spawn":
                    self.spawn_swarm(self.swarm_controller.active_swarm_type, 50)
                elif button_name == "pause":
                    self.paused = not self.paused

    def reset_simulation(self):
        """Reset simulation to initial state."""
        self.swarm_controller.clear_all_swarms()
        self.targets.clear()
        self.obstacles.clear()
        self.total_damage_dealt = 0
        self.targets_destroyed = 0
        self.switch_environment("air")

    def run(self):
        """Main simulation loop."""
        self.running = True

        # Spawn initial flock
        self.spawn_swarm("bird", 50)

        while self.running:
            delta_time = self.renderer.tick()
            self.handle_events()
            self.update(delta_time)
            self.render()

        self.renderer.quit()

    def quit(self):
        """Clean shutdown."""
        self.running = False
