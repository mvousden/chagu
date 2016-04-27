# This source file defines rendering methods for the visualisation class. They
# create renderers and other such objects and attach them to the VTK pipeline
# specified by the visualisation object calling them.

import numpy as np
import vtk


def build_renderer_and_window(self):
    """
    Create a vtkRenderer and vtkRenderWindow object.

    This function is useful if you wish to define your own visualise function
    for your purposes. The visualising functions defined in this class use this
    function internally, so you should not need to call this function directly
    if you are using those to render your visualisation.

    This function will autopipe if no pipeline has been created.

    Returns, in order, a vtkRenderer instance and a vtkRenderWindow instance.
    """
    # We should complain if no data has been loaded correctly. This will be the
    # case if all of the bounding box values are still zero. This also handily
    # stops a zero-division error that would occur later if the camera position
    # was not defined.
    if self._boundingBox == [0 for zI in range(6)]:
        raise RuntimeError("Creating renderer before loading a data file "
                           "is a recipe for disaster. Consider loading "
                           "your input data file with "
                           "visualisation.load_visualisation_toolkit_file "
                           "first.")

    # Attempt to autopipe if the pipeline has not been created.
    if self._pipeline == []:
        self.autopipe()

    # Build the renderer, and add all the actors that this visualisation object
    # is looking after.
    renderer = vtk.vtkRenderer()
    for terminus in self._vtkTermini.itervalues():
        renderer.AddActor(terminus.actor)
    renderer.SetBackground(*self._background)

    # Now we manipulate the camera. Add defaults to values that have not been
    # defined. Defaults are defined here. The default is to look down on the
    # centre of the domain along the "z-axis".
    for key in self._validCameraKeys:
        if key not in self._camera:
            if key == "focal point":
                # Look at the centre!
                value = [(self._boundingBox[1] - self._boundingBox[0]) / 2.,
                         (self._boundingBox[3] - self._boundingBox[2]) / 2.,
                         (self._boundingBox[5] - self._boundingBox[4]) / 2.]
            if key == "position":
                # This is a conservative estimate that doesn't account for
                # camera orientation and non-squre geometries. It should fit
                # the whole domain in though. <!>
                elevation = max(self._windowSize) /\
                    max(np.abs(self._boundingBox[:4]))
                xCentre = (self._boundingBox[1] - self._boundingBox[0]) / 2.
                value = [(self._boundingBox[1] - self._boundingBox[0]) / 2.,
                         (self._boundingBox[3] - self._boundingBox[2]) / 2.,
                          elevation]
            if key == "parallel projection":
                value = False
            if key == "view up":
                value = [0., 1., 0.]
            if key == "zoom":
                value = 1
            self._camera[key] = value

    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(*self._camera["focal point"])
    camera.SetParallelProjection(self._camera["parallel projection"])
    camera.SetPosition(*self._camera["position"])
    camera.SetViewUp(*self._camera["view up"])
    camera.Zoom(self._camera["zoom"])

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(*self._windowSize)

    return renderer, renderWindow


def save_snapshot(renderWindow, imageFilename):
    """
    Save a rendered vtkRenderWindow to a file.

    Create a vtkWindowToImageFilter and vtkImageWriter to save a render window.

    Arguments:
      - renderWindow: Rendered vtkRenderWindow instance to save a snapshot of.
      - imageFilename: String to save output file to.

    Returns nothing.
    """
    extension = imageFilename.split(".")[-1]

    if extension == "png":
        im = vtk.vtkWindowToImageFilter()
        im.SetInput(renderWindow)

        writer = vtk.vtkPNGWriter()
        writer.SetInputConnection(im.GetOutputPort())
        writer.SetFileName(imageFilename)
        writer.Write()
    elif extension in ["ps", "pdf", "eps"]:
        writer = vtk.vtkGL2PSExporter()
        writer.SetRenderWindow(renderWindow)
        if extension == "eps":
            writer.SetFileFormatToEPS()
        elif extension == "pdf":
            writer.SetFileFormatToPDF()
        elif extension == "ps":
            writer.SetFileFormatToPS()
        writer.SetFilePrefix(".".join(imageFilename.split(".")[:-1]))
        writer.Write()
    else:
        raise NotImplementedError


