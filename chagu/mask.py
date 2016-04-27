# This source file deals with masking functions for termini, specifically
# vector-like termini. It contains functions used to create good masks for
# vector data.

import numpy as np
import vtk


def create_mask_from_opts(boundingBox, glyphSize, maskDomain=None,
                          maskResolution=None, maskType=None):
    """
    Create a mask from a set of parameters, trying to figure out what the user
    wants from incomplete information. The mask is a vtkProbeFilter positioned
    with a vtkPlaneSource.

    There are eight expected behaviours this function takes care of:
      1) Create a plane mask over the entire dataset with unknown resolution.
      2) Create a volume mask over the entire dataset with unknown resolution.
      3) Create a plane mask over a subdomain with unknown resolution.
      4) Create a volume mask over a subdomain with unknown resolution.
      5) Create a plane mask over the entire dataset with known resolution.
      6) Create a volume mask over the entire dataset with known resolution.
      7) Create a plane mask over a subdomain with known resolution.
      8) Create a volume mask over a subdomain with known resolution.

    For these behaviors, required input arguments are summarised in this table:

    +--------+----------+--------------+----------------+
    |Behavior|maskDomain|maskResolution|    maskType    |
    +--------+----------+--------------+----------------+
    |   1)   |   None   |     None     |     "plane"    |
    |   2)   |   None   |     None     |    "volume"    |
    |   3)   |    3x3   |     None     |"plane" or None |
    |   4)   |    4x3   |     None     |"volume" or None|
    |   5)   |   None   |      2       |"plane" or None |
    |   6)   |   None   |      3       |"volume" or None|
    |   7)   |    4x3   |      2       |"plane" or None |
    |   8)   |    4x3   |      3       |"volume" or None|
    +--------+----------+--------------+----------------+

    Arguments:

      - boundingBox: Six element list denoting minimum and maximum co-ordinates
          for each dimension in this order: xMin, xMax, yMin, yMax, zMin, zMax.

      - glyphSize: Floating point value denoting the size of the vector glyph.
          This is used to determine resolution if a value is not passed as an
          argument.

      - maskDomain: Either twelve or nine element list defining a cuboid or
          rectangle in three-dimensional space (or None). The input data
          represents three (or four) adjacent corners as follows:
            > 0-2: Co-ordinates describing point P1 in the three dimensions
                (x, y, z).
            > 3-5: As above for one corner P2 which is adjacent to P1.
            > 6-8: As above for the other corner P3 which is adjacent to P1.
          For a cuboid, the final data is:
            > 9-11: As above for the other corner P4 which is adjacent to P1.

      - maskResolution: Two or three element list of integers denoting the
           number of points in each direction of a rectangle or cuboid
           respectively (or None).

      - maskType: String denoting the type of masking to do. Can be either
           "plane", "volume", or None.

    Returns a vtkProbeFilter that resamples data on the mask plane or volume.
    """
    # Check for inconsistent inputs.
    if maskType == "plane":
        if maskDomain is not None:
            if len(maskDomain) != 9:
                errorMsg = ("Invalid maskDomain length {} while creating the "
                            "the plane mask".format(len(maskDomain)))
                raise ValueError(errorMsg)
        if maskResolution is not None:
            if len(maskResolution) != 2:
                errorMsg = ("Invalid maskResolution length {} while creating "
                            "the plane mask.".format(len(maskResolution)))
                raise ValueError(errorMsg)

    elif maskType == "volume":
        if maskDomain is not None:
            if len(maskDomain) != 12:
                errorMsg = ("Invalid maskDomain length {} while creating the "
                            "the volume mask".format(len(maskDomain)))
                raise ValueError(errorMsg)
        if maskResolution is not None:
            if len(maskResolution) != 3:
                errorMsg = ("Invalid maskResolution length {} while creating "
                            "the volume mask.".format(len(maskResolution)))
                raise ValueError(errorMsg)

    elif type(maskType) == str:
        raise ValueError("Invalid maskType value \"{}\". Should be either \""
                         "plane\", \"volume\", or None.".format(maskType))

    else:
        if maskDomain is not None and maskResolution is not None:
            if (len(maskDomain) == 9 and len(maskResolution) == 2) or\
               (len(maskDomain) == 12 and len(maskResolution) == 3):
                errorMsg = ("Invalid combination for the lengths of "
                            "maskDomain and maskResolution: {}-{}. Must "
                            "be either 9-2 or 12-3."
                            .format(len(maskDomain), len(maskResolution)))
                raise ValueError(errorMsg)

        # Fill in the mask type since it has not been defined before.
        maskType = "plane" if len(maskDomain) == 9 else "volume"

    # We will need to know the geometry of the dataset if we have to guess
    # the domain or the resolution, so we find that now if appropriate. We
    # take a small amount from the edges to ensure the sampling is inside
    # the bounding box.
    if maskDomain is None or maskResolution is None:
        minX, maxX, minY, maxY, minZ, maxZ = boundingBox
        minX *= 1 - 1e-3
        maxX *= 1 - 1e-3
        minY *= 1 - 1e-3
        maxY *= 1 - 1e-3
        minZ *= 1 - 1e-3
        maxZ *= 1 - 1e-3

    # If we are masking but don't know our domain, just use the bounding box
    # data. If we are plane-masking, put the plane between the maximum and
    # minimum depth co-ordinate.
    if maskDomain is None:
        if maskType == "volume":
            domain = [minX, minY, minZ,
                      maxX, minY, minZ,
                      minX, maxY, minZ,
                      minX, minY, maxZ]
        elif maskType == "plane":
            plane_z = (maxZ + minZ) / 2.
            domain = [minX, minY, plane_z,
                      maxX, minY, plane_z,
                      minX, maxY, plane_z]
    else:
        domain = maskDomain

    # If we are masking but don't know our resolution, use glyphSize and the
    # bounding box to estimate a nice resolution. We use integer division
    # because resolution values must be integers.
    if maskResolution is None:
        resolution = [max((maxX - minX) // (glyphSize * 1.1), 1),
                      max((maxY - minY) // (glyphSize * 1.1), 1)]
        if maskType == "volume":
            resolution += [max((maxZ - minZ) // (glyphSize * 1.1), 1)]
    else:
        resolution = maskResolution

    # Now we can actually construct the mask filter.
    if maskType == "volume":
        return cube_mask(domain, resolution)
    else:
        return plane_mask(domain, resolution)


def plane_mask(domain, resolution):
    """
    Create a vtkProbeFilter that masks input data in a plane.

    Arguments:

      - domain: Nine element list that defines a rectangle in three-dimensional
          space. The input data represents three adjacent corners as follows:
            > 0-2: Co-ordinates describing point P1 in the three dimensions
                (x, y, z).
            > 3-5: As above for one corner P2 which is adjacent to P1.
            > 6-8: As above for the other corner P3 which is adjacent to P1.

      - resolution: Two element list of integers denoting the number of points
          in each direction of the plane.

    Returns a vtkProbeFilter that resamples data on the mask plane.
    """
    return cube_mask(domain + domain[0:3], resolution + [1])


def cube_mask(domain, resolution):
    """
    Create a vtkProbeFilter that masks input data in a cube-shape.

    We use a probe filter to mask the points instead of vtkMaskPoints, because
    it doesn't let the user to specify where the resulting points are supposed
    to be. To use that filter however, we need to define a volume polydata. To
    do that, we need to create multiple planes and stick them together.

    Arguments:

      - domain: Twelve element list that defines a cuboid. The input data
          represents four adjacent perpendicular corners as follows:
            > 0-2: Co-ordinates describing point P1 in the three dimensions
                (x, y, z).
            > 3-5: As above for one corner P2 which is adjacent to P1.
            > 6-8: As above for another corner P3 which is adjacent to P1.
            > 9-11: As above for the final corner P4 which is adjacent to P1.

      - resolution: Three element list of integers denoting the number of
          points in each direction of the volume.

    Returns a vtkProbeFilter that resamples data on the masking volume.
    """
    # Convert the points to numpy arrays so that adding them in intervals
    # becomes much easier.
    corners = np.array([domain[0:3], domain[3:6], domain[6:9], domain[9:]])

    # This is quite a complicated job. We create the first plane using the
    # first three corners. We then add a multiple of the co-ordinate of the
    # final corner to the others, until the volume is filled out. This is
    # acceptable because we assume that the input corners are perpendicular.
    maskVolume = vtk.vtkAppendPolyData()
    numberOfPlanes = resolution[-1]

    # Define the vector along which to propogate the planes.
    propVector = corners[3] - corners[0]

    # Define the multiples from the number of planes to draw.
    if numberOfPlanes == 1:
        multiples = np.array([0.5])
    else:
        multiples = np.linspace(0., 1., numberOfPlanes)

    # Iterate through each plane.
    for multiple in multiples:
        theseCorners = []

        # Add some multiple of the final corner to each corner.
        for zI in xrange(3):
            theseCorners += list(corners[zI] + multiple * propVector)

        # Create the plane and add it to the volume.
        thisPlane = quadrilateral_plane_source(theseCorners, resolution[:-1])
        maskVolume.AddInputConnection(thisPlane.GetOutputPort())

    # Phew!
    maskFilter = vtk.vtkProbeFilter()
    maskFilter.SetInputConnection(maskVolume.GetOutputPort())
    return maskFilter


def quadrilateral_plane_source(domain, resolution):
    """
    Create a quadrilateral vtkPlaneSource object from simple input.

    Arguments:

      - domain: Nine element list that defines a rectangle in three-dimensional
          space. The input data represents three adjacent corners as follows:
            > 0-2: Co-ordinates describing point P1 in the three dimensions
                (x, y, z).
            > 3-5: As above for one corner P2 which is adjacent to P1.
            > 6-8: As above for the other corner P3 which is adjacent to P1.

      - resolution: Two element list of integers denoting the number of points
          in each direction of the plane, in the order [P1->P2, P1->P3].

    Returns the vtkPlaneSource object describing the requested geometry.
    """

    # Check that the resolution integerises well.
    integerisedResolution = [int(zI) for zI in resolution]
    if (integerisedResolution[0] != resolution[0] or\
        integerisedResolution[1] != resolution[1]):
        raise TypeError("Non-integer resolution {} passed.".format(resolution))

    # Check that the resolution has no negative elements.
    if integerisedResolution[0] < 0 or integerisedResolution[1] < 0:
        raise ValueError("Negative resolution {} passed.".format(resolution))

    # Check that no points are duplicates.
    if (domain[0:3] == domain[3:6] or domain[0:3] == domain[6:] or\
        domain[3:6] == domain[6:]):
        raise ValueError("Points have an overlap: {}, {}, {}"
                         .format(domain[0:3], domain[3:6], domain[6:]))

    # Build the plane.
    maskPlane = vtk.vtkPlaneSource()
    maskPlane.SetOrigin(*domain[0:3])
    maskPlane.SetPoint1(*domain[3:6])
    maskPlane.SetPoint2(*domain[6:])
    maskPlane.SetResolution(*integerisedResolution)
    return maskPlane
