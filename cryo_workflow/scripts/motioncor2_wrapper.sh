#!/bin/bash
. /spack/apps/lmod/8.2/init/bash
module use /spack/apps/lmod/linux-centos7-x86_64/Core
module load usc motioncor2

nvidia-smi

MotionCor2 "$@"

exit $?



