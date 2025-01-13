#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /apps/conda/envs/eman2

e2proc2d.py "$@"

exit $?



