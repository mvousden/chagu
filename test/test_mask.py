"""
This python file tests the functionality of functions defined in
chagu/mask.py. Tests are detailed in the function documentation.
"""

import chagu
import pytest
import vtk


def test_create_mask_from_opts():
    """
    Test chagu.mask.create_mask_from_opts. We test the following cases:

    1. Test!
    """

    # Test 1: Test!


def test_plane_mask():
    """
    Test chagu.mask.plane_mask. We test the following cases:

    1. Test!
    """

    # Test 1: Test!


@pytest.mark.xfail
def test_cube_mask():
    """
    Test chagu.mask.cube_mask. We test the following cases:

    1. If resolution contains a value that doesn't typecast well into an
        integer, a TypeError is raised.
    2. If any of the domain points overlap, a ValueError is raised.
    3. If a negative resolution is passed, a ValueError is raised.
    4. If the length of any input is incorrect, a ValueError is raised.
    5. If the final element of resolution is one, ensure only one plane is
         created.
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

    # Test 5: If the final element of resolution is one, ensure only one plane
    # is created.
    domain = [0., 0., 0.,
              5., 0., 0.,
              0., 5., 0.,
              0., 0., 1.]
    maskFilter = chagu.mask.cube_mask(domain, [10, 10, 1])
    maskVolumeData = maskFilter.GetInputDataObject(0, 0)
    # <!> More assertions?


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

    assert type(maskPlane) == type(vtk.vtkPlaneSource())
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
