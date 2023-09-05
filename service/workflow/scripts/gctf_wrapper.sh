#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH
#provide old cuda libs for gctf to work with newer cuda on a40
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/gctf_libs_from_c10.1.243_to_work_with_c11.2.0_on_a40:$LD_LIBRARY_PATH

#debug
#ldd `which gctf`
# echo `hostname`
# echo $CUDA_VISIBLE_DEVICES
# echo
# echo "gctf $@"
# echo
# gctf "$@"

# exit $?



kev=${1}
pxsize=${2}
file0_star=${3}
file0_in=${4}
file0_stdout=${5}
file0_stderr=${6}


gctf --apix $pxsize --kV $kev --Cs 2.7 --ac 0.1 --ctfstar $file0_star --boxsize 1024 $file0_in --gid 0 2> $file0_stderr 1> $file0_stdout & PIDONE=$!

wait $PIDONE

echo "gctf --apix $pxsize --kV $kev --Cs 2.7 --ac 0.1 --ctfstar $file0_star --boxsize 1024 $file0_in --gid 0 2> $file0_stderr 1> $file0_stdout" >> $file0_stderr

exit $?
