from core_models import Element, Material, Room, Environment, Universe

# Example: Build a simple system hierarchy

def build_sample_universe() -> Universe:
    # Create elements
    iron = Element(26, "Fe", "Iron", 55.845, state="solid", melting_point=1538, boiling_point=2862, hardness=4, durability="moderate", stability="stable")
    carbon = Element(6, "C", "Carbon", 12.011, state="solid", melting_point=3550, boiling_point=4827, hardness=10, durability="very high", stability="stable")

    # Create a material (e.g., steel)
    steel = Material(
        name="Steel",
        elements=[iron, carbon],
        composition={"Fe": 0.98, "C": 0.02},
        density=7.85
    )

    # Create a room containing the material
    lab_room = Room(
        name="Lab Room 1",
        materials=[steel],
        temperature=298.15,  # K
        pressure=1.0         # atm
    )

    # Create an environment with the room
    lab_env = Environment(
        name="Main Lab",
        rooms=[lab_room],
        global_conditions={"humidity": 0.5}
    )

    # Create the universe with the environment
    universe = Universe(
        environments=[lab_env],
        metadata={"created_by": "system", "purpose": "demo"}
    )
    return universe
