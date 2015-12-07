"""
This python file tests the functionality of the functions defined in
chagu/sources.py. Tests are detailed in the function documentation
"""

import chagu
import os
import pytest


pathToThisFile = os.path.dirname(os.path.realpath(__file__))
relativeVtuFilePathData = "../example/data/data.vtu"
absFilePathData = "{}/{}".format(pathToThisFile, relativeVtuFilePathData)

relativeVtuFilePathData2d = "../example/data/data_2d.vtu"
absFilePathData2d = "{}/{}".format(pathToThisFile, relativeVtuFilePathData2d)


def test_load_visualisation_toolkit_file():
    """
    Test chagu.sources.load_visualisation_toolkit_file. We test the following
    cases:

    1. If filePath does not match a file, a ValueError is raised.
    2. If filePath has an invalid extension (i.e. not in
        sources.validExtensions.keys()), a ValueError is raised.
    3. If filePath is valid and readerName is set, readerName maps to this
        vtkReader in the _vtkObjects dictionary in the visualisation instance,
        and the _boundingBox value is set appropriately.
    4. If two reader objects are created using the test outlined in 3, then
        the _boundingBox value is the combined value of the two geometries.
    """

    vis = chagu.Visualisation()

    # Test 1: If filePath does not match a file, a ValueError is raised.

    # Obtain the name of a file that does not exist.
    falseFileSuffix = "_0"
    while True:
        falseFile = "falsefile" + falseFileSuffix
        if os.path.isfile(falseFile) is False:
            break


    # Run test.
    expectedMsg = ("\"{}\" does not exist".format(falseFile))
    with pytest.raises(ValueError) as testException:
        vis.load_visualisation_toolkit_file(falseFile)
    assert expectedMsg in testException.value.message

    # Test 2: If filePath has an invalid extension (i.e. not in
    # sources.validExtensions.keys()), a ValueError is raised.

    # Create the testFile.
    testFile = "testFile.xyz"
    assert os.path.isfile(testFile) is False
    with open(testFile, "w") as fl:
        pass

    # Run test.
    expectedMsg = ("\"{}\" has invalid extension \"{}\""
                   .format(testFile, falseExt))
    with py.test.raises(ValueError) as testException:
        vis.load_visualisation_toolkit_file(testFile)
        os.remove(testFile)  # Remove test file.
    assert expectedMsg in testException.value.message

    # Test 3: If filePath is valid and readerName is set, readerName maps to
    # this vtkReader in the _vtkObjects dictionary in the visualisation
    # instance, and the _boundingBox value is set appropriately.
    readerName = "test_reader"
    vis.load_visualisation_toolkit_file(absFilePathData, readerName)
    assert vis.is_tracked(readerName) is True
    assert vis._boundingBox[:-2] == [-9.3, 9.3, -16.1, 16.1]

    # Test 4: If two reader objects are created using the test outlined in 3,
    # then the _boundingBox value is the combined value of the two geometries.

    # To achieve this, we use the same visualisation object from before, but
    # load a second file.
    print(dir(vis))
    vis.load_visualisation_toolkit_file(absFilePathData2d)
    assert vis._boundingBox[:-2] == [-15, 15, -16.1, 16.1]
    assert 0 not in vis._boundingBox


if __name__ == "__main__":
    test_load_visualisation_toolkit_file()
