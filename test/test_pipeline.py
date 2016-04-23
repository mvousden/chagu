"""
This python file tests the functionality of the functions defined in
chagu/pipeline.py. Tests are detailed in the function documentation
"""

import chagu
import os
import pytest
import subprocess as sp


pathToThisFile = os.path.dirname(os.path.realpath(__file__))
relativeVtuFilePathData = "../example/data/data.vtu"
absFilePathData = "{}/{}".format(pathToThisFile, relativeVtuFilePathData)


def test_autopipe():
    """
    Test chagu.pipeline.autopipe. We test the following cases:

    1. Connecting objects without a fileReader raises a RuntimeError.
    2. Nasty vector termini are connected directly to the filereader.
    3. Termini with no inputs are not present in the pipeline.
    4. Changing the order filters are added modifies the pipeline accordingly;
        most recent filters are connected to termini.
    """

    vis = chagu.Visualisation()
    compName = vis.extract_vector_components(component=2)
    surfaceName = vis.act_surface()
    conesName = vis.act_cone_vector_field(1, 1, 1)
    nastyName = vis.act_nasty_vector_field(1)
    cmapName = vis.act_colourbar()

    # Test 1: Connecting objects without a fileReader raises a RuntimeError.
    with pytest.raises(RuntimeError) as testException:
        vis.autopipe()
    assert "read" in testException.value.message

    # Test 2: Nasty vector termini are connected directly to the filereader.
    readerName = vis.load_visualisation_toolkit_file(absFilePathData)
    vis.autopipe()
    assert [readerName, nastyName] in vis._pipeline

    # Test 3: Termini with no inputs are not present in the pipeline.
    for connection in vis._pipeline:
        assert cmapName not in connection

    # Test 4: Changing the order filters are added modifies the pipeline
    # accordingly; most recent filters are connected to termini.
    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePathData)
    compName = vis.extract_vector_components(component=2)
    sliceName = vis.slice_data_with_plane()
    surfaceName = vis.act_surface()
    vis.autopipe()

    # Check that only the expected connections are in the pipeline (in any
    # order, we're not that mean).
    expectedConnections = [[readerName, compName],
                           [compName, sliceName],
                           [sliceName, surfaceName]]
    resultingPipeline = vis._pipeline
    for connection in expectedConnections:
        assert connection in resultingPipeline
        resultingPipeline.remove(connection)
    assert resultingPipeline == []

    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePathData)
    sliceName = vis.slice_data_with_plane()  # Switched in order.
    compName = vis.extract_vector_components(component=2)  # Switched in order.
    surfaceName = vis.act_surface()
    nastyName = vis.act_nasty_vector_field(1, maskType="plane")
    vis.autopipe()

    expectedConnections = [[readerName, sliceName],
                           [sliceName, compName],
                           [compName, surfaceName],
                           [readerName, nastyName]]
    resultingPipeline = vis._pipeline
    for connection in expectedConnections:
        assert connection in resultingPipeline
        resultingPipeline.remove(connection)
    assert resultingPipeline == []


def test_build_pipeline_from_dict():
    """
    Test chagu.pipeline.build_pipeline_from_dict. We test the following cases:

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
    7. A successful connection writes the pipeline to vis._pipeline.
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
                [compName, [conesName, 0, 1]],
                [compName, [conesName, 2, 0]]]
    print("One VTK error should appear here, because we are connecting "
          "objects inappropriately.\n")
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

    # Test 7: A successful connection writes the pipeline to vis._pipeline.
    assert pipeline == vis._pipeline


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
    compInputData = vis.get_vtk_object(compName).GetInputDataObject(0, 0)
    readerOutputData = vis.get_vtk_object(readerName).GetOutputDataObject(0)
    assert compInputData == readerOutputData


def test_draw_pipeline_graphviz():
    """
    Test chagu.pipeline.draw_pipeline_graphviz. We test the following cases:

    1. Test that the PDF is produced using the name of the visualisation.
    2. Test that all object names are in the PDF.
    """

    visName = "test_draw_pipeline_graphviz"
    objectNames = []
    vis = chagu.Visualisation(visName)
    objectNames.append(vis.load_visualisation_toolkit_file(absFilePathData))
    objectNames.append(vis.extract_vector_components(component=2))
    objectNames.append(vis.act_surface())
    objectNames.append(vis.act_cone_vector_field(1, 1, 1))
    objectNames.append(vis.act_nasty_vector_field(1))
    objectNames.append(vis.act_colourbar())
    vis.autopipe()

    graphvizFile = "{}/{}_pipeline.gv.pdf".format(pathToThisFile, visName)
    textFile = "{}.txt".format(graphvizFile[:-4])

    try:
        # Test 1: Test that the PDF is produced using the name of the
        # visualisation.
        vis.draw_pipeline_graphviz(directory=pathToThisFile)
        assert os.path.isfile(graphvizFile)

        # Test 2: Test that all object names are in the PDF.
        sp.Popen(["pdftotext", graphvizFile, textFile]).wait()
        with open(textFile) as fl:
            content = fl.read()
        for objectName in objectNames:
            assert objectName in content

    # Cleanup
    finally:
        if os.path.exists(graphvizFile):
            os.remove(graphvizFile)
        if os.path.exists(textFile):
            os.remove(textFile)


if __name__ == "__main__":
    test_autopipe()
    test_build_pipeline_from_dict()
    test_check_connection()
    test_connect_vtk_objects()
    test_draw_pipeline_graphviz()
