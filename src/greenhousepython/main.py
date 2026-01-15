# 11/11/2025
# 
# The main file.

# CFG ****************************************************************************************
norm_font = 'Calibri 18'
recording_status = "Start Recording"
light_length = 16
header_font = 'Calibri 50 bold'
resolution = '1920x1080'
latitude = 43.0972
longitude = -89.5043
dt = 200
lightPin = 21
waterPin = 16
MAX_VALUE = 1024
use_camera = False
file_debug = True
use_gpio = False

if use_camera:
	from picamera2 import Picamera2
else:
	from nonsense import Picamera2
if use_gpio:
	import RPi.GPIO as GPIO
	import busio
	import digitalio
	import board
	import adafruit_mcp3xxx.mcp3008 as MCP
	from adafruit_mcp3xxx.analog_in import AnalogIn
else:
	from nonsense import GPIO, busio, digitalio, board, MCP, AnalogIn
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import datetime
from datetime import timedelta, timezone
from suntime import Sun

# init part 1

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.CE0)
# create the mcp object
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)#these pins should not be hard-coded!
chan1 = AnalogIn(mcp, MCP.P1)
chan2 = AnalogIn(mcp, MCP.P2)
chan_list = [chan0, chan1, chan2]
GPIO.setmode(GPIO.BCM)
GPIO.setup(waterPin, GPIO.OUT)
GPIO.setup(lightPin, GPIO.OUT)

# methods   ***********************************************************************************

def testing():
	print(light_length)
	
# new_light_control
# 
# Get user input and store it
# Clear the input
# Set light_length to the stored input value

def new_light_control():
	global light_length
	global light_cycle
	new_light_length = light_cycle.get()
	light_cycle.delete(0, len(new_light_length))
	if(new_light_length != ""):
		try:
			if(int(new_light_length) <= 24):
				light_length = int(new_light_length)
			else:
				light_length = 24
			print(light_length)
			light_label.config(text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + str(light_length) + " hours per day.")
		except ValueError as e:
			print("Invalid value entered. Please enter a valid value.")
			print("length is still " + str(light_length))

#break things into 20% intervals from 0 to 50k based on the values returned from the MCP
def water(control_parameter):
	global MAX_VALUE
	moisture = 0
	for x in range(3):#this logic must be fixed, it does not comply w/ the design reqs
		moisture += get_data(x)
	moisture = moisture / 3
	if(MAX_VALUE * control_parameter > moisture):
		GPIO.output(waterPin, GPIO.HIGH)
		print("high")
	else:
		GPIO.output(waterPin, GPIO.LOW)
		print("low")
		
def image_update(attrs,camera):
    global image_label
    cameraCapture(attrs,camera)
    img = ImageTk.PhotoImage(Image.open(lastFileName()))
    image_label.configure(image=img) 
    image_label.image = img
	
# TODO: Fix
def repeater(dt,latitude,longitude):
	current_time = datetime.datetime.now(timezone.utc) - timedelta(hours=5)#add variable timezone, this is stuck on UTC-5
	four_pm = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day) + timedelta(hours=16)#This is the least efficient way to do this
	#print(current_time.time())
	#print(four_pm.time())
	#print(current_time.time() > four_pm.time())
	if current_time.time() > four_pm.time():
		light(light_length,latitude,longitude,theSun)
	window.after(dt, lambda : repeater(dt,latitude,longitude))

def light(light_length,latitude,longitude,sun):
  mcpasd = datetime.datetime.now(timezone.utc) - timedelta(hours=5)
  # Get today's sunrise and sunset in CST
  today_sr = sun.get_sunrise_time() + timedelta(hours=7)
  today_ss = sun.get_sunset_time() + timedelta(hours=7)
  if today_sr > mcpasd:
    today_sr = today_sr - timedelta(days=1)
  if today_sr > today_ss:
    today_ss = today_ss + timedelta(days=1)
  today_suntime = today_ss - today_sr
  light_on_time = today_suntime - today_suntime + timedelta(hours = light_length)
  today_suntime = mcpasd - today_sr
  if(mcpasd.time() > today_ss.time() and today_suntime < light_on_time):
    light_on = True
  else:
    light_on = False
  GPIO.output(lightPin, light_on)
	
