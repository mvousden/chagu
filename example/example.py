# This is an example script demonstrating the elegance of the visualisation
# class I've just written.

import os
import sys
sys.path.append("../")  # Equivalent to adding the previous directory to the
                        # pythonpath.
import chagu


def example_tiny():
    vis = chagu.Visualisation(filePath="data/data.vtu")
    vis.extract_vector_components(component=2)
    vis.act_cone_vector_field(1, .5, 20, maskType="plane")
    vis.act_surface(opacity=0.5)
    vis.visualise_interact()


def example_autopipe_1():
    vis = chagu.Visualisation(name="autopipe_example_1",
                              filePath="data/data.vtu")
    compName = vis.extract_vector_components(component=2)

    coneLength = 1.0
    coneRes = 20
    maskType = "volume"
    conesName = vis.act_cone_vector_field(coneLength, coneLength / 2., coneRes,
                                          maskType=maskType)
    surfaceName = vis.act_surface(opacity=0.5)
    cmapName = vis.act_colourbar()

    vis.visualise_interact()
    vis.visualise_save("output/out.png")
    vis.draw_pipeline_graphviz(directory="output")


def example_autopipe_2():
    vis = chagu.Visualisation(name="autopipe_example_2",
                                      filePath="data/data.vtu")
    sliceName = vis.slice_data_with_plane()
    compName = vis.extract_vector_components(component=2)

    arrowLength = 1.0
    nastyName = vis.act_nasty_vector_field(arrowLength, maskType="plane")
    surfaceName = vis.act_surface(position=[0., 0., -arrowLength / 2.])
    cmapName = vis.act_colourbar()

    vis.visualise_interact()
    vis.draw_pipeline_graphviz(directory="output")


def example_nasty_2d():
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
    vis.draw_pipeline_graphviz(directory="output")


def example_the_works():
    vis = chagu.Visualisation(name="full_example")
    readerName = vis.load_visualisation_toolkit_file("data/data.vtu")
    compName = vis.extract_vector_components(component=2)

    coneLength = 1.0
    coneRes = 20
    maskType = "volume"
    conesName = vis.act_cone_vector_field(coneLength, coneLength / 2., coneRes,
                                          maskType=maskType)
    surfaceName = vis.act_surface(opacity=0.5)
    cmapName = vis.act_colourbar()

    pipeline = [[readerName, compName],
                [compName, surfaceName],
                [compName, conesName]]
    vis.build_pipeline_from_dict(pipeline)

    vis.visualise_interact()
    vis.visualise_save("output/out.png")
    vis.draw_pipeline_graphviz(directory="output")


def example_animate_rotate():
    vis = chagu.Visualisation(filePath="data/data.vtu")
    horiz = 1680
    ratio = 3.0
    vis.windowSize = [horiz, horiz * ratio]
    vis.extract_vector_components(component=2)
    vis.act_cone_vector_field(1, .5, 20, maskType="plane")
    vis.act_surface(opacity=0.5)
    vis.visualise_animate_rotate("output/rot", offscreenRendering=True,
                                 rotation_resolution=4)


# if __name__ == "__main__":
#     if os.path.exists("output") is False:
#         os.mkdir("output")
#     example_tiny()
#     example_autopipe_1()
#     example_autopipe_2()
#     example_nasty_2d()
#     example_the_works()
#     example_animate_rotate()
