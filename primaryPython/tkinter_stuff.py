import PIL
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import datetime
from datetime import timedelta, timezone, tzinfo
from suntime import Sun, SunTimeException
import time
import cameraControl as cc
import Sunrise_Stuff as ss
#import water_control as water

# Setup variables and GPIO
norm_font = 'Calibri 18'
recording_status = "Start Recording"
light_length = 16



# methods   ***********************************************************************************

def testing():
	print(light_length)
	
# get stuff from the entry box
# clear the entry box
# set the value of light_length to new value

def new_light_control():

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
			print("length is still " + light_length)



def image_update():
    cc.cameraCapture(attributes)
    img = ImageTk.PhotoImage(Image.open(cc.lastFileName()))
    #image2 = image.resize((640, 480))
    image_label.configure(image=img) 
    image_label.image = img
	
	
#****************************************************************************************	

#get attributes
attributes = cc.getDataAttributes()
time = 0

# window
window = tk.Tk()
window.title =('Greenhouse')
window.geometry('1920x1080')

# title
title_label = ttk.Label(master = window, text = 'Greenhouse', font = 'Calibri 50 bold')
title_label.pack()

#first layer
layer1_frame = ttk.Frame(master = window)

# image information
image_frame = ttk.Frame(master = layer1_frame)
image = Image.open("UMBER.jpg")
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
bzone1 = ttk.Button(master = zone_frame, text = "Left Bed: ")# + str(MCP.get_data(0)))
bzone2 = ttk.Button(master = zone_frame, text = "Middle Bed: ")# + str(MCP.get_data(1)))
bzone3 = ttk.Button(master = zone_frame, text = "Right Bed: ")# + str(MCP.get_data(2)))

moisture_frame = ttk.Frame(master = top_right_frame)
moisture_label = ttk.Label(master = moisture_frame, text = "Select Moisture Level", font = norm_font)
top_buttons = ttk.Frame(master = moisture_frame)
bottom_buttons = ttk.Frame(master = moisture_frame)
bmoisture0 = ttk.Button(master = top_buttons, text = "0%")
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

# lower layer stuff
layer2_frame = ttk.Frame(master = window)

# captures picture, command= cameraCapture
# ISSUE: taking picture on boot
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


def repeater():
	current_time = datetime.datetime.now(timezone.utc) - timedelta(hours=5)
	four_pm = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day) + timedelta(hours=16)
	print(current_time.time())
	print(four_pm.time())
	print(current_time.time() > four_pm.time())
	if current_time.time() > four_pm.time():
		ss.lights()
	window.after(2000, repeater)
		
window.after(2000, repeater)
window.mainloop()