def getDataAttributes():
    dataIndex = open("dataIndex.txt", "r")#this must be fixed
    last_file_number = dataIndex.readline().split()[1]
    last_file_number = int(last_file_number)
    interval_in_seconds = dataIndex.readline().split()[1]
    interval_in_seconds = int(interval_in_seconds)
    prefix = dataIndex.readline().split()[1]
    dataIndex.close()
    return [last_file_number, interval_in_seconds, prefix]

# sets attributes in dataindex.txt file
def setAttributes(attributes):
    dataIndex = open("dataIndex.txt", "w")
    dataIndex.writelines(["last_file_number: " + str(attributes[0]), '\n', "interval_in_seconds: " + str(attributes[1]), '\n', "file_name_prefix: " + attributes[2]])
    dataIndex.close()

#input camera attributes and capture image, updates attributes and returns new attributes
def cameraCapture(attributes,camera):
	if not use_camera:
		return attributes
	name = "../../images/" + attributes[2] + (str(attributes[0] + 1)) + ".jpg"
	camera.capture_file(name)
	attributes[0] += 1
	setAttributes(attributes)
	return attributes

def lastFileName():
    attributes = getDataAttributes()
    if (attributes[0] == 0):
        return "../../images/placeholder.jpg"
    return "../../images/" + attributes[2] + str(attributes[0]) + ".jpg"

def create_video(image_paths, output_video_path, fps=24, size=None):
	if not image_paths:
		raise ValueError("The list of image paths is empty")
	print(":IORHGUIGHUBHSULIGH")
	print(image_paths[0])
	first_frame = cv2.imread(image_paths[0])
	if first_frame is None:
		raise ValueError("Cannot read image at path")
	if size is None:
		height, width, _ = first_frame.shape
		size = (width, height)
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter(output_video_path, fourcc, fps, size)
	for path in image_paths:
		frame = cv2.imread(path)
		if frame is None:
			print(f"Warning: Could not read {path}, skipping.")
			continue
		frame_resized = cv2.resize(frame, size)
		out.write(frame_resized)
	out.release()
	print(f"Vido saved to {output_video_path}")

def see_data():
	print('Chan 0 Raw ADC Value: ', chan0.value)
	print('Chan 0 ADC Voltage: ' + str(chan0.voltage) + 'V')
	print('Chan 1 Raw ADC Value: ', chan1.value)
	print('Chan 1 ADC Voltage: ' + str(chan1.voltage) + 'V')
	print('Chan 2 Raw ADC Value: ', chan2.value)
	print('Chan 2 ADC Voltage: ' + str(chan2.voltage) + 'V')

def get_data(num):
	num = int(num)
	return(chan_list[num].value)

def compare(num):
	for x in chan_list:
		if(num > 1.2 * x.value or num < 0.8 * x.value):
			return False
	return True
	
# GUI ****************************************************************************************	

# window
window = tk.Tk()
window.title =('Greenhouse')
window.geometry(resolution)#This needs to be changed

# title
title_label = ttk.Label(master = window, text = 'Greenhouse', font = header_font)
title_label.pack()

#first layer
layer1_frame = ttk.Frame(master = window)

# image information
image_frame = ttk.Frame(master = layer1_frame)
image = Image.open(lastFileName())
image2 = image.resize((640, 480))
last_plant_image = ImageTk.PhotoImage(image2)#BUG: initial image is too big
image_label = ttk.Label(master = image_frame, image = last_plant_image)

image_label_frame = ttk.Frame(master = image_frame)
interval_label = ttk.Label(master = image_label_frame, text = 'Interval is set to ', font = norm_font)
capture_label = ttk.Label(master = image_label_frame, text = 'There have been __ captures\nsince last time-lapse.', font = norm_font)

# packing image stuff
image_label.pack(side = 'left', padx = 10, pady = 10)
interval_label.pack(padx = 5, pady = 30)
capture_label.pack(padx = 5, pady = 5)
image_label_frame.pack(side = 'left', padx = 10, pady = 10)
image_frame.pack(side = 'left')

