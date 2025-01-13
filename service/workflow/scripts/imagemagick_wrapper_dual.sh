#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH


file0_in=${1}
file0_out=${2}
file1_in=${3}
file1_out=${4}

magick convert -resize 20% $file0_in $file0_out & PIDONE=$!
magick convert -resize 20% $file1_in $file1_out & PIDTWO=$!

wait $PIDONE
wait $PIDTWO

exit $?



