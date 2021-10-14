#!/bin/bash
img_file_path=$1
gctf_output_fn=$2
mc2_output_fn=$3
slack_notify_out_fn=$4
#resolution="$2"
#shifts="$3"

resolution=`cat ${gctf_output_fn} | grep RES_LIMIT | awk '{print $NF}'`

echo "${resolution}" >> $slack_notify_out_fn
echo "" >> $slack_notify_out_fn

shifts=`cat ${mc2_output_fn} | grep "...... Frame"`

echo "${shifts}" >> $slack_notify_out_fn
echo "" >> $slack_notify_out_fn

message="\"Estimated resolution limit: *${resolution}*\nMotion correction shifts:\n${shifts}\""

echo "${message}" >> $slack_notify_out_fn
echo "" >> $slack_notify_out_fn

curl --data-urlencode "file=${img_file_path}" --data-urlencode "message=\"$(printf 'Estimated resolution limit: *%s*\nMotion correction shifts:\n%s\n' "${resolution}" "${shifts}")\"" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'
echo "curl --data-urlencode \"file=${img_file_path}\" --data-urlencode \"message=\"${message}\"\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn

exit $?



