#!/bin/bash
#. /spack/apps/lmod/8.2/init/bash
#module use /spack/apps/lmod/linux-centos7-x86_64/Core
#module load usc imod

export LD_PRELOAD=/spack/apps/gcc/8.3.0/lib64/libstdc++.so.6
export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/lib64:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/lib64:$LIBRARY_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb/include:$CPATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb:$CMAKE_PREFIX_PATH
export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb
export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-10.1.243-ti55aznlgai3utc7jwrryt2ykxoiz3bb
export IMOD_DIR=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imod-4.12.3
export IMOD_JAVADIR=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/jdk-12.0.2_10-2wddza7an2d4clp63xtw5xt7jvpyuyx6
export IMOD_PLUGIN_DIR=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imod-4.12.3/lib/imodplug
export IMOD_QTLIBDIR=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imod-4.12.3/qtlib
export FOR_DISABLE_STACK_TRACE=1
#export IMOD_CALIB_DIR=/usr/local/ImodCalib
export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imod-4.12.3/bin:$PATH
export MANPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imod-4.12.3/man:$MANPATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imod-4.12.3/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imod-4.12.3/qtlib:$LD_LIBRARY_PATH

#function subm () { 
#submfg $* & }", modeA={"load"}
#}

tif2mrc "$@"

exit $?



