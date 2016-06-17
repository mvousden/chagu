#!/usr/bin/env python2

# This script demonstrates isosurfaces, and how they're often not the best idea
# :p.

import chagu


vis = chagu.Visualisation(filePath="data/data.vtu")

# Create a z-component isosurface/streamsurface
comp1 = vis.extract_vector_components(component=2)
cont1 = vis.contour([-0.9, -.5, 0, 0.5, 0.9])
surf1 = vis.act_surface()

# Create a y-component isosurface/streamsurface
comp2 = vis.extract_vector_components(component=1)
cont2 = vis.contour([-0.9, -.5, 0, 0.5, 0.9])
surf2 = vis.act_surface(colourMap="RdBu")

# Create an x-component isosurface/streamsurface
comp3 = vis.extract_vector_components(component=0)
cont3 = vis.contour([-0.9, -.5, 0, 0.5, 0.9])
surf3 = vis.act_surface(colourMap="BrBG")

pipeline = [["reader", comp1],
            [comp1, cont1],
            [cont1, surf1],
            ["reader", comp2],
            [comp2, cont2],
            [cont2, surf2],
            ["reader", comp3],
            [comp3, cont3],
            [cont3, surf3]]
vis.build_pipeline_from_dict(pipeline)
vis.visualise_interact()
