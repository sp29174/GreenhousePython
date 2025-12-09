import datetime
from datetime import timedelta, timezone, tzinfo
from suntime import Sun, SunTimeException
import RPi.GPIO as GPIO

# Lighting GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)

def lights(light_length):
  latitude = 43.0972
  longitude = -89.5043

  mcpasd = datetime.datetime.now(timezone.utc) - timedelta(hours=5)

  sun = Sun(latitude, longitude)

  light_on = False

  # Get today's sunrise and sunset in CST
  today_sr = sun.get_sunrise_time() + timedelta(hours=7)
  today_ss = sun.get_sunset_time() + timedelta(hours=7)
  if today_sr > mcpasd:
    today_sr = today_sr - timedelta(days=1)
  if today_sr > today_ss:
    today_ss = today_ss + timedelta(days=1)
    
  today_suntime = today_ss - today_sr

  light_on = today_suntime - today_suntime + timedelta(hours = light_length)

  today_suntime = mcpasd - today_sr

  if(mcpasd.time() > today_ss.time() and today_suntime < light_on):
    light_on = True
  else:
    light_on = False
  GPIO.output(21, True)

