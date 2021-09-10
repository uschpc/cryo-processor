#!/bin/bash
img_file_path="$1"
shift
message="$@"
#resolution="$2"
#shifts="$3"

#resolution=`cat ${gctf_output} | grep RES_LIMIT | awk '{print $NF}'`


#shifts=`cat ${mc2_output} | grep "...... Frame"`


#message="Estimated resolution limit: $resolution\nMotion correction shifts:\n${shifts}"

curl --data-urlencode "file=${filepath}" --data-urlencode "message=${message}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'

exit $?



