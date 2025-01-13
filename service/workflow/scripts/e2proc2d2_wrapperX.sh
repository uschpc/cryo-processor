#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /apps/conda/envs/eman2

file0_in=${1}
file0_out=${2}

e2proc2d.py --fixintscaling=sane $file0_in $file0_out & PIDONE=$!

wait $PIDONE

exit $?



