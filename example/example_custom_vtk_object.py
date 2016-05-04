#!/usr/bin/env python2

# This script shows how to add a VTK object that is not otherwise supported to
# Chagu.
#
# In this case, the data is plotted in cells as opposed to on points, which
# makes it incompatible with Chagu's cone plotting method. As such, a filter is
# needed which converts cell data to point data. Chagu gracefully handles the
# pipeline in this case.

import chagu
import vtk


##

print("First, we attempt to draw a slice of the vector field without any "
      "additional filter. Notice that the vectors are all parallel, which is "
      "not represented by the data.\n")
vis = chagu.Visualisation(filePath="data/data_ascii_space.vtk")
vis.extract_vector_components(component=2)
vis.act_cone_vector_field(0.5, 0.25, 15, maskType="plane")
vis.visualise_interact()

##

print("Now we try to add an additional filter from VTK. The vectors orient "
      "and are coloured correctly.\n")
vis = chagu.Visualisation(filePath="data/data_ascii_space.vtk")

# Here's the magic.
vis.track_object(vtk.vtkCellDataToPointData(), "Cell to point data filter")

vis.extract_vector_components(component=2)
vis.act_cone_vector_field(0.5, 0.25, 15, maskType="plane")
vis.visualise_interact()

print("Note that Chagu handles the pipeline intelligently, and uses the name "
      "gave to the object. Here is the pipeline:")
print(vis._pipeline)
