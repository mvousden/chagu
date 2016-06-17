# This source file defines the so-called modules that are applied to VTK data
# to describe how the data should be drawn. They manipulate data after the
# filters have applied to them. In VTK terms, termini are the combination of
# mappers and actors for an object to draw.

import matplotlib.cm
import numpy as np
import vtk

import chagu.helpers as helpers
import chagu.mask as mask


class Terminus:
    """
    This class wraps around a number of vtk objects that are responsible for
    drawing a certain entity only.

    If you want to draw a cone vector field in VTK, you must connect a source
    object for the cone to a mapper object, and connect the mapper object to an
    actor object. In addition if you want to mask your points in a sensible
    manner, you need to pass your data through a probefilter object, which also
    needs to be connected to your mapper. This whole connection buisness is
    more complicated for the average user than it needs to be, so this class
    tries to simplify that.

    This class holds a number of these objects that are linear in the pipeline
    (that is, they only connect to and from one other object), where there is
    an actor at end of the pipeline. It handles the input connection to the
    object at the input of the collection of objects, but does not connect
    objects internally.

    Initialisation arguments:

      - actor: A vtkActor object that communicates directly with the renderer.
          It is the object at the end of the pipeline. If it has no mapper,
          updates will fail.

      - variety: A string denoting the type of terminus this is. This is
          deliberatly vague, but is designed so that internal scripts can
          identify the "type" of the object by intention. This is not good
          design, but it's convenient design that works.

      - vtkEndObject: The VTK object at the end of the pipeline managed by this
          terminus. It should know how to update itself and manage its own
          input connections. If None, input connections will fail.
    """
    def __init__(self, actor, variety=None, vtkEndObject=None):

        self.actor = actor
        self.variety = variety

        if self.actor.GetMapper() is not None:
            self.Update = self.actor.GetMapper().Update

        if vtkEndObject is not None:
            self.SetInputConnection = vtkEndObject.SetInputConnection
            self.GetNumberOfInputPorts = vtkEndObject.GetNumberOfInputPorts


def act_colourbar(self, colourBarName=None, colourMap=None, labelProps={},
                  numLabels=5, resolution=1024, title=None, titleProps={}):
    """
    Define a vtkScalarBarActor that draws the colourbar intelligently.

    Arguments:

      - colourBarName: String or None denoting the name to give to the colour
          bar object. This should not clash with an existing name. If this is
          None, a sensible name is chosen. If there is a clash, the name is
          changed (and returned).

      - colourMap: LinearSegmentedColormap object from matplotlib to create a
          vtkLookupTable with, or the name of an attribute from matplotlib.cm
          as a string, or None. If None, the _colourmap_lut attribute of the
          visualisation object is used.

      - numLabels: Integer denoting the number of labels to use.

      - labelProps: Dictionary with string keys denoting properties of the
          labels on the colour bar. Valid entries are:
            > "bold": boolean denoting whether or not to bold text.
            > "font": string denoting font family to use, either "arial",
                "times", or "courier". The selection is small due to VTK not
                directly implementing more fonts, apparently.
            > "italic": boolean denoting whether or not to italicise text.
            > "justification": string denoting how to horizontally justify
                text. Either "left", "centre", or "right".
            > "shadow": boolean denoting whether or not to add a shadow to the
                text.
            > "size": integer denoting the font size of the text.

      - resolution: Integer denoting number of colours to draw on the
          colourbar.

      - titleProps: Dictionary with string keys denoting the properties of the
          colourbar title. Entries are identical to the labelProps argument.

      - title: String or None denoting the title for the colourbar.

    """
    # Come up with a name for the object.
    sensibleName = colourBarName if colourBarName is not None else "colourbar"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Create the lookup table for this colourbar if a different map is
    # required.
    if colourMap is not None:
        lut = lookup_table_from_RGB_colourmap(colourMap)
    else:
        lut = self._colourmap_lut

    # Create the actor.
    colourBarActor = vtk.vtkScalarBarActor()
    colourBarActor.SetLookupTable(lut)
    colourBarActor.SetNumberOfLabels(numLabels)
    colourBarActor.SetMaximumNumberOfColors(resolution)
    if title is not None:
        colourBarActor.SetTitle(title)

    # Change label and title properties.
    propertyObjs = [colourBarActor.GetLabelTextProperty(),
                    colourBarActor.GetTitleTextProperty()]
    propertyDicts = [labelProps, titleProps]

    for zI in range(2):
        for key, value in propertyDicts[zI]:
            if key == "bold":
                propertyObjs[zI].SetBold(value)
            elif key == "font":
                propertyObjs[zI].SetFontFamilyAsString(value)
            elif key == "italic":
                propertyObjs[zI].SetItalic(value)
            elif key == "justification":
                if value == "left":
                    propertyObjs[zI].SetJustification(0)
                elif value == "centre":
                    propertyObjs[zI].SetJustification(1)
                elif value == "right":
                    propertyObjs[zI].SetJustification(2)
                else:
                    errorMsg = ("Invalid justification value {} specified."
                                .format(value))
                    raise ValueError(errorMsg)
            elif key == "shadow":
                propertyObjs[zI].SetShadow(value)
            elif key == "size":
                propertyObjs[zI].SetFontSize(value)
            else:
                errorMsg = ("Invalid label or title property {} specified."
                            .format(key))
                raise ValueError(errorMsg)

    # Connect internal stuff together.
    terminus = Terminus(colourBarActor, variety="ColourBar")
    self.track_object(terminus, sensibleName)
    return sensibleName


