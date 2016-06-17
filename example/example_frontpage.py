#!/usr/bin/env python2

# This script creates the visualisation on the frontpage of our GitHub
# repository. It showcases slices, surfaces, cones, and isosurfaces. Oh my!

import chagu
import os


# Parameters from our data file. These can be read using VTK, but I include
# them like this for clarity.
xMax = 50
yMax = 50
zMax = 50

# I'd like to think that this doesn't need commenting, since the objective of
# Chagu is that it should be apparent what's going on with a little bit of
# understanding. Let me know if anything here is not clear!
vis = chagu.Visualisation()
readerName = vis.load_visualisation_toolkit_file("data/data3.vtu")
vis.camera = {"position": [75., 115., 45],
              "view up": [0., 0., 1.],
              "focal point": [0., 0., -7.]}
compName = vis.extract_vector_components(component=2)
surfName = vis.act_surface(opacity=0.2)

contourName = vis.contour(-0.3)
isoSurfaceName = vis.act_surface(opacity=0.5)

slices = []
cones = []

slices.append(vis.slice_data_with_plane(origin=[0, 0, zMax / 2.]))
cones.append(vis.act_cone_vector_field(1, .45, 25))
slices.append(vis.slice_data_with_plane(origin=[0, 0, 0.01 - zMax / 2.]))
cones.append(vis.act_cone_vector_field(1, .45, 25))
slices.append(vis.slice_data_with_plane(origin=[0, 0, 0]))
cones.append(vis.act_cone_vector_field(2., 1., 50,
                                       maskResolution=[20, 20, 1],
                                       maskType="volume"))

# So this bit might be confusing, but basically visualisation objects maintain
# an internal set of objects. This set of objects is connected by a
# pipeline. For simple visualisations (like example_tiny), Chagu can guess this
# pipeline itself. For more elaborate constructions however, we need to specify
# it ourselves.
pipeline = [[readerName, compName]] +\
           [[compName, surfName]] +\
           [[compName, contourName]] +\
           [[contourName, isoSurfaceName]] +\
           [[compName, slices[zI]] for zI in range(3)] +\
           [[slices[zI], cones[zI]] for zI in range(3)]

vis.build_pipeline_from_dict(pipeline)
if os.path.exists("output") is False:
    os.mkdir("output")
vis.visualise_save("output/out.png")
vis.visualise_interact()
