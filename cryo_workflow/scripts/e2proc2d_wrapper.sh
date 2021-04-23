#!/bin/bash
. "/spack/apps/linux-centos7-x86_64/gcc-8.3.0/anaconda3-2019.10-bpb6unkhyvkirwkg44uqchcy5jyhzhvt/etc/profile.d/conda.sh"
conda activate /spack/apps/linux-centos7-x86_64/gcc-8.3.0/cryoem/eman2

e2proc2d.py "$@"

exit $?



