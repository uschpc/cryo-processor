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


PROGNAME=`type $0 | awk '{print $3}'`  # search for executable on path
PROGDIR=`dirname $PROGNAME`            # extract directory of program
PROGNAME=`basename $PROGNAME`          # base name of program

# gctf_output_fn=$3
# shift
# mc2_output_fn=$4
# shift

resolution="`$PROGDIR/get_data.sh ctf_r $4`"
asti="`$PROGDIR/get_data.sh ctf_a $4`"
shifts="`$PROGDIR/get_data.sh mc $5`"
#dw_jpg_file, jpg_ctf_file, magick_combined_jpg_file, gctf_log_file.lfn, mc2_stdout.lfn

#fout=$6

#echo "$PROGDIR/get_data.sh ctf_r $4" >> $fout
#echo $resolution  >> $fout
#echo "$PROGDIR/get_data.sh ctf_a $4"  >> $fout
#echo $asti  >> $fout
#echo "$PROGDIR/get_data.sh mc $5"  >> $fout
#echo $shifts  >> $fout

magick convert +append $1 $2 -resize x1024 - | magick convert - -font DejaVu-Sans -fill blue -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolution}Å" -annotate +40+140 "A: ${asti}" -annotate +40+240 "S: ${shifts/_/ }" $3
#magick "$@"

exit $?



