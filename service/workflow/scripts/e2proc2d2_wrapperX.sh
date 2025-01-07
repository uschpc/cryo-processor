#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /spack/conda/eman2

file0_in=${1}
file0_out=${2}

e2proc2d.py --fixintscaling=sane $file0_in $file0_out & PIDONE=$!

wait $PIDONE

exit $?



