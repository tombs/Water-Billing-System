#!/bin/sh
envi="/home/wbs/envs/waterbilling"
app_dir="/home/wbs/webapps/waterbilling/src/waterbilling/waterbilling"
wbs_user="admin"
wbs_pswd="captainbuggy"

$envi/bin/python $app_dir/manage.py generate --type notice --business-date now --file-prefix NOTICE --monitor --username $wbs_user --password $wbs_pswd  2>&1 | tee $app_dir/logs/monitor_notices.log  &

NOW=$(date +"%Y-%m-%d")
emails_to="edwin.tumbaga@gmail.com"
email_from="apebi.ph@gmail.com"
emails_me="edwin.tumbaga@gmail.com"
subject="Water Billing: Notices Compiled PDF Monitor Now Running"
message="Water Billing: Notices Compiled PDF Monitor Now Running" 
server="smtp.gmail.com:587"
user="apebi.ph@gmail.com"
password="apebifamily"
option="tls=yes"
sendemail -f $email_from -t "$emails_to" -u "$subject" -m "$message"  -s $server -xu $user -xp $password -o $option
