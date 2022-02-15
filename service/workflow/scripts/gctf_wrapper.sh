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

#provide old cuda libs for gctf to work with newer cuda on a40
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/gctf_libs_from_c10.1.243_to_work_with_c11.2.0_on_a40:$LD_LIBRARY_PATH

#debug
#ldd `which gctf`
echo `hostname`
echo

gctf "$@"

exit $?



