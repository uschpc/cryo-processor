#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH
#provide old cuda libs for gctf to work with newer cuda on a40
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/gctf_libs_from_c10.1.243_to_work_with_c11.2.0_on_a40:$LD_LIBRARY_PATH

#debug
#ldd `which gctf`
#echo `hostname`
#echo $CUDA_VISIBLE_DEVICES
#echo


kev=${1}
pxsize=${2}
file0_star=${3}
file0_in=${4}
file0_stdout=${5}
file0_stderr=${6}
file1_star=${7}
file1_in=${8}
file1_stdout=${9}
file1_stderr=${10}
file2_star=${11}
file2_in=${12}
file2_stdout=${13}
file2_stderr=${14}
file3_star=${15}
file3_in=${16}
file3_stdout=${17}
file3_stderr=${18}


gctf --apix $pxsize --kV $kev --Cs 2.7 --ac 0.1 --ctfstar $file0_star --boxsize 1024 $file0_in --gid 0 2> $file0_stdout 1> $file0_stderr & PIDONE=$!
gctf --apix $pxsize --kV $kev --Cs 2.7 --ac 0.1 --ctfstar $file1_star --boxsize 1024 $file1_in --gid 1 2> $file1_stdout 1> $file1_stderr & PIDTWO=$!
gctf --apix $pxsize --kV $kev --Cs 2.7 --ac 0.1 --ctfstar $file2_star --boxsize 1024 $file2_in --gid 2 2> $file2_stdout 1> $file2_stderr & PIDTHREE=$!
gctf --apix $pxsize --kV $kev --Cs 2.7 --ac 0.1 --ctfstar $file3_star --boxsize 1024 $file3_in --gid 3 2> $file3_stdout 1> $file3_stderr & PIDFOUR=$!

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR


exit $?



