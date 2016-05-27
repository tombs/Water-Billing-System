#!/bin/sh
envi="/home/wbs/envs/waterbilling"
app_dir="/home/wbs/webapps/waterbilling/src/waterbilling/waterbilling"

$envi/bin/python $app_dir/manage.py dataloader --business-date now --active-period now

NOW=$(date +"%Y-%m-%d")
emails_to="edwin.tumbaga@gmail.com"
email_from="apebi.ph@gmail.com"
emails_me="edwin.tumbaga@gmail.com"
subject="Water Billing: New Business Date Set --> $NOW"
message="Water Billing: New Business Date Set --> $NOW" 
server="smtp.gmail.com:587"
user="apebi.ph@gmail.com"
password="apebifamily"
option="tls=yes"

sendemail -l /home/wbs/email.log -v -f $email_from -t "$emails_to" -u "$subject" -m "$message"  -s $server -xu $user -xp $password -o $option
