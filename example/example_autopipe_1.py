# This script demonstrates the functionality of the autopipe by drawing pretty
# cones.

import chagu
import os


vis = chagu.Visualisation(name="autopipe_example_1", filePath="data/data.vtu")
compName = vis.extract_vector_components(component=2)

coneLength = 1.0
coneRes = 20
maskType = "volume"
conesName = vis.act_cone_vector_field(coneLength, coneLength / 2., coneRes,
                                      maskType=maskType)
surfaceName = vis.act_surface(opacity=0.5)
cmapName = vis.act_colourbar()

vis.visualise_interact()
if os.path.exists("output") is False:
    os.mkdir("output")
vis.visualise_save("output/out.png")
vis.draw_pipeline_graphviz(directory="output")

