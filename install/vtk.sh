#!/bin/bash

set -e

# This bash script makes VTK in the VTK_BUILD_PATH directory. The version of
# VTK that is made is 5.10.1 by default, but can be changed by setting the
# environment variable VTK_BUILD_VERSION.
VTK_BUILD_VERSION=${VTK_BUILD_VERSION:-5.10.1}

# The build path is likewise defined as:
VTK_BUILD_PATH=${VTK_BUILD_PATH:-$HOME}

# Note that this script does not install VTK and will not make it importable by
# default. If you wish this to happen, navigate to the VTK_BUILD_PATH directory
# and "make install", with appropriate permissions.

# Now we define some other useful variables.
VTK_BUILD_PREFIX=${VTK_BUILD_VERSION::-2}
VTK_TARBALL=vtk-$VTK_BUILD_VERSION.tar.gz
VTK_UNTAR_PATH=$VTK_BUILD_PATH/VTK$VTK_BUILD_VERSION

# When we build VTK, we place a temporary file marking that it has been
# built. This is largely to speed up execution on circleCI, so if you find this
# script doesn't do what you need it to, remove "VTK_UNTAR_PATH/.is_built".
if [ ! -f $VTK_UNTAR_PATH/.is_built ]; then

    # Download the tarball from Kitware and untar it into the build path
    # directory.
    pushd $VTK_BUILD_PATH/
    wget http://www.vtk.org/files/release/$VTK_BUILD_PREFIX/$VTK_TARBALL
    tar -xvf $VTK_TARBALL
    cd $VTK_UNTAR_PATH

    # Make.
    cmake -D VTK_WRAP_PYTHON:BOOL=ON -D BUILD_SHARED_LIBS:BOOL=ON ./
    make all

    # If we made it here, we assume that the build was successful. Hence we
    # create a file that prevents this script from running unnecessarily in
    # future.
    touch .is_built
    popd
fi
