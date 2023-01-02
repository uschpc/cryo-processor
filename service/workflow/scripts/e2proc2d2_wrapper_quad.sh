#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /spack/apps/linux-centos7-x86_64/gcc-8.3.0/cryoem/eman2

file0_in=${1}
file0_out=${2}
file1_in=${3}
file1_out=${4}
file2_in=${5}
file2_out=${6}
file3_in=${7}
file3_out=${8}

e2proc2d.py --process=filter.lowpass.gauss:cutoff_freq=0.1 --fixintscaling=sane $file0_in $file0_out & PIDONE=$!
e2proc2d.py --process=filter.lowpass.gauss:cutoff_freq=0.1 --fixintscaling=sane $file1_in $file1_out & PIDTWO=$!
e2proc2d.py --process=filter.lowpass.gauss:cutoff_freq=0.1 --fixintscaling=sane $file2_in $file2_out & PIDTHREE=$!
e2proc2d.py --process=filter.lowpass.gauss:cutoff_freq=0.1 --fixintscaling=sane $file3_in $file3_out & PIDFOUR=$!

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR

exit $?



