#!/bin/sh
envi="/home/wbs/webapps/waterbilling"
app_dir="/home/wbs/webapps/waterbilling/src/waterbilling/waterbilling"

$envi/bin/python $app_dir/manage.py dataloader --business-date now --active-period now

NOW=$(date +"%Y-%m-%d")
emails_to="edwin.tumbaga@woohoow.com,dax.reyes@woohoow.com,rob.nanola@woohoow.com,mara.reyes@woohoow.com"
email_from="noreply@woohoow.com"
emails_me="edwin.tumbaga@woohoow.com"
subject="Water Billing: New Business Date Set --> $NOW"
message="Water Billing: New Business Date Set --> $NOW" 
server="smtp.gmail.com:587"
user="noreply@woohoow.com"
password="IeShe5oo"
option="tls=yes"

sendemail -f $email_from -t "$emails_to" -u "$subject" -m "$message"  -s $server -xu $user -xp $password -o $option
