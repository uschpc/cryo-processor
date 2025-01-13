#!/bin/bash
. "/apps/conda/miniforge3/24.3.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH


PROGNAME=`type $0 | awk '{print $3}'`  # search for executable on path
PROGDIR=`dirname $PROGNAME`            # extract directory of program
PROGNAME=`basename $PROGNAME`          # base name of program

resolution="`$PROGDIR/get_data.sh ctf_r $4`"
asti="`$PROGDIR/get_data.sh ctf_a $4`"
shifts="`$PROGDIR/get_data.sh mc $5`"
#dw_jpg_file, jpg_ctf_file, magick_combined_jpg_file, gctf_log_file.lfn, mc2_stdout.lfn


magick convert +append $1 $2 -resize x1024 - | magick convert - -font DejaVu-Sans -fill LightGoldenrod2 -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolution}Å" -annotate +40+140 "A: ${asti}" -annotate +40+240 "S: ${shifts/_/ }" $3
#magick convert +append $1 $2 -resize x1024 - | magick convert - -font DejaVu-Sans -fill bisque -pointsize 80 -interline-spacing 12 -gravity NorthWest -annotate +40+40 "R: ${resolution}Å" -annotate +40+140 "A: ${asti}" -annotate +40+240 "S: ${shifts/_/ }" $3


exit $?