def act_cone_vector_field(self, coneLength, coneRadius, coneResolution,
                          colourMap="PuOr", coneCentre="base", maskDomain=None,
                          maskResolution=None, maskType=None,
                          uniformLength=True, vectorsName=None):
    """
    Define a vtkActor that draws a vector field of cones representing the data.

    Mathematically speaking, pyramids are used (which are a type of cone) to do
    this because the base of the cone is never a perfect circle.

    Arguments:

      - coneLength: Float denoting the length of the cone.

      - coneRadius: Float denoting the distance between one vertex of the base
          polygon from the centre of the base polygon.

      - coneResolution: Integer denoting the number of sides to use in the base
          of the cone.

      - colourMap: LinearSegmentedColormap object from matplotlib to create a
          vtkLookupTable with, or the name of an attribute from matplotlib.cm
          as a string, or None. If None, the _colourmap_lut attribute of the
          visualisation object is used.

      - coneCentre: Three element list of floats defining how to position the
          cones locally. If "base", centre cones at their base. Changing this
          is great if your cones look misaligned with each other.

      - maskDomain: Nine element list that defines a rectangle in
          three-dimensional space. The input data represents three adjacent
          corners as follows:
            > 0-2: Co-ordinates describing point P1 in the three dimensions
                (x, y, z).
            > 3-5: As above for one corner P2 which is adjacent to P1.
            > 6-8: As above for the other corner P3 which is adjacent to P1.
          Alternatively, the user can pass a twelve element list defining a
          cuboid if such a mask is needed. The final data are:
            > 9-11: As above for the other corner P4 which is adjacent to P1.

      - maskResolution: Two or three element list of integers denoting the
           number of points in each direction of the plane. If "maskType" is
           "volume", three elements are required. If "maskType" is "plane", two
           elements are required.

      - maskType: String denoting the type of masking to do. Either "plane",
          "volume", or None.

      # A note on the above three masking variables: There are nine different
      # masking behaviours the user may wish to consider. They are summarised
      # by the table in the documentation of mask.create_mask_from_opts.

      - uniformLength: Boolean determining whether or not to make all cones the
          same length.

      - vectorsName: String or None denoting the name to give to the vector
          field object. This should not clash with an existing name. If this is
          None, a sensible name is chosen. If there is a clash, the name is
          changed (and returned).

    Returns the name of the conical vector field actor object.
    """
    # Come up with a name for the object.
    sensibleName = vectorsName if vectorsName is not None else "cones"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Create the lookup table for this colourbar if a different map is
    # required.
    if colourMap is not None:
        lut = lookup_table_from_RGB_colourmap(colourMap)
    else:
        lut = self._colourmap_lut

    # Create the mask (resampling) filter if desired.
    if maskDomain is None and maskResolution is None and maskType is None:
        masking = False
    else:
        masking = True
        glyphSize = (coneLength if coneLength > 2 * coneRadius else
                     coneRadius * 2)
        maskFilter = mask.create_mask_from_opts(self._boundingBox, glyphSize,
                                                maskDomain=maskDomain,
                                                maskResolution=maskResolution,
                                                maskType=maskType)

    # Define vector glyphs.
    cones = vtk.vtkConeSource()
    cones.SetRadius(coneRadius)
    cones.SetHeight(coneLength)
    cones.SetResolution(coneResolution)

    if coneCentre == "base":
        cones.SetCenter(coneLength / 3., 0., 0.)
    else:
        cones.SetCenter(*coneCentre)

    # Create the mapper for the vectors.
    vectorMapper = vtk.vtkGlyph3DMapper()
    vectorMapper.SetLookupTable(lut)
    vectorMapper.SetUseLookupTableScalarRange(True)

    if uniformLength is True:
        vectorMapper.SetScaleModeToNoDataScaling()
    elif uniformLength is False:
        vectorMapper.SetScaleModeToScaleByMagnitude()

    # Create the actor for the vectors.
    vectorActor = vtk.vtkActor()

    # Connect internal stuff together.
    vectorMapper.SetSourceConnection(cones.GetOutputPort())
    vectorActor.SetMapper(vectorMapper)

    if masking is True:
        vectorMapper.SetInputConnection(maskFilter.GetOutputPort())
        terminus = Terminus(vectorActor, variety="cone_field",
                            vtkEndObject=maskFilter)

        # Secretly, maskFilter has two input ports; one for the input and one
        # for the source. Hence, we need to be specific here...
        terminus.default_input_port = 1
    else:
        terminus = Terminus(vectorActor, variety="cone_field",
                            vtkEndObject=vectorMapper)

    self.track_object(terminus, sensibleName)
    return sensibleName


