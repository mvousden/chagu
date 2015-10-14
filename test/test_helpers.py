"""
This python file tests the functionality of functions defined in
chagu/helpers.py. Tests are detailed in the function documentation.
"""

import chagu
import pytest


def test_generate_sensible_name():
    """
    Test chagu.helpers.generate_sensible_name. We test the following cases:

    1. If testFunction is not callable, a TypeError is raised.
    2. If testFunction is a function that returns False with guessName as its
         only argument, guessName is returned.
    3. If testFunction is a function that returns True with guessName as its
         only argument, "{}_0".format(guessName) is returned.
    4. If testFunction is a function that returns True with testName as its
         only argument, where testName is one of [testName] +
         ["{}_{}".format(testName, zI) for zI in range(11)],
         "{}_11".format(guessName) is returned.
    5. As with test 4, but where testName ends with "_11".
    """

    # Test 1: If testFunction is not callable, a TypeError is raised.
    testFunction_1 = 5
    guessName_1 = "obj"
    expectedMsg = "object is not callable"
    with pytest.raises(TypeError) as testException:
        chagu.helpers.generate_sensible_name(guessName_1, testFunction_1)
    assert expectedMsg in testException.value.message

    # Test 2: If testFunction is a function that returns False with guessName
    # as its only argument, guessName is returned.
    guessName_2 = guessName_1

    def testFunction_2(guessName):
        return False

    out_2 = chagu.helpers.generate_sensible_name(guessName_2, testFunction_2)
    assert out_2 == guessName_2

    # Test 3: If testFunction is a function that returns True with guessName as
    # its only argument, "{}_0".format(guessName) is returned.
    guessName_3 = guessName_1

    def testFunction_3(guessName):
        if guessName == guessName_3:
            return True
        return False

    out_3 = chagu.helpers.generate_sensible_name(guessName_3, testFunction_3)
    assert out_3 == "{}_0".format(guessName_3)

    # Test 4: If testFunction is a function that returns True with testName as
    # its only argument, where testName is one of [testName] +
    # ["{}_{}".format(testName, zI) for zI in range(11)],
    # "{}_11".format(guessName) is returned.
    guessName_4 = guessName_1

    def testFunction_4(guessName):
        if guessName in [guessName_4] + ["{}_{}".format(guessName_4, zI)
                                         for zI in range(11)]:
            return True
        return False

    out_4 = chagu.helpers.generate_sensible_name(guessName_4, testFunction_4)
    assert out_4 == "{}_11".format(guessName_4)

    # Test 5: As with test 4, but where testName ends with "_11".
    guessName_5 = guessName_1 + "_11"

    def testFunction_5(guessName):
        if guessName in [guessName_5] + ["{}_{}".format(guessName_5, zI)
                                         for zI in range(11)]:
            return True
        return False

    out_5 = chagu.helpers.generate_sensible_name(guessName_5, testFunction_5)
    assert out_5 == "{}_11".format(guessName_5)


def test_vtk_base_version():
    """
    Test chagu.helpers.vtk_base_version. We test the following cases:

    1. vtk_base_version returns an integer object.
    2. If vtk_base_version returns 5, vtk.vtkDataObjectSource must be
       defined. If vtk_base_version returns 6, vtk.vtkDataObjectSource must not
       be defined.
    """

    # Test 1: vtk_base_version returns integer object.
    vtkVersion = chagu.helpers.vtk_base_version()
    assert type(vtkVersion) == int

    # Test 2: If vtk_base_version returns 5, vtk.vtkDataObjectSource must be
    # defined. If vtk_base_version returns 6, vtk.vtkDataObjectSource must not
    # be defined.
    if vtkVersion == 5:
        assert hasattr(chagu.helpers.vtk, "vtkDataObjectSource") is True
    elif vtkVersion == 6:
        assert hasattr(chagu.helpers.vtk, "vtkDataObjectSource") is True


if __name__ == "__main__":
    test_generate_sensible_name()
    test_vtk_base_version()
