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
    expectedMsg = ("Background value \"{}\" must be iterable."
                   .format(backgroundInput_1))
    with pytest.raises(TypeError) as testException:
        vis.background = backgroundInput_1
    assert expectedMsg in testException.value.message

    # Test 2: If backgroundInput is iterable and does not have three elements
    # exactly, a ValueError is raised.
    backgroundInput_2 = [2, "b"]
    expectedMsg = ("Background value \"{}\" should contain exactly three "
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
    expectedMsg_b = ("Background value \"{}\" has element \"{}\", which is "
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


def test_set_camera():
    """
    Test chagu.Visualisation setter "camera". We test the following cases:

    1. If cameraInput does not have keys and values, a TypeError is raised.
    2. If cameraInput contains an invalid camera key, a ValueError is raised.
    3. If cameraInput["view up"] does not have three elements exactly, a
         ValueError is raised.
    4. If cameraInput["position"] does not have three elements exactly, a
         ValueError is raised.
    5. If cameraInput["focal point"] does not have three elements exactly, a
         ValueError is raised.
    6. If any element of cameraInput["view up"] is not numerical, a ValueError
         is raised.
    7. If any element of cameraInput["position"] is not numerical, a ValueError
         is raised.
    8. If any element of cameraInput["focal point"] is not numerical, a
         ValueError is raised.
    9. If cameraInput["zoom"] is not numerical, a TypeError is raised.
    10. If cameraInput["zoom"] is less than or equal to zero, a ValueError is
          raised.
    11. If cameraInput["parallel projection"] is not boolean, a TypeError is
          raised.
    12. If cameraInput contains only valid camera keys with valid items, the
          visualisation instance has _camera value identical to cameraInput.
    13. The most recent cameraInput used to set camera is identical to the
          _camera value in the visualisation instance.
    """

    vis = chagu.Visualisation()

    # Test 1: If cameraInput does not have keys and values, a TypeError is
    # raised.
    cameraInput_1 = []
    expectedMsg = ("camera input \"{}\" must have keys and values."
                   .format(cameraInput_1))
    with pytest.raises(TypeError) as testException:
        vis.camera = cameraInput_1
    assert expectedMsg in testException.value.message

    # Test 2: If cameraInput contains an invalid camera key, a ValueError is
    # raised.
    cameraKey = "c"
    while cameraKey in vis._validCameraKeys.keys():
        cameraKey += cameraKey
    cameraInput_2 = {cameraKey: cameraKey}
    expectedMsg = ("Camera key \"{}\" is not valid. Try one of \"{}\"."
                   .format(cameraKey, vis._validCameraKeys))
    with pytest.raises(ValueError) as testException:
        vis.camera = cameraInput_2
    assert expectedMsg in testException.value.message

    # Test 3, 4, 5: If cameraInput["view up"] does not have three elements
    # exactly, a ValueError is raised. If cameraInput["position"] does not have
    # three elements exactly, a ValueError is raised. If cameraInput["focal
    # point"] does not have three elements exactly, a ValueError is raised.
    for key in "view up", "position", "focal point":
        cameraInput_345 = {key: [2, "b"]}
        expectedMsg = ("Camera key \"{}\" has invalid value \"{}\", which "
                       "should contain exactly three elements."
                       .format(key, cameraInput[key]))
        with pytest.raises(ValueError) as testException:
            vis.camera = cameraInput_345
        assert expectedMsg in testException.value.message

    # Test 6, 7, 8: If any element of cameraInput["view up"] is not numerical,
    # a ValueError is raised. If any element of cameraInput["position"] is not
    # numerical, a ValueError is raised. If any element of cameraInput["focal
    # point"] is not numerical, a ValueError is raised.
    for key in "view up", "position", "focal point":
        cameraInput_678_a = {key: [1, 2, "d"]}
        with pytest.raises(ValueError) as testException:
            vis.camera = cameraInput_678_a

        cameraInput_678_b = {key: [1, [], "d"]}
        expectedMsg_b = ("Camera key \"{}\" has value with element \"{}\", "
                         "which is not numerical")
                         .format(key, cameraInput_678_b[key][1]))
        with pytest.raises(ValueError) as testException:
            vis.camera = cameraInput_678_b
        assert expectedMsg_b in testException.value.message

    # Test 9: If cameraInput["zoom"] is not numerical, a TypeError is raised.
    cameraInput_9 = {"zoom": {}}
    expectedMsg = ("Invalid zoom value \"{}\". This must be greater than zero."
                   .format(cameraInput_10["zoom"]))
    with pytest.raises(TypeError) as testException:
        vis.camera = cameraInput_9
    assert expectedMsg in testException.value.message

    # Test 10: If cameraInput["zoom"] is less than or equal to zero, a
    # ValueError is raised.
    cameraInput_10 = {"zoom": 0}
    expectedMsg = ("Invalid zoom value \"{}\". This must be greater than zero."
                   .format(cameraInput_10["zoom"]))
    with pytest.raises(ValueError) as testException:
        vis.camera = cameraInput_10
    assert expectedMsg in testException.value.message

    # Test 11: If cameraInput["parallel projection"] is not boolean, a
    # TypeError is raised.
    cameraInput_11 = {"parallel projection": 1}
    expectedMsg = ("Invalid parallel projection value \"{}\". This must be a "
                   "boolean.".format(cameraInput_11["parallel projection"]))
    with pytest.raises(TypeError) as testException:
        vis.camera = cameraInput_11
    assert expectedMsg in testException.value.message

    # Test 12: If cameraInput contains only valid camera keys with valid items,
    # the visualisation instance has _camera value identical to cameraInput.
    cameraInput_12 = {"zoom": 10, "parallel projection": True,
                      "view up": [2, 4, 6], "position": [-4, 72, 8.2],
                      "focal point": [0, 0, 0]}
    vis.camera = cameraInput_12
    assert vis._camera == cameraInput_12

    # Test 13: The most recent cameraInput used to set camera is identical to
    # the _camera value in the visualisation instance.
    cameraInput_13a = {"zoom": 10, "parallel projection": True,
                      "view up": [2, 4, 6], "position": [-4, 72, 8.2],
                      "focal point": [0, 0, 0]}
    vis.camera = cameraInput_13a
    cameraInput_13b = {}
    vis.camera = cameraInput_13b
    assert vis._camera == cameraInput_13b


if __name__ == "__main__":
    test_set_background()
