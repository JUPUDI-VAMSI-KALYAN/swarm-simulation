"""Direct swarm communication system."""

from src.core.vector2d import Vector2D
from enum import Enum


class MessageType(Enum):
    """Types of messages swarms can send."""
    TARGET_FOUND = "target_found"
    TARGET_LOCATION = "target_location"
    UNDER_ATTACK = "under_attack"
    TARGET_DESTROYED = "target_destroyed"
    ATTACK_NOW = "attack_now"


class Message:
    """Communication message between swarm members."""

    def __init__(self, msg_type, sender_id, position, target_pos=None, priority=1, target=None):
        """
        Create a message.

        Args:
            msg_type: MessageType enum
            sender_id: ID of sending agent
            position: Position of sender
            target_pos: Target position (if relevant)
            priority: Message priority (1-10, higher = more important)
            target: Target entity reference (for passing actual object)
        """
        self.msg_type = msg_type
        self.sender_id = sender_id
        self.position = position
        self.target_pos = target_pos
        self.priority = priority
        self.hops = 0  # Track message propagation
        self.target = target  # Actual target entity reference


class CommunicationSystem:
    """Manages swarm communication."""

    def __init__(self):
        """Initialize communication system."""
        self.messages = []
        self.target_cache = {}  # target_id -> agent_id (who found it)

    def broadcast_target_found(self, agent_id, position, target_pos, agents_list, communication_radius):
        """
        Broadcast target discovery to nearby agents.

        Args:
            agent_id: Agent that found target
            position: Agent position
            target_pos: Target position
            agents_list: List of all agents in swarm
            communication_radius: How far to broadcast
        """
        # First agent tells nearby agents
        nearby_count = 0
        for agent in agents_list:
            if agent.id != agent_id:
                dist = position.distance(agent.position)
                if dist < communication_radius and agent.alive:
                    # Tell them about the target
                    agent.target = None  # Will be set during update
                    agent.target_position = target_pos
                    nearby_count += 1

        return nearby_count

    def propagate_target_info(self, agents_list, communication_radius):
        """
        Propagate target information through swarm.
        Each agent tells nearby agents about known targets.

        Args:
            agents_list: List of all swarm members
            communication_radius: Communication range
        """
        propagated = 0

        for agent in agents_list:
            if not agent.alive or agent.target is None:
                continue

            # This agent knows about a target, tell neighbors
            for other_agent in agents_list:
                if other_agent.id != agent.id and other_agent.alive:
                    dist = agent.position.distance(other_agent.position)
                    if dist < communication_radius:
                        # Propagate target info
                        if other_agent.target is None:
                            other_agent.target = agent.target
                            propagated += 1

        return propagated

    def make_swarm_aggressive(self, agents_list, target):
        """
        Make all agents in swarm aggressive toward target.
        Called once per target selection.

        Args:
            agents_list: List of agents
            target: Target entity
        """
        for agent in agents_list:
            if agent.alive:
                agent.target = target
                agent.state = "attacking"
                agent.aggressive = True
                agent.attack_priority = 10  # Maximum priority

    def clear(self):
        """Clear message queue."""
        self.messages.clear()
