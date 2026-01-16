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
mode = "GUI"
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
if mode == "GUI":
	from PIL import ImageTk
	import tkinter as tk
	from tkinter import ttk
else:
	assert True == False#Not implemeted
import cv2
from PIL import Image
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
	
# new_light_control
# 
# Get user input and store it
# Clear the input
# Set light_length to the stored input value

def new_light_control(mode,output):
	global light_lengthx
	if mode == "GUI":
		light_cycle = output.light_cycle
		new_light_length = light_cycle.get()
		light_cycle.delete(0, len(new_light_length))
	else:
		assert True==False#Not Implemented
	if(new_light_length != ""):
		try:
			if(int(new_light_length) <= 24):
				light_length = int(new_light_length)
			else:
				light_length = 24
			print(light_length)
			if mode == "GUI":
				output.light_label.config(text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + str(light_length) + " hours per day.")
			else:
				assert True==False#Not Implemented
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

# TODO: Fix
def repeater(dt,latitude,longitude,mode,output):
	current_time = datetime.datetime.now(timezone.utc) - timedelta(hours=5)#add variable timezone, this is stuck on UTC-5
	four_pm = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day) + timedelta(hours=16)#This is the least efficient way to do this
	#print(current_time.time())
	#print(four_pm.time())
	#print(current_time.time() > four_pm.time())
	if current_time.time() > four_pm.time():
		light(light_length,latitude,longitude,theSun)
	if mode == "GUI":
		output.window.after(dt, lambda : repeater(dt,latitude,longitude,mode,output))
	else:
		assert True==False#Not Implemented

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

