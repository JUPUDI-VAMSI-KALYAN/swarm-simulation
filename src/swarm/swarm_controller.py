"""SwarmController manages all swarms and their coordination."""

import random
from src.swarm.bird import Bird
from src.swarm.fish import Fish
from src.swarm.ant import Ant
from src.intelligence.flocking import FlockingBehavior
from src.intelligence.schooling import SchoolingBehavior
from src.intelligence.pheromone import PheromoneMap
from src.core.vector2d import Vector2D
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class SwarmController:
    """Manages all swarms and coordinates their behavior."""

    def __init__(self):
        """Initialize the swarm controller."""
        self.swarms = {
            "bird": [],
            "fish": [],
            "ant": []
        }
        self.active_swarm_type = "bird"
        self.neighbor_update_counter = 0
        self.neighbor_update_frequency = 5  # Update neighbors every N frames

        # Pheromone map for ants
        self.pheromone_map = PheromoneMap()

        # Wave attack state
        self.fish_wave_target = None
        self.fish_wave_active = False

    def spawn_swarm(self, swarm_type, count, position, environment=None):
        """
        Spawn a new swarm of agents.

        Args:
            swarm_type: Type of swarm ("bird", "fish", "ant")
            count: Number of agents to spawn
            position: Center position for spawning (Vector2D)
            environment: Environment object

        Returns:
            List of spawned agents
        """
        spawned = []

        if swarm_type == "bird":
            flock_behavior = FlockingBehavior(
                cohesion_weight=0.3,
                separation_weight=0.3,
                alignment_weight=0.4
            )

            for _ in range(count):
                offset = Vector2D(
                    random.uniform(-30, 30),
                    random.uniform(-30, 30)
                )
                pos = position + offset
                pos.x = max(10, min(SCREEN_WIDTH - 10, pos.x))
                pos.y = max(10, min(SCREEN_HEIGHT - 10, pos.y))

                bird = Bird(position=pos, flock_behavior=flock_behavior)
                self.swarms["bird"].append(bird)
                spawned.append(bird)

        elif swarm_type == "fish":
            schooling_behavior = SchoolingBehavior(
                cohesion_weight=0.25,
                separation_weight=0.4,
                alignment_weight=0.35
            )

            for _ in range(count):
                offset = Vector2D(
                    random.uniform(-40, 40),
                    random.uniform(-40, 40)
                )
                pos = position + offset
                pos.x = max(10, min(SCREEN_WIDTH - 10, pos.x))
                pos.y = max(10, min(SCREEN_HEIGHT - 10, pos.y))

                fish = Fish(position=pos, schooling_behavior=schooling_behavior)
                self.swarms["fish"].append(fish)
                spawned.append(fish)

        elif swarm_type == "ant":
            for _ in range(count):
                offset = Vector2D(
                    random.uniform(-30, 30),
                    random.uniform(-30, 30)
                )
                pos = position + offset
                pos.x = max(10, min(SCREEN_WIDTH - 10, pos.x))
                pos.y = max(10, min(SCREEN_HEIGHT - 10, pos.y))

                ant = Ant(position=pos, pheromone_map=self.pheromone_map)
                self.swarms["ant"].append(ant)
                spawned.append(ant)

        return spawned

    def update_swarms(self, delta_time, targets_list, obstacles_list=None):
        """
        Update all active swarms.

        Args:
            delta_time: Time since last update
            targets_list: List of target entities
            obstacles_list: List of obstacles
        """
        # Update pheromone map
        self.pheromone_map.update()

        # Update neighbor cache periodically
        self.neighbor_update_counter += 1
        should_update_neighbors = (self.neighbor_update_counter % self.neighbor_update_frequency) == 0

        # Update each swarm type
        self._update_bird_swarm(delta_time, targets_list, should_update_neighbors)
        self._update_fish_swarm(delta_time, targets_list, should_update_neighbors)
        self._update_ant_swarm(delta_time, targets_list, should_update_neighbors)

    def _update_bird_swarm(self, delta_time, targets_list, should_update_neighbors):
        """
        Update all birds in the swarm.

        Args:
            delta_time: Time since last update
            targets_list: List of targets
            should_update_neighbors: Whether to recalculate neighbors
        """
        birds = self.swarms["bird"]
        alive_birds = [b for b in birds if b.alive]

        if not alive_birds:
            return

        # Update neighbor lists
        if should_update_neighbors:
            for bird in alive_birds:
                bird.sense_environment(alive_birds, targets_list)

        # Update each bird
        for bird in alive_birds:
            # Get target
            if bird.target is None and targets_list:
                bird.target = random.choice([t for t in targets_list if t.alive])

            # Update bird
            neighbors = bird.neighbors if bird.neighbors else []
            bird.update(delta_time, neighbors, bird.target)

            # Attack if in range
            if bird.target and bird.target.alive:
                dist = bird.distance_to(bird.target)

                # Decide to dive or normal attack
                if bird.can_dive() and dist < 200 and random.random() < 0.02:  # 2% chance per frame
                    bird.initiate_dive(bird.target)

                # Perform attacks
                if bird.is_diving:
                    damage = bird.perform_dive(bird.target, delta_time)
                    if damage > 0:
                        bird.target.take_damage(damage)
                else:
                    damage = bird.perform_normal_attack(bird.target)
                    if damage > 0:
                        bird.target.take_damage(damage)

        # Remove dead birds
        self.swarms["bird"] = [b for b in self.swarms["bird"] if b.alive and b.energy > 0]

    def _update_fish_swarm(self, delta_time, targets_list, should_update_neighbors):
        """Update all fish in the swarm."""
        fish_list = self.swarms["fish"]
        alive_fish = [f for f in fish_list if f.alive]

        if not alive_fish:
            return

        # Update neighbor lists
        if should_update_neighbors:
            for fish in alive_fish:
                fish.sense_environment(alive_fish, targets_list)

        # Get collective vote for wave attack
        wave_target = None
        votes = {}
        for fish in alive_fish:
            fish.vote_for_target(targets_list, fish.neighbors if fish.neighbors else [])
            if fish.wave_vote:
                votes[fish.wave_vote] = votes.get(fish.wave_vote, 0) + 1

        # Check if wave should start
        if votes and len(alive_fish) > 0:
            max_votes = max(votes.values())
            if max_votes / len(alive_fish) >= 0.6:
                wave_target = [t for t, v in votes.items() if v == max_votes][0]

        self.fish_wave_target = wave_target
        self.fish_wave_active = wave_target is not None

        # Update each fish
        for fish in alive_fish:
            neighbors = fish.neighbors if fish.neighbors else []
            fish.update(delta_time, neighbors, fish.target, attacking=self.fish_wave_active)

            # Attack if in range
            if fish.target and fish.target.alive:
                damage = fish.perform_attack(fish.target)
                if damage > 0:
                    fish.target.take_damage(damage)

        self.swarms["fish"] = [f for f in self.swarms["fish"] if f.alive and f.energy > 0]

    def _update_ant_swarm(self, delta_time, targets_list, should_update_neighbors):
        """Update all ants in the swarm."""
        ant_list = self.swarms["ant"]
        alive_ants = [a for a in ant_list if a.alive]

        if not alive_ants:
            return

        # Update neighbor lists
        if should_update_neighbors:
            for ant in alive_ants:
                ant.sense_environment(alive_ants, targets_list)

        # Update each ant
        for ant in alive_ants:
            neighbors = ant.neighbors if ant.neighbors else []
            ant.update(delta_time, ant.target, neighbors)

            # Attack if in range
            if ant.target and ant.target.alive:
                damage = ant.perform_attack(ant.target)
                if damage > 0:
                    ant.target.take_damage(damage)

        self.swarms["ant"] = [a for a in self.swarms["ant"] if a.alive and a.energy > 0]

    def get_all_agents(self):
        """Get all active agents from all swarms."""
        agents = []
        agents.extend(self.swarms["bird"])
        agents.extend(self.swarms["fish"])
        agents.extend(self.swarms["ant"])
        return [a for a in agents if a.alive]

    def get_swarm_stats(self):
        """Get statistics about all swarms."""
        stats = {
            "bird_count": len([a for a in self.swarms["bird"] if a.alive]),
            "fish_count": len([a for a in self.swarms["fish"] if a.alive]),
            "ant_count": len([a for a in self.swarms["ant"] if a.alive]),
            "total_agents": len(self.get_all_agents())
        }
        return stats

    def broadcast_target_info(self, target):
        """
        Broadcast information about a target to nearby swarms.

        Args:
            target: Target entity
        """
        # Birds will naturally find targets through sensing
        pass

    def remove_dead_agents(self):
        """Remove all dead agents from swarms."""
        for swarm_type in self.swarms:
            self.swarms[swarm_type] = [
                agent for agent in self.swarms[swarm_type]
                if agent.alive and agent.energy > 0
            ]

    def switch_swarm_type(self, new_type):
        """
        Switch the active swarm type.

        Args:
            new_type: New swarm type ("bird", "fish", "ant")
        """
        if new_type in self.swarms:
            self.active_swarm_type = new_type

    def clear_all_swarms(self):
        """Remove all swarms."""
        for swarm_type in self.swarms:
            self.swarms[swarm_type].clear()
