# This source file defines the filters that are applied to loaded VTK data to
# emphasise some of its characteristics. These filters should live in the
# pipeline between the data source and the actors responsible for drawing the
# data to the renderer.

import vtk

import chagu.helpers as helpers


def contour(self, values=0, contourName=None):
    """
    Use a vtkContourFilter to, well, create a contour filter. If this filter is
    applied to a surface, an isosurface is produced.

    Arguments:

      - values: Float or iterable object of floats denoting the values of the
          contours to draw.

      - contourName: String or None denoting the name to give to the contour
          object. This should not clash with an existing name. If this is None,
          a sensible name is chosen. If there is a clash, the name is changed
          (and returned).

    Returns the name of the contour object.
    """
    # Come up with a name for the object.
    sensibleName = contourName if contourName is not None else "contour"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Create the object.
    contourFilter = vtk.vtkContourFilter()
    if hasattr(values, "__getitem__"):
        for zI in range(len(values)):
            contourFilter.SetValue(zI, values[zI])
    else:
        contourFilter.SetValue(0, values)
    self.track_object(contourFilter, sensibleName)
    return sensibleName


def extract_vector_components(self, componentsName=None, component=0):
    """
    Use a vtkExtractVectorComponents object to, well, extract the vector
    components. We use an intermediate class to store the component until
    the pipeline is used.

    Arguments:

      - componentsName: String or None denoting the name to give to the extract
          components object. This should not clash with an existing name. If
          this is None, a sensible name is chosen. If there is a clash, the
          name is changed (and returned).

      - component: Index of component to extract.

    Returns the name of the extration object.
    """
    # Come up with a name for the object.
    sensibleName = componentsName if componentsName is not None\
        else "extract_components"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Create the object.
    extractComponents = vtk.vtkExtractVectorComponents()
    extractComponents.default_output_port = component
    self.track_object(extractComponents, sensibleName)
    return sensibleName


def slice_data_with_plane(self, normal=[0., 0., 1.], origin=[0., 0., 0.],
                          sliceName=None):
    """
    Use a vtkCutter object to slice the input, whatever it may be.

    Arguments:

      - normal: Three-element iterable object of floats denoting the normal
          vector of the slice plane.

      - origin: Three-element iterable object of floats denoting a location on
          the slice plane.

      - sliceName: String or None denoting the name to give to the slice
          object. This should not clash with an existing name. If this is None,
          a sensible name is chosen. If there is a clash, the name is changed
          (and returned).

    Returns the name of the slice object.
    """
    # Come up with a name for the object.
    sensibleName = sliceName if sliceName is not None else "slice"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Define the plane geometry on which the slice exists.
    cutPlane = vtk.vtkPlane()
    cutPlane.SetOrigin(origin)
    cutPlane.SetNormal(normal)

    # Create a cutter object to slice the data.
    imageSlice = vtk.vtkCutter()
    imageSlice.SetCutFunction(cutPlane)

    self.track_object(imageSlice, sensibleName)
    return sensibleName
