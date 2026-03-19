def test_adapter_import():
    import importlib
    m = importlib.import_module('game_module.adapter')
    assert hasattr(m, 'PhysicsAdapter')


def test_entity_import():
    import importlib
    m = importlib.import_module('game_module.entity')
    assert hasattr(m, 'Entity')
