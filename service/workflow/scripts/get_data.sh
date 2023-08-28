#!/bin/bash
export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/bin:$PATH
export MANPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/share/man:$MANPATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/lib:$LIBRARY_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/include:$CPATH
export PKG_CONFIG_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/lib/pkgconfig:$PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/:$CMAKE_PREFIX_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun/include/python3.6m:$CPATH
export PYTHON_ROOT=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/python-3.6.8-273lxvvtkjyasslzvmxufcdzgwgubbun
export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/lib:$LD_LIBRARY_PATH


PROGNAME=`type $0 | awk '{print $3}'`  # search for executable on path
PROGDIR=`dirname $PROGNAME`            # extract directory of program
PROGNAME=`basename $PROGNAME`          # base name of program

#$1 - function; can be mc or ctf_r or ctf_a
#$2 - log filename (full path) from one of the above
#returns:
#ctf_r: "resolution"
#ctf_a: "astigmatism"
#mc: "avg shifts"
#echo $PROGNAME
#echo $PROGDIR

python3 $PROGDIR/get_data.py ${1} ${2}