class GUI:
	def __init__(self,resolution,header_font,norm_font,recording_status):
		# window
		self.window = tk.Tk()
		self.window.title =('Greenhouse')
		self.window.geometry(resolution)#This needs to be changed
		
		# title
		self.title_label = ttk.Label(master = self.window, text = 'Greenhouse', font = header_font)
		self.title_label.pack()
		
		#first layer
		self.layer1_frame = ttk.Frame(master = self.window)
		
		# image information
		self.image_frame = ttk.Frame(master = self.layer1_frame)
		self.image = Image.open(lastFileName())
		self.image2 = self.image.resize((640, 480))
		self.last_plant_image = ImageTk.PhotoImage(self.image2)#BUG: initial image is too big
		self.image_label = ttk.Label(master = self.image_frame, image = self.last_plant_image)
		
		self.image_label_frame = ttk.Frame(master = self.image_frame)
		self.interval_label = ttk.Label(master = self.image_label_frame, text = 'Interval is set to ', font = norm_font)
		self.capture_label = ttk.Label(master = self.image_label_frame, text = 'There have been __ captures\nsince last time-lapse.', font = norm_font)
		
		# packing image stuff
		self.image_label.pack(side = 'left', padx = 10, pady = 10)
		self.interval_label.pack(padx = 5, pady = 30)
		self.capture_label.pack(padx = 5, pady = 5)
		self.image_label_frame.pack(side = 'left', padx = 10, pady = 10)
		self.image_frame.pack(side = 'left')
		
		# far right info
		self.top_right_frame = ttk.Frame(master = self.layer1_frame)
		self.last_capture = ttk.Label(master = self.top_right_frame, text = 'Last capture was taken ___ minutes ago.', font = norm_font)
		self.zone_frame = ttk.Frame(master = self.top_right_frame)
		self.zone_label = ttk.Label(master = self.zone_frame, text = "Zone Moistures", font = norm_font)
		self.bzone1 = ttk.Button(master = self.zone_frame, text = "Left Bed: " + str(get_data(0)))#These only update once
		self.bzone2 = ttk.Button(master = self.zone_frame, text = "Middle Bed: " + str(get_data(1)))
		self.bzone3 = ttk.Button(master = self.zone_frame, text = "Right Bed: " + str(get_data(2)))

		self.moisture_frame = ttk.Frame(master = self.top_right_frame)
		self.moisture_label = ttk.Label(master = self.moisture_frame, text = "Select Moisture Level", font = norm_font)
		self.top_buttons = ttk.Frame(master = self.moisture_frame)
		self.bottom_buttons = ttk.Frame(master = self.moisture_frame)
		self.bmoisture0 = ttk.Button(master = self.top_buttons, text = "0%", command = lambda : water(0))#these should not be hardcoded
		self.bmoisture1 = ttk.Button(master = self.top_buttons, text = "20%", command = lambda : water(0.2))
		self.bmoisture2 = ttk.Button(master = self.top_buttons, text = "40%", command = lambda : water(0.4))
		self.bmoisture3 = ttk.Button(master = self.bottom_buttons, text = "60%", command = lambda : water(0.6))
		self.bmoisture4 = ttk.Button(master = self.bottom_buttons, text = "80%", command = lambda : water(0.8))
		self.bmoisture5 = ttk.Button(master = self.bottom_buttons, text = "100%", command = lambda : water(1))
		
		# far right packing
		self.last_capture.pack(padx = 10, pady = 20)
		self.zone_label.pack(padx = 10, pady = 20)
		self.bzone1.pack(side = 'left', padx = 5, pady = 5)
		self.bzone2.pack(side = 'left', padx = 5, pady = 5)
		self.bzone3.pack(side = 'left', padx = 5, pady = 5)
		self.zone_frame.pack(padx = 10, pady = 10)
		
		self.moisture_label.pack(padx = 5, pady = 20)
		self.bmoisture0.pack(side = 'left', padx = 5, pady = 5)
		self.bmoisture1.pack(side = 'left', padx = 5, pady = 5)
		self.bmoisture2.pack(padx = 5, pady = 5)
		self.top_buttons.pack(padx = 5, pady = 5)
		self.bmoisture3.pack(side = 'left', padx = 5, pady = 5)
		self.bmoisture4.pack(side = 'left', padx = 5, pady = 5)
		self.bmoisture5.pack(padx = 5, pady = 5)
		self.bottom_buttons.pack(padx = 5, pady = 5)
		self.moisture_frame.pack(padx = 10, pady = 10)
		
		self.top_right_frame.pack(padx=10, pady=10)
		self.layer1_frame.pack(padx = 20, pady = 20)
		
		# lower layer
		self.layer2_frame = ttk.Frame(master = self.window)
		
		# captures picture, command= cameraCapture
		# ISSUE: taking picture on boot
		#I disagree, that's a feature!
		self.manual_pic_button = ttk.Button(master = self.layer2_frame, text = "Take Manual\nPicture", command = lambda : self.image_update(attrs,theCamera))
		
		# should start recording function
		self.start_record = ttk.Button(master = self.layer2_frame, text = recording_status)
		self.light_label = ttk.Label(master = self.layer2_frame, text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + str(light_length) + " hours per day.", font = self.norm_font)
		self.light_cycle = ttk.Entry(master = self.layer2_frame)
		self.enter_button = ttk.Button(master = self.layer2_frame, text = "Enter Hours", command = lambda : new_light_control("GUI", this))
		
		#packing lower layer
		self.manual_pic_button.pack(side = 'left', padx = 25, pady = 5)
		self.start_record.pack(side = 'left', padx = 25, pady = 5)
		self.light_label.pack(padx = 25, pady = 5)
		self.light_cycle.pack(padx = 25, pady = 5)
		self.enter_button.pack(padx = 25, pady = 5)
		self.layer2_frame.pack(padx = 5, pady = 5)
		self.window.after(dt, lambda : repeater(dt,latitude,longitude,"GUI",this))
		self.window.mainloop()
	def image_update(self,attrs,camera):
		cameraCapture(attrs,camera)
		img = ImageTk.PhotoImage(Image.open(lastFileName()))
		self.image_label.configure(image=img) 
		self.image_label.image = img

# CLI ****************************************************************************************	

class CLI:
	pass


# startup ****************************************************************************************

#get attrs
attrs = getDataAttributes()
see_data()
theSun = Sun(latitude, longitude)
theCamera = Picamera2()
camera_cfg = theCamera.create_still_configuration()
theCamera.start()
if type == "GUI":
	gui = GUI(resolution,header_font,norm_font,recording_status)
elif type == "CLI":
	cli = CLI()
else:
	assert True==False#Not implemented






