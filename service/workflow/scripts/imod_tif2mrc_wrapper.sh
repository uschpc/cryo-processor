#!/bin/bash
. ${HOME}/software/cryo-processor-progs/imod/IMOD-linux.sh

#function subm () { 
#submfg $* & }", modeA={"load"}
#}

tif2mrc "$@"

exit $?



