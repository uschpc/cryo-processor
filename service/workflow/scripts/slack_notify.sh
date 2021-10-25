#!/bin/bash
img_file_path=$1
#gctf_output_fn=$2
#mc2_output_fn=$3
#slack_notify_out_fn=$4
slack_notify_out_fn=$2
#resolution="$2"
#shifts="$3"

#PROGNAME=`type $0 | awk '{print $3}'`  # search for executable on path
#PROGDIR=`dirname $PROGNAME`            # extract directory of program
#PROGNAME=`basename $PROGNAME`          # base name of program



#resolution=`$PROGDIR/get_data.sh ctf_r $gctf_output_fn`
#asti=resolution=`$PROGDIR/get_data.sh ctf_a $gctf_output_fn`
#shifts=`$PROGDIR/get_data.sh mc $mc2_output_fn`

#echo "${resolution}" >> $slack_notify_out_fn
#echo "" >> $slack_notify_out_fn

#shifts=`cat ${mc2_output_fn} | grep "...... Frame"`

#echo "${shifts}" >> $slack_notify_out_fn
#echo "" >> $slack_notify_out_fn

#message="\"Estimated resolution limit: *${resolution}Å*\nMotion correction shifts:\n${shifts}\""

#echo "${message}" >> $slack_notify_out_fn
#echo "" >> $slack_notify_out_fn

#curl --data-urlencode "file=${img_file_path}" --data-urlencode "message=$(printf 'Estimated resolution limit: *%sÅ*\nMotion correction shifts:\n```%s```\n' "${resolution}" "${shifts}")" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'

curl --data-urlencode "file=${img_file_path}" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'

echo "command used during processing:" >> $slack_notify_out_fn
echo "curl --data-urlencode \"file=${img_file_path}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn
echo "command to use for debuggging:" >> $slack_notify_out_fn
echo "curl --data-urlencode \"file=${img_file_path}\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn


#echo "curl --data-urlencode \"file=${img_file_path}\" --data-urlencode \"message=\"${message}\"\" -X POST 'https://hpcaccount.usc.edu/public/cryoem/slack/postimage.php'" >> $slack_notify_out_fn

exit $?



