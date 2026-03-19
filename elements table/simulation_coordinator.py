from core_models import Universe
from typing import Any, Dict

class SimulationCoordinator:
    """
    Orchestrates simulation flow, state propagation, and event routing
    for the system hierarchy (Universe, Environment, Room, etc.).
    """
    def __init__(self, universe: Universe):
        self.universe = universe
        self.state: Dict[str, Any] = {}
        self.events: list = []

    def step(self):
        # Example: propagate a simulation step through the hierarchy
        for env in self.universe.environments:
            for room in env.rooms:
                for material in room.materials:
                    for element in material.elements:
                        # Placeholder: update state, emit events, etc.
                        self.events.append({
                            "type": "element_step",
                            "element": element.symbol,
                            "room": room.name,
                            "env": env.name
                        })
        # Add more orchestration logic as needed

    def get_events(self):
        return self.events
