#!/bin/bash
#. /spack/apps/lmod/8.2/init/bash
#module use /spack/apps/lmod/linux-centos7-x86_64/Core
#module load usc imagemagick

export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imagemagick-7.0.8-7-hqic326ns3rzzub2ioxar4hvzkfjko6k/bin:$PATH
export MANPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imagemagick-7.0.8-7-hqic326ns3rzzub2ioxar4hvzkfjko6k/share/man:$MANPATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imagemagick-7.0.8-7-hqic326ns3rzzub2ioxar4hvzkfjko6k/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imagemagick-7.0.8-7-hqic326ns3rzzub2ioxar4hvzkfjko6k/lib:$LIBRARY_PATH
export CPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imagemagick-7.0.8-7-hqic326ns3rzzub2ioxar4hvzkfjko6k/include:$CPATH
export PKG_CONFIG_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imagemagick-7.0.8-7-hqic326ns3rzzub2ioxar4hvzkfjko6k/lib/pkgconfig:$PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/imagemagick-7.0.8-7-hqic326ns3rzzub2ioxar4hvzkfjko6k/:$CMAKE_PREFIX_PATH
export XLOCALEDIR=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libx11-1.6.7-hg57h3uawa776mbgc3tadzcjwgcaktnm/share/X11/locale:$XLOCALEDIR
export XDG_DATA_DIRS=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/gobject-introspection-1.56.1-v2m526skuvzolrcfzki27gfrauitna47/share:$XDG_DATA_DIRS
export XDG_DATA_DIRS=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/atk-2.30.0-sktxfdsokxmgszykbjrmeuxa7adky6bx/share:$XDG_DATA_DIRS
export XDG_DATA_DIRS=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/gdk-pixbuf-2.40.0-tlbf4okbuvsgqzxfbrebl3ipucgz43lz/share:$XDG_DATA_DIRS
export XDG_DATA_DIRS=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pango-1.41.0-ts335os6w4tutjlshm4lm4glzk6spbpo/share:$XDG_DATA_DIRS
export XDG_DATA_DIRS=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/shared-mime-info-1.9-sttvs5aj7qp4w7rawclgis7t45f5cuit/share:$XDG_DATA_DIRS
export XDG_DATA_DIRS=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/gtkplus-3.20.10-dukwopcup426l3mgedykk7w4kyuh4af4/share:$XDG_DATA_DIRS

file0_in=${1}
file0_out=${2}
file1_in=${3}
file1_out=${4}
file2_in=${5}
file2_out=${6}
file3_in=${7}
file3_out=${8}

magick convert -resize 20% $file0_in $file0_out & PIDONE=$!
magick convert -resize 20% $file1_in $file1_out & PIDTWO=$!
magick convert -resize 20% $file2_in $file2_out & PIDTHREE=$!
magick convert -resize 20% $file3_in $file3_out & PIDFOUR=$!

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR

exit $?



