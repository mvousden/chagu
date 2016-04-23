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


def test_build_pipeline_from_dict():
    """
    Test chagu.build_pipeline_from_dict. We test the following cases:

    1. If a connection in the dictionary is invalid, a ValueError is raised.
    2. If a connection is specified with an output port, ensure that port is
        used in the connection.
    3. If a connection is specified with an input port, ensure that port is
        used in the connection.
    4. If a default output port is specified in an object, ensure that port is
        used in the connection if no other port information is passed.
    5. If a default input port is specified in an object, ensure that port is
        used in the connection if no other port information is passed.
    6. If build_pipeline_from_dict is called again after a successful pipeline
        build, a RuntimeError is raised.
    """

    # For reference, here's a quick chart showing numbers of inputs and
    # outputs for the objects created below.

    # +-------------+---------+--------+
    # |    Name     | Outputs | Inputs |
    # +-------------+---------+--------+
    # | readerName  |    1    |    0   |
    # | compName    |    3    |    1   |
    # | surfaceName |    0    |    1   |
    # | conesName   |    0    |    2   |
    # +-------------+---------+--------+

    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePathData)
    compName = vis.extract_vector_components(component=2)
    surfaceName = vis.act_surface()
    conesName = vis.act_cone_vector_field(1, 1, 1)

    # Test 1: If a connection in the dictionary is invalid, a ValueError is
    # raised.
    badName = compName + " ooh look a dragon"
    pipeline = [[readerName, badName],
                [compName, surfaceName]]
    with pytest.raises(ValueError) as testException:
        vis.build_pipeline_from_dict(pipeline)
    assert badName in testException.value.message

    # Test 2: If a connection is specified with an output port, ensure that port
    # is used in the connection.

    # Look closely, output port 1 of components is used, even though port 2 is
    # the default here because component=2 was passed.
    pipeline = [[readerName, compName],
                [compName, [surfaceName, 1, 0]],
                [compName, [conesName, 0, 1]]]
    vis.build_pipeline_from_dict(pipeline)

    compObjectOutputData = vis.get_vtk_object(compName).GetOutputDataObject(1)
    surfObjectInputData = vis.get_vtk_object(surfaceName).actor.GetMapper()\
                          .GetInputDataObject(0, 0)
    assert compObjectOutputData == surfObjectInputData

    # Test 3: If a connection is specified with an input port, ensure that
    # port is used in the connection.
    compObjectOutputData = vis.get_vtk_object(compName).GetOutputDataObject(0)
    coneObjectInputData = vis.get_vtk_object(conesName).actor.GetMapper()\
                          .GetInputDataObject(1, 0)
    assert compObjectOutputData == coneObjectInputData

    # Test 4: If a default output port is specified in an object, ensure that
    # port is used in the connection if no other port information is passed.
    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePathData)
    compName = vis.extract_vector_components(component=2)
    surfaceName = vis.act_surface()
    conesName = vis.act_cone_vector_field(1, 1, 1)

    pipeline = [[readerName, compName],
                [compName, surfaceName],
                [compName, conesName]]
    vis.build_pipeline_from_dict(pipeline)

    compObjectOutputData = vis.get_vtk_object(compName).GetOutputDataObject(2)
    surfObjectInputData = vis.get_vtk_object(surfaceName).actor.GetMapper()\
                          .GetInputDataObject(0, 0)
    assert compObjectOutputData == surfObjectInputData

    # Test 5: If a default input port is specified in an object, ensure that
    # port is used in the connection if no other port information is passed.
    compObjectOutputData = vis.get_vtk_object(compName).GetOutputDataObject(2)
    coneObjectInputData = vis.get_vtk_object(surfaceName).actor.GetMapper()\
                          .GetInputDataObject(0, 0)
    assert compObjectOutputData == coneObjectInputData

    # Test 6: If build_pipeline_from_dict is called again after a successful
    # pipeline build, a RuntimeError is raised.
    expectedMsg = "once per visualisation instance"
    with pytest.raises(RuntimeError) as testException:
        vis.build_pipeline_from_dict([])
    assert expectedMsg in testException.value.message


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
    compInputData = vis._vtkObjects[compName].GetInputDataObject(0, 0)
    readerOutputData = vis._vtkObjects[readerName].GetOutputDataObject(0)
    assert compInputData == readerOutputData


if __name__ == "__main__":
    test_build_pipeline_from_dict()
    test_check_connection()
    test_connect_vtk_objects()
