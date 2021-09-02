#!/bin/bash
img_file_path="$1"
mc2_output="$2"
gctf_output="$3"

resolution=`cat ${gctf_output} | grep RES_LIMIT | awk '{print $NF}'`


shifts=`cat ${mc2_output} | grep "...... Frame"`


message="Estimated resolution limit: $resolution\nMotion correction shifts:\n${shifts}"

curl --data-urlencode "file=${filepath}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'
curl --data-urlencode "message=${message}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postmessage.php'

exit $?



