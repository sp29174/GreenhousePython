import cameraControl
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
import time

# solenoid opens when 12V applied at 0.3A

dataIndex = open("/home/Gardener/GreenhousePython/images/dataIndex.txt", "r+")
DataA = cameraControl.getDataAttributes()
print(cameraControl.getDataAttributes())

for element in DataA:
    print(element)
    print(type(element))

DataA = cameraControl.cameraCapture(DataA)
print(DataA)
'''
picam2 = Picamera2()
camera_config = picam2.create_still_configuration()
print(camera_config)
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("test.jpg")
'''

'''
GPIO.setmode(GPIO.BCM)
print(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
print("LED on")
GPIO.output(18, GPIO.HIGH)
time.sleep(1)
print("LED off")
GPIO.output(18, GPIO.LOW)
'''
