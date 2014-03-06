"""Xcoin Alert

Usage:

"""
import requests
import json
import time
from datetime import datetime
import logging
from pyfetion import PyFetion

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

useGoogle = True
useFection = True
#check delay time, default check every 10 minutes
delaytime = 10 * 60

try:
  from urllib2 import urlopen, Request
  from urllib import urlencode
except ImportError:
  from urllib.parse import urlencode
  from urllib.request import urlopen, Request

_CALS_PATH = '/calendars'
_CAL_LIST_PATH = '/users/me/calendarList'
_CAL_URL = 'https://www.googleapis.com/calendar/v3'
_DEV_CODE_ENDPT = 'https://accounts.google.com/o/oauth2/device/code'
_EVENT_PATH = '/calendars/%s/events'
_GLOBAL = 'global'
_GRANT_TYPE = 'http://oauth.net/grant_type/device/1.0'
_PROGNAME = 'gcsms'
_SCOPE = 'https://www.googleapis.com/auth/calendar'
_TOKEN_ENDPT = 'https://accounts.google.com/o/oauth2/token'

cfg = {}

class GCSMSError(Exception):
  """GCSMS specific exceptions."""
  pass

def cmd_auth(cfg):
  """Authenticate with Google."""

  # Obtain a user code

  req = Request(
    _DEV_CODE_ENDPT,
    data=urlencode({
      'client_id': cfg.get('client_id'),
      'scope': _SCOPE
    }).encode('utf8')
  )
  ucres = json.loads(urlopen(req).read().decode('utf8'))

  print("Visit %s\nand enter the code '%s'\n"
        "Waiting for you to grant access ..."
        % (ucres['verification_url'], ucres['user_code']))

  # Obtain refresh token by polling token end point

  req = Request(
    _TOKEN_ENDPT,
    data=urlencode({
      'client_id': cfg.get('client_id'),
      'client_secret': cfg.get('client_secret'),
      'code': ucres['device_code'],
      'grant_type': _GRANT_TYPE
    }).encode('utf8')
  )

  while True:
    rtres = json.loads(urlopen(req).read().decode('utf8'))
    error = rtres.get('error', None)
    refresh_token = rtres.get('refresh_token', None)
    if error in ('slow_down', 'authorization_pending'):
      time.sleep(int(ucres['interval']))
    elif error:
      raise GCSMSError("got auth error '%s' while polling" % error)
    elif refresh_token:
      break
    else:
      raise GCSMSError('unexpected error while polling')

  # Store the refresh token in the config file

  cfg['refresh_token'] = refresh_token

  print("Successful.")

def cmd_send(cfg, text):
  """Send SMS."""

  try:
    refresh_token = cfg.get('refresh_token')
  except NoOptionError:
    raise GCSMSError("you must first run 'gcsms auth' to authenticate")

  # Obtain an access token

  req = Request(
    _TOKEN_ENDPT,
    data=urlencode({
      'client_id': cfg.get('client_id'),
      'client_secret': cfg.get('client_secret'),
      'refresh_token': refresh_token,
      'grant_type': 'refresh_token'
    }).encode('utf8')
  )
  tres = json.loads(urlopen(req).read().decode('utf8'))
  access_token = tres.get('access_token', None)
  if access_token is None:
    raise GCSMSError("you must first run 'gcsms auth' to authenticate")
  

  # Get a list of all calendars

  callist = do_api(
    '%s?minAccessRole=writer&showHidden=true' % _CAL_LIST_PATH,
    access_token
  )['items']
  cal = None
  for c in callist:
    if c['summary'] == _PROGNAME:
      cal = c['id']
      break

  # If our calendar doesn't exist, create one

  if cal is None:
    cres = do_api(_CALS_PATH, access_token, {'summary': _PROGNAME})
    if cres.get('summary', None) == _PROGNAME:
      cal = cres['id']
    else:
      raise GCSMSError('cannot create calendar')

  # Read the stdin and create a calendar event out of it

  #text = sys.stdin.read()
  try:
    ts = datetime.utcfromtimestamp(
      time.time() + 65).isoformat(b'T') + 'Z'
  except TypeError:
    ts = datetime.utcfromtimestamp(
      time.time() + 65).isoformat('T') + 'Z'
  event = {
    'start': {'dateTime': ts},
    'end': {'dateTime': ts},
    'reminders': {
      'useDefault': False,
      'overrides': [
        {'method': 'sms', 'minutes': 1}
      ]
    },
    'summary': text,
    'visibility': 'private',
    'transparency': 'transparent'
  }

  cres = do_api(_EVENT_PATH % cal, access_token, event)
  if cres.get('kind', None) != 'calendar#event':
    raise GCSMSError('failed to send SMS')
  
def do_api(path, auth, body = None):
  """Do a calendar API call.

  path -- access URL path
  auth -- access token
  body -- JSON request body

  """

  req = Request(
    '%s%s' % (_CAL_URL, path),
    data=json.dumps(body).encode('utf8') if body else None,
    headers={
      'Authorization': 'Bearer %s' % auth,
      'Content-type': 'application/json'
    }
  )
  return json.loads(urlopen(req).read().decode('utf8'))
 
def sms_send(text):
   if useFection:
       #send msg by fection
       f = PyFetion(username, password)
       f.send(username, text)
 
   global cfg
   if useGoogle:
      cfg['client_id'] = client_id
      cfg['client_secret'] = client_secret
      cmd_send(cfg, text)

def main():

    global cfg
    global btcLowPrice 
    global btcHighPrice
    global ltcLowPrice 
    global ltcHighPrice
 
    cfg['client_id'] = client_id
    cfg['client_secret'] = client_secret
    cmd_auth(cfg)
    while True:
      try:
        r = requests.get("https://btc-e.com/api/2/ltc_usd/ticker", verify=False)
        if r.status_code == 200:
             j = json.loads(r.text)
             sell = j['ticker']['sell']
             buy = j['ticker']['buy']
             if (float(buy) > ltcHighPrice):
                 ltcHighPrice = float(buy) + 2
                 text = "xcoinAlert: ltc-USD sell %s, buy %s " % (sell, buy)
                 sms_send(text)
             elif (float(sell) < ltcLowPrice):
                 text = "xcoinAlert: ltc-USD sell %s, buy %s " % (sell, buy)
                 ltcLowPrice = float(sell) - 2
                 sms_send(text)

        r = requests.get("https://btc-e.com/api/2/btc_usd/ticker", verify=False)
        if r.status_code == 200:
             j = json.loads(r.text)
             sell = j['ticker']['sell']
             buy = j['ticker']['buy']
             if (float(buy) > btcHighPrice):
                 text = "xcoinAlert: ltc-USD sell %s, buy %s " % (sell, buy)
                 btcHighPrice = float(buy) + 10
                 sms_send(text)
             elif (float(sell) < btcLowPrice):
                 text = "xcoinAlert: ltc-USD sell %s, buy %s " % (sell, buy)
                 btcLowPrice = float(sell) - 10
                 sms_send(text)
      except Exception, e:
        print str(e)
        sms_send("xcoinAlert fail exit")
        exit(0)
      time.sleep(delaytime)

if __name__ == '__main__':
    main() 
