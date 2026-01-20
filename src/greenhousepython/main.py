# 11/11/2025
# 
# The main file.

#Preinitialization ****************************************************************************************

from typer import Typer, Option
app = Typer()
attrs = {}

#Helpers ****************************************************************************************

#read configuration information from cfg.txt and use it
def getDataAttributes():
	global attrs
	cfg = open("cfg.txt", "r")
	for thing in cfg.readlines():#find all things seperated by newlines
		kvp = thing.split(":")#get key-value pairs
		attrs[kvp[0]] = kvp[1].rstrip("\n")#add key-value pair to dictionary, no random trailing newline for you
	cfg.close()

#rewrite the list with updated values
def setAttributes():
	global attrs
	cfg = open("cfg.txt", "w")#open file to write
	accumulator = []
	keys = attrs.keys()#get all the keys
	for key in keys:
		accumulator.append(key + ":" + attrs[key] + "\n")#assemble key and values into new format
	cfg.writelines(accumulator)#append to file
	cfg.close()

def FileName(fileNumber):
    global attrs
    if (fileNumber == 0):
        return "../../images/placeholder.jpg"
    return "../../images/" + attrs["file_name_prefix"] + str(fileNumber) + ".jpg"

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
from datetime import datetime, timedelta, timezone
from astral import sun, Observer

# Postinitialization ****************************************************************************************
timeoff = datetime.now(timezone.utc)
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
GPIO.setup(int(attrs["pumpPin"]), GPIO.OUT)
for x in range(int(attrs["beds"])):
	GPIO.setup(int(attrs["waterPin"+str(x)]), GPIO.OUT)
GPIO.setup(int(attrs["lightPin"]), GPIO.OUT)
theCamera = Picamera2()
camera_cfg = theCamera.create_still_configuration()
theCamera.start()


# CLI commands   ***********************************************************************************

#a simple command to allow the user to change settings-this lets them define nonsense parameters, but I could care less, because my getdataattributes can ignore them.
#However, this almost certainly breaks if you pass in a thing that contains a newline, which we should fix later.
@app.command()
def change_setting(key : str, value : str):
	global attrs
	attrs[key] = value
	setAttributes()

#control pumps using hysteresis based on the values returned from the MCP
@app.command()
def water(input : float = None):
	global attrs
	global chan_list
	if input != None:
		attrs["control_parameter"] = str(input)
		setAttributes()
	elif attrs["is_debug"] == "True":
		print("The system says your input is None, BTW")
	moisture = 0
	run_pump = False
	for x in range(int(attrs["beds"])):
		moisture = chan_list[x].value
		if (attrs["bed" + str(x)] == "True"):
			run_pump = True#If any bed is on, then run the pump.
		if (attrs["bed" + str(x)] == "False") and (moisture < int(attrs["MAX_VALUE"]) * (float(attrs["control_parameter"]) - (float(attrs["deadband"])/2))):
			GPIO.output(int(attrs["waterPin" + str(x)]), GPIO.HIGH)
			attrs["bed" + str(x)] = "True"
			setAttributes()
		elif (attrs["bed" + str(x)] == "True") and (moisture > int(attrs["MAX_VALUE"]) * (float(attrs["control_parameter"]) + (float(attrs["deadband"])/2))):
			GPIO.output(int(attrs["waterPin" + str(x)]), GPIO.LOW)
			attrs["bed" + str(x)] = "False"
			setAttributes()
	if run_pump:
		GPIO.output(int(attrs["pumpPin"]), GPIO.HIGH)
	else:
		GPIO.output(int(attrs["pumpPin"]), GPIO.LOW)

