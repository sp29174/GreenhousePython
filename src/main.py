# 11/11/2025
# 
# The main file.

import PIL
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import datetime
from datetime import timedelta, timezone, tzinfo
from suntime import Sun, SunTimeException
import time
import cameraControl as cc
import lights as ss#should be fixed
import water_control as water
import mcp as MCP

# Setup variables and GPIO ****************************************************************************************
norm_font = 'Calibri 18'
recording_status = "Start Recording"
light_length = 16
attributes = cc.getDataAttributes()
time = 0
header_font = 'Calibri 50 bold'
resolution = '1920x1080'
	
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
image = Image.open("../images/placeholder.jpg")#this should not be hardcoded
image2 = image.resize((640, 480))
last_plant_image = ImageTk.PhotoImage(image2)
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
bzone1 = ttk.Button(master = zone_frame, text = "Left Bed: " + str(MCP.get_data(0)))#These only update once
bzone2 = ttk.Button(master = zone_frame, text = "Middle Bed: " + str(MCP.get_data(1)))
bzone3 = ttk.Button(master = zone_frame, text = "Right Bed: " + str(MCP.get_data(2)))

moisture_frame = ttk.Frame(master = top_right_frame)
moisture_label = ttk.Label(master = moisture_frame, text = "Select Moisture Level", font = norm_font)
top_buttons = ttk.Frame(master = moisture_frame)
bottom_buttons = ttk.Frame(master = moisture_frame)
bmoisture0 = ttk.Button(master = top_buttons, text = "0%")#these should not be hardcoded
bmoisture1 = ttk.Button(master = top_buttons, text = "20%")
bmoisture2 = ttk.Button(master = top_buttons, text = "40%")
bmoisture3 = ttk.Button(master = bottom_buttons, text = "60%")
bmoisture4 = ttk.Button(master = bottom_buttons, text = "80%")
bmoisture5 = ttk.Button(master = bottom_buttons, text = "100%")

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
manual_pic_button = ttk.Button(master = layer2_frame, text = "Take Manual\nPicture", command = image_update)

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



def image_update():
	global image_label
    cc.cameraCapture(attributes)
    img = ImageTk.PhotoImage(Image.open(cc.lastFileName()))
    #image2 = image.resize((640, 480))
    image_label.configure(image=img) 
    image_label.image = img
	
# TODO: Fix
def repeater():
	current_time = datetime.datetime.now(timezone.utc) - timedelta(hours=5)#add variable timezone, this is stuck on UTC-5
	four_pm = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day) + timedelta(hours=16)#This is the least efficient way to do this
	print(current_time.time())
	print(four_pm.time())
	print(current_time.time() > four_pm.time())
	if current_time.time() > four_pm.time():
		ss.light(light_length)
	window.after(200, repeater)#timedelta should not be hardcoded, also this will overflow the stack eventually.
		
window.after(200, repeater)
window.mainloop()

















