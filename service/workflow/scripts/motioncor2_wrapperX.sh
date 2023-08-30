#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

mcin=${1}
kev=${2}
pxsize=${3}
fmdose=${4}
eer_rendered_frames=${5}
no_of_frames=${6}
eer_divisor=${7}
eer_sampling=${8}
dose_per_eer_frame=${9}
eer_fmintfilepath=${10}
file0_in=${11}
file0_out=${12}
file0_stderr=${13}
file0_stdout=${14}


#create fmintfile
echo "$no_of_frames $eer_divisor $dose_per_eer_frame" > $eer_fmintfilepath

if [ "$mcin" == "InTiff" ] ; then
  MotionCor2 -InTiff ${file0_in} -OutMrc ${file0_out} -FtBin ${eer_sampling} -Iter 7 -Tol 0.5 -Kv ${kev} -PixSize ${pxsize} -FmDose ${fmdose} -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 2> ${file0_stderr} 1> ${file0_stdout} & PIDONE=$!
elif [ "$mcin" == "InMrc" ] ; then
  MotionCor2 -InMrc ${file0_in} -OutMrc ${file0_out} -FtBin ${eer_sampling} -Iter 7 -Tol 0.5 -Kv ${kev} -PixSize ${pxsize} -FmDose ${fmdose} -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 2> ${file0_stderr} 1> ${file0_stdout} & PIDONE=$!
elif [ "$mcin" == "InEer" ] ; then
  MotionCor2 -InEer ${file0_in} -OutMrc ${file0_out} -FmIntFile ${eer_fmintfilepath} -EerSampling ${eer_sampling} -FtBin ${eer_sampling} -Iter 7 -Tol 0.5 -Kv ${kev} -PixSize ${pxsize} -FmDose ${fmdose} -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 2> ${file0_stderr} 1> ${file0_stdout} & PIDONE=$!
fi

wait $PIDONE

#rm -rf $eer_fmintfilepath

exit $?




