"""
This python file tests the functionality of functions defined in
chagu/tracking.py. Tests are detailed in the function documentation.
"""

import chagu
import os
import pytest
import vtk


pathToThisFile = os.path.dirname(os.path.realpath(__file__))
relativeVtuFilePath = "../example/data/data.vtu"
absFilePath = "{}/{}".format(pathToThisFile, relativeVtuFilePath)


def test_get_vtk_object():
    """
    Test chagu.tracking.get_vtk_object. We test the following cases:

    1. If objectName is not in self._vtkObjects, a ValueError is raised.
    2. If objectName maps to a vtkObject in self._vtkObjects, a vtkObject is
         returned.
    3. If objectName maps to a Terminus in self._vtkObjects, a terminus is
         returned.
    """

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


def test_is_nasty():
    """
    Test chagu.tracking.is_nasty. We test the following cases:

    1. If objectName is not mapped, False is returned.
    2. If objectName maps to a vtkObject, False is returned.
    3. If objectName maps to a Terminus instance that is not nasty, False is
         returned.
    4. If objectName maps to a nasty Terminus instance, True is returned.
    """

    vis = chagu.Visualisation()

    # Test 1: If objectName is not tracked, False is returned.
    assert vis.is_nasty("Object that doesn't exist.") is False

    # Test 2: If objectName is a vtkObject, False is returned.
    componentsName = vis.extract_vector_components()
    assert vis.is_nasty(componentsName) is False

    # Test 3: If objectName is a Terminus instance that is not nasty, False
    # is returned.
    surfaceName = vis.act_surface()
    assert vis.is_nasty(surfaceName) is False

    # Test 4: If objectName is a nasty Terminus instance, True is returned.
    nastyName = vis.act_nasty_vector_field(1)
    assert vis.is_nasty(nastyName) is True


def test_is_reader():
    """
    Test chagu.tracking.is_reader. We test the following cases:

    1. If objectName is not mapped, False is returned.
    2. If objectName is mapped to an object that is not a reader, False is
         returned.
    3. If objectName is mapped to a reader object, True is returned.
    """

    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePath)

    # Test 1: If objectName is not mapped, False is returned.
    assert vis.is_reader("Object that doesn't exist.") is False

    # Test 2: If objectName is mapped to an object that is not a reader, False
    # is returned.
    surfaceName = vis.act_surface()
    componentsName = vis.extract_vector_components()
    assert vis.is_reader(surfaceName) is False
    assert vis.is_reader(componentsName) is False

    # Test 3: If objectName is mapped to a reader object, True is returned.
    assert vis.is_reader(readerName) is True


def test_is_tracked():
    """
    Test chagu.tracking.is_tracked. We test the following cases:

    1. If objectName is not mapped, False is returned.
    2. If objectName is the return value of a method that creates a vtkObject
         and tracks it, True is returned.
    3. If objectname is used with track_vtk_object to track an arbitrary
         object, True is returned.
    """

    vis = chagu.Visualisation()
    readerName = vis.load_visualisation_toolkit_file(absFilePath)

    # Test 1: If objectName is not mapped, False is returned.
    assert vis.is_tracked("Object that doesn't exist.") is False

    # Test 2: If objectName is the return value of a method that creates a
    # vtkObject and tracks it, True is returned.
    surfaceName = vis.act_surface()
    componentsName = vis.extract_vector_components()
    assert vis.is_tracked(surfaceName) is True
    assert vis.is_tracked(componentsName) is True

    # Test 3: If objectname is used with track_vtk_object to track an arbitrary
    # object, True is returned.
    trackName = "test_object"
    vis.track_vtk_object("A proxy vtkObject", trackName)
    assert vis.is_tracked(trackName) is True


if __name__ == "__main__":
    test_get_vtk_object()
    test_is_nasty()
    test_is_reader()
    test_is_tracked()
