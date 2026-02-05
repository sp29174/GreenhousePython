# 11/11/2025
# 
# The main file.

#Preinitialization ****************************************************************************************

from typer import Typer
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
try:
	from picamera2 import Picamera2
except ImportError:
	from nonsense import Picamera2
try:
	import RPi.GPIO as GPIO
	import busio
	import digitalio
	import board
	import mcp3008 as MCP
except ImportError:
	from nonsense import GPIO, busio, digitalio, board, MCP
import sys
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk
import asyncio
from gi.events import GLibEventLoopPolicy
import cv2
from PIL import Image
from datetime import datetime, timedelta, timezone
from astral import sun, Observer

# Postinitialization ****************************************************************************************
timesoff = []
for n in range(int(attrs["lights"])):
	timesoff.append(datetime.now(timezone.utc))
# create the mcp object
mcp = MCP.MCP3008()
# setup other GPIO
GPIO.setmode(GPIO.BCM)
for x in range(int(attrs["lights"])):
	GPIO.setup(int(attrs["lightPin" + str(x)]), GPIO.OUT)
for x in range(int(attrs["beds"])):
	GPIO.setup(int(attrs["waterPin" + str(x)]), GPIO.OUT)
GPIO.setup(int(attrs["pumpPin"]), GPIO.OUT)
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
def water():
	global attrs
	global chan_list
	moisture = 0
	run_pump = False
	for x in range(int(attrs["beds"])):
		moisture = mcp.read_all()[x]
		if (attrs["bed" + str(x)] == "False") and (moisture < int(attrs["MAX_VALUE"]) * (float(attrs["control_parameter" + str(x)]) - (float(attrs["deadband" + str(x)])/2))):
			GPIO.output(int(attrs["waterPin" + str(x)]), GPIO.HIGH)
			attrs["bed" + str(x)] = "True"
			setAttributes()
		elif (attrs["bed" + str(x)] == "True") and (moisture > int(attrs["MAX_VALUE"]) * (float(attrs["control_parameter" + str(x)]) + (float(attrs["deadband" + str(x)])/2))):
			GPIO.output(int(attrs["waterPin" + str(x)]), GPIO.LOW)
			attrs["bed" + str(x)] = "False"
			setAttributes()
		if (attrs["bed" + str(x)] == "True"):
			run_pump = True#If any bed is on, then run the pump.
	if run_pump:
		GPIO.output(int(attrs["pumpPin"]), GPIO.HIGH)
	else:
		GPIO.output(int(attrs["pumpPin"]), GPIO.LOW)

@app.command()
def light(): 
	global attrs
	global timesoff
	observer = Observer(float(attrs["latitude"]),float(attrs["longitude"]),float(attrs["elevation"]))
	theSun = sun.daylight(observer)
	if (datetime.now(timezone.utc) > theSun[1]):
		if attrs["is_debug"] == "True":
			print("We think that it's after sunset.")
		for n in range(int(attrs["lights"])):
			timesoff[n] = theSun[0] + timedelta(days=float(attrs["light_length" + str(n)]))
	elif attrs["is_debug"] == "True":
		print("We think that it's before sunset.")
	for n in range(int(attrs["lights"])):
		light_on = False
		if (datetime.now(timezone.utc) < timesoff[n]):
			light_on = True
			if attrs["is_debug"] == "True":
				print("The light should be on.")
		elif attrs["is_debug"] == "True":
			print("The light should be off.")
		GPIO.output(int(attrs["lightPin" + str(n)]), light_on)

#input camera attributes and capture image, updates attributes and returns new attributes
@app.command()
def cameraCapture():#updated to not badly reimplement last_file_name
	global theCamera
	global attrs
	try:
		theCamera.capture_file(FileName(int(attrs["last_file_number"]) + 1))
		attrs["last_file_number"] = str(int(attrs["last_file_number"]) + 1)
		setAttributes()
		return attrs
	except Exception:
		if attrs["is_debug"] == "True":
			print("we failed at photography, for some reason")
		return attrs

