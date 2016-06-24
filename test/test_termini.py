"""
This python file tests the functionality of functions defined in
chagu/termini.py. Tests are detailed in the function documentation.
"""

import chagu
import numpy as np
import pytest
import vtk


@pytest.mark.skipif(True, reason="Not yet implemented")
def test_lookup_table_from_RGB_colourmap():
    """
    Test chagu.termini.lookup_table_from_RGB_colourmap. We test the following
    cases:
    """
    return


def test_nasty_arrow_polydata():
    """
    Test chagu.termini.nasty_arrow_polydata. We test the following cases:

    1. If any dimension is not positive, a ValueError is raised.
    2. If all is well, check the number of points and their positions for a few
        configurations.
    """

    # Test 1: If any dimension is not positive, a ValueError is raised
    with pytest.raises(ValueError) as testException:
        chagu.termini.nasty_arrow_polydata(-14.34, 10, 2)
    assert "positive" in testException.value.message
    assert "-14.34" in testException.value.message

    with pytest.raises(ValueError) as testException:
        chagu.termini.nasty_arrow_polydata(14, -7.5, 2)
    assert "positive" in testException.value.message
    assert "-7.5" in testException.value.message

    with pytest.raises(ValueError) as testException:
        chagu.termini.nasty_arrow_polydata(14, 7, 0)
    assert "positive" in testException.value.message
    assert "0" in testException.value.message

    # Test 2: If all is well, check the number of points and their positions
    # for a few configurations.
    lx = 10
    ly = 5
    lz = 2
    arrowPolyData = chagu.termini.nasty_arrow_polydata(lx, ly, lz)

    assert arrowPolyData.GetNumberOfPoints() == 18
    assert (np.abs(np.array(arrowPolyData.GetPoint(0)) -
                   np.array([-lx / 2., lz / 2., lz / 2.])) < 1e-3).all()
    assert (np.abs(np.array(arrowPolyData.GetPoint(4)) -
                   np.array([lx / 2., 0., lz / 2.])) < 1e-3).all()

    # I could easily waste all day checking each point meticulously, but a
    # visual check would save so much time if this is changed in future.


if __name__ == "__main__":
    test_lookup_table_from_RGB_colourmap()
    test_nasty_arrow_polydata()
