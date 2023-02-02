#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /spack/apps/linux-centos7-x86_64/gcc-8.3.0/cryoem/eman2

e2proc2d.py "$@"

exit $?