def visualise_animate_rotate(self, imageStackName, offscreenRendering=True,
                             rotation_resolution=360, verbose=True,
                             xyMax=None, zMax=None):
    """
    Create a stack of images by rotating a camera around a scene. This stack of
    images can be used by avconv or similar to create an animation. This
    visualisation commandeers the camera, and so does not use settings defined
    by self._camera.

    Arguments:

      - imageStackName: A string used as the prefix for the output image
        stack.
      - offscrenRendering: Boolean denoting whether or not to render
          offscreen.
      - rotation_resolution: Integer determining number of images to save.
      - verbose: Boolean determining whether or not progress is printed.
      - xyMax: Float determining the distance in the xy plane of the camera
          from x, y = 0, 0, or None.
      - zMax: Float determining camera elevation, or None.

    Returns nothing.
    """
    # Building the render window also populates missing parameters defining the
    # position and orientation of the camera. We use this information to create
    # a guess to fit the geometry completely into the window if xyMax and zMax
    # are None.
    renderer, renderWindow = self.build_renderer_and_window()
    renderWindow.SetOffScreenRendering(offscreenRendering)
    camera = renderer.GetActiveCamera()

    if zMax is None:
        zMax = self._camera["position"][2]  # Elevation
        xyMax = zMax * 1.95  # <!> Not sure why.

    plane_tilt_angle = np.tan(zMax / xyMax)
    angles = np.linspace(0, np.pi * 2, rotation_resolution)

    # Create a newline for verbose printing.
    if verbose is True:
        print()

    # Render each frame independently.
    for zI in xrange(rotation_resolution):
        if verbose is True:
            print "Rendering frame {} of {}.".format(zI + 1,
                                                     rotation_resolution)
        xPos = np.cos(angles[zI]) * xyMax
        yPos = np.sin(angles[zI]) * xyMax
        zPos = zMax
        camera.SetPosition(xPos, yPos, zPos)

        zUp = np.sin(plane_tilt_angle)
        xUp = (1 - zUp) * np.cos(angles[zI])
        yUp = (1 - zUp) * np.sin(angles[zI])
        camera.SetViewUp(xUp, yUp, zUp)

        # The format specifier of the output filename should vary with the
        # resolution.
        outSpecifier = len(str(rotation_resolution))
        outPath = "{}_{:0{}}.png".format(imageStackName, zI, outSpecifier)
        save_snapshot(renderWindow, outPath)


def visualise_interact(self):
    """
    Begin an interactive visualisation.

    Create a vtkRenderWindow and vtkRenderWindowInteractor with the intention
    of creating an interactive VTK window. This can be interfaced with using
    various keyboard commands, or the mouse.

    Returns nothing.
    """
    renderer, renderWindow = self.build_renderer_and_window()

    interactor = vtk.vtkRenderWindowInteractor()
    renderWindow.SetInteractor(interactor)
    interactor.Initialize()
    interactor.Start()

    renderWindow.Finalize()
    interactor.TerminateApp()


def visualise_save(self, imageFilename, offscreenRendering=True):
    """
    Save a visualisation to a file.

    Create a vtkWindowToImageFilter and vtkPNGWriter to save a render window
    created from this class. Do so using offscreen rendering if desired.

    Arguments:

      - imageFilename: String to save output file to.
      - offscrenRendering: Boolean denoting whether or not to render offscreen.

    Returns nothing.
    """
    renderer, renderWindow = self.build_renderer_and_window()
    renderWindow.SetOffScreenRendering(offscreenRendering)
    renderWindow.Render()
    save_snapshot(renderWindow, imageFilename)
