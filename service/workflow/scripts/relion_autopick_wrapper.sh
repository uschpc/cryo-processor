#!/bin/bash
#. /spack/apps/lmod/8.2/init/bash
#module use /spack/apps/lmod/linux-centos7-x86_64/Core
#module load usc relion

#export GCC_ROOT=/spack/apps/gcc/8.3.0
export LD_LIBRARY_PATH=/spack/apps/gcc/8.3.0/lib64:$LD_LIBRARY_PATH
export PATH=/spack/apps/gcc/8.3.0/bin:$PATH
#export MANPATH=/spack/apps/gcc/8.3.0/share/man:$MANPATH
export CMAKE_PREFIX_PATH=/spack/apps/gcc/8.3.0/:$CMAKE_PREFIX_PATH
export LD_PRELOAD=/spack/apps/gcc/8.3.0/lib64/libstdc++.so.6

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openblas-0.3.8-2no6mfziiclwxb7lstxoos335gnhjpes/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openblas-0.3.8-2no6mfziiclwxb7lstxoos335gnhjpes/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openblas-0.3.8-2no6mfziiclwxb7lstxoos335gnhjpes/lib/pkgconfig:$PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openblas-0.3.8-2no6mfziiclwxb7lstxoos335gnhjpes/:$CMAKE_PREFIX_PATH
#export OPENBLAS_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openblas-0.3.8-2no6mfziiclwxb7lstxoos335gnhjpes

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/bin:$PATH
#export MANPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/share/man:$MANPATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/lib/pkgconfig:$PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/:$CMAKE_PREFIX_PATH
#export LIBTIFF_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb

#export MANPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/zlib-1.2.11-dp3wfr26pumq5x4dltujahr4qse4agnk/share/man:$MANPATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/zlib-1.2.11-dp3wfr26pumq5x4dltujahr4qse4agnk/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/zlib-1.2.11-dp3wfr26pumq5x4dltujahr4qse4agnk/lib/pkgconfig:PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/zlib-1.2.11-dp3wfr26pumq5x4dltujahr4qse4agnk/:$CMAKE_PREFIX_PATH
#export ZLIB_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/zlib-1.2.11-dp3wfr26pumq5x4dltujahr4qse4agnk

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libpng-1.6.37-xagwrmfxi5g25gukpaci4rr3omqjj2ov/bin:$PATH
#export MANPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libpng-1.6.37-xagwrmfxi5g25gukpaci4rr3omqjj2ov/share/man:$MANPATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libpng-1.6.37-xagwrmfxi5g25gukpaci4rr3omqjj2ov/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libpng-1.6.37-xagwrmfxi5g25gukpaci4rr3omqjj2ov/lib/pkgconfig:$PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libpng-1.6.37-xagwrmfxi5g25gukpaci4rr3omqjj2ov/:$CMAKE_PREFIX_PATH
#export LIBPNG_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libpng-1.6.37-xagwrmfxi5g25gukpaci4rr3omqjj2ov

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pmix-3.1.3-3sm6emyqaxapunh7rwbjvtaqoqe2e5z3/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pmix-3.1.3-3sm6emyqaxapunh7rwbjvtaqoqe2e5z3/lib:$LD_LIBRARY_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pmix-3.1.3-3sm6emyqaxapunh7rwbjvtaqoqe2e5z3/:$CMAKE_PREFIX_PATH
#export PMIX_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pmix-3.1.3-3sm6emyqaxapunh7rwbjvtaqoqe2e5z3

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq/bin:$PATH
#export MANPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq/share/man:$MANPATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq/lib:$LIBRARY_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq/include:$CPATH
export PKG_CONFIG_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq/lib/pkgconfig:$PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq/:$CMAKE_PREFIX_PATH
#export OPENMPI_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/openmpi-4.0.2-ipm3dnvlbtxawpi4ifz7jma6jgr7mexq

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/lib64:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/lib64:$LIBRARY_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/include:$CPATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7/:$CMAKE_PREFIX_PATH
export CUDA_HOME=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7
#export CUDA_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/cuda-11.1-1-kjouyuzherpxox24nfkmedp777ouy4i7

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/relion-3.1.1_c11.1-1-k40/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/relion-3.1.1_c11.1-1-k40/lib:$LD_LIBRARY_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/relion-3.1.1_c11.1-1-k40/:$CMAKE_PREFIX_PATH
export RELION_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/relion-3.1.1_c11.1-1-k40

relion_autopick "$@"

exit $?



