"""
This python file tests the examples in examples/ to ensure they run. We also
check the creation of files and directories if appropriate. These tests are a
bit rubbish in that they do not test the visual output.
"""

import chagu
import pytest
import os
import shutil
import subprocess as sp
import sys


pathToThisFile = os.path.dirname(os.path.realpath(__file__))
examplesPath = "{}/../example".format(pathToThisFile)
outputPath = "{}/output".format(examplesPath)
interactive = True if "--interactive" in sys.argv else False


def run_check_output(examplePath, outputFiles):
    """
    Runs the script at examplePath, and checks for the existence of
    outputFiles in the outputPath directory defined above.

    Raises a RuntimeError if an outputFile is missing or stderr is not
    empty. Otherwise returns nothing.
    """

    # Clear existing outputs
    shutil.rmtree(outputPath, ignore_errors=True)

    # Run the example using the same Python executable used to run this script.
    print
    ex = sp.Popen([sys.executable, examplePath], cwd=examplesPath,
                  stderr=sp.PIPE)
    _, stderr = ex.communicate()  # Har har

    try:
        # Check for errors.
        assert len(stderr) == 0

        # Check output files.
        for outputFile in outputFiles:
            if outputFile not in os.listdir(outputPath):
                raise RuntimeError("File {} not produced by script {}."
                                   .format(outputFile, examplePath))
    # Cleanup mess.
    finally:
        shutil.rmtree(outputPath, ignore_errors=True)


def test_no_examples_missing():
    """
    Tests the examples directory to ensure no examples are missing.
    """

    examplesContent = os.listdir(examplesPath)
    exampleScripts = filter(lambda x: x[:7] == "example" and x[-3:] == ".py",
                            examplesContent)
    testedExamples = ["example_animate_rotate.py",
                      "example_autopipe_1.py",
                      "example_autopipe_2.py",
                      "example_custom_vtk_object.py",
                      "example_frontpage_slices.py",
                      "example_nasty_2d.py",
                      "example_the_works.py",
                      "example_tiny.py"]

    # Now for the gauntlet!
    for example in exampleScripts:
        assert example in testedExamples


def test_example_animate_rotate():
    run_check_output("example_animate_rotate.py",
                     ["rot_{:02}.png".format(zI) for zI in range(10)])


@pytest.mark.skipif(interactive is False, reason="Requires user interaction.")
def test_example_autopipe_1():
    run_check_output("example_autopipe_1.py",
                     ["out.png", "autopipe_example_1_pipeline.gv.pdf"])


@pytest.mark.skipif(interactive is False, reason="Requires user interaction.")
def test_example_autopipe_2():
    run_check_output("example_autopipe_2.py",
                     ["autopipe_example_2_pipeline.gv.pdf"])


@pytest.mark.skipif(interactive is False, reason="Requires user interaction.")
def test_example_custom_vtk_object():
    run_check_output("example_custom_vtk_object.py", [])


@pytest.mark.skipif(interactive is False, reason="Requires user interaction.")
def test_example_frontpage_slices():
    run_check_output("example_frontpage_slices.py", ["out.png"])


@pytest.mark.skipif(interactive is False, reason="Requires user interaction.")
def test_example_nasty_2d():
    run_check_output("example_nasty_2d.py",
                     ["2d_nasty_pipeline.gv.pdf"])


@pytest.mark.skipif(interactive is False, reason="Requires user interaction.")
def test_example_the_works():
    run_check_output("example_the_works.py",
                     ["out.png", "full_example_pipeline.gv.pdf"])


@pytest.mark.skipif(interactive is False, reason="Requires user interaction.")
def test_example_tiny():
    run_check_output("example_tiny.py", [])


if __name__ == "__main__":
    test_no_examples_missing()
    test_example_animate_rotate()
    if interactive is True:
        test_example_autopipe_1()
        test_example_autopipe_2()
        test_example_custom_vtk_object()
        test_example_frontpage_slices()
        test_example_nasty_2d()
        test_example_the_works()
        test_example_tiny()
