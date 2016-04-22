"""
This python file tests the functionality of functions defined in
chagu/visualisation.py. Tests are detailed in the function documentation.
"""

import chagu
import numpy
import os
import pytest


def test_initialisation():
    """
    Test chagu.Visualisation initialisation method "__init__". We test the
    following cases:

    1. If name is provided as an optional argument, the visualisation instance
         has name value equal to the argument.
    2. If no arguments are provided, the visualisation object has _background
         value equal to [0., 0., 0.], a two element list as its windowSize
         value, a six element list as its _boundingBox value, a colourmap_lut
         value of type vtkLookupTable, _order and _pipeline values defined as
         empty lists, and _vtkObjects, camera, and _vtkTermini values defined
         as empty dictionaries.
    3. If a valid filePath is provided, the visualisation object has
         _vtkObjects value as a dictionary with one key-value pair in it, a six
         element list _boundingBox value with no zeros in it, and all other
         parameters the same. The functionality of adding a file source should
         be covered by the tests of sources.load_visualisation_toolkit_file.
    """

    # Test 1: If name is provided as an optional argument, the visualisation
    # instance has name value equal to the argument.
    name_1 = "Hello world!"
    vis_1 = chagu.Visualisation(name=name_1)
    assert vis_1.name == name_1

    # Test 2: If no arguments are provided, the visualisation object has
    # _background value equal to [0., 0., 0.], a two element list as its
    # windowSize value, a six element list as its _boundingBox value, a
    # colourmap_lut value of type vtkLookupTable, _order and _pipeline values
    # defined as empty lists, and _vtkObjects, camera, and _vtkTermini values
    # defined as empty dictionaries.
    def check_clean(vis):
        assert vis_2._background == [0., 0., 0.]
        assert len(vis_2.windowSize) == 2
        assert type(vis_2.windowSize) == list
        assert len(vis_2._boundingBox) == 6
        assert type(vis_2._boundingBox) == list
        assert vis_2.colourmap_lut.IsA("vtkLookupTable") == 1
        assert vis_2._order == []
        assert vis_2._pipeline == []
        assert vis_2.camera == {}
        assert vis_2._vtkTermini == {}

    vis_2 = chagu.Visualisation()
    check_clean(vis_2)
    assert vis_2._vtkObjects == {}

    # Test 3: If a valid filePath is provided, the visualisation object has
    # _vtkObjects value as a dictionary with one key-value pair in it, a six
    # element list _boundingBox value with one or more non-zero elements, and
    # all other parameters the same. The functionality of adding a file source
    # should be covered by the tests of
    # sources.load_visualisation_toolkit_file.
    pathToThisFile = os.path.dirname(os.path.realpath(__file__))
    relativeVtuFilePath = "../example/data/data.vtu"
    absFilePath = "{}/{}".format(pathToThisFile, relativeVtuFilePath)
    vis_3 = chagu.Visualisation(filePath=absFilePath)

    check_clean(vis_3)
    assert len(vis_3._vtkObjects) == 1
    for element in vis_3._boundingBox:
        if element != 0:
            break
    else:
        assert False


def test_set_background():
    """
    Test chagu.Visualisation setter "background". We test the following cases:

    1. If backgroundInput is not iterable, a TypeError is raised.
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
          visualisation instance has camera value identical to cameraInput.
    13. The most recent cameraInput used to set camera is identical to the
          camera value in the visualisation instance.
    """

    vis = chagu.Visualisation()

    # Test 1: If cameraInput does not have keys and values, a TypeError is
    # raised.
    cameraInput_1 = []
    expectedMsg = ("Camera input \"{}\" must have keys and values."
                   .format(cameraInput_1))
    with pytest.raises(TypeError) as testException:
        vis.camera = cameraInput_1
    assert expectedMsg in testException.value.message

    # Test 2: If cameraInput contains an invalid camera key, a ValueError is
    # raised.
    cameraKey = "c"
    while cameraKey in vis._validCameraKeys:
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
                       .format(key, cameraInput_345[key]))
        with pytest.raises(ValueError) as testException:
            vis.camera = cameraInput_345
        assert expectedMsg in testException.value.message

    # Test 6, 7, 8: If any element of cameraInput["view up"] is not numerical,
    # a TypeError is raised. If any element of cameraInput["position"] is not
    # numerical, a TypeError is raised. If any element of cameraInput["focal
    # point"] is not numerical, a TypeError is raised.
    for key in "view up", "position", "focal point":
        cameraInput_678_a = {key: [1, 2, "d"]}
        with pytest.raises(TypeError) as testException:
            vis.camera = cameraInput_678_a

        cameraInput_678_b = {key: [1, [], "d"]}
        expectedMsg_b = ("Camera key \"{}\" has value with element \"{}\", "
                         "which is not numerical"
                         .format(key, cameraInput_678_b[key][1]))
        with pytest.raises(TypeError) as testException:
            vis.camera = cameraInput_678_b
        assert expectedMsg_b in testException.value.message

    # Test 9: If cameraInput["zoom"] is not numerical, a TypeError is raised.
    cameraInput_9 = {"zoom": {}}
    expectedMsg = ("Invalid zoom value \"{}\" is not numerical."
                   .format(cameraInput_9["zoom"]))
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
    # the visualisation instance has camera value identical to cameraInput.
    cameraInput_12 = {"zoom": 10, "parallel projection": True,
                      "view up": [2, 4, 6], "position": [-4, 72, 8.2],
                      "focal point": [0, 0, 0]}
    vis.camera = cameraInput_12
    assert vis.camera == cameraInput_12

    # Test 13: The most recent cameraInput used to set camera is identical to
    # the camera value in the visualisation instance.
    cameraInput_13a = {"zoom": 10, "parallel projection": True,
                       "view up": [2, 4, 6], "position": [-4, 72, 8.2],
                       "focal point": [0, 0, 0]}
    vis.camera = cameraInput_13a
    cameraInput_13b = {}
    vis.camera = cameraInput_13b
    assert vis.camera == cameraInput_13b


