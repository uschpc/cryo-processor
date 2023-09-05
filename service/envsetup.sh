#!/bin/bash

module purge
module load usc/8.3.0
module load python/3.6.8
module load openjdk/11.0.2
. venv/bin/activate
#. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
#conda activate /home1/cryoemadmin/software/cryo-processor-progs
#export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

#export PEGASUS_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pegasus-5.0.0-esezn6jgoegtjkugiaacbdotigbgevwu
#export PEGASUS_HOME=/project/cryoem/software/pegasus-5.0.1dev
export PEGASUS_HOME=/home1/cryoemadmin/software/pegasus-5.0.1dev
export PATH=$PEGASUS_HOME/bin:$PATH
export PYTHONPATH=$(pegasus-config --python)
export LANG=en_US.UTF-8

