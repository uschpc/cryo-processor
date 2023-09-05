#!/bin/bash
. "/spack/conda/miniconda3/4.12.0/etc/profile.d/conda.sh"
conda activate /home1/cryoemadmin/software/cryo-processor-progs
export LD_LIBRARY_PATH=/home1/cryoemadmin/software/cryo-processor-progs/lib:$LD_LIBRARY_PATH


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
