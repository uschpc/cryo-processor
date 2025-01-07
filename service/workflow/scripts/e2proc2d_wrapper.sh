#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /spack/conda/eman2

e2proc2d.py "$@"

exit $?



