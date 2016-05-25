#!/bin/bash

set -ex

# This script installs conda and creates an environment suitable for Chagu
# idempotently. It uses environment variables defined in circle.yml.

pushd $HOME/chagu > /dev/null

# If the miniconda directory doesn't exist, we need to install conda.
if [ ! -d "$CONDA_BIN" ]; then

    # Download installer
    wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh

    # Run installer (without prompts)
    bash Miniconda2-latest-Linux-x86_64.sh -b

fi

# If the conda environment we want doesn't exist, we need to create it.
if [ ! -d "~/miniconda2/envs/$CONDA_ENV" ]; then

    # Create environment from conda requirements file. This installs some
    # conda packages (including VTK).
    $CONDA_BIN/conda create --yes --name $CONDA_ENV --file $CHAGU_CI/requirements_conda.txt

    # Activate the environment, install some python packages, then deactivate
    # the environment for more operations.
    source $CONDA_BIN/activate $CONDA_ENV
    pip install --requirement $CHAGU_CI/requirements_pip.txt
    source $CONDA_BIN/deactivate

fi

popd