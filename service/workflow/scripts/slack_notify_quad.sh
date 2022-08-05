#!/bin/bash
#!/bin/bash
img_file_path0=${1}
slack_notify_out_fn0=${2}
img_file_path1=${3}
slack_notify_out_fn1=${4}
img_file_path2=${5}
slack_notify_out_fn2=${6}
img_file_path3=${7}
slack_notify_out_fn3=${8}

curl -k --data-urlencode "file=${img_file_path0}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'
echo "`date --iso-8601=seconds`" >> $slack_notify_out_fn0
echo "command used during processing:" >> $slack_notify_out_fn0
echo "curl -k --data-urlencode \"file=${img_file_path0}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn0
echo "command to use for debuggging:" >> $slack_notify_out_fn0
echo "curl -k --data-urlencode \"file=${img_file_path0}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn0
#echo "curl -k --data-urlencode \"file=${img_file_path0}\" --data-urlencode \"message=\"${message}\"\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn0
echo "Sent at: `date`" >> $slack_notify_out_fn0



curl -k --data-urlencode "file=${img_file_path1}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'
echo "`date --iso-8601=seconds`" >> $slack_notify_out_fn1
echo "command used during processing:" >> $slack_notify_out_fn1
echo "curl -k --data-urlencode \"file=${img_file_path1}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn1
echo "command to use for debuggging:" >> $slack_notify_out_fn1
echo "curl -k --data-urlencode \"file=${img_file_path1}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn1
#echo "curl -k --data-urlencode \"file=${img_file_path1}\" --data-urlencode \"message=\"${message}\"\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn1
echo "Sent at: `date`" >> $slack_notify_out_fn1

curl -k --data-urlencode "file=${img_file_path2}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'
echo "`date --iso-8601=seconds`" >> $slack_notify_out_fn2
echo "command used during processing:" >> $slack_notify_out_fn2
echo "curl -k --data-urlencode \"file=${img_file_path2}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn2
echo "command to use for debuggging:" >> $slack_notify_out_fn2
echo "curl -k --data-urlencode \"file=${img_file_path2}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn2
#echo "curl -k --data-urlencode \"file=${img_file_path1}\" --data-urlencode \"message=\"${message}\"\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn1
echo "Sent at: `date`" >> $slack_notify_out_fn2


curl -k --data-urlencode "file=${img_file_path3}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'
echo "`date --iso-8601=seconds`" >> $slack_notify_out_fn3
echo "command used during processing:" >> $slack_notify_out_fn3
echo "curl -k --data-urlencode \"file=${img_file_path3}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn3
echo "command to use for debuggging:" >> $slack_notify_out_fn3
echo "curl -k --data-urlencode \"file=${img_file_path3}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn3
#echo "curl -k --data-urlencode \"file=${img_file_path1}\" --data-urlencode \"message=\"${message}\"\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn1
echo "Sent at: `date`" >> $slack_notify_out_fn3

exit $?







