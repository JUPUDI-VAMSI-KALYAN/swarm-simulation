"""Main tactical simulation loop."""

import pygame
import random
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_DRONE, COLOR_TARGET,
    COLOR_WHITE, COLOR_GROUND, COLOR_WATER, COLOR_AIR, SwarmConfig
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
from src.environment.osm_map import OSMMapManager
from src.intelligence.communication import CommunicationSystem


class Simulation:
    """Main tactical simulation controller."""

    def __init__(self):
        """Initialize the simulation."""
        self.renderer = Renderer("DualHQ Tactical Swarm Simulation - v2")
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

        # Geographic maps (OpenStreetMap)
        self.map_manager = OSMMapManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.show_map = True
        self.map_type = "india"  # "india" or "indian_ocean"

    def spawn_swarm(self, swarm_type, count=50, position=None):
        """
        Spawn a swarm of the specified type.

        Args:
            swarm_type: Type of swarm ("drone", "pod", "bot")
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
        Sets nearest agent as scout, which broadcasts to swarm.

        Args:
            position: Vector2D position
        """
        target = Target(position=position, health=100)
        self.targets.append(target)

        # Find nearest agent and tell it first (scout discovery)
        all_agents = self.swarm_controller.get_all_agents()
        if all_agents:
            nearest_agent = min(all_agents, key=lambda a: a.position.distance(position))
            # Set target on nearest agent (first scout discovers target)
            nearest_agent.target = target
            nearest_agent.aggressive = True
            nearest_agent.aggressive_timeout = SwarmConfig.DEFAULT_AGGRESSIVE_TIMEOUT
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

            # Map follows environment: air -> India, water -> Indian Ocean, ground -> India
            if env_type == "water":
                self.map_manager.indian_ocean_renderer.set_region("indian_ocean")
                self.map_type = "indian_ocean"
            else:
                self.map_manager.india_renderer.set_region("india")
                self.map_type = "india"

            # Clear incompatible swarms and set active button
            if env_type == "air":
                self.swarm_controller.swarms["pod"].clear()
                self.swarm_controller.swarms["bot"].clear()
                self.swarm_controller.active_swarm_type = "drone"
                self.ui_manager.set_active_button("drone")
                if not self.swarm_controller.swarms["drone"]:
                    self.spawn_swarm("drone", 50)
            elif env_type == "water":
                self.swarm_controller.swarms["drone"].clear()
                self.swarm_controller.swarms["bot"].clear()
                self.swarm_controller.active_swarm_type = "pod"
                self.ui_manager.set_active_button("pod")
                if not self.swarm_controller.swarms["pod"]:
                    self.spawn_swarm("pod", 50)
            elif env_type == "ground":
                self.swarm_controller.swarms["drone"].clear()
                self.swarm_controller.swarms["pod"].clear()
                self.swarm_controller.active_swarm_type = "bot"
                self.ui_manager.set_active_button("bot")
                if not self.swarm_controller.swarms["bot"]:
                    self.spawn_swarm("bot", 50)

    def _broadcast_swarm_messages(self, all_agents):
        """
        Broadcast target information through swarm using neighbor communication.
        This replaces O(n²) propagation with neighbor-based message passing.

        Args:
            all_agents: List of all agents in simulation
        """
        from src.intelligence.communication import Message, MessageType

        for agent in all_agents:
            if not agent.alive or agent.target is None:
                continue

            # Agent has a target - broadcast to neighbors only
            if agent.neighbors:
                message = Message(
                    msg_type=MessageType.TARGET_FOUND,
                    sender_id=agent.id,
                    position=agent.position,
                    target_pos=agent.target.position if agent.target else None,
                    priority=max(7, agent.attack_priority),
                    target=agent.target
                )
                agent.broadcast_to_neighbors(agent.neighbors, message)

    def update(self, delta_time):
        """Update tactical simulation state."""
        if self.paused:
            return

        # Update environment dynamics
        self.current_environment.update(delta_time)

        # Update swarms logic
        self.swarm_controller.update_swarms(delta_time, self.targets, self.obstacles)

        # Process C2 mesh messaging
        all_agents = self.swarm_controller.get_all_agents()
        self._broadcast_swarm_messages(all_agents)

        # Update targets / hostiles
        for target in self.targets:
            if target.alive:
                target.update(delta_time)

            if target.is_destroyed():
                self.targets_destroyed += 1

        self.targets = [t for t in self.targets if t.alive]
        self.swarm_controller.remove_dead_agents()

    def render(self):
        """Render the simulation HUD and units."""
        
        # Render geographic map if enabled
        if self.show_map:
            renderer = self.map_manager.get_renderer(self.map_type)
            renderer.render(self.renderer.screen)
        else:
            self.renderer.screen.fill(self.current_environment.color)

        for obstacle in self.obstacles:
            self.renderer.draw_rectangle(
                obstacle.position, obstacle.width, obstacle.height, obstacle.color
            )

        # Draw signals if on ground (bots mesh network visualizer)
        if self.current_environment_type == "ground" and self.swarm_controller.swarms["bot"]:
            # Optionally we could render the pheromones/signals grid here 
            pass

        for target in self.targets:
            if target.alive:
                self.renderer.draw_rectangle(
                    target.position,
                    target.radius * 2 + 4,
                    target.radius * 2 + 4,
                    COLOR_TARGET,
                    filled=False  # outlined shape
                )
                self.renderer.draw_rectangle(
                    target.position, target.radius * 1.5, target.radius * 1.5, COLOR_TARGET
                )

                health_bar_width = 40
                health_bar_height = 5
                bar_pos = Vector2D(target.position.x, target.position.y - target.radius - 12)
                self.renderer.draw_health_bar(
                    bar_pos, health_bar_width, health_bar_height,
                    target.health, target.max_health
                )

        # Render explicit agent shapes
        agents = self.swarm_controller.get_all_agents()
        for agent in agents:
            if not agent.alive:
                continue

            if agent.swarm_type == "drone":
                # Triangles for drones
                dir_vec = agent.velocity.normalize()
                if dir_vec.magnitude() == 0:
                    dir_vec = Vector2D(0, -1)
                p1 = agent.position + dir_vec * agent.radius * 2
                p2 = agent.position - dir_vec * agent.radius + Vector2D(-dir_vec.y, dir_vec.x) * agent.radius * 1.5
                p3 = agent.position - dir_vec * agent.radius - Vector2D(-dir_vec.y, dir_vec.x) * agent.radius * 1.5
                self.renderer.draw_polygon([p1.to_tuple(), p2.to_tuple(), p3.to_tuple()], agent.color)

            elif agent.swarm_type == "pod":
                # Torpedo shapes (pills) or elongated rects for pods
                dir_vec = agent.velocity.normalize()
                if dir_vec.magnitude() == 0:
                    dir_vec = Vector2D(1, 0)
                length = agent.radius * 3
                thick = agent.radius * 1.2
                # Center is agent.position
                p1 = agent.position + dir_vec * (length/2)
                p2 = agent.position - dir_vec * (length/2)
                self.renderer.draw_line(p1, p2, agent.color, width=int(thick))
                # Add a lighter front tip
                self.renderer.draw_circle(p1, thick/2, COLOR_WHITE)

            elif agent.swarm_type == "bot":
                # Square chassis for ground bots
                self.renderer.draw_rectangle(agent.position, agent.radius * 2.5, agent.radius * 2.5, agent.color)
                # Maybe add a small dot indicating forward
                dir_vec = agent.velocity.normalize()
                if dir_vec.magnitude() > 0:
                    fwd_pt = agent.position + dir_vec * agent.radius * 1.5
                    self.renderer.draw_circle(fwd_pt, 2, COLOR_WHITE)

            else:
                self.renderer.draw_circle(agent.position, agent.radius, agent.color)

        self.ui_manager.update(Vector2D(*pygame.mouse.get_pos()))
        self.ui_manager.draw(self.renderer)

        stats = self.swarm_controller.get_swarm_stats()
        stats["targets_alive"] = len([t for t in self.targets if t.alive])
        stats["targets_destroyed"] = self.targets_destroyed
        self.ui_manager.draw_stats(self.renderer, stats)
        self.ui_manager.draw_help(self.renderer)
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

                # Swarm cycling
                if button_name == "swarm_cycle_next":
                    swarm_types = ["drone", "pod", "bot"]
                    current = self.swarm_controller.active_swarm_type
                    next_idx = (swarm_types.index(current) + 1) % len(swarm_types)
                    next_swarm = swarm_types[next_idx]
                    env_map = {"drone": "air", "pod": "water", "bot": "ground"}
                    self.switch_environment(env_map[next_swarm])

                elif button_name == "swarm_cycle_prev":
                    swarm_types = ["drone", "pod", "bot"]
                    current = self.swarm_controller.active_swarm_type
                    prev_idx = (swarm_types.index(current) - 1) % len(swarm_types)
                    prev_swarm = swarm_types[prev_idx]
                    env_map = {"drone": "air", "pod": "water", "bot": "ground"}
                    self.switch_environment(env_map[prev_swarm])

                # Environment cycling
                elif button_name == "env_cycle_next":
                    envs = ["air", "water", "ground"]
                    current_env = self.current_environment_type
                    next_idx = (envs.index(current_env) + 1) % len(envs)
                    self.switch_environment(envs[next_idx])

                elif button_name == "env_cycle_prev":
                    envs = ["air", "water", "ground"]
                    current_env = self.current_environment_type
                    prev_idx = (envs.index(current_env) - 1) % len(envs)
                    self.switch_environment(envs[prev_idx])

                # Direct swarm type buttons (fallback)
                elif button_name in ["drone", "pod", "bot"]:
                    swarm_type = button_name
                    if not self.swarm_controller.swarms[swarm_type]:
                        self.spawn_swarm(swarm_type, 50)
                    else:
                        self.swarm_controller.active_swarm_type = swarm_type
                        self.ui_manager.set_active_button(swarm_type)

                # Environment buttons (fallback)
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

        # Spawn initial drone swarm
        self.spawn_swarm("drone", 50)

        while self.running:
            delta_time = self.renderer.tick()
            self.handle_events()
            self.update(delta_time)
            self.render()

        self.renderer.quit()

    def quit(self):
        """Clean shutdown."""
        self.running = False
