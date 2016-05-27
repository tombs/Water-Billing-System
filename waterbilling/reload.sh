##### MIGRATION  START 

# 1) Drop / Sync DB
dropdb wbs -h localhost -U postgres;createdb wbs -h localhost --owner wbs -U postgres;python manage.py syncdb
# 2) Load Rates, Rate Charges, Account Types, Billing Schedules, Business Date (with Active Period)
python manage.py dataloader --rate core/fixtures/rate.csv;python manage.py dataloader --accounttype core/fixtures/accounttype.csv;python manage.py dataloader --ratecharge core/fixtures/ratecharge.csv;python manage.py dataloader --billingschedule core/fixtures/billingschedule.csv; python manage.py dataloader --business-date 2014-03-14 --active-period 2014-03-14;
# 3) Load Migrated AEMI data with initial balances starting from Billing of February 18 (Post-Billing, January 11 to February 10 period)
python manage.py dataloader --migrate core/fixtures/felizana_customer_info_2014-03.csv
# 4) Load AEMI customer payments. Last payment is as of March 15, 2014 (Pre-Billing, February 11 to March 10 period)
python manage.py dataloader --payment core/fixtures/paymentuploadfinal.xlsx
# 5) Load Business Date for February 11 to March 10 Reading period (March 16 to April 15 Billing Period), Set that period as Active period
python manage.py dataloader --business-date 2014-03-16 --active-period 2014-03-16 
# 6) Upload MeterReads (Reading Period:  February 11 to March 10, Billing Period, March 16 to April 15)
python manage.py dataloader --meterread core/fixtures/meterreaduploadfinal.xlsx
# 7) Generate bills (Billing, February 11 to March 10 Reading period)
python manage.py generate --type bill --business-date 2014-03-16 --create --username admin --password password
# 8) Generate compiled Bills PDF, for download at Bills Page
python manage.py generate --type bill --business-date 2014-03-16 --file-prefix BILL --pdf --username admin --password password
# 9) Set current date and business period
python manage.py dataloader --business-date 2014-03-31 --active-period 2014-03-31
# 10) Generate Notices (Billing, February 11 to March 10 Reading period)
python manage.py generate --type notice --business-date 2014-03-31 --file-prefix NOTICE --create
# 11)  Generate compiled Notices PDF, for download at Notices Page
python manage.py generate --type notice --business-date 2014-03-31 --file-prefix NOTICE --pdf --username admin --password password
# 12) Set current date and business period
python manage.py dataloader --business-date now --active-period now 

##### MIGRATION  END
