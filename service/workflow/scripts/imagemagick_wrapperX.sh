#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH


file0_in=${1}
file0_out=${2}

magick convert -resize 20% $file0_in $file0_out & PIDONE=$!

wait $PIDONE

exit $?


