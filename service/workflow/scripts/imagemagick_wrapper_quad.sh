#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH


file0_in=${1}
file0_out=${2}
file1_in=${3}
file1_out=${4}
file2_in=${5}
file2_out=${6}
file3_in=${7}
file3_out=${8}

magick convert -resize 20% $file0_in $file0_out & PIDONE=$!
magick convert -resize 20% $file1_in $file1_out & PIDTWO=$!
magick convert -resize 20% $file2_in $file2_out & PIDTHREE=$!
magick convert -resize 20% $file3_in $file3_out & PIDFOUR=$!

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR

exit $?



