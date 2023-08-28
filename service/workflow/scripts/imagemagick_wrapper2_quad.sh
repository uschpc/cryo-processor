#!/bin/bash
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
export PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/bin:$PATH
export LD_LIBRARY_PATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/libtiff-4.0.10-ird6lyk2kk7c5aumxivzass4hfiv3bwb/lib:$LD_LIBRARY_PATH


PROGNAME=`type $0 | awk '{print $3}'`  # search for executable on path
PROGDIR=`dirname $PROGNAME`            # extract directory of program
PROGNAME=`basename $PROGNAME`          # base name of program

jpgX_in=${1}
jpgctfX_in=${2}
combinedX=${3}
ctflogX=${4}
mclogX=${5}

jpgY_in=${6}
jpgctfY_in=${7}
combinedY=${8}
ctflogY=${9}
mclogY=${10}

jpgZ_in=${11}
jpgctfZ_in=${12}
combinedZ=${13}
ctflogZ=${14}
mclogZ=${15}

jpgW_in=${16}
jpgctfW_in=${17}
combinedW=${18}
ctflogW=${19}
mclogW=${20}

#resolutionX="`$PROGDIR/get_data.py ctf_r $ctflogX`"
#astiX="`$PROGDIR/get_data.py ctf_a $ctflogX`"
#shiftsX="`$PROGDIR/get_data.py mc $mclogX`"

#resolutionY="`$PROGDIR/get_data.py ctf_r $ctflogY`"
#astiY="`$PROGDIR/get_data.py ctf_a $ctflogY`"
#shiftsY="`$PROGDIR/get_data.py mc $mclogY`"

#resolutionZ="`$PROGDIR/get_data.py ctf_r $ctflogZ`"
#astiZ="`$PROGDIR/get_data.py ctf_a $ctflogZ`"
#shiftsZ="`$PROGDIR/get_data.py mc $mclogZ`"

#resolutionW="`$PROGDIR/get_data.py ctf_r $ctflogW`"
#astiW="`$PROGDIR/get_data.py ctf_a $ctflogW`"
#shiftsW="`$PROGDIR/get_data.py mc $mclogW`"

#magick convert +append $jpg0_in $jpgctf0_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolution}Å" -annotate +40+140 "A: ${asti}" -annotate +40+240 "S: ${shifts/_/ }" $combined0 & PIDONE=$!
#magick convert +append $jpg1_in $jpgctf1_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolution}Å" -annotate +40+140 "A: ${asti}" -annotate +40+240 "S: ${shifts/_/ }" $combined1 & PIDTWO=$!
(magick convert +append $jpgX_in $jpgctfX_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: `$PROGDIR/get_data.py ctf_r $ctflogX`Å" -annotate +40+140 "A: `$PROGDIR/get_data.py ctf_a $ctflogX`" -annotate +40+240 "S: `$PROGDIR/get_data.py mc $mclogX`" $combinedX) & PIDONE=$!
(magick convert +append $jpgY_in $jpgctfY_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: `$PROGDIR/get_data.py ctf_r $ctflogY`Å" -annotate +40+140 "A: `$PROGDIR/get_data.py ctf_a $ctflogY`" -annotate +40+240 "S: `$PROGDIR/get_data.py mc $mclogY`" $combinedY) & PIDTWO=$!
(magick convert +append $jpgZ_in $jpgctfZ_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: `$PROGDIR/get_data.py ctf_r $ctflogZ`Å" -annotate +40+140 "A: `$PROGDIR/get_data.py ctf_a $ctflogZ`" -annotate +40+240 "S: `$PROGDIR/get_data.py mc $mclogZ`" $combinedZ) & PIDTHREE=$!
(magick convert +append $jpgW_in $jpgctfW_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: `$PROGDIR/get_data.py ctf_r $ctflogW`Å" -annotate +40+140 "A: `$PROGDIR/get_data.py ctf_a $ctflogW`" -annotate +40+240 "S: `$PROGDIR/get_data.py mc $mclogW`" $combinedW) & PIDFOUR=$!

wait $PIDONE
wait $PIDTWO
wait $PIDTHREE
wait $PIDFOUR

exit $?



