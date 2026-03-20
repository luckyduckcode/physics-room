from physics_engine.chem_visualizer import build_molecule_splats, _sto3g_effective_alpha
import numpy as np


def test_build_splats_basic():
    splats = build_molecule_splats('H2O')
    assert len(splats) == 3
    assert all(hasattr(s, 'center') for s in splats)


def test_sto3g_alpha():
    a_h = _sto3g_effective_alpha('H')
    a_c = _sto3g_effective_alpha('C')
    assert a_h > 0
    assert a_c > 0
    assert not np.isclose(a_h, a_c)


def test_build_splats_sto3g_flag():
    splats_default = build_molecule_splats('H2', parsed_atoms=[('H',2)])
    splats_sto = build_molecule_splats('H2', parsed_atoms=[('H',2)], use_sto3g=True)
    assert splats_default[0].alpha != splats_sto[0].alpha
