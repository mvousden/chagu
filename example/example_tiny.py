# This script shows that a respectable visualisation can be created in only a
# few lines.

import chagu


vis = chagu.Visualisation(filePath="data/data.vtu")
vis.extract_vector_components(component=2)
vis.act_cone_vector_field(1, .5, 20, maskType="plane")
vis.act_surface(opacity=0.5)
vis.visualise_interact()
