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

#echo "Starting at `date`"
#echo "Running on hosts: $SLURM_NODELIST"
#echo "Running on $SLURM_NNODES nodes."
#echo "Running $SLURM_NTASKS tasks."
#echo "Current working directory is `pwd`"
#echo `hostname`
#echo `nvidia-smi`
#echo $CUDA_VISIBLE_DEVICES

mcin=$1
kev=$2
pxsize=$3
fmdose=$4
gainref=$5
file0_in=$6
file0_out=$7
file0_stderr=$8
file0_stdout=$9
file1_in=$10
file1_out=$11
file1_stderr=$12
file1_stdout=$13



#echo 
MotionCor2 $mcin $file0_in -OutMrc $file0_out -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.4 -Gpu 0 -Gain $gainref 2> $file0_stderr 1> $file0_stdout & PIDONE=$!
MotionCor2 $mcin $file1_in -OutMrc $file1_out -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.4 -Gpu 1 -Gain $gainref 2> $file1_stderr 1> $file1_stdout & PIDTWO=$!

wait $PIDONE
wait $PIDTWO


echo "MotionCor2 $mcin $file0_in -OutMrc $file0_out -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.2 -Gpu 0 -Gain $gainref 2> $file0_stderr 1> $file0_stdout" >> $file0_stderr
echo "MotionCor2 $mcin $file1_in -OutMrc $file1_out -Iter 7 -Tol 0.5 -Kv $kev -PixSize $pxsize -FmDose $fmdose -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.2 -Gpu 1 -Gain $gainref 2> $file1_stderr 1> $file1_stdout" >> $file1_stderr


exit $?



