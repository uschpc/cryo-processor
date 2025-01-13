#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

mcin=${1}
kev=${2}
pxsize=${3}
fmdose=${4}
gainref=${5}
eer_rendered_frames=${6}
no_of_frames=${7}
eer_divisor=${8}
eer_sampling=${9}
dose_per_eer_frame=${10}
eer_fmintfilepath=${11}
file0_in=${12}
file0_out=${13}
file0_stderr=${14}
file0_stdout=${15}
file1_in=${16}
file1_out=${17}
file1_stderr=${18}
file1_stdout=${19}
file2_in=${20}
file2_out=${21}
file2_stderr=${22}
file2_stdout=${23}
file3_in=${24}
file3_out=${25}
file3_stderr=${26}
file3_stdout=${27}


#create fmintfile
echo "${no_of_frames} ${eer_divisor} ${dose_per_eer_frame}" > ${eer_fmintfilepath}


if [ "$mcin" == "InTiff" ] ; then
  MotionCor2 -InTiff $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Gain $gainref 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InTiff $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Gain $gainref 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InTiff $file2_in -OutMrc $file2_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Gain $gainref 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InTiff $file3_in -OutMrc $file3_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Gain $gainref 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
elif [ "$mcin" == "InMrc" ] ; then
  MotionCor2 -InMrc $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Gain $gainref 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InMrc $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Gain $gainref 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InMrc $file2_in -OutMrc $file2_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Gain $gainref 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InMrc $file3_in -OutMrc $file3_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Gain $gainref 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
elif [ "$mcin" == "InEer" ] ; then
  MotionCor2 -InEer $file0_in -OutMrc $file0_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Gain $gainref 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InEer $file1_in -OutMrc $file1_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Gain $gainref 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InEer $file2_in -OutMrc $file2_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Gain $gainref 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InEer $file3_in -OutMrc $file3_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Gain $gainref 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
fi

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR

#rm -rf $eer_fmintfilepath

exit $?


