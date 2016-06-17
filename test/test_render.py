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
    assert renderer.IsA("vtkRenderer")
    assert renderWindow.IsA("vtkRenderWindow")

    # Test 3: The visualisation object has a pipeline defined.
    assert vis._pipeline != []


@pytest.mark.skipif(vtk.vtkVersion().GetVTKVersion() != "5.8.0",
                    reason="vtkGL2PSExporter is not defined in VTK 5.8.")
def test_save_snapshot():
    """
    Test chagu.render.save_snapshot. We test the following cases:

    1. If imageFilename is a supported type, produce a file of that type.
    2. If imageFilename is not of a supported type, raise a
         NotImplementedError.
    """
    vis = chagu.Visualisation()
    vis.load_visualisation_toolkit_file(absFilePath)
    vis.extract_vector_components(component=2)
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


def test_visualise_animate_rotate():
    """
    Test chagu.render.visualise_animate_rotate. We test the following cases:

    1. If rotationResolution is 0, no images are produced.
    2. If rotationResolution is 200, 200 images are produced.

    This function is largely tested by test_save_snapshot and
    test_build_renderer_and_window.
    """
    vis = chagu.Visualisation()
    vis.load_visualisation_toolkit_file(absFilePath)
    vis.extract_vector_components(component=2)
    vis.act_surface()

    imageStackName = "{}/test_visualise_animate_rotate".format(pathToThisFile)
    try:
        # Test 1: If rotationResolution is 0, no images are produced.
        vis.visualise_animate_rotate(imageStackName + "_1",
                                     rotation_resolution=0)
        assert imageStackName not in\
          os.listdir(os.path.dirname(os.path.realpath(__file__)))

        # Test 2: If rotationResolution is 200, 200 images are produced.
        vis.visualise_animate_rotate(imageStackName + "_2",
                                     rotation_resolution=200)
        for zI in xrange(10):
            assert os.path.exists("{}_2_{:03d}.png".format(imageStackName, zI))

    # Remove images as a cleanup activity.
    finally:
        filesToRemove = [imageStackName + "_1"] +\
           ["{}_2_{:03d}.png".format(imageStackName, zI) for zI in xrange(200)]
        for imageFilename in filesToRemove:
            if os.path.exists(imageFilename):
                os.remove(imageFilename)


def test_visualise_interact():
    """
    This should test chagu.render.visualise_interact, but there is no easy way
    to do that. Instead, we check that the classes used in the function are
    defined.
    """
    vtk.vtkRenderWindowInteractor()


def test_visualise_save():
    """
    Test chagu.render.visualise_save. We test the following cases:

    1. If imageFilename is a supported type, produce a file of that type.

    This function is largely tested by test_save_snapshot and
    test_build_renderer_and_window.
    """
    vis = chagu.Visualisation()
    vis.load_visualisation_toolkit_file(absFilePath)
    vis.extract_vector_components(component=2)
    vis.act_surface()

    # Test 1: If imageFilename is a supported type, produce a file of that
    # type.
    imageFilename = "{}/test_visualise_save.png".format(pathToThisFile)
    try:
        vis.visualise_save(imageFilename)
        assert os.path.exists(imageFilename)

    # Remove the image as a cleanup activity.
    finally:
        if os.path.exists(imageFilename):
            os.remove(imageFilename)


if __name__ == "__main__":
    test_build_renderer_and_window()
    test_save_snapshot()
