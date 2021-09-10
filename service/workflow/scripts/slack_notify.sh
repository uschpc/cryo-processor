#!/bin/bash
img_file_path="$1"
gctf_output_fn="$2"
mc2_output_fn="$3"
#resolution="$2"
#shifts="$3"

resolution=`cat ${gctf_output_fn} | grep RES_LIMIT | awk '{print $NF}'`


shifts=`cat ${mc2_output_fn} | grep "...... Frame"`


message="Estimated resolution limit: ${resolution}\nMotion correction shifts:\n${shifts}"

curl --data-urlencode "file=${filepath}" --data-urlencode "message=${message}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'

exit $?



