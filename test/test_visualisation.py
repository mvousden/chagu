"""
This python file tests the functionality of functions defined in
chagu/visualisation.py. Tests are detailed in the function documentation.
"""

import chagu
import numpy
import pytest


def test_set_background():
    """
    Test chagu.Visualisation setter "background". We test the following cases:

    1. If backgroundInput is not iterable, a ValueError is raised.
    2. If backgroundInput is iterable and does not have three elements exactly,
         a ValueError is raised.
    3. If any element of backgroundInput is not numerical, a ValueError is
         raised.
    4. If an element of backgroundInput is greater than one, the visualisation
         instance has _background value in the position of the element equal to
         one, and all other valid elements unchanged.
    5. If an element of backgroundInput is less than zero, the visualisation
         instance has _background value in the position of the element equal to
         zero, and all other valid elements unchanged
    6. If an element of backgroundinput is less than zero, and another element
         is greater than zero, the visualisation instance has _background value
         in the position of the former equal to zero, and the latter equal to
         one.
    """

    vis = chagu.Visualisation()

    # Test 1: If backgroundInput is not iterable, a TypeError is raised.
    backgroundInput_1 = -4.3
    expectedMsg = ("background value \"{}\" must be iterable."
                   .format(backgroundInput_1))
    with pytest.raises(TypeError) as testException:
        vis.background = backgroundInput_1
    assert expectedMsg in testException.value.message

    # Test 2: If backgroundInput is iterable and does not have three elements
    # exactly, a ValueError is raised.
    backgroundInput_2 = [2, "b"]
    expectedMsg = ("background value \"{}\" should contain exactly three "
                   "elements.".format(backgroundInput_2))
    with pytest.raises(ValueError) as testException:
        vis.background = backgroundInput_2
    assert expectedMsg in testException.value.message

    # Test 3: If the elements of backgroundInput are not numerical, a
    # ValueError is raised.
    backgroundInput_3a = [1, 2, "d"]
    with pytest.raises(ValueError) as testException:
        vis.background = backgroundInput_3a

    backgroundInput_3b = [1, [], "d"]
    expectedMsg_b = ("background value \"{}\" has element \"{}\", which is "
                     "not numerical".format(backgroundInput_3b,
                                            backgroundInput_3b[1]))
    with pytest.raises(ValueError) as testException:
        vis.background = backgroundInput_3b
    assert expectedMsg_b in testException.value.message

    # Test 4: If an element of backgroundInput is greater than one, the
    # visualisation instance has _background value in the position of the
    # element equal to one.
    backgroundInput_4 = [0.5, 0.2, numpy.inf]
    vis.background = backgroundInput_4
    assert vis.background[0] == backgroundInput_4[0]
    assert vis.background[1] == backgroundInput_4[1]
    assert vis.background[2] == 1

    # Test 5: If an element of backgroundInput is less than zero, the
    # visualisation instance has _background value in the position of the
    # element equal to zero.
    backgroundInput_5 = [-numpy.inf, 0.2, 0.35]
    vis.background = backgroundInput_5
    assert vis.background[0] == 0
    assert vis.background[1] == backgroundInput_5[1]
    assert vis.background[2] == backgroundInput_5[2]

    # Test 6: If an element of backgroundinput is less than zero, and another
    # element is greater than zero, the visualisation instance has _background
    # value in the position of the former equal to zero, and the latter equal
    # to one.
    backgroundInput_6 = [-40, 0.3, 7034]
    vis.background = backgroundInput_6
    assert vis.background[0] == 0
    assert vis.background[1] == backgroundInput_6[1]
    assert vis.background[2] == 1


if __name__ == "__main__":
    test_set_background()