def act_nasty_vector_field(self, arrowLength, arrowColour=[0., 0., 0.],
                           maskDomain=None, maskResolution=None, maskType=None,
                           uniformLength=True, vectorsName=None):
    """
    Define a vtkActor that draws a vector field of nasty arrows representing
    the data.

    Arguments:

      - arrowLength: Float denoting the length of the nasty arrow vectors.

      - arrowColour: Three element list of floats between 0 and 1 that define
          the colour of the arrows in RGB format.

      - maskDomain: Nine element list that defines a rectangle in
          three-dimensional space. The input data represents three adjacent
          corners as follows:
            > 0-2: Co-ordinates describing point P1 in the three dimensions
                (x, y, z).
            > 3-5: As above for one corner P2 which is adjacent to P1.
            > 6-8: As above for the other corner P3 which is adjacent to P1.
          Alternatively, the user can pass a twelve element list defining a
          cuboid if such a mask is needed. The final data are:
            > 9-11: As above for the other corner P4 which is adjacent to P1.

      - maskResolution: Two or three element list of integers denoting the
           number of points in each direction of the plane. If "maskType" is
           "volume", three elements are required. If "maskType" is "plane", two
           elements are required.

      - maskType: String denoting the type of masking to do. Either "plane",
          "volume", or None.

      # A note on the above three masking variables: There are nine different
      # masking behaviours the user may wish to consider. They are summarised
      # by the table in the documentation of mask.create_mask_from_opts.

      - uniformLength: Boolean determining whether or not to make all arrows
          the same length.

      - vectorsName: String or None denoting the name to give to the vector
          field object. This should not clash with an existing name. If this is
          None, a sensible name is chosen. If there is a clash, the name is
          changed (and returned).

    Returns the name of the nasty vector field actor object.
    """
    # Come up with a name for the object.
    sensibleName = vectorsName if vectorsName is not None else "nasty_arrows"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Create the mask (resampling) filter if desired.
    if maskDomain is None and maskResolution is None and maskType is None:
        masking = False
    else:
        masking = True
        maskFilter = mask.create_mask_from_opts(self._boundingBox, arrowLength,
                                                maskDomain=maskDomain,
                                                maskResolution=maskResolution,
                                                maskType=maskType)

    # Create the nasty arrow polydata.
    arrowPolyData = nasty_arrow_polydata(arrowLength, arrowLength / 2.,
                                         arrowLength / 16.)

    # Create the mapper for the vectors.
    vectorMapper = vtk.vtkGlyph3DMapper()
    vectorMapper.SetScalarVisibility(False)
    if uniformLength is True:
        vectorMapper.SetScaleModeToNoDataScaling()
    elif uniformLength is False:
        vectorMapper.SetScaleModeToScaleByMagnitude()

    # Create the actor for the vectors.
    vectorActor = vtk.vtkActor()
    vectorActor.GetProperty().SetColor(arrowColour)

    # Connect internal stuff together.
    vectorActor.SetMapper(vectorMapper)

    if helpers.vtk_base_version() < 6:
        vectorMapper.SetSource(arrowPolyData)
    else:
        vectorMapper.SetSourceData(arrowPolyData)

    if masking is True:
        vectorMapper.SetInputConnection(maskFilter.GetOutputPort())
        terminus = Terminus(vectorActor, variety="nasty_vector_field",
                            vtkEndObject=maskFilter)

        # Secretly, maskFilter has two input ports; one for the input and one
        # for the source. Hence, we need to be specific here...
        terminus.default_input_port = 1
    else:
        terminus = Terminus(vectorActor, variety="nasty_vector_field",
                            vtkEndObject=vectorMapper)

    self.track_object(terminus, sensibleName)
    return sensibleName


