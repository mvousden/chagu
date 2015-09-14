# This source file defines functions that load VTK data sources. These sources
# are at the starting terminus of the pipeline, as one might expect.

import vtk

import helpers


def load_visualisation_toolkit_file(self, filePath, readerName=None):
    """
    Create a vtkXMLDataReader object that loads the file "filePath". The type
    of object created depends on the extension of "filePath".

    Arguments:

      - filePath: String containing the path to the file to read.

      - readerName: String or None denoting the name to give to the reader
          object. This should not clash with an existing name. If this is None,
          a sensible name is chosen. If there is a clash, the name is changed
          (and returned).

    Returns the name of the filereader object.
    """
    # Come up with a name for the object.
    sensibleName = readerName if readerName is not None else "reader"
    sensibleName = helpers.generate_sensible_name(sensibleName,
                                                  self.is_tracked)

    # Get the extension.
    extension = filePath.split(".")[-1]

    # VTK is a special case, since they can be of many different types. We use
    # a different reader type for this.
    errorMsg = ("I don't know what to do with data set type {}. Please "
                "consider modifying my code to include this type :(.")
    if extension == "vtk":
        with open(filePath, "r") as dataFile:
            for line in dataFile.readlines():
                if line.split()[0] == "DATASET":
                    dataSetType = line.split()[1]
                    if dataSetType not in validBinaryDataTypes.keys():
                        raise NotImplementedError(errorMsg.format(dataSetType))
                    vtReader = validBinaryDataTypes[dataSetType]()
                    break

    # Complain if we don't recognise the extension.
    elif extension not in validExtensions.keys():
        errorMsg = ("The extension of the input file, {}, is not supported. "
                    "Instead, consider one of {}."
                    .format(extension, validExtensions.keys()))
        raise ValueError(errorMsg)

    # If we do recognise the extension, create an instance of the class for
    # this extension and track it.
    else:
        vtReader = validExtensions[extension]()

    vtReader.SetFileName(filePath)
    vtReader.Update()

    self.track_vtk_object(vtReader, sensibleName)

    # Get some bounding box data for later. If we have already loaded some
    # data, keep the most extreme.
    thisBoundingBox = vtReader.GetOutputDataObject(0).GetBounds()
    for zI in xrange(3):
        self._boundingBox[zI * 2] = min(self._boundingBox[zI * 2],
                                        thisBoundingBox[zI * 2])
        self._boundingBox[zI * 2 + 1] = max(self._boundingBox[zI * 2 + 1],
                                            thisBoundingBox[zI * 2 + 1])

    return sensibleName


# Define valid extensions for load_visualisation_toolkit_file to
# support. Each extension is mapped to a class, so that an instance can
# be created in the aforementioned function.
validExtensions = {"vti": vtk.vtkXMLImageDataReader,
                   "vtp": vtk.vtkXMLPolyDataReader,
                   "vtr": vtk.vtkXMLRectilinearGridReader,
                   "vts": vtk.vtkXMLStructuredGridReader,
                   "vtu": vtk.vtkXMLUnstructuredGridReader}
validBinaryDataTypes = {"STRUCTURED_GRID": vtk.vtkStructuredGridReader}
