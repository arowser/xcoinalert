xcoinalert
==========

free sms bitcoin, litecoin price alter

need pyfection support
some code based gcms

support btc-e.com 
support ltcoin btcoin price alert

configure these values in xcoinalert.py before use:
```

#send sms by
useFection = True  #only for china mobile user
useGoogle = True 

#pyfection settings
username =       
password =       

#google settings 
client_id =      
client_secret =  

#set alert price with xx$
btcLowPrice = 500  #$
btcHighPrice = 600
ltcLowPrice = 12 
ltcHighPrice = 20
                 

#check delay time, default check every 10 minutes
delaytime = 10 * 60
```
How to get google  client_id and client_secret?

Setup a Google account if you don't already have one (https://gmail.com).
In Google Calendar (https://calendar.google.com), under 'Calendar Settings' -> 'Mobile Setup', enter your mobile number and verify it.
In API Console (https://code.google.com/apis/console), click 'Create Project' and enable 'Calendar API'.
In API Console, under 'API Access', click 'Create an OAuth 2.0 client ID...' and input 'gcsms' as Product Name. Click 'Next' and under 'Application type' choose 'Installed application'. It should default to 'Other' in 'Installed application type' section. Finalize by clicking 'Create Client ID' and note down 'Client ID' and 'Client Secret' from the following window.

