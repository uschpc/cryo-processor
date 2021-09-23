#!/bin/bash

set -e

# ensure we start in the right directory
cd $(dirname $0)

module load usc
module load python/3.6.8
module load openjdk/11.0.2

if [ ! -e venv ]; then
    python3 -m venv venv
    . venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

fi

. venv/bin/activate

#export PEGASUS_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pegasus-5.0.0-esezn6jgoegtjkugiaacbdotigbgevwu
#export PEGASUS_HOME=/project/cryoem/software/pegasus-5.0.1dev
#export PEGASUS_HOME=/home1/rynge/software/pegasus-5.0.1dev
export PEGASUS_HOME=/home1/cryoemadmin/software/pegasus-5.0.1dev
export PATH=$PEGASUS_HOME/bin:$PATH
export PYTHONPATH=$(pegasus-config --python)
export LANG=en_US.UTF-8
#uvicorn main:app --reload --host 0.0.0.0 --port 8111
python3 main.py

