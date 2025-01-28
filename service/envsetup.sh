#!/bin/bash

#. venv/bin/activate

module purge
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate ${HOME}/software/cryo-processor-progs
export LD_LIBRARY_PATH=${HOME}/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

export PEGASUS_HOME=/home1/cryoemadmin/software/pegasus-5.0.9
export PATH=$PEGASUS_HOME/bin:$PATH
export PYTHONPATH=$(pegasus-config --python)
export LANG=en_US.UTF-8

