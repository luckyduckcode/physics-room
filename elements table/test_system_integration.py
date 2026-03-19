
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) or '.')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_hierarchy import build_sample_universe
from simulation_coordinator import SimulationCoordinator
from derived_properties import DerivedProperties

class TestSystemIntegration(unittest.TestCase):
    def test_hierarchy_and_derived_properties(self):
        universe = build_sample_universe()
        coordinator = SimulationCoordinator(universe)
        coordinator.step()
        events = coordinator.get_events()
        self.assertTrue(len(events) > 0)
        # Test derived properties for first element
        element = universe.environments[0].rooms[0].materials[0].elements[0]
        derived = DerivedProperties.from_element(element)
        self.assertIsNotNone(derived.melting_point_K)
        self.assertIsNotNone(derived.fusion_enthalpy_kJ_per_mol)

if __name__ == "__main__":
    unittest.main()
