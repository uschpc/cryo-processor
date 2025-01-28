#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate ${HOME}/software/cryo-processor-progs
export LD_LIBRARY_PATH=${HOME}/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH


file0_in=${1}
file0_out=${2}

magick convert -resize 20% $file0_in $file0_out & PIDONE=$!

wait $PIDONE

exit $?


