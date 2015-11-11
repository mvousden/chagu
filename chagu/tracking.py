# This source file defines tracking methods for the visualisation object to
# keep a record of VTK objects it is looking after.

import termini
import vtk


def get_vtk_object(self, objectName):
    """
    Return the VTK object with a given name. Useful for users wishing to modify
    objects themselves with the VTK interface.

    Arguments:

      - objectName: String denoting the name of the object to get.

    Returns the VTK object.
    """

    if self.is_tracked(objectName) is False:
        raise ValueError("Object name \"{}\" is not tracked by visualisation "
                         "object \"{}\".".format(objectName, self))
    return self._vtkObjects[objectName]


def is_nasty(self, objectName):
    """
    Returns True if the object is tracked and is nasty, and False otherwise.
    """

    if self.is_tracked(objectName):
        if hasattr(self.get_vtk_object(objectName), "variety") is True:
            variety = self.get_vtk_object(objectName).variety
            if variety == "nasty_vector_field":
                return True
    return False


def is_reader(self, objectName):
    """
    Returns True if the object is tracked and is a reader, and False otherwise.
    """

    if self.is_tracked(objectName):
        vtkObject = self.get_vtk_object(objectName)
        return isinstance(vtkObject, vtk.vtkXMLReader) or\
            isinstance(vtkObject, vtk.vtkDataReader)
    return False


def is_tracked(self, objectName):
    """
    Determine whether or not an object is tracked by this visualisation.

    Arguments:

      - objectName: String denoting the name of the object to identify.

    Returns True if the name is attached to an object is being tracked, and
    False otherwise.
    """

    return True if objectName in self._vtkObjects.keys() else False


def track_object(self, objectToTrack, objectName):
    """
    Add an object to the objects tracked by this visualisation.

    Objects tracked in this way can be used in the pipeline. User should call
    functions defined in termini.py and filters.py to create VTK objects if
    their desired object is supported. This method is for users whos objects
    are not yet supported, and for internal use. Non-terminus objects tracked
    in this way must have pipeline methods defined. The handles for these
    methods are listed in requiredAllMethodHandles and requiredVTKMethodHandles
    below.

    Arguments:

      - objectToTrack: The object (VTK or otherwise) to track.

      - objectName: String denoting the name to assign the object in this
          visualisation.

    Returns nothing.
    """

    # Define the method handles required by objects.
    requiredMethodHandles = ["Update", "SetInputConnection",
                             "GetNumberOfInputPorts", "GetNumberOfOutputPorts",
                             "GetOutputPort"]

    # Check that the object has these methods if it is not a Terminus, and that
    # they are callable.
    isTerminus = isinstance(objectToTrack, termini.Terminus)
    if isTerminus is False:
        for methodHandle in requiredMethodHandles:
            if hasattr(objectToTrack, methodHandle) is True:
                method = getattr(objectToTrack, methodHandle)
                if hasattr(method, "__call__") is False:
                    raise ValueError("Member \"{}\" of object \"{}\" must be "
                                     "callable."
                                     .format(methodHandle, objectName))
            else:
                raise ValueError("Object \"{}\" has no method \"{}\", which "
                                 "is required for the pipeline."
                                 .format(objectName, methodHandle))

    # All pipeline methods are defined, so we track the object.
    self._order.append(objectName)
    if isTerminus is True:
        self._vtkObjects[objectName] = objectToTrack
        self._vtkTermini[objectName] = objectToTrack
    else:
        self._vtkObjects[objectName] = objectToTrack
