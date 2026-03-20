import numpy as np
from physics_engine.chem_visualizer import AtomicGaussianSplat, assign_nearest_vertices, update_splat_coeffs_from_vertex_values


def test_assign_nearest_vertices_and_update():
    # create synthetic vertices (grid)
    verts = np.array([[0.0, 0.0, 0.0], [1.0,0.0,0.0], [0.0,1.0,0.0], [1.0,1.0,0.0]])
    splats = [AtomicGaussianSplat('X', np.array([0.1,0.0,0.0]), 0.1), AtomicGaussianSplat('X', np.array([0.9,1.0,0.0]), 0.1)]
    mapping = assign_nearest_vertices(splats, verts)
    assert len(mapping) == 2
    # test that mapping indices are plausible
    assert mapping[0] in (0,1)
    assert mapping[1] in (2,3)

    # create vertex values and update coeffs
    vvals = np.array([0.2, 0.4, 0.6, 0.8])
    update_splat_coeffs_from_vertex_values(splats, vvals, mapping=mapping)
    assert splats[0].coeff in (0.2, 0.4)
    assert splats[1].coeff in (0.6, 0.8)
