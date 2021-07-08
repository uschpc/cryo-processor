#!/bin/bash
#. /spack/apps/lmod/8.2/init/bash
#module use /spack/apps/lmod/linux-centos7-x86_64/Core
#module load usc gctf


export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/lib64:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/lib64:$LIBRARY_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/include:$CPATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb:$CMAKE_PREFIX_PATH
export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb
export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/gctf-1.18/bin:$PATH


gctf "$@"

exit $?



