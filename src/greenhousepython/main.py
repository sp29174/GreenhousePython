# 11/11/2025
# 
# The main file.

#pre-initialization

from typer import Typer, Option
app = Typer()
attrs = {}
mode = "CLI"

#read configuration information from cfg.txt and use it
def getDataAttributes():
	global attrs
	cfg = open("cfg.txt", "r")
	accumulator = {}
	for thing in cfg.readlines():#find all things seperated by newlines
		kvp = thing.split(":")#get key-value pairs
		accumulator[kvp[0]] = kvp[1].rstrip("\n")#add key-value pair to dictionary, no random trailing newline for you
	cfg.close()
	attrs = accumulator

#rewrite the list with updated values
def setAttributes():
	global attrs
	cfg = open("cfg.txt", "w")#open file to write
	accumulator = []
	keys = attrs.keys()#get all the keys
	for key in keys:
		accumulator.append(key + ":" + attrs[key])#assemble key and values into new format
		accumulator.append("\n")#seperate with newlines
	cfg.writelines(accumulator)#append to file
	cfg.close()



# Initialization ****************************************************************************************

getDataAttributes()
if attrs["use_camera"] == "True":
	from picamera2 import Picamera2
else:
	from nonsense import Picamera2
if attrs["use_gpio"] == "True":
	import RPi.GPIO as GPIO
	import busio
	import digitalio
	import board
	import adafruit_mcp3xxx.mcp3008 as MCP
	from adafruit_mcp3xxx.analog_in import AnalogIn
else:
	from nonsense import GPIO, busio, digitalio, board, MCP, AnalogIn
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import datetime
from datetime import timedelta, timezone
from suntime import Sun

# Postinitialization

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
GPIO.setup(int(attrs["waterPin"]), GPIO.OUT)
GPIO.setup(int(attrs["lightPin"]), GPIO.OUT)
theSun = Sun(float(attrs["latitude"]), float(attrs["longitude"]))
theCamera = Picamera2()
camera_cfg = theCamera.create_still_configuration()
theCamera.start()


# methods   ***********************************************************************************

#a simple command to allow the user to change settings-this lets them define nonsense parameters, but I could care less, because my getdataattributes can ignore them.
#However, this almost certainly breaks if you pass in a thing that contains a newline, which we should fix later.
@app.command()
def change_setting(key : str, value : str):
	global attrs
	attrs[key] = value
	setAttributes()

# new_light_control
# 
# Get user input and store it
# Clear the input
# Set light_length to the stored input value

def new_light_control(output = None):
	global attrs
	light_cycle = output.light_cycle
	new_light_length = light_cycle.get()
	light_cycle.delete(0, len(new_light_length))
	if(new_light_length != ""):
		try:
			if(int(new_light_length) <= 24):
				attrs["light_length"] = new_light_length
			else:
				attrs["light_length"] = "24"
			print(attrs["light_length"])
			setAttributes()
			output.light_label.config(text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + attrs["light_length"] + " hours per day.")
		except ValueError as e:
			print("Invalid value entered. Please enter a valid value.")
			print("length is still " + attrs["light_length"])

#break things into 20% intervals from 0 to 50k based on the values returned from the MCP
@app.command()
def water(input : float = None):
	global attrs
	if input != None:
		attrs["control_parameter"] = str(input)
		setAttributes()
	elif attrs["is_debug"] == "True":
		print("The system says your input is None, BTW")
	moisture = 0
	for x in range(3):#this logic must be fixed, it does not comply w/ the design reqs
		moisture += get_data(x)
	moisture = moisture / 3
	if(int(attrs["MAX_VALUE"]) * float(attrs["control_parameter"]) > moisture):
		GPIO.output(int(attrs["waterPin"]), GPIO.HIGH)
		print("high")
	else:
		GPIO.output(int(attrs["waterPin"]), GPIO.LOW)
		print("low")

# TODO: Fix the Nonsense
@app.command()
def repeater(output = None):
	global attrs
	global mode
	current_time = datetime.datetime.now(timezone.utc) - timedelta(hours=5)#add variable timezone, this is stuck on UTC-5
	four_pm = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day) + timedelta(hours=16)#This is the least efficient way to do this
	#print(current_time.time())
	#print(four_pm.time())
	#print(current_time.time() > four_pm.time())
	if current_time.time() > four_pm.time():
		light()
		water()
		cameraCapture()
	if mode == "GUI":
		output.bzone1.config(text = "Left Bed: " + str(get_data(0)))
		output.bzone2.config(text = "Middle Bed: " + str(get_data(1)))
		output.bzone3.config(text = "Right Bed: " + str(get_data(2)))
		output.window.after(int(attrs["interval_in_milliseconds"]), lambda : repeater(output))
	else:
		assert True==False#Not Implemented