def act_surface(self, colourMap="PuOr", opacity=1., position=[0., 0., 0.],
                surfaceName=None, wireframe=False):
    """
    Define a vtkActor that draws a surface of the data. For three-dimensional
    data, a surface around the volume is drawn instead.

    Arguments:

      - colourMap: LinearSegmentedColormap object from matplotlib to create a
          vtkLookupTable with, or the name of an attribute from matplotlib.cm
          as a string, or None. If None, the _colourmap_lut attribute of the
          visualisation object is used.

      - opacity: Floating point value between one and zero denoting the
          translucency of the surface, where one is an opaque surface and zero
          is a transparent surface.

      - position: Three element array of floats to displace the surface.

      - surfaceName: String or None denoting the name to give to the surface
          object. This should not clash with an existing name. If this is None,
          a sensible name is chosen. If there is a clash, the name is changed
          (and returned).

      - wireframe: Boolean denoting whether or not to draw the surface as a
          wireframe.

    Returns the name of the surface actor object.
    """
    # Come up with a name for the object.
    sensibleName = surfaceName if surfaceName is not None else "surface"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Create the lookup table for this colourbar if a different map is
    # required.
    if colourMap is not None:
        lut = lookup_table_from_RGB_colourmap(colourMap)
    else:
        lut = self._colourmap_lut

    # Create the mapper for the surface.
    surfaceMapper = vtk.vtkDataSetMapper()
    surfaceMapper.SetUseLookupTableScalarRange(True)

    # Create the actor for the surface.
    surfaceActor = vtk.vtkActor()
    surfaceActor.SetPosition(*position)
    surfaceActor.GetProperty().SetOpacity(opacity)
    if wireframe is True:  # We don't do point representations here!
        surfaceActor.GetProperty().SetRepresentationToWireframe()
    else:
        surfaceActor.GetProperty().SetRepresentationToSurface()

    # Connect internal stuff together.
    surfaceMapper.SetLookupTable(lut)
    surfaceActor.SetMapper(surfaceMapper)

    terminus = Terminus(surfaceActor, variety="surface",
                        vtkEndObject=surfaceMapper)
    self.track_object(terminus, sensibleName)
    return sensibleName


def lookup_table_from_RGB_colourmap(colourMap, scalarRange=[-1., 1.],
                                    tableSize=1024):
    """
    Create a vtkLookupTable object from the matplotlib LinearSegmentedColormap
    object "colourmap", which can be used to manage colours in VTK renders. The
    resulting lookup table can be used to colour scalar fields and vector
    fields.

    Arguments:

      - colourMap: LinearSegmentedColormap object from matplotlib to create a
          vtkLookupTable with, or the name of an attribute from matplotlib.cm
          as a string.

      - scalarRange: Two element list of floats denoting minimum and maximum
          values for the colourmap to plot.

      - tableSize: Resolution of the resulting lookup table.

    Returns the resulting vtkLookupTable object.
    """

    if type(colourMap) is str:
        colourMap = getattr(matplotlib.cm, colourMap)

    # Create the colour function from the input colourmap. This colour function
    # defines the colours for the lookup table, which in turn are used for
    # plotting.
    segments = colourMap._segmentdata
    ctf = vtk.vtkColorTransferFunction()
    for zI in xrange(len(segments['blue'])):

        # Segment data is a dictionary with three values corresponding to
        # "red", "green", and "blue". These values are arrays of tuples, where
        # the tuples contain the co-ordinate between zero and one, and the
        # value of the colour at that point. We exploit this scheme here.

        # Could be any colour really, but I like red.
        point = segments['red'][zI][0]
        ctf.AddRGBPoint(point, segments['red'][zI][1],
                        segments['green'][zI][1], segments['blue'][zI][1])

    # Define the lookup table.
    lutOutput = vtk.vtkLookupTable()
    lutOutput.SetNumberOfTableValues(tableSize)
    lutOutput.SetRange(*scalarRange)

    lutOutput.Build()
    for zI in range(0, tableSize):
        rgb = list(ctf.GetColor(float(zI) / tableSize)) + [1]
        lutOutput.SetTableValue(zI, rgb)

    return lutOutput


