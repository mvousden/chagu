# This script showcases nasty vectors on a 2D surface.

import chagu
import os


vis = chagu.Visualisation(name="2d_nasty")
readerName = vis.load_visualisation_toolkit_file("data/data.vtu")
sliceName = vis.slice_data_with_plane()
compName = vis.extract_vector_components(component=2)

arrowLength = 1.0
nastyName = vis.act_nasty_vector_field(arrowLength, maskType="plane")
surfaceName = vis.act_surface(position=[0., 0., -arrowLength / 2.])
cmapName = vis.act_colourbar()

pipeline = [[readerName, sliceName],
            [sliceName, compName],
            [compName, surfaceName],
            [readerName, nastyName]]
vis.build_pipeline_from_dict(pipeline)

vis.visualise_interact()
if os.path.exists("output") is False:
    os.mkdir("output")
vis.draw_pipeline_graphviz(directory="output")
