#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate ${HOME}/software/cryo-processor-progs
export LD_LIBRARY_PATH=${HOME}/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

mcin=${1}
kev=${2}
pxsize=${3}
fmdose=${4}
throw=${5}
trunc=${6}
eer_rendered_frames=${7}
no_of_frames=${8}
eer_divisor=${9}
eer_sampling=${10}
dose_per_eer_frame=${11}
eer_fmintfilepath=${12}
file0_in=${13}
file0_out=${14}
file0_stderr=${15}
file0_stdout=${16}
file1_in=${17}
file1_out=${18}
file1_stderr=${19}
file1_stdout=${20}


#create fmintfile
echo "$no_of_frames $eer_divisor $dose_per_eer_frame" > $eer_fmintfilepath



if [ "$mcin" == "InTiff" ] ; then
  MotionCor2 -InTiff $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.45 -Gpu 0 -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InTiff $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.45 -Gpu 1 -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
elif [ "$mcin" == "InMrc" ] ; then
  MotionCor2 -InMrc $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.45 -Gpu 0 -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InMrc $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.45 -Gpu 1 -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
elif [ "$mcin" == "InEer" ] ; then
  MotionCor2 -InEer $file0_in -OutMrc $file0_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.45 -Gpu 0 -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InEer $file1_in -OutMrc $file1_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.45 -Gpu 1 -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
fi


wait $PIDONE
wait $PIDTWO

#rm -rf $eer_fmintfilepath

exit $?



