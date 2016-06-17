#!/usr/bin/env python2

# This script demonstrates the functionality of the autopipe by drawing nasty
# vectors.

import chagu


vis = chagu.Visualisation(name="autopipe_example_2", filePath="data/data.vtu")
sliceName = vis.slice_data_with_plane()
compName = vis.extract_vector_components(component=2)

arrowLength = 1.0
nastyName = vis.act_nasty_vector_field(arrowLength, maskType="plane")
surfaceName = vis.act_surface(position=[0., 0., -arrowLength / 2.],
                              wireframe=True)
cmapName = vis.act_colourbar()

vis.visualise_interact()
vis.draw_pipeline_graphviz(directory="output")
