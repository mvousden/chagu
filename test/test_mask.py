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


def test_volume_mask():
    """
    Test chagu.mask.volume_mask. We test the following cases:

    1. Test!
    """

    # Test 1: Test!


@pytest.mark.xfail(strict=True)
def test_quadrilateral_plane_source():
    """
    Test chagu.mask.quadrilateral_plane_source. We test the following cases:

    1. If resolution contains a value that doesn't typecast well into an
        integer, a TypeError is raised.
    2. If any of the domain points overlap, a ValueError is raised.
    3. If all is well, check that the vtkPlaneSource has the correct points and
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
        chagu.mask.quadrilateral_plane_source(domain, [-10, 12.00001])
    assert "integer" in testException.value.message
    assert "12.00001" in testException.value.message

    # Test 2: If any of the domain points overlap, a ValueError is raised.
    domain = [0., 0., 0.,
              0., 0., 1.,
              0., 0., 1.]

    with pytest.raises(ValueError) as testException:
        chagu.mask.quadrilateral_plane_source(domain, [10, 10])
    assert "overlap" in testException.value.message

    # Test 3: If all is well, check that the returned vtkPlaneSource has the
    # correct points and resolution.
    domain = [0., 0., 0.,
              1., 0., 0.,
              0., 1., 0.]
    resolution = [10, 10]
    maskPlane = chagu.mask.quadrilateral_plane_source(domain, [10, 10])

    assert type(maskPlane) == type(vtk.vtkPlaneSource)
    # <!> some other assertions


if __name__ == "__main__":
    test_create_mask_from_opts()
    test_plane_mask()
    test_volume_mask()
    test_quadrilateral_plane_source()
