import datetime
from datetime import timedelta, timezone, tzinfo
from suntime import Sun, SunTimeException
import RPi.GPIO as GPIO

# Lighting GPIO (GPIO pinouts will probably have to change when we get things working)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)

def lights(light_length):
  latitude = 43.0972
  longitude = -89.5043

  mcpasd = datetime.datetime.now() - timedelta(hours=6)

  sun = Sun(latitude, longitude)

  light_on = False

  # Get today's sunrise and sunset in CST
  today_sr = sun.get_sunrise_time() - timedelta(hours=6)
  today_ss = sun.get_sunset_time() - timedelta(hours=6)
  # unsure of use of this
  if today_sr > mcpasd:
    today_sr = today_sr - timedelta(days=1)
  if today_sr > today_ss:
    today_ss = today_ss + timedelta(days=1)
    
  today_suntime = today_ss - today_sr

  if(mcpasd > today_sr and mcpasd < today_ss):
    light_on = False
    return light_on
  else:
    light_on = True
    return light_on
  GPIO.output(21, True)


