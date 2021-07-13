#!/bin/bash

module load openjdk/11.0.2
. venv/bin/activate

#export PEGASUS_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pegasus-5.0.0-esezn6jgoegtjkugiaacbdotigbgevwu
#export PEGASUS_HOME=/project/cryoem/software/pegasus-5.0.1dev
export PEGASUS_HOME=/home1/rynge/software/pegasus-5.0.1dev
export PATH=$PEGASUS_HOME/bin:$PATH
export PYTHONPATH=$(pegasus-config --python)
export LANG=en_US.UTF-8

