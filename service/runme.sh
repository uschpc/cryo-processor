#!/bin/bash

set -e

# ensure we start in the right directory
cd $(dirname $0)

module purge
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate ${HOME}/software/cryo-processor-progs
export LD_LIBRARY_PATH=${HOME}/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

#module load usc
#module load openjdk

#if [ ! -e venv ]; then
#    python3 -m venv venv
#    . venv/bin/activate
#    python3 -m pip install --upgrade pip
#    python3 -m pip install -r requirements.txt
#fi

#. venv/bin/activate

export PEGASUS_HOME=/home1/cryoemadmin/software/pegasus-5.0.1dev
export PATH=$PEGASUS_HOME/bin:$PATH
export PYTHONPATH=$(pegasus-config --python)
export LANG=en_US.UTF-8
#uvicorn main:app --reload --host 0.0.0.0 --port 8111
python3 main.py

