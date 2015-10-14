# This source file contains general helper functions that are not associated
# with the visualisation class specifically, and so have been abstracted.

import vtk


def generate_sensible_name(guessName, testFunction):
    """
    Generate a sensible name given a guess. testFunction says whether or not
    a given name is invalid, and this is used to generate a sensible name.

    Arguments:

      - guessName: String denoting the name to generate.

      - testFunction: Function that returns either True or False given
          guessName as a solitary argument. If True is returned, the name is
          deemed as not sensible.

    Returns a sensible name.
    """

    # If the guess is sensible, return it right away. Otherwise we have some
    # work to do...
    if testFunction(guessName) is False:
        sensibleName = guessName

    # Try guessName_0, guessName_1 etc. and find the first one that works.
    else:
        zI = 0
        nameIsInvalid = True
        while nameIsInvalid is True:
            sensibleName = "{}_{}".format(guessName, zI)
            if testFunction(sensibleName) is True:
                zI += 1
            else:
                nameIsInvalid = False

    return sensibleName


def vtk_base_version():
    """
    Returns the base version number of VTK being used, as an integer.
    """

    return int(vtk.vtkVersion().GetVTKVersion().split(".")[0])
