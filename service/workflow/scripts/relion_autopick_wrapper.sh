#!/bin/bash
module load usc relion cuda/12.6.3

relion_autopick "$@"

exit $?



