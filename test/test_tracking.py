"""
This python file tests the functionality of functions defined in
chagu/tracking.py. Tests are detailed in the function documentation.
"""

import chagu
import os
import pytest
import vtk


def test_get_vtk_object():
    """
    Test chagu.tracking.get_vtk_object. We test the following cases:

    1. If objectName is not in self._vtkObjects, a ValueError is raised.
    2. If objectName maps to a vtkObject in self._vtkObjects, a vtkObject is
         returned.
    3. If objectName maps to a Terminus in self._vtkObjects, a terminus is
         returned.
    """

    # Create the visualisation object for these tests.
    pathToThisFile = os.path.dirname(os.path.realpath(__file__))
    relativeVtuFilePath = "../example/data/data.vtu"
    absFilePath = "{}/{}".format(pathToThisFile, relativeVtuFilePath)

    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePath)

    # Test 1: If objectName is not in self._vtkObjects, a ValueError is raised.
    fakeReaderName = readerName + " fake"
    expectedMsg = ("Object name \"{}\" is not tracked by visualisation object "
                   "\"{}\".".format(fakeReaderName, vis))
    with pytest.raises(ValueError) as testException:
        vis.get_vtk_object(fakeReaderName)
    assert expectedMsg in testException.value.message

    # Test 2: If objectName maps to a vtkObject in self._vtkObjects, a
    # vtkObject is returned.
    reader = vis.get_vtk_object(readerName)
    assert type(reader) == type(vtk.vtkActor())

    # Test 3: If objectName maps to a Terminus in self._vtkObjects, a terminus
    # is returned.
    surfaceName = vis.act_surface()
    assert isinstance(vis.get_vtk_object(surfaceName), chagu.termini.Terminus)


if __name__ == "__main__":
    test_get_vtk_object()
