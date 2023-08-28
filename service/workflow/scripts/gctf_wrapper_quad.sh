#!/bin/bash
export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/lib64:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/lib64:$LIBRARY_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c/include:$CPATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c:$CMAKE_PREFIX_PATH
export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c
export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.2.0-7uwimxj27s4cptafhkw6a6fpyqf5nw4c

# export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/lib64:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/lib64:$LIBRARY_PATH
# export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm/include:$CPATH
# export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm:$CMAKE_PREFIX_PATH
# export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm
# export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.0.130-t6gcqrfrbeyep65wpy6erigjcovs7pjm

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/gctf-1.18/bin:$PATH

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/lib:$LD_LIBRARY_PATH




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



