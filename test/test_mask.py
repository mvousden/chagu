"""
This python file tests the functionality of functions defined in
chagu/mask.py. Tests are detailed in the function documentation.
"""

import chagu
import numpy as np
import pytest
import vtk


def test_create_mask_from_opts():
    """
    Test chagu.mask.create_mask_from_opts. We test the following cases:

    1. Check for inconsistent inputs regarding the type of the mask, and the
        length of the domain and resolution lists.
    2. Behaviours function as intended (see the function's docstring).
    """

    # Test 1: Check for inconsistent inputs regarding the type of the mask, and
    # the length of the domain and resolution lists.
    boundingBox = [-10, 10, -5, 5, -2, 2]
    glyphSize = 1

    # Plane mask, len(domain) != 9.
    with pytest.raises(ValueError) as testException:
        chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                         maskDomain=range(10),
                                         maskResolution=None, maskType="plane")
    assert "maskDomain" in testException.value.message

    # Plane mask, len(resolution) != 2.
    with pytest.raises(ValueError) as testException:
        chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                         maskDomain=None,
                                         maskResolution=range(5),
                                         maskType="plane")
    assert "maskResolution" in testException.value.message

    # Volume mask, len(domain) != 12.
    with pytest.raises(ValueError) as testException:
        chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                         maskDomain=range(50),
                                         maskResolution=None,
                                         maskType="volume")
    assert "maskDomain" in testException.value.message

    # Volume mask, len(resolution) != 3.
    with pytest.raises(ValueError) as testException:
        chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                         maskDomain=None,
                                         maskResolution=range(5),
                                         maskType="volume")
    assert "maskResolution" in testException.value.message

    # len(domain)-len(resolution) != 9-2 or 12-3
    with pytest.raises(ValueError) as testException:
        chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                         maskDomain=range(9),
                                         maskResolution=range(3),
                                         maskType=None)
    assert "9-3" in testException.value.message

    with pytest.raises(ValueError) as testException:
        chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                         maskDomain=range(2),
                                         maskResolution=range(12),
                                         maskType=None)
    assert "2-12" in testException.value.message

    with pytest.raises(ValueError) as testException:
        chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                         maskDomain=range(1),
                                         maskResolution=range(2),
                                         maskType=None)
    assert "1-2" in testException.value.message

    # Test 2: Behaviours function as intended (see the function's docstring).
    #
    # We check each behaviour in order.
    boundingBox = [-10, 10, -5, 5, -2, 2]
    glyphSize = 1
    planeDomain = [-5, -2.5, 0,
                   5, -2.5, 0,
                   -5, 2.5, 0]
    volumeDomain = [-5, -2.5, -1.5,
                    5, -2.5, -1.5,
                    -5, 2.5, -1.5,
                    -5, -2.5, 1.5]
    planeResolution = [5, 3]
    volumeResolution = [5, 3, 2]
    aTol = 2e-2

    # Behaviour 1.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=None,
                                            maskResolution=None,
                                            maskType="plane")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array(boundingBox[:4] + [0, 0])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == 18 * 9 * 1

    # Behaviour 2.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=None,
                                            maskResolution=None,
                                            maskType="volume")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array(boundingBox)) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == 18 * 9 * 3

    # Behaviour 3.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=planeDomain,
                                            maskResolution=None,
                                            maskType="plane")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([planeDomain[0], planeDomain[3],
                             planeDomain[1], planeDomain[7],
                             planeDomain[2], planeDomain[2]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == 9 * 4 * 1

    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=planeDomain,
                                            maskResolution=None,
                                            maskType=None)
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([planeDomain[0], planeDomain[3],
                             planeDomain[1], planeDomain[7],
                             planeDomain[2], planeDomain[2]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == 9 * 4 * 1

    # Behaviour 4.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=volumeDomain,
                                            maskResolution=None,
                                            maskType="volume")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([volumeDomain[0], volumeDomain[3],
                             volumeDomain[1], volumeDomain[7],
                             volumeDomain[2], volumeDomain[11]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == 9 * 4 * 2

    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=volumeDomain,
                                            maskResolution=None,
                                            maskType=None)
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([volumeDomain[0], volumeDomain[3],
                             volumeDomain[1], volumeDomain[7],
                             volumeDomain[2], volumeDomain[11]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == 9 * 4 * 2

    # Behaviour 5.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=None,
                                            maskResolution=planeResolution,
                                            maskType="plane")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array(boundingBox[:4] + [0, 0])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        planeResolution)

    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=None,
                                            maskResolution=planeResolution,
                                            maskType=None)
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array(boundingBox[:4] + [0, 0])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        planeResolution)

    # Behaviour 6.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=None,
                                            maskResolution=volumeResolution,
                                            maskType="volume")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array(boundingBox)) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        volumeResolution)

    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=None,
                                            maskResolution=volumeResolution,
                                            maskType=None)
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array(boundingBox)) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        volumeResolution)

    # Behaviour 7.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=planeDomain,
                                            maskResolution=planeResolution,
                                            maskType="plane")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([planeDomain[0], planeDomain[3],
                             planeDomain[1], planeDomain[7],
                             planeDomain[2], planeDomain[2]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        planeResolution)

    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=planeDomain,
                                            maskResolution=planeResolution,
                                            maskType=None)
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([planeDomain[0], planeDomain[3],
                             planeDomain[1], planeDomain[7],
                             planeDomain[2], planeDomain[2]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        planeResolution)

    # Behaviour 8.
    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=volumeDomain,
                                            maskResolution=volumeResolution,
                                            maskType="volume")
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([volumeDomain[0], volumeDomain[3],
                             volumeDomain[1], volumeDomain[7],
                             volumeDomain[2], volumeDomain[11]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        volumeResolution)

    mask = chagu.mask.create_mask_from_opts(boundingBox, glyphSize,
                                            maskDomain=volumeDomain,
                                            maskResolution=volumeResolution,
                                            maskType=None)
    assert mask.IsA("vtkProbeFilter")
    assert (np.abs(np.array(mask.GetInput().GetBounds()) -
                   np.array([volumeDomain[0], volumeDomain[3],
                             volumeDomain[1], volumeDomain[7],
                             volumeDomain[2], volumeDomain[11]])) < aTol).all()
    assert mask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                        volumeResolution)

    # Well that was fun!


