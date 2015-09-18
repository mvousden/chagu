# This source file defines tracking methods for the visualisation object to
# keep a record of VTK objects it is looking after.

import vtk


def get_vtk_object(self, objectName):
    """
    Return the VTK object with a given name. Useful for users wishing to modify
    objects themselves with the VTK interface.

    Arguments:

      - objectName: String denoting the name of the object to get.

    Returns the VTK object.
    """
    return self._vtkObjects[objectName]


def is_nasty(self, vtkObjectName):
    """
    Returns True if the object is tracked and is nasty, and False otherwise.
    """
    if self.is_tracked(vtkObjectName):
        if self.get_vtk_object(vtkObjectName).variety == "nasty_vector_field":
            return True
    return False


def is_reader(self, vtkObjectName):
    """
    Returns True if the object is tracked and is a reader, and False otherwise.
    """
    if self.is_tracked(vtkObjectName):
        if (isinstance(self.get_vtk_object(vtkObjectName), vtk.vtkXMLReader) or
            isinstance(self.get_vtk_object(vtkObjectName), vtk.vtkDataReader))\
            is True:
            return True
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


def track_vtk_object(self, vtkObject, objectName, asTerminus=False):
    """
    Add a VTK object to the objects tracked by this visualisation. Objects
    tracked in this way can be used in the pipeline. User should call
    'act_' functions to create VTK objects if their desired object is
    supported, but this method is here for people whos objects are not
    supported currently, and for internal use.

    Arguments:

      - vtkObject: The instance of the VTK object to track.

      - objectName: String denoting the name to assign the object in this
          visualisation.

      - asTerminus: Boolean denoting whether or not to track this object as a
          terminus as well as a VTK Object. This is only for Terminus objects.

    Returns nothing.
    """
    self._order.append(objectName)
    if asTerminus is True:
        self._vtkObjects[objectName] = vtkObject
        self._vtkTermini[objectName] = vtkObject
    else:
        self._vtkObjects[objectName] = vtkObject
