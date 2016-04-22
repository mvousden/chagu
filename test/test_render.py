"""
This python file tests the functionality of functions defined in
chagu/helpers.py. Tests are detailed in the function documentation.
"""

import chagu
import os
import pytest
import vtk


pathToThisFile = os.path.dirname(os.path.realpath(__file__))
relativeVtuFilePath = "../example/data/data.vtu"
absFilePath = "{}/{}".format(pathToThisFile, relativeVtuFilePath)


def test_build_renderer_and_window():
    """
    Test chagu.render.build_renderer_and_window. We test the following cases:

    1. If no file has been loaded by the visualisation object, a RuntimeError
         is raised.
    2. A vtkRenderer and a vtkRenderWindow are both returned if successful.
    3. The visualisation object has a pipeline defined.
    """

    vis = chagu.Visualisation()

    # Test 1: If no file has been loaded by the visualisation object, a
    # RuntimeError is raised.
    with pytest.raises(RuntimeError):
        vis.build_renderer_and_window()

    # Test 2: A vtkRenderer and a vtkRenderWindow are both returned if
    # successful.
    vis.load_visualisation_toolkit_file(absFilePath)
    vis.act_surface()

    renderer, renderWindow = vis.build_renderer_and_window()
    assert type(renderer) == type(vtk.vtkRenderer())
    assert type(renderWindow) == type(vtk.vtkRenderWindow())

    # Test 3: The visualisation object has a pipeline defined.
    assert vis._pipeline != []


def test_save_snapshot():
    """
    Test chagu.render.save_snapshot. We test the following cases:

    1. If imageFilename is a supported type, produce a file of that type.
    2. If imageFilename is not of a supported type, raise a
         NotImplementedError.
    """

    vis = chagu.Visualisation()
    vis.load_visualisation_toolkit_file(absFilePath)
    vis.act_surface()
    renderer, renderWindow = vis.build_renderer_and_window()
    renderWindow.SetOffScreenRendering(True)

    imageFiles = ["{}/test_save_snapshot.{}".format(pathToThisFile, zI)\
                  for zI in ["png", "ps", "pdf", "eps"]]

    try:
        # Test 1: If imageFilename is a supported type, produce a file of that
        # type.
        for imageFilename in imageFiles:
            chagu.render.save_snapshot(renderWindow, imageFilename)
            assert os.path.exists(imageFilename)

        # Test 2: If imageFilename is not of a supported type, raise a
        # NotImplementedError.
        imageFilename = "{}/test_save_snapshot.jpg".format(pathToThisFile)
        with pytest.raises(NotImplementedError):
            chagu.render.save_snapshot(renderWindow, imageFilename)

    # Remove the images as a cleanup activity.
    finally:
        for imageFilename in imageFiles:
            if os.path.exists(imageFilename):
                os.remove(imageFilename)


if __name__ == "__main__":
    test_build_renderer_and_window()
    test_save_snapshot()