def test_plane_mask():
    """
    Test chagu.mask.plane_mask. These tests are very similar to those used in
    test_cube_mask, since plane_mask is a convenience function for cube_mask.
    """

    # Test 1: If resolution contains a value that doesn't typecast well into an
    # integer, a TypeError is raised.
    domain = [0., 0., 0.,
              0., 0., 1.,
              0., 1., 0.]
    with pytest.raises(TypeError) as testException:
        chagu.mask.plane_mask(domain, [14.2, 10])
    assert "integer" in testException.value.message
    assert "14.2" in testException.value.message

    with pytest.raises(TypeError) as testException:
        chagu.mask.plane_mask(domain, [10, 3.1412, 1])
    assert "integer" in testException.value.message
    assert "3.14" in testException.value.message

    # Test 2: If any of the domain points overlap, a ValueError is raised.
    domain = [0., 0., 0.,
              0., 0., 1.,
              0., 0., 1.]
    with pytest.raises(ValueError) as testException:
        chagu.mask.plane_mask(domain, [10, 10])
    assert "overlap" in testException.value.message

    # Test 3: If a negative resolution is passed, a ValueError is raised.
    domain = [0., 0., 1.,
              1., 0., 0.,
              0., 1., 0.]
    with pytest.raises(ValueError) as testException:
        chagu.mask.plane_mask(domain, [1, -4])
    assert "-4" in testException.value.message

    # Test 4: If the length of any input is incorrect, a ValueError is raised.
    with pytest.raises(ValueError) as testException:
        chagu.mask.plane_mask(domain + [5], [1, 1])
    assert "omain" in testException.value.message
    with pytest.raises(ValueError) as testException:
        chagu.mask.plane_mask(domain, [1, 1, 1])
    assert "esolution" in testException.value.message

    # Test 5: If all is well, check that the polydata has the correct points
    # and resolution.
    domain = [-2, -2, 0,
               2, -2, 0,
              -2,  2, 0]
    resolution = [5, 11]
    planeMask = chagu.mask.plane_mask(domain, resolution)

    assert planeMask.IsA("vtkProbeFilter")
    assert planeMask.GetInput().GetBounds() == (domain[0], domain[3],
                                               domain[1], domain[7],
                                               domain[2], domain[2])
    assert planeMask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                            resolution)