@app.command()
def light(): #Todo: Fix Logic
	global attrs
	global theSun
	mcpasd = datetime.datetime.now(timezone.utc) - timedelta(hours=5)
	# Get today's sunrise and sunset in CST
	today_sr = theSun.get_sunrise_time() + timedelta(hours=7)
	today_ss = theSun.get_sunset_time() + timedelta(hours=7)
	if today_sr > mcpasd:
		today_sr = today_sr - timedelta(days=1)
	if today_sr > today_ss:
		today_ss = today_ss + timedelta(days=1)
	today_suntime = today_ss - today_sr
	light_on_time = today_suntime - today_suntime + timedelta(hours = int(attrs["light_length"]))
	today_suntime = mcpasd - today_sr
	if(mcpasd.time() > today_ss.time() and today_suntime < light_on_time):
		light_on = True
	else:
		light_on = False
	GPIO.output(int(attrs["lightPin"]), light_on)

#input camera attributes and capture image, updates attributes and returns new attributes
@app.command()
def cameraCapture():#update to support new attr system, and to not badly reimplement last_file_name
	global theCamera
	global attrs
	if attrs["use_camera"] == "False":
		return attrs
	name = "../../images/" + attrs["file_name_prefix"] + (str(int(attrs["last_file_number"]) + 1)) + ".jpg"
	theCamera.capture_file(name)
	attrs["last_file_number"] = str(int(attrs["last_file_number"]) + 1)
	setAttributes()
	return attrs

def lastFileName():
    global attrs
    if (int(attrs["last_file_number"]) == 0):
        return "../../images/placeholder.jpg"
    return "../../images/" + attrs["file_name_prefix"] + str(attrs["last_file_number"]) + ".jpg"

@app.command()
def create_video(image_paths, output_video_path : str, fps : int = 24, size : str = None):
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

@app.command()
def see_data():#Expand on me
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
	def __init__(self,attrs):#fix attribute handling in here
		# window
		self.window = tk.Tk()
		self.window.title =('Greenhouse')
		self.window.geometry(attrs["resolution"])#This needs to be changed
		
		# title
		self.title_label = ttk.Label(master = self.window, text = 'Greenhouse', font = attrs["header_font"])
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
		self.interval_label = ttk.Label(master = self.image_label_frame, text = 'Interval is set to ', font = attrs["norm_font"])
		self.capture_label = ttk.Label(master = self.image_label_frame, text = 'There have been __ captures\nsince last time-lapse.', font = attrs["norm_font"])
		
		# packing image stuff
		self.image_label.pack(side = 'left', padx = 10, pady = 10)
		self.interval_label.pack(padx = 5, pady = 30)
		self.capture_label.pack(padx = 5, pady = 5)
		self.image_label_frame.pack(side = 'left', padx = 10, pady = 10)
		self.image_frame.pack(side = 'left')
		
		# far right info
		self.top_right_frame = ttk.Frame(master = self.layer1_frame)
		self.last_capture = ttk.Label(master = self.top_right_frame, text = 'Last capture was taken ___ minutes ago.', font = attrs["norm_font"])
		self.zone_frame = ttk.Frame(master = self.top_right_frame)
		self.zone_label = ttk.Label(master = self.zone_frame, text = "Zone Moistures", font = attrs["norm_font"])
		self.bzone1 = ttk.Button(master = self.zone_frame, text = "Left Bed: " + str(get_data(0)))#These only update once
		self.bzone2 = ttk.Button(master = self.zone_frame, text = "Middle Bed: " + str(get_data(1)))
		self.bzone3 = ttk.Button(master = self.zone_frame, text = "Right Bed: " + str(get_data(2)))

		self.moisture_frame = ttk.Frame(master = self.top_right_frame)
		self.moisture_label = ttk.Label(master = self.moisture_frame, text = "Select Moisture Level", font = attrs["norm_font"])
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
		self.start_record = ttk.Button(master = self.layer2_frame, text = attrs["recording_status"])
		self.light_label = ttk.Label(master = self.layer2_frame, text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + attrs["light_length"] + " hours per day.", font = attrs["norm_font"])
		self.light_cycle = ttk.Entry(master = self.layer2_frame)
		self.enter_button = ttk.Button(master = self.layer2_frame, text = "Enter Hours", command = lambda : new_light_control("GUI", self))
		
		#packing lower layer
		self.manual_pic_button.pack(side = 'left', padx = 25, pady = 5)
		self.start_record.pack(side = 'left', padx = 25, pady = 5)
		self.light_label.pack(padx = 25, pady = 5)
		self.light_cycle.pack(padx = 25, pady = 5)
		self.enter_button.pack(padx = 25, pady = 5)
		self.layer2_frame.pack(padx = 5, pady = 5)
		self.window.after(int(attrs["interval_in_milliseconds"]), lambda : repeater(self))
		self.window.mainloop()
	def image_update(self,attrs,camera):
		cameraCapture(camera)
		img = ImageTk.PhotoImage(Image.open(lastFileName()))
		self.image_label.configure(image=img) 
		self.image_label.image = img

#A quick little command that just starts the GUI.
@app.command()
def start_gui():
	global attrs
	global mode
	mode = "GUI"
	gui = GUI(attrs)
	

# Finalization and execution ****************************************************************************************
app()







