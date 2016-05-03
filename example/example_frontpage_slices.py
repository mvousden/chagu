# This script creates the visualisation on the frontpage of our GitHub
# repository. It showcases slices.

import chagu
import os


xMax = 50
yMax = 50
zMax = 50

vis = chagu.Visualisation()
readerName = vis.load_visualisation_toolkit_file("data/data3.vtu")
vis.camera = {"position": [75., 115., 55],
              "view up": [0., 0., 1.],
              "focal point": [0., 0., -7.]}
compName = vis.extract_vector_components(component=2)
surfName = vis.act_surface(opacity=0.5)
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

pipeline = [[readerName, compName]] +\
           [[compName, surfName]] +\
           [[compName, slices[zI]] for zI in range(3)] +\
           [[slices[zI], cones[zI]] for zI in range(3)]

vis.build_pipeline_from_dict(pipeline)
if os.path.exists("output") is False:
    os.mkdir("output")
vis.visualise_save("output/out.png")
vis.visualise_interact()