def test_cube_mask():
    """
    Test chagu.mask.cube_mask. We test the following cases:

    1. If resolution contains a value that doesn't typecast well into an
        integer, a TypeError is raised.
    2. If any of the domain points overlap, a ValueError is raised.
    3. If a negative resolution is passed, a ValueError is raised.
    4. If the length of any input is incorrect, a ValueError is raised.
    5. If all is well, check that the polydata has the correct points and
        resolution.
    """

    # Test 1: If resolution contains a value that doesn't typecast well into an
    # integer, a TypeError is raised.
    domain = [0., 0., 0.,
              0., 0., 1.,
              0., 1., 0.,
              1., 0., 0.]
    with pytest.raises(TypeError) as testException:
        chagu.mask.cube_mask(domain, [10.5, 10, 1])
    assert "integer" in testException.value.message
    assert "10.5" in testException.value.message

    with pytest.raises(TypeError) as testException:
        chagu.mask.cube_mask(domain, [10, 12.00001, 1])
    assert "integer" in testException.value.message
    assert "12.00001" in testException.value.message

    with pytest.raises(TypeError) as testException:
        chagu.mask.cube_mask(domain, [10, 12., 6.8])
    assert "integer" in testException.value.message
    assert "6.8" in testException.value.message

    # Test 2: If any of the domain points overlap, a ValueError is raised.
    domain = [0., 0., 0.,
              0., 0., 1.,
              0., 0., 1.,
              1., 0., 1.,]
    with pytest.raises(ValueError) as testException:
        chagu.mask.cube_mask(domain, [10, 10, 10])
    assert "overlap" in testException.value.message

    # Test 3: If a negative resolution is passed, a ValueError is raised.
    domain = [0., 0., 1.,
              1., 0., 0.,
              0., 1., 0.,
              0., 0., 1.]
    with pytest.raises(ValueError) as testException:
        chagu.mask.cube_mask(domain, [1, 4, -1])
    assert "-1" in testException.value.message

    # Test 4: If the length of any input is incorrect, a ValueError is raised.
    with pytest.raises(ValueError) as testException:
        chagu.mask.cube_mask(domain + [5], [1, 1, 1])
    assert "omain" in testException.value.message
    with pytest.raises(ValueError) as testException:
        chagu.mask.cube_mask(domain, [1])
    assert "esolution" in testException.value.message

    # Test 5: If all is well, check that the polydata has the correct points
    # and resolution.
    domain = [-2, -2, -2,
               2, -2, -2,
              -2,  2, -2,
              -2, -2, 2]
    resolution = [10, 11, 13]
    cubeMask = chagu.mask.cube_mask(domain, resolution)

    assert cubeMask.IsA("vtkProbeFilter")
    assert cubeMask.GetInput().GetBounds() == (domain[0], domain[3],
                                               domain[1], domain[7],
                                               domain[2], domain[11])
    assert cubeMask.GetInput().GetNumberOfCells() == reduce(lambda x, y: x * y,
                                                            resolution)


def test_quadrilateral_plane_source():
    """
    Test chagu.mask.quadrilateral_plane_source. We test the following cases:

    1. If resolution contains a value that doesn't typecast well into an
        integer, a TypeError is raised.
    2. If any of the domain points overlap, a ValueError is raised.
    3. If a negative resolution is passed, a ValueError is raised.
    4. If the length of any input is incorrect, a ValueError is raised.
    5. If all is well, check that the vtkPlaneSource has the correct points and
        resolution.
    """

    # Test 1: If resolution contains a value that doesn't typecast well into an
    # integer, a TypeError is raised.
    domain = [0., 0., 0.,
              0., 0., 1.,
              0., 1., 0.]
    with pytest.raises(TypeError) as testException:
        chagu.mask.quadrilateral_plane_source(domain, [10.5, 10])
    assert "integer" in testException.value.message
    assert "10.5" in testException.value.message

    with pytest.raises(TypeError) as testException:
        chagu.mask.quadrilateral_plane_source(domain, [10, 12.00001])
    assert "integer" in testException.value.message
    assert "12.00001" in testException.value.message

    # Test 2: If any of the domain points overlap, a ValueError is raised.
    domain = [0., 0., 0.,
              0., 0., 1.,
              0., 0., 1.]
    with pytest.raises(ValueError) as testException:
        chagu.mask.quadrilateral_plane_source(domain, [10, 10])
    assert "overlap" in testException.value.message

    # Test 3: If a negative resolution is passed, a ValueError is raised.
    domain = [0., 0., 1.,
              1., 0., 0.,
              0., 1., 0.]
    with pytest.raises(ValueError) as testException:
        chagu.mask.quadrilateral_plane_source(domain, [-1, 4])
    assert "-1" in testException.value.message

    # Test 4: If the length of any input is incorrect, a ValueError is raised.
    with pytest.raises(ValueError) as testException:
        chagu.mask.quadrilateral_plane_source(domain + [5], [1, 1])
    assert "omain" in testException.value.message
    with pytest.raises(ValueError) as testException:
        chagu.mask.quadrilateral_plane_source(domain, [1])
    assert "esolution" in testException.value.message

    # Test 5: If all is well, check that the returned vtkPlaneSource has the
    # correct points and resolution.
    resolution = [10, 11]
    maskPlane = chagu.mask.quadrilateral_plane_source(domain, resolution)

    assert maskPlane.IsA("vtkPlaneSource")
    assert list(maskPlane.GetOrigin()) == domain[:3]
    assert list(maskPlane.GetPoint1()) == domain[3:6]
    assert list(maskPlane.GetPoint2()) == domain[6:]
    assert maskPlane.GetXResolution() == resolution[0]
    assert maskPlane.GetYResolution() == resolution[1]


if __name__ == "__main__":
    test_create_mask_from_opts()
    test_plane_mask()
    test_cube_mask()
    test_quadrilateral_plane_source()