@app.command()
def light(): 
	global attrs
	global timeoff
	observer = Observer(float(attrs["latitude"]),float(attrs["longitude"]),float(attrs["elevation"]))
	theSun = sun.daylight(observer)
	light_on = False
	if (datetime.now(timezone.utc) > theSun[1]):
		if attrs["is_debug"] == "True":
			print("We think that it's after sunset.")
		timeoff = theSun[0] + timedelta(hours=float(attrs["light_length"]))
	elif attrs["is_debug"] == "True":
		print("We think that it's before sunset.")
	if (datetime.now(timezone.utc) < timeoff):
		light_on = True
		if attrs["is_debug"] == "True":
			print("The light should be on.")
	elif attrs["is_debug"] == "True":
		print("The light should be off.")
	GPIO.output(int(attrs["lightPin"]), light_on)

#input camera attributes and capture image, updates attributes and returns new attributes
@app.command()
def cameraCapture():#updated to not badly reimplement last_file_name
	global theCamera
	global attrs
	if attrs["use_camera"] == "False":
		if attrs["is_debug"] == "True":
			print("We won't genertate an image, actually")
		return attrs
	theCamera.capture_file(FileName(int(attrs["last_file_number"]) + 1))
	attrs["last_file_number"] = str(int(attrs["last_file_number"]) + 1)
	setAttributes()
	return attrs

@app.command()
def create_video(image_paths, output_video_path : str, fps : int = 24, size : str = None):#update to automatically build image_paths
	if not image_paths:
		raise ValueError("The list of image paths is empty")
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
	keys = attrs.keys()#get all the settings
	for key in keys:
		print(key + ":" + attrs[key])#assemble key and values into new format

#A quick little command that just starts the GUI.
@app.command()
def start_gui():
	global attrs
	gui = GUI()
	
# GUI ****************************************************************************************	

