#!/bin/bash
export LD_PRELOAD=/spack/apps/gcc/11.3.0/lib64/libstdc++.so.6
export PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/cuda-11.5.1-wyisbl5/bin:$PATH
export LD_LIBRARY_PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/cuda-11.5.1-wyisbl5/lib64:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/cuda-11.5.1-wyisbl5/lib64:$LIBRARY_PATH
export CPATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/cuda-11.5.1-wyisbl5/include:$CPATH
export CMAKE_PREFIX_PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/cuda-11.5.1-wyisbl5:$CMAKE_PREFIX_PATH
export CUDA_HOME=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/cuda-11.5.1-wyisbl5
export CUDA_ROOT=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/cuda-11.5.1-wyisbl5
export IMOD_DIR=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/imod-4.12.3
export IMOD_JAVADIR=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/openjdk-11.0.15_10-62tcbpi
export IMOD_PLUGIN_DIR=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/imod-4.12.3/lib/imodplug
export IMOD_QTLIBDIR=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/imod-4.12.3/qtlib
export FOR_DISABLE_STACK_TRACE=1
export PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/imod-4.12.3/bin:$PATH
export MANPATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/imod-4.12.3/man:$MANPATH
export LD_LIBRARY_PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/imod-4.12.3/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/imod-4.12.3/qtlib:$LD_LIBRARY_PATH
export PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/libtiff-4.4.0-f2neolq/bin:$PATH
export LD_LIBRARY_PATH=/spack/2206/apps/linux-centos7-x86_64_v3/gcc-11.3.0/libtiff-4.4.0-f2neolq/lib:$LD_LIBRARY_PATH


#function subm () { 
#submfg $* & }", modeA={"load"}
#}

dm2mrc "$@"

exit $?



