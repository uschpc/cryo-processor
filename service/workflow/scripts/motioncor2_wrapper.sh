#!/bin/bash
. /spack/apps/lmod/8.2/init/bash
module use /spack/apps/lmod/linux-centos7-x86_64/Core
#temporary to use K40 gpus
module load usc motioncor2/1.2.3
#as soon as p100 will be available - switch to this one
#module load usc motioncor2/1.4.0

nvidia-smi

MotionCor2 "$@"

exit $?