class GUI:
	def __init__(self):#fix attribute handling in here
		global attrs
		global chan_list
		
		# window
		self.window = tk.Tk()
		self.window.title =('Greenhouse')
		self.window.geometry(attrs["resolution"])
		
		# title
		self.title_label = ttk.Label(master = self.window, text = 'Greenhouse', font = attrs["header_font"])
		self.title_label.pack()
		
		#first layer
		self.layer1_frame = ttk.Frame(master = self.window)
		
		# image information
		self.image_frame = ttk.Frame(master = self.layer1_frame)
		self.image = Image.open(FileName(int(attrs["last_file_number"])))
		self.image2 = self.image.resize((640, 480))
		self.last_plant_image = ImageTk.PhotoImage(self.image2)#BUG: initial image is too big
		self.image_label = ttk.Label(master = self.image_frame, image = self.last_plant_image)
		
		self.image_label_frame = ttk.Frame(master = self.image_frame)
		self.interval_label = ttk.Label(master = self.image_label_frame, text = 'Interval is set to ' + attrs["interval_in_milliseconds"] + " milliseconds.", font = attrs["norm_font"])
		self.capture_label = ttk.Label(master = self.image_label_frame, text = "There have been " + attrs["last_file_number"] + " captures\nsince last time-lapse.", font = attrs["norm_font"])
		
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
		self.bzone1 = ttk.Button(master = self.zone_frame, text = "Left Bed: " + str(chan_list[0].value))
		self.bzone2 = ttk.Button(master = self.zone_frame, text = "Middle Bed: " + str(chan_list[1].value))
		self.bzone3 = ttk.Button(master = self.zone_frame, text = "Right Bed: " + str(chan_list[2].value))

		self.moisture_frame = ttk.Frame(master = self.top_right_frame)
		self.moisture_label = ttk.Label(master = self.moisture_frame, text = "Select Moisture Level", font = attrs["norm_font"])
		self.top_buttons = ttk.Frame(master = self.moisture_frame)
		self.bar_state = 0.0
		self.slider = ttk.Scale(self.top_buttons, from_=0, to=1, orient="horizontal", variable=self.bar_state, command = lambda event: water(self.bar_state))

		
		# far right packing
		self.last_capture.pack(padx = 10, pady = 20)
		self.zone_label.pack(padx = 10, pady = 20)
		self.bzone1.pack(side = 'left', padx = 5, pady = 5)
		self.bzone2.pack(side = 'left', padx = 5, pady = 5)
		self.bzone3.pack(side = 'left', padx = 5, pady = 5)
		self.zone_frame.pack(padx = 10, pady = 10)
		
		self.moisture_label.pack(padx = 5, pady = 20)
		self.slider.pack(padx = 5, pady = 5)
		self.top_buttons.pack(padx = 5, pady = 5)
		self.moisture_frame.pack(padx = 10, pady = 10)
		
		self.top_right_frame.pack(padx=10, pady=10)
		self.layer1_frame.pack(padx = 20, pady = 20)
		
		# lower layer
		self.layer2_frame = ttk.Frame(master = self.window)
		
		# captures picture, command= cameraCapture
		# ISSUE: taking picture on boot
		#I disagree, that's a feature!
		self.manual_pic_button = ttk.Button(master = self.layer2_frame, text = "Take Manual\nPicture", command = lambda : self.image_update())
		
		# should start recording function
		self.start_record = ttk.Button(master = self.layer2_frame, text = attrs["recording_status"])
		self.light_label = ttk.Label(master = self.layer2_frame, text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + attrs["light_length"] + " hours per day.", font = attrs["norm_font"])
		self.light_cycle = ttk.Entry(master = self.layer2_frame)
		self.enter_button = ttk.Button(master = self.layer2_frame, text = "Enter Hours", command = lambda : self.new_light_control())
		
		#packing lower layer
		self.manual_pic_button.pack(side = 'left', padx = 25, pady = 5)
		self.start_record.pack(side = 'left', padx = 25, pady = 5)
		self.light_label.pack(padx = 25, pady = 5)
		self.light_cycle.pack(padx = 25, pady = 5)
		self.enter_button.pack(padx = 25, pady = 5)
		self.layer2_frame.pack(padx = 5, pady = 5)
		self.window.after(int(attrs["interval_in_milliseconds"]), lambda : self.repeater())
		self.window.mainloop()
	#update the image
	def image_update(self):
		global attrs
		cameraCapture()
		img = ImageTk.PhotoImage(Image.open(FileName(int(attrs["last_file_number"]))))
		self.image_label.configure(image=img) 
		self.image_label.image = img
	# Set light_length to the stored input value
	def new_light_control(self):
		global attrs
		new_light_length = self.light_cycle.get()#get user input
		self.light_cycle.delete(0, len(new_light_length))#clear input field
		if (new_light_length != ""):#I don't fully understand why this if statement is here
			try:#Catch-all
				if(float(new_light_length) > 24):#No superlights for you
					attrs["light_length"] = "24"
				elif (float(new_light_length) < 0):#No antilights for you
					attrs["light_length"]  = "0"
				else:
					attrs["light_length"] = new_light_length#set lights
				if attrs["is_debug"] == "True":
					print(attrs["light_length"])
				setAttributes()
				self.light_label.config(text = "Enter the number of hours the selected\ngrowlight should remain on.\nCurrently " + attrs["light_length"] + " hours per day.")
			except ValueError as e:
				self.light_label.config(text = "Nope. That's not a number of hours the selected\ngrowlight can remain on.\nStill " + attrs["light_length"] + " hours per day.")
	def repeater(self):
		global attrs
		global chan_list
		light()#check lights
		water()#update beds
		cameraCapture()#capture image
		#update GUI
		self.bzone1.config(text = "Left Bed: " + str(chan_list[0].value))
		self.bzone2.config(text = "Middle Bed: " + str(chan_list[1].value))
		self.bzone3.config(text = "Right Bed: " + str(chan_list[2].value))
		self.interval_label.config(text = 'Interval is set to ' + attrs["interval_in_milliseconds"] + " milliseconds.")
		self.capture_label.config(text = "There have been " + attrs["last_file_number"] + " captures\nsince last time-lapse.")
		self.window.after(int(attrs["interval_in_milliseconds"]), lambda : self.repeater())

	
# Finalization and execution ****************************************************************************************
app()







