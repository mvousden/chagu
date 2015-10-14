#!/bin/bash

set -e

# This bash script makes Python2 in the PYTHON_BUILD_PATH. The version of
# Python that is made is 2.7.10 by default, but can be changed by setting the
# environment variable PYTHON_BUILD_VERSION.
PYTHON_BUILD_VERSION=${PYTHON_BUILD_VERSION:-2.7.10}

# The build path is likewise defined as:
PYTHON_BUILD_PATH=${PYTHON_BUILD_PATH:-$HOME}

# Note that this script does not install Python and does not add it to your
# path. If you wish to use this executable, you need to either add the build
# directory to your path, or run it from the PYTHON_EXEC_PATH.

# Now we define some other useful variables.
PYTHON_TARBALL=Python-$PYTHON_BUILD_VERSION.tar.xz
PYTHON_UNTAR_PATH=$PYTHON_BUILD_PATH/Python-$PYTHON_BUILD_VERSION

# When we build Python, we place a temporary file marking that it has been
# built. This is largely to speed up execution on circleCI, so if you find this
# script doesn't do what you need it to, remove "PYTHON_UNTAR_PATH/.is_built".
if [ ! -f $PYTHON_UNTAR_PATH/.is_built ]; then

    # Download the tarball and untar it into the build path directory.
    pushd $PYTHON_BUILD_PATH/
    wget https://www.python.org/ftp/python/$PYTHON_BUILD_VERSION/$PYTHON_TARBALL
    tar -xvf $VTK_TARBALL
    cd $PYTHON_UNTAR_PATH

    # Build.
    ./configure --enable-unicode=ucs4 --prefix=$PYTHON_UNTAR_PATH --with-ensurepip="upgrade"
    make
    make install

    # If we made it here, we assume that the build was successful. Hence we
    # create a file that prevents this script from running unnecessarily in
    # future.
    touch .is_built
    popd
