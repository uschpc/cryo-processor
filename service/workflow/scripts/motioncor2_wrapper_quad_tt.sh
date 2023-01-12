#!/bin/bash

GPU_NAME=`grep -R Model /proc/driver/nvidia/gpus/* | head -n 1 | awk '{print $(NF)}'`
if [ "$GPU_NAME" == "K40m" ]; then
  #Motioncor2 v1.2.3 with CUDA 10.0.130 # too old for EER files; necessary if K40 GPUs are used
  export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/bin:$PATH
  export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/lib64:$LD_LIBRARY_PATH
  export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/lib64:$LIBRARY_PATH
  export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/include:$CPATH
  export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm:$CMAKE_PREFIX_PATH
  export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm
  export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm
  export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/motioncor2-1.2.3/bin:$PATH
else
  # #Motioncor2 v1.4.2 with CUDA 11.1-1 # for EER files; For P100 or newer GPUs
  # export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/bin:$PATH
  # export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/lib64:$LD_LIBRARY_PATH
  # export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/lib64:$LIBRARY_PATH
  # export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/include:$CPATH
  # export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7:$CMAKE_PREFIX_PATH
  # export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7
  # export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7
  # export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/motioncor2-1.4.2/bin:$PATH


  #Motioncor2 v1.4.4 with CUDA 11.2.0 # for EER files; For P100 or newer GPUs
  export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/bin:$PATH
  export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/lib64:$LD_LIBRARY_PATH
  export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/lib64:$LIBRARY_PATH
  export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/include:$CPATH
  export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c:$CMAKE_PREFIX_PATH
  export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c
  export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c
  export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/motioncor2-1.4.4/bin:$PATH
fi

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
file2_in=${21}
file2_out=${22}
file2_stderr=${23}
file2_stdout=${24}
file3_in=${25}
file3_out=${26}
file3_stderr=${27}
file3_stdout=${28}

#create fmintfile
echo "$no_of_frames $eer_divisor $dose_per_eer_frame" > $eer_fmintfilepath


if [ "$mcin" == "InTiff" ] ; then
  MotionCor2 -InTiff $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InTiff $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InTiff $file2_in -OutMrc $file2_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Throw $throw -Trunc $trunc 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InTiff $file3_in -OutMrc $file3_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Throw $throw -Trunc $trunc 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
elif [ "$mcin" == "InMrc" ] ; then
  MotionCor2 -InMrc $file0_in -OutMrc $file0_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InMrc $file1_in -OutMrc $file1_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InMrc $file2_in -OutMrc $file2_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Throw $throw -Trunc $trunc 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InMrc $file3_in -OutMrc $file3_out -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Throw $throw -Trunc $trunc 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
elif [ "$mcin" == "InEer" ] ; then
  MotionCor2 -InEer $file0_in -OutMrc $file0_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 0 -Throw $throw -Trunc $trunc 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
  MotionCor2 -InEer $file1_in -OutMrc $file1_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 1 -Throw $throw -Trunc $trunc 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!
  MotionCor2 -InEer $file2_in -OutMrc $file2_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 2 -Throw $throw -Trunc $trunc 2> $file2_stderr 1> $file2_stdout & PIDTHREE=$!
  MotionCor2 -InEer $file3_in -OutMrc $file3_out -FmIntFile $eer_fmintfilepath -EerSampling $eer_sampling -FtBin $eer_sampling -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.25 -Gpu 3 -Throw $throw -Trunc $trunc 2> $file3_stderr 1> $file3_stdout & PIDFOUR=$!
fi

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR

#rm -rf $eer_fmintfilepath

exit $?



