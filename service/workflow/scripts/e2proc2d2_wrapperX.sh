#!/bin/bash
. "/spack/apps/linux-centos7-x86_64/gcc-8.3.0/anaconda3-2019.10-bpb6unkhyvkirwkg44uqchcy5jyhzhvt/etc/profile.d/conda.sh"
conda activate /spack/apps/linux-centos7-x86_64/gcc-8.3.0/cryoem/eman2

file0_in=$1
file0_out=$2

e2proc2d.py --fixintscaling=sane $file0_in $file0_out & PIDONE=$!

wait $PIDONE

exit $?



