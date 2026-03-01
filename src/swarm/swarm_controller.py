"""SwarmController manages all tactical swarms and their coordination."""

import random
from src.swarm.drone import Drone
from src.swarm.pod import Pod
from src.swarm.bot import Bot
from src.intelligence.tactical_formation import TacticalFormationBehavior
from src.intelligence.sonar_sweeps import SonarSweepBehavior
from src.intelligence.signal_network import SignalNetworkMap
from src.core.vector2d import Vector2D
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class SwarmController:
    """Manages all tactical swarms (Drones, Pods, Bots) and coordinates their behavior."""

    def __init__(self):
        """Initialize the swarm controller."""
        self.swarms = {
            "drone": [],
            "pod": [],
            "bot": []
        }
        self.active_swarm_type = "drone"
        self.neighbor_update_timer = 0 # Track time for 10Hz sensing updates

        # Digital signal map for bots
        self.signal_map = SignalNetworkMap()

        # Torpedo barrage state
        self.pod_barrage_target = None
        self.pod_barrage_active = False

    def _create_grid_positions(self, center, count, spacing=60):
        """
        Create grid positions for agents to spread out.

        Args:
            center: Center position (Vector2D)
            count: Number of positions to create
            spacing: Distance between grid points

        Returns:
            List of Vector2D positions
        """
        positions = []
        grid_size = int((count ** 0.5) + 1)  # sqrt(count) x sqrt(count) grid

        for i in range(count):
            row = i // grid_size
            col = i % grid_size

            # Calculate grid position relative to center
            x = center.x + (col - grid_size / 2) * spacing
            y = center.y + (row - grid_size / 2) * spacing

            # Clamp to screen bounds
            x = max(10, min(SCREEN_WIDTH - 10, x))
            y = max(10, min(SCREEN_HEIGHT - 10, y))

            positions.append(Vector2D(x, y))

        return positions

    def spawn_swarm(self, swarm_type, count, position, environment=None):
        """
        Spawn a new swarm of tactical agents in a grid pattern.

        Args:
            swarm_type: Type of swarm ("drone", "pod", "bot")
            count: Number of agents to spawn
            position: Center position for spawning (Vector2D)
            environment: Environment object

        Returns:
            List of spawned agents
        """
        spawned = []

        # Generate grid positions for spreading
        grid_positions = self._create_grid_positions(position, count, spacing=60)

        if swarm_type == "drone":
            formation_behavior = TacticalFormationBehavior()

            for idx, grid_pos in enumerate(grid_positions):
                drone = Drone(position=grid_pos, formation_behavior=formation_behavior)
                self.swarms["drone"].append(drone)
                spawned.append(drone)

        elif swarm_type == "pod":
            sweep_behavior = SonarSweepBehavior()

            for idx, grid_pos in enumerate(grid_positions):
                pod = Pod(position=grid_pos, sweep_behavior=sweep_behavior)
                self.swarms["pod"].append(pod)
                spawned.append(pod)

        elif swarm_type == "bot":
            for idx, grid_pos in enumerate(grid_positions):
                bot = Bot(position=grid_pos, signal_map=self.signal_map)
                self.swarms["bot"].append(bot)
                spawned.append(bot)

        return spawned

    def update_swarms(self, delta_time, targets, obstacles):
        """
        Main update loop for all swarms.
        """
        # Update signal network map
        self.signal_map.update()

        self.neighbor_update_timer += delta_time
        should_update_neighbors = False
        if self.neighbor_update_timer >= 0.1: # Update neighbors at 10Hz
            should_update_neighbors = True
            self.neighbor_update_timer = 0

        # Gather all agents for neighbor sensing across types
        all_agents = self.get_all_agents()

        # Update each sub-swarm
        self._update_drone_swarm(delta_time, targets, should_update_neighbors, all_agents)
        self._update_pod_swarm(delta_time, targets, should_update_neighbors, all_agents)
        self._update_bot_swarm(delta_time, targets, should_update_neighbors, all_agents)

    def _update_drone_swarm(self, delta_time, targets_list, should_update_neighbors, all_agents=None):
        """Update all drones in the air fleet."""
        drone_list = self.swarms["drone"]
        alive_drones = [d for d in drone_list if d.alive]

        if not alive_drones:
            return

        # Update neighbor lists (Universal sensing for cross-swarm mesh)
        if should_update_neighbors:
            sensing_entities = all_agents if all_agents else alive_drones
            for drone in alive_drones:
                drone.sense_environment(sensing_entities, targets_list)

        # Update each drone
        for drone in alive_drones:
            neighbors = drone.neighbors if drone.neighbors else []
            drone.update(delta_time, neighbors, drone.target, targets_list)

            # Attack if in range
            if drone.target and drone.target.alive:
                dist = drone.distance_to(drone.target)

                # Decide to kamikaze strike or normal payload
                if drone.can_strike() and dist < 250 and random.random() < 0.02:  # 2% chance per frame
                    drone.initiate_strike(drone.target)

                # Perform attacks
                if drone.is_striking:
                    damage = drone.perform_strike(drone.target, delta_time)
                    if damage > 0:
                        drone.target.take_damage(damage)
                else:
                    damage = drone.perform_normal_attack(drone.target)
                    if damage > 0:
                        drone.target.take_damage(damage)

        # Remove dead drones
        self.swarms["drone"] = [d for d in self.swarms["drone"] if d.alive]

    def _update_pod_swarm(self, delta_time, targets_list, should_update_neighbors, all_agents=None):
        """Update all pods in the fleet."""
        pod_list = self.swarms["pod"]
        alive_pods = [p for p in pod_list if p.alive]

        if not alive_pods:
            return

        # Update neighbor lists (Universal sensing for cross-swarm mesh)
        if should_update_neighbors:
            sensing_entities = all_agents if all_agents else alive_pods
            for pod in alive_pods:
                pod.sense_environment(sensing_entities, targets_list)

        # Get collective vote for torpedo barrage
        barrage_target = None
        votes = {}
        for pod in alive_pods:
            pod.vote_for_target(targets_list, pod.neighbors if pod.neighbors else [])
            if pod.barrage_vote:
                votes[pod.barrage_vote] = votes.get(pod.barrage_vote, 0) + 1

        # Check if barrage should start
        if votes and len(alive_pods) > 0:
            max_votes = max(votes.values())
            if max_votes / len(alive_pods) >= 0.6:
                barrage_target = [t for t, v in votes.items() if v == max_votes][0]

        self.pod_barrage_target = barrage_target
        self.pod_barrage_active = barrage_target is not None

        # Update each pod
        for pod in alive_pods:
            neighbors = pod.neighbors if pod.neighbors else []
            pod.update(delta_time, neighbors, pod.target, targets_list, attacking=self.pod_barrage_active)

            # Attack if in range
            if pod.target and pod.target.alive:
                damage_per_sec = pod.perform_attack(pod.target)
                if damage_per_sec > 0:
                    final_damage = damage_per_sec * delta_time
                    pod.target.take_damage(final_damage)

        self.swarms["pod"] = [p for p in self.swarms["pod"] if p.alive]

    def _update_bot_swarm(self, delta_time, targets_list, should_update_neighbors, all_agents=None):
        """Update all bots in the ground unit."""
        bot_list = self.swarms["bot"]
        alive_bots = [b for b in bot_list if b.alive]

        if not alive_bots:
            return

        # Update neighbor lists (Universal sensing for cross-swarm mesh)
        if should_update_neighbors:
            sensing_entities = all_agents if all_agents else alive_bots
            for bot in alive_bots:
                bot.sense_environment(sensing_entities, targets_list)

        # Update each bot
        for bot in alive_bots:
            neighbors = bot.neighbors if bot.neighbors else []
            bot.update(delta_time, neighbors, bot.target, targets_list)

            # Attack if in range
            if bot.target and bot.target.alive:
                damage_per_sec = bot.perform_attack(bot.target)
                if damage_per_sec > 0:
                    final_damage = damage_per_sec * delta_time
                    bot.target.take_damage(final_damage)

        self.swarms["bot"] = [b for b in self.swarms["bot"] if b.alive]

    def get_all_agents(self):
        """Get all active agents from all swarms."""
        agents = []
        agents.extend(self.swarms["drone"])
        agents.extend(self.swarms["pod"])
        agents.extend(self.swarms["bot"])
        return [a for a in agents if a.alive]

    def get_swarm_stats(self):
        """Get statistics about all swarms."""
        stats = {
            "drone_count": len([a for a in self.swarms["drone"] if a.alive]),
            "pod_count": len([a for a in self.swarms["pod"] if a.alive]),
            "bot_count": len([a for a in self.swarms["bot"] if a.alive]),
            "total_agents": len(self.get_all_agents())
        }
        return stats

    def broadcast_target_info(self, target):
        """
        Broadcast information about a target to nearby swarms.

        Args:
            target: Target entity
        """
        # Drones naturally find targets through sensors
        pass

    def remove_dead_agents(self):
        """Remove all dead agents from swarms."""
        for swarm_type in self.swarms:
            self.swarms[swarm_type] = [
                agent for agent in self.swarms[swarm_type]
                if agent.alive
            ]

    def switch_swarm_type(self, new_type):
        """
        Switch the active swarm type.

        Args:
            new_type: New swarm type ("drone", "pod", "bot")
        """
        if new_type in self.swarms:
            self.active_swarm_type = new_type

    def clear_all_swarms(self):
        """Remove all swarms."""
        for swarm_type in self.swarms:
            self.swarms[swarm_type].clear()
