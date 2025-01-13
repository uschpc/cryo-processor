#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

mcin=${1}
kev=${2}
pxsize=${3}
fmdose=${4}
gainref=${5}
throw=${6}
trunc=${7}
eer_rendered_frames=${8}
no_of_frames=${9}
eer_divisor=${10}
eer_sampling=${11}
dose_per_eer_frame=${12}
eer_fmintfilepath=${13}
file0_in=${14}
file0_out=${15}
file0_stderr=${16}
file0_stdout=${17}
file1_in=${18}
file1_out=${19}
file1_stderr=${20}
file1_stdout=${21}
file2_in=${22}
file2_out=${23}
file2_stderr=${24}
file2_stdout=${25}
file3_in=${26}
file3_out=${27}
file3_stderr=${28}
file3_stdout=${29}


#create fmintfile
echo "$no_of_frames $eer_divisor $dose_per_eer_frame" > $eer_fmintfilepath


if [ "$mcin" == "InTiff" ] ; then
  MotionCor2 -InTiff $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InTiff $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InTiff $file2_in -OutMrc $file2_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InTiff $file3_in -OutMrc $file3_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
elif [ "$mcin" == "InMrc" ] ; then
  MotionCor2 -InMrc $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InMrc $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InMrc $file2_in -OutMrc $file2_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InMrc $file3_in -OutMrc $file3_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
elif [ "$mcin" == "InEer" ] ; then
  MotionCor2 -InEer $file0_in -OutMrc $file0_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InEer $file1_in -OutMrc $file1_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InEer $file2_in -OutMrc $file2_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InEer $file3_in -OutMrc $file3_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Gain $gainref -Throw $throw -Trunc $trunc 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
fi

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR

#rm -rf $eer_fmintfilepath

exit $?



