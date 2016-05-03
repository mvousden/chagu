# This script showcases the animate_rotate render method, which produces a
# stack of images showing a visualisation rotating about the Z-axis.

import chagu
import os


vis = chagu.Visualisation(filePath="data/data.vtu")
horiz = 1680
ratio = 3.0
vis.windowSize = [horiz, horiz * ratio]
vis.extract_vector_components(component=2)
vis.act_cone_vector_field(1, .5, 20, maskType="plane")
vis.act_surface(opacity=0.5)
if os.path.exists("output") is False:
    os.mkdir("output")
vis.visualise_animate_rotate("output/rot", offscreenRendering=True,
                             rotation_resolution=10)
