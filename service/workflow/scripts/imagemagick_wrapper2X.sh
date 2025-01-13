#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH

PROGNAME=`type $0 | awk '{print $3}'`  # search for executable on path
PROGDIR=`dirname $PROGNAME`            # extract directory of program
PROGNAME=`basename $PROGNAME`          # base name of program

jpgX_in=${1}
jpgctfX_in=${2}
combinedX=${3}
ctflogX=${4}
mclogX=${5}
resolutionX="`$PROGDIR/get_data.py ctf_r $ctflogX`"
astiX="`$PROGDIR/get_data.py ctf_a $ctflogX`"
shiftsX="`$PROGDIR/get_data.py mc $mclogX`"

magick convert +append $jpgX_in $jpgctfX_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolutionX}Å" -annotate +40+140 "A: ${astiX}" -annotate +40+240 "S: ${shiftsX/_/ }" $combinedX

exit $?