def nasty_arrow_polydata(length, width, thickness):
    """
    Create polydata representing a 3D arrow that looks like this:


                             length
                      |-------------------|

                                  +--+       -
                                 / \  \      |
                                +   \  \     |
                      +--------------+  \    |w
                     /|           \ /    \   |i
                  - +--------------+      +  |d
                  | |O|                  /   |t
        thickness | | +--------------+  /    |h
                  | |/              /  /     |
                  - +--------------/  /      |
                                  +--+       -
                      y          /  /
                     /|\        +--+   \
                      |               /thickness
                      O-->x          \
                     /
                   |/
                   z-


    or as a bird's eye view:

                                 +--+       -
                                  \  \      |
                                   \  \     |
                   - +--------------+  \    |w
                   | |                  \   |i
         thickness | |                   +  |d
                   | |                  /   |t
                   - +--------------+  /    |h
                                   /  /     |
                                  /  /      |
                                 +--+       -

                     |------------------|
                            length

    The origin of the arrow (O) is at the centre of the shaft pointing in the
    positive x-direction. Polydata in this case is a series of points, and the
    connectivity between these points used to form cells.

    Arguments:

      - length: Floating point number denoting the length of the arrow, from
          base to top.

      - width: Floating point number denoting the width of the tip of the
          arrow.

      - thickness: Floating point number denoting the thickness of the shaft
          and tip. Would recommend this to be pretty small compared to the
          length and width.

    Returns a vtkPolyData object representing the arrow.
    """
    # Checking inputs.
    if length <= 0:
        raise ValueError("Non-positive length '{}' passed to "
                         "nasty_arrow_polydata.".format(length))
    if width <= 0:
        raise ValueError("Non-positive width '{}' passed to "
                         "nasty_arrow_polydata.".format(width))
    if thickness <= 0:
        raise ValueError("Non-positive thickness '{}' passed to "
                         "nasty_arrow_polydata.".format(thickness))

    # Some shorthand for readability.
    lHf = length / 2.
    wHf = width / 2.
    zHf = thickness / 2.

    # Some diagonal lengths using Pythagoras.
    x = (0.5 * thickness ** 2) ** 0.5
    y = (3.0 * thickness ** 2) ** 0.5

    # Define arrow shape.
    points = np.ndarray([18, 3])

    # Positive width and thickness coordinates.
    points[0] = -lHf, zHf, zHf
    points[1] = lHf - y, zHf, zHf
    points[2] = lHf - wHf - x, wHf - x, zHf
    points[3] = lHf - wHf, wHf, zHf

    # Pointy bit.
    points[4] = lHf, 0., zHf

    # Abusing symmetry to calculate negative width coordinates.
    for zI in xrange(4):
        cloneIx = 3 - zI
        points[zI + 5] = [points[cloneIx, 0], -points[cloneIx, 1],
                          points[cloneIx, 2]]

    # Abusing symmetry to calculate negative depth coordinates.
    for zI in xrange(9):
        points[9 + zI] = points[zI, 0], points[zI, 1], -points[zI, 2]

    # Create a vtkPoints object to use with polydata, and populate it.
    arrowPoints = vtk.vtkPoints()
    for point in points:
        arrowPoints.InsertNextPoint(*point)

    # Define cells representing faces of the arrow.
    arrowCells = vtk.vtkCellArray()

    # Upper face.
    upperCellIndices = [[0, 1, 7, 8],
                        [1, 2, 3, 4],
                        [4, 5, 6, 7],
                        [1, 4, 7]]

    for cellData in upperCellIndices:
        arrowCells.InsertNextCell(len(cellData))
        for cellIndex in cellData:
            arrowCells.InsertCellPoint(cellIndex)

    # Lower face.
    lowerCellIndices = [[9, 10, 16, 17],
                        [10, 11, 12, 13],
                        [13, 14, 15, 16],
                        [10, 13, 16]]

    for cellData in lowerCellIndices:
        arrowCells.InsertNextCell(len(cellData))
        for cellIndex in cellData:
            arrowCells.InsertCellPoint(cellIndex)

    # Middle faces.
    middleCellIndices = [[0, 1, 9, 10],
                         [1, 2, 11, 10],
                         [2, 3, 12, 11],
                         [3, 4, 13, 12],
                         [4, 5, 14, 13],
                         [5, 6, 15, 14],
                         [6, 7, 16, 15],
                         [7, 8, 17, 16],
                         [8, 0, 9, 17]]

    for cellData in middleCellIndices:
        arrowCells.InsertNextCell(len(cellData))
        for cellIndex in cellData:
            arrowCells.InsertCellPoint(cellIndex)

    # Create polydata representing the glyph.
    arrowPolyData = vtk.vtkPolyData()
    arrowPolyData.SetPoints(arrowPoints)
    arrowPolyData.SetPolys(arrowCells)

    if helpers.vtk_base_version() < 6:
        arrowPolyData.Update()

    return arrowPolyData