@app.command()
def create_video(output_video_path : str, fps : int = 24, size : str = None):#update to automatically build image_paths
	image_paths = []
	for num in range(1,int(attrs["last_file_number"])+1):
		image_paths.append(FileName(num))
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
	print(mcp.read_all(norm = False))
	print(mcp.read_all(norm = True))
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
	def __init__(self):
		self.lock = asyncio.Lock()
		self.Policy = GLibEventLoopPolicy()
		asyncio.set_event_loop_policy(self.Policy)
		self.loop = self.Policy.get_event_loop()
		self.tasks = []
		self.App = Gtk.Application(application_id="com.github.sp29174.GreenhousePython")
		print("we have super")
		self.App.connect("activate",self.do_activate)
		print("we can bind")
		self.App.run(None)
		print("we get to a weird place")
	def do_activate(self,useless):
		global attrs
		self.window = Gtk.ApplicationWindow(application=self.App)
		self.notebook = Gtk.Notebook()
		self.window.set_child(self.notebook)
		#stuff goes here
		self.CameraPage = Gtk.Box()
		self.CameraPage.append(Gtk.Label(label="This is a test of whether the camera page will work."))
		self.notebook.append_page(self.CameraPage,Gtk.Label(label="Camera Control"))
		self.WaterPage = Gtk.Notebook()
		self.waterpages = []
		self.waterscales = []
		self.deadbandscales = []
		for n in range(int(attrs["beds"])):
			self.waterpages.append(Gtk.CenterBox())
			self.waterpages[n].set_start_widget(Gtk.Label(label="This text should vanish before you can read it."))
			self.waterscales.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,1,0.01))
			self.waterscales[n].set_value(float(attrs["control_parameter" + str(n)]))
			self.waterscales[n].set_hexpand(True)
			self.waterscales[n].set_vexpand(True)
			self.waterscales[n].connect("value-changed" , lambda scale, g=n : self.tasks.append(self.loop.create_task(self.doUpdateWaterControl(g,scale.get_value()))))
			self.waterpages[n].set_center_widget(self.waterscales[n])
			self.deadbandscales.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,1,0.01))
			self.deadbandscales[n].set_value(float(attrs["deadband" + str(n)]))
			self.deadbandscales[n].set_hexpand(True)
			self.deadbandscales[n].set_vexpand(True)
			self.deadbandscales[n].connect("value-changed" , lambda scale, g=n : self.tasks.append(self.loop.create_task(self.doUpdateDeadband(g,scale.get_value()))))
			self.waterpages[n].set_end_widget(self.deadbandscales[n])
			self.WaterPage.append_page(self.waterpages[n],Gtk.Label(label="Bed " + str(n)))
		self.notebook.append_page(self.WaterPage,Gtk.Label(label="Water Control"))
		self.LightPage = Gtk.Notebook()
		self.lightpages = []
		self.lightscales = []
		for n in range(int(attrs["lights"])):
			self.lightpages.append(Gtk.Box())
			self.lightpages[n].append(Gtk.Label(label="This is a test of the light control interface."))
			self.lightpages[n].append(Gtk.Label(label="This will eventually display an indicator of if the light is running and a slider to control hours."))
			self.lightscales.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,1,0.01))
			self.lightscales[n].set_value(float(attrs["light_length" + str(n)]))
			self.lightscales[n].set_hexpand(True)
			self.lightscales[n].set_vexpand(True)
			self.lightscales[n].connect("value-changed" , lambda scale, g=n : self.tasks.append(self.loop.create_task(self.doUpdateLights(g,scale.get_value()))))
			self.lightpages[n].append(self.lightscales[n])
			self.LightPage.append_page(self.lightpages[n],Gtk.Label(label="Light" + str(n)))
		self.notebook.append_page(self.LightPage,Gtk.Label(label="Light Control"))
		self.HelpPage = Gtk.Box()
		self.HelpPage.append(Gtk.Label(label="This is a test of whether buttons work."))
		self.HelpPage.append(Gtk.Button.new_with_label("this is a button."))
		self.notebook.append_page(self.HelpPage,Gtk.Label(label="Help"))
		self.SettingsPage = Gtk.Box()
		self.SettingsPage.append(Gtk.Label(label="This is a test of whether buttons work."))
		self.notebook.append_page(self.SettingsPage,Gtk.Label(label="Settigs"))
		self.window.present()
		self.tasks.append(self.loop.create_task(self.autocontrol()))
	async def doUpdateWaterControl(self,n,value):
		global attrs
		await self.lock.acquire()
		attrs["control_parameter" + str(n)] = str(value)
		setAttributes()
		self.lock.release()
	async def doUpdateDeadband(self,n,value):
		global attrs
		await self.lock.acquire()
		attrs["deadband" + str(n)] = str(value)
		setAttributes()
		self.lock.release()
	async def doUpdateLights(self,n,value):
		global attrs
		await self.lock.acquire()
		attrs["light_length" + str(n)] = str(value)
		setAttributes()
		self.lock.release()
	async def autocontrol(self):
		global attrs
		while True:
			await self.lock.acquire()
			water()
			light()
			cameraCapture()
			self.lock.release()
			await self.doUpdateGUI()
			await asyncio.sleep(float(attrs["interval"]))
	async def doUpdateGUI(self):
		for n in range(int(attrs["beds"])):
			if (attrs["bed" + str(n)] == "True"):
				self.waterpages[n].get_start_widget().set_label("Bed " + str(n) + " is running.")
			else:
				self.waterpages[n].get_start_widget().set_label("Bed " + str(n) + " is not running.")
		return None
# Finalization and execution ****************************************************************************************
app()



