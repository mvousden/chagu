"""
This python file tests the functionality of the functions defined in
chagu/pipeline.py. Tests are detailed in the function documentation
"""

import chagu
import os
import pytest


pathToThisFile = os.path.dirname(os.path.realpath(__file__))
relativeVtuFilePathData = "../example/data/data.vtu"
absFilePathData = "{}/{}".format(pathToThisFile, relativeVtuFilePathData)


def test_check_connection():
    """
    Test chagu.pipeline.check_connection. We test the following cases:

    1. If inputObjectName does not map to an object in the visualisation
        instance, a ValueError is raised.
    2. If outputObjectName does not map to an object in the visualisation
        instance, a ValueError is raised.
    3. If outputPortIndex is greater than the number of output ports an object
        has, a ValueError is raised.
    4. If inputPortIndex is greater than the number of input ports an object
        has, a ValueError is raised.
    5. If input arguments are fine, no error is raised.
    """

    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePathData)
    compName = vis.extract_vector_components(component=2)

    # Test 1: If inputObjectName does not map to an object in the visualisation
    # instance, a ValueError is raised.
    fakeInputName = compName + "lies"
    expectedMsgs = ["nvalid input object name", fakeInputName]
    with pytest.raises(ValueError) as testException:
        vis.check_connection(readerName, fakeInputName)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 2: If outputObjectName does not map to an object in the
    # visualisation instance, a ValueError is raised.
    fakeOutputName = readerName + "lies"
    expectedMsgs = ["nvalid output object name", fakeOutputName]
    with pytest.raises(ValueError) as testException:
        vis.check_connection(fakeOutputName, compName)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 3: If outputPortIndex is greater than the number of output ports an
    # object has, a ValueError is raised.
    expectedMsgs = ["utput port index", "100"]
    with pytest.raises(ValueError) as testException:
        vis.check_connection(readerName, compName, outputPortIndex=100)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 4: If inputPortIndex is greater than the number of input ports an
    # object has, a ValueError is raised.
    expectedMsgs = ["nput port index", "100"]
    with pytest.raises(ValueError) as testException:
        vis.check_connection(readerName, compName, inputPortIndex=100)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 5: If input arguments are fine, no error is raised.
    vis.check_connection(readerName, compName)


def test_connect_vtk_objects():
    """
    Test chagu.pipeline.connect_vtk_objects. We test the following cases:

    1. Test that the connection is checked before being made.
    2. If input arguments are fine, check that the objects are actually
        connected according to VTK.
    """

    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePathData)
    compName = vis.extract_vector_components(component=2)

    # Test 1: Test that the connection is checked before being made.

    # Test 1a: If inputObjectName does not map to an object in the
    # visualisation instance, a ValueError is raised.
    fakeInputName = compName + "lies"
    expectedMsgs = ["nvalid input object name", fakeInputName]
    with pytest.raises(ValueError) as testException:
        vis.connect_vtk_objects(readerName, fakeInputName)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 1b: If outputObjectName does not map to an object in the
    # visualisation instance, a ValueError is raised.
    fakeOutputName = readerName + "lies"
    expectedMsgs = ["nvalid output object name", fakeOutputName]
    with pytest.raises(ValueError) as testException:
        vis.connect_vtk_objects(fakeOutputName, compName)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 1c: If outputPortIndex is greater than the number of output ports an
    # object has, a ValueError is raised.
    expectedMsgs = ["utput port index", "100"]
    with pytest.raises(ValueError) as testException:
        vis.connect_vtk_objects(readerName, compName, outputPortIndex=100)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 1d: If inputPortIndex is greater than the number of input ports an
    # object has, a ValueError is raised.
    expectedMsgs = ["nput port index", "100"]
    with pytest.raises(ValueError) as testException:
        vis.connect_vtk_objects(readerName, compName, inputPortIndex=100)
    for expectedMsg in expectedMsgs:
        assert expectedMsg in testException.value.message

    # Test 2: If input arguments are fine, check that the objects are actually
    # connected according to VTK.
    vis.connect_vtk_objects(readerName, compName)
    compObject = vis._vtkObjects[compName]
    assert compObject.GetInputAlgorithm() == vis._vtkObjects[readerName]


if __name__ == "__main__":
    test_check_connection()
    test_connect_vtk_objects()
