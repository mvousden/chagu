# This is an example script demonstrating the elegance of the visualisation
# class I've just written.

import visualisation
import os


def mmm():
    vis = visualisation.Visualisation(name="mmm")
    readerName = vis.load_visualisation_toolkit_file("example_data/data2.vtu")
    sliceName = vis.slice_data_with_plane()
    compName = vis.extract_vector_components(component=2)
    compName_2 = vis.extract_vector_components(component=2)

    coneLength = 2.0
    coneLengthHf = coneLength / 2.
    xMin, xMax, yMin, yMax, zMin, zMax = vis._boundingBox
    xMin += coneLength * 3 / 4.
    yMin += coneLength * 3 / 4.
    xMax -= coneLength * 3 / 4.
    yMax -= coneLength * 3 / 4.
    maskDomain = [xMin, yMin, zMin,
                  xMax, yMin, zMin,
                  xMin, yMax, zMin]
    maskResolution = [7, 11]
    coneRes = 30
    maskType = "plane"
    conesName = vis.act_cone_vector_field(coneLength, coneLengthHf, coneRes,
                                          maskType=maskType,
                                          maskDomain=maskDomain,
                                          maskResolution=maskResolution)

    surfaceName = vis.act_surface(opacity=0.5, position=[0., 0., -coneLength])

    pipeline = [[readerName, sliceName],
                [readerName, compName_2],
                [sliceName, compName],
                [compName, surfaceName],
                [compName_2, conesName]]
    vis.build_pipeline_from_dict(pipeline)

    vis.camera = {"view up": [1., 0., 0.],
                  "position": [0., 0., 32.5]}
    vis.windowSize = [1650, 950]

#    vis.visualise_interact()
    vis.visualise_save("example_data/out.png")


def example_nasty_2d():
    vis = visualisation.Visualisation(name="2d_nasty")
    readerName = vis.load_visualisation_toolkit_file("example_data/data.vtu")
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
    vis.draw_pipeline_graphviz(directory="example_data")


def example_the_works():
    vis = visualisation.Visualisation(name="full_example")
    readerName = vis.load_visualisation_toolkit_file("example_data/data.vtu")
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
    vis.visualise_save("example_data/out.png")
    vis.draw_pipeline_graphviz(directory="example_data")


def example_tiny():
    vis = visualisation.Visualisation(filePath="example_data/data.vtu")
    vis.extract_vector_components(component=2)
    vis.act_cone_vector_field(1, .5, 20, maskType="plane")
    vis.act_surface(opacity=0.5)
    vis.visualise_interact()


def example_autopipe_1():
    vis = visualisation.Visualisation(name="autopipe_example_1",
                                      filePath="example_data/data.vtu")
    compName = vis.extract_vector_components(component=2)

    coneLength = 1.0
    coneRes = 20
    maskType = "volume"
    conesName = vis.act_cone_vector_field(coneLength, coneLength / 2., coneRes,
                                          maskType=maskType)
    surfaceName = vis.act_surface(opacity=0.5)
    cmapName = vis.act_colourbar()

    vis.visualise_interact()
    vis.visualise_save("example_data/out.png")
    vis.draw_pipeline_graphviz(directory="example_data")


def example_autopipe_2():
    vis = visualisation.Visualisation(name="autopipe_example_2",
                                      filePath="example_data/data.vtu")
    sliceName = vis.slice_data_with_plane()
    compName = vis.extract_vector_components(component=2)

    arrowLength = 1.0
    nastyName = vis.act_nasty_vector_field(arrowLength, maskType="plane")
    surfaceName = vis.act_surface(position=[0., 0., -arrowLength / 2.])
    cmapName = vis.act_colourbar()

    vis.visualise_interact()
    vis.draw_pipeline_graphviz(directory="example_data")


def example_animate_rotate():
    vis = visualisation.Visualisation(filePath="example_data/data.vtu")
    horiz = 1680
    ratio = 3.0
    vis.windowSize = [horiz, horiz * ratio]
    vis.extract_vector_components(component=2)
    vis.act_cone_vector_field(1, .5, 20, maskType="plane")
    vis.act_surface(opacity=0.5)
    vis.visualise_animate_rotate("example_data/rot", offscreenRendering=True,
                                 rotation_resolution=4)


if __name__ == "__main__":
    if os.path.exists("example_data") is False:
        os.mkdir("example_data")
    # example_the_works()
    # example_nasty_2d()
    # mmm()
    # example_autopipe_1()
    # example_autopipe_2()
    # example_tiny()
    example_animate_rotate()