def test_set_colourmap_lut():
    """
    Test chagu.Visualisation setter "colourmap_lut". We test the following
    cases:

    1. If arguments are valid, the visualisation instance has colourmap_lut
         value of type vtkLookupTablevalue.

    The functionality of this is largely tested by tests for the function
    lookup_table_from_RGB_colourmap defined in termini.py
    """

    vis = chagu.Visualisation()

    # Test 1: If arguments are valid, the visualisation instance has
    # colourmap_lut value of type vtkLookupTablevalue.
    vis.colourmap_lut = "PuOr"
    assert vis.colourmap_lut.IsA("vtkLookupTable") == 1


def test_set_windowsize():
    """
    Test chagu.Visualisation setter "windowSize". We test the following cases:

    1. If windowSizeInput is not iterable, a TypeError is raised.
    2. If windowSizeInput is iterable and does not have two elements exactly, a
         ValueError is raised.
    3. If any element of windowSizeInput is not like an integer, a ValueError
         is raised.
    4. If any element of windowSizeInput is zero or less, a ValueError is
         raised.
    5. If windowSizeInput is a two-element object containing integer-like
       objects, the visualisation instance has windowSize value equal to
       windowSizeInput.
    """

    vis = chagu.Visualisation()

    # Test 1: If windowSizeInput is not iterable, a TypeError is raised.
    windowSizeInput_1 = -4.3
    expectedMsg = ("Window size value \"{}\" must be iterable."
                   .format(windowSizeInput_1))
    with pytest.raises(TypeError) as testException:
        vis.windowSize = windowSizeInput_1
    assert expectedMsg in testException.value.message

    # Test 2: If windowSizeInput is iterable and does not have two elements
    # exactly, a ValueError is raised.
    windowSizeInput_2 = [2, "b", {}]
    expectedMsg = ("Window size value \"{}\" should contain exactly two "
                   "elements.".format(windowSizeInput_2))
    with pytest.raises(ValueError) as testException:
        vis.windowSize = windowSizeInput_2
    assert expectedMsg in testException.value.message

    # Test 3: If any element of windowSizeInput is not like an integer, a
    # ValueError is raised.
    windowSizeInput_3a = [4.3, 1]
    expectedMsg_a = ("Window size value \"{}\" has element \"{}\", which is "
                     "not an integer.".format(windowSizeInput_3a,
                                              windowSizeInput_3a[0]))
    with pytest.raises(ValueError) as testException:
        vis.windowSize = windowSizeInput_3a
    assert expectedMsg_a in testException.value.message

    windowSizeInput_3b = ["1", []]
    expectedMsg_b = ("Window size value \"{}\" has element \"{}\", which is "
                     "not an integer.".format(windowSizeInput_3b,
                                              windowSizeInput_3b[1]))
    with pytest.raises(ValueError) as testException:
        vis.windowSize = windowSizeInput_3b
    assert expectedMsg_b in testException.value.message

    # Test 4: If any element of windowSizeInput is zero or less, a ValueError
    # is raised.
    windowSizeInput_4a = [-2, "180"]
    expectedMsg_a = ("Window size value \"{}\" has element \"{}\", which must "
                     "be greater than zero.".format(windowSizeInput_4a,
                                                    windowSizeInput_4a[0]))
    with pytest.raises(ValueError) as testException:
        vis.windowSize = windowSizeInput_4a
    assert expectedMsg_a in testException.value.message

    windowSizeInput_4b = [2000, -4.3]
    expectedMsg_b = ("Window size value \"{}\" has element \"{}\", which must "
                     "be greater than zero.".format(windowSizeInput_4b,
                                                    windowSizeInput_4b[1]))
    with pytest.raises(ValueError) as testException:
        vis.windowSize = windowSizeInput_4b
    assert expectedMsg_b in testException.value.message

    # Task 5: If windowSizeInput is a two-element object containing
    # integer-like objects, the visualisation instance has windowSize value
    # equal to windowSizeInput.
    windowSizeInput_5 = [1680, 1050]
    vis.windowSize = windowSizeInput_5
    assert vis.windowSize == windowSizeInput_5


@pytest.mark.skipif(True, reason="Takes a long time, and is obnoxious.")
def test_memory():
    """
    This test is a bit obnoxious: it checks that a visualisation instance does
    not retain memory after being unbound.
    """

    pathToThisFile = os.path.dirname(os.path.realpath(__file__))
    relativeVtuFilePath = "../example/data/data.vtu"
    absFilePath = "{}/{}".format(pathToThisFile, relativeVtuFilePath)

    for zI in range(int(1e6)):
        if zI % 1 == 0:
            print("Creating visualisation object {} of {}."
                  .format(zI, int(1e6)))
        vis = chagu.Visualisation(filePath=absFilePath)
        vis.extract_vector_components(component=2)
        vis.act_surface
        vis.act_cone_vector_field(1,1,20)
        vis.build_renderer_and_window()


if __name__ == "__main__":
    test_initialisation()
    test_set_background()
    test_set_camera()
    test_set_colourmap_lut()
    test_set_windowsize()
    # test_memory()
