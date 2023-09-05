#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
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

jpgY_in=${6}
jpgctfY_in=${7}
combinedY=${8}
ctflogY=${9}
mclogY=${10}
resolutionY="`$PROGDIR/get_data.py ctf_r $ctflogY`"
astiY="`$PROGDIR/get_data.py ctf_a $ctflogY`"
shiftsY="`$PROGDIR/get_data.py mc $mclogY`"

#magick convert +append $jpg0_in $jpgctf0_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolution}Å" -annotate +40+140 "A: ${asti}" -annotate +40+240 "S: ${shifts/_/ }" $combined0 & PIDONE=$!
#magick convert +append $jpg1_in $jpgctf1_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolution}Å" -annotate +40+140 "A: ${asti}" -annotate +40+240 "S: ${shifts/_/ }" $combined1 & PIDTWO=$!
magick convert +append $jpgX_in $jpgctfX_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolutionX}Å" -annotate +40+140 "A: ${astiX}" -annotate +40+240 "S: ${shiftsX/_/ }" $combinedX
magick convert +append $jpgY_in $jpgctfY_in -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolutionY}Å" -annotate +40+140 "A: ${astiY}" -annotate +40+240 "S: ${shiftsY/_/ }" $combinedY



#wait $PIDONE
#wait $PIDTWO

exit $?



