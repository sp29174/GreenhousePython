import RPi.GPIO as GPIO
import time
import mcp as MCP


GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)

MAX_VALUE = 50000

#break things into 20% intervals from 0 to 50k based on the values returned from the MCP

def water(percent):
	if(percent == 0):
		GPIO.output(16, GPIO.LOW)
		print("low")
		return
	moisture = 0
	for x in range(3):
		moisture += MCP.get_data(x)
	moisture = moisture / 3
	if(MAX_VALUE / (100 / percent) > moisture):
		GPIO.output(16, GPIO.HIGH)
		print("high")
	else:
		GPIO.output(16, GPIO.LOW)
		print("low")
		


GPIO.cleanup()
