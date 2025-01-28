#!/bin/bash
. ${HOME}/software/cryo-processor-progs/imod/IMOD-linux.sh


#function subm () { 
#submfg $* & }", modeA={"load"}
#}

dm2mrc "$@"

exit $?