# far right info
top_right_frame = ttk.Frame(master = layer1_frame)
last_capture = ttk.Label(master = top_right_frame, text = 'Last capture was taken ___ minutes ago.', font = norm_font)
zone_frame = ttk.Frame(master = top_right_frame)
zone_label = ttk.Label(master = zone_frame, text = "Zone Moistures", font = norm_font)
bzone1 = ttk.Button(master = zone_frame, text = "Left Bed: " + str(get_data(0)))#These only update once
bzone2 = ttk.Button(master = zone_frame, text = "Middle Bed: " + str(get_data(1)))
bzone3 = ttk.Button(master = zone_frame, text = "Right Bed: " + str(get_data(2)))

moisture_frame = ttk.Frame(master = top_right_frame)
moisture_label = ttk.Label(master = moisture_frame, text = "Select Moisture Level", font = norm_font)
top_buttons = ttk.Frame(master = moisture_frame)
bottom_buttons = ttk.Frame(master = moisture_frame)
bmoisture0 = ttk.Button(master = top_buttons, text = "0%", command = lambda : water(0))#these should not be hardcoded
bmoisture1 = ttk.Button(master = top_buttons, text = "20%", command = lambda : water(0.2))
bmoisture2 = ttk.Button(master = top_buttons, text = "40%", command = lambda : water(0.4))
bmoisture3 = ttk.Button(master = bottom_buttons, text = "60%", command = lambda : water(0.6))
bmoisture4 = ttk.Button(master = bottom_buttons, text = "80%", command = lambda : water(0.8))
bmoisture5 = ttk.Button(master = bottom_buttons, text = "100%", command = lambda : water(1))

# far right packing
last_capture.pack(padx = 10, pady = 20)
zone_label.pack(padx = 10, pady = 20)
bzone1.pack(side = 'left', padx = 5, pady = 5)
bzone2.pack(side = 'left', padx = 5, pady = 5)
bzone3.pack(side = 'left', padx = 5, pady = 5)
zone_frame.pack(padx = 10, pady = 10)

moisture_label.pack(padx = 5, pady = 20)
bmoisture0.pack(side = 'left', padx = 5, pady = 5)
bmoisture1.pack(side = 'left', padx = 5, pady = 5)
bmoisture2.pack(padx = 5, pady = 5)
top_buttons.pack(padx = 5, pady = 5)
bmoisture3.pack(side = 'left', padx = 5, pady = 5)
bmoisture4.pack(side = 'left', padx = 5, pady = 5)
bmoisture5.pack(padx = 5, pady = 5)
bottom_buttons.pack(padx = 5, pady = 5)
moisture_frame.pack(padx = 10, pady = 10)

top_right_frame.pack(padx=10, pady=10)
layer1_frame.pack(padx = 20, pady = 20)

# lower layer
layer2_frame = ttk.Frame(master = window)

# captures picture, command= cameraCapture
# ISSUE: taking picture on boot
#I disagree, that's a feature!
manual_pic_button = ttk.Button(master = layer2_frame, text = "Take Manual\nPicture", command = lambda : image_update(attrs,theCamera))

# should start recording function
start_record = ttk.Button(master = layer2_frame, text = recording_status)
light_label = ttk.Label(master = layer2_frame, text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + str(light_length) + " hours per day.", font = norm_font)
light_cycle = ttk.Entry(master = layer2_frame)
enter_button = ttk.Button(master = layer2_frame, text = "Enter Hours", command = new_light_control)

#packing lower layer
manual_pic_button.pack(side = 'left', padx = 25, pady = 5)
start_record.pack(side = 'left', padx = 25, pady = 5)
light_label.pack(padx = 25, pady = 5)
light_cycle.pack(padx = 25, pady = 5)
enter_button.pack(padx = 25, pady = 5)
layer2_frame.pack(padx = 5, pady = 5)


# startup ****************************************************************************************

#get attrs
attrs = getDataAttributes()
see_data()
theSun = Sun(latitude, longitude)
theCamera = Picamera2()
camera_cfg = theCamera.create_still_configuration()
theCamera.start()
window.after(dt, lambda : repeater(dt,latitude,longitude))
window.mainloop()





