#!/bin/bash
img_file_path=$1
slack_notify_out_fn=$2

curl -k --data-urlencode "file=${img_file_path}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'
echo "command used during processing:" >> $slack_notify_out_fn
echo "curl -k --data-urlencode \"file=${img_file_path}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn
echo "command to use for debuggging:" >> $slack_notify_out_fn
echo "curl -k --data-urlencode \"file=${img_file_path}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn
#echo "curl -k --data-urlencode \"file=${img_file_path}\" --data-urlencode \"message=\"${message}\"\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn

exit $?



