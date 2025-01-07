#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /spack/conda/eman2

file0_in=${1}
file0_out=${2}
file1_in=${3}
file1_out=${4}

e2proc2d.py --fixintscaling=sane $file0_in $file0_out & PIDONE=$!
e2proc2d.py --fixintscaling=sane $file1_in $file1_out & PIDTWO=$!

wait $PIDONE
wait $PIDTWO

exit $?



