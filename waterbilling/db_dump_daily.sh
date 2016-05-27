#!/bin/sh
NOW=$(date +"%Y-%m-%d")
dump_file="/home/wbs/webapps/waterbilling/src/waterbilling/db_dumps/wbs_end-of-day_backup_$NOW.sql.gz"
pgdump_command="/usr/bin/pg_dump"
pg_user="wbs"
pg_db="wbs"

$pgdump_command -U $pg_user -h localhost $pg_db | gzip -9 > $dump_file


emails_to="edwin.tumbaga@gmail.com"
email_from="apebi.ph@gmail.com"
emails_me="edwin.tumbaga@gmail.com"
subject="Water Billing: Database Backup --> $NOW"
message="Water Billing: Database Backup --> $NOW"
server="smtp.gmail.com:587"
user="apebi.ph@gmail.com"
password="apebifamily"
option="tls=yes"

sendemail -f $email_from -t "$emails_to" -u "$subject" -m "$message"  -s $server -xu $user -xp $password -o $option
