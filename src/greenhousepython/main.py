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
	for key in keys:#Conveniently, we only refer to these using their names, which means it doesn't  matter if this reorganizes our cfg constantly. It was never even well-ordered to begin with!
		accumulator.append(key + ":" + attrs[key] + "\n")#assemble key and values into new format
	cfg.writelines(accumulator)#append to file
	cfg.close()

#figure out where the nth photo is (or at least should be)
def FileName(fileNumber):
    global attrs
    if (fileNumber == 0):
        return "../../images/placeholder.jpg"
    return "../../images/" + attrs["file_name_prefix"] + str(fileNumber) + ".jpg"

# Initialization ****************************************************************************************

getDataAttributes()
hasGUI = True
try:
	import cv2
except ImportError:
	from nonsense import cv2
try:
	import RPi.GPIO as GPIO
	import mcp3008 as MCP
	from mcp3008 import MCP3008
except ImportError:
	from nonsense import GPIO, MCP, MCP3008
import sys
import asyncio
try:
	import gi
	gi.require_version("Gtk", "4.0")
	from gi.repository import GLib, Gtk
	from gi.events import GLibEventLoopPolicy
except Exception:
	hasGUI = False
from datetime import datetime, timedelta, timezone
from astral import sun, Observer
import signal

# Postinitialization ****************************************************************************************

timesoff = []
for n in range(int(attrs["lights"])):
	timesoff.append(datetime.now(timezone.utc))
# create the mcp object
mcp = MCP3008.fixed([MCP.CH0, MCP.CH1, MCP.CH2, MCP.CH3, MCP.CH4, MCP.CH5, MCP.CH6, MCP.CH7])
# setup other GPIO
GPIO.setmode(GPIO.BCM)
for x in range(int(attrs["lights"])):
	GPIO.setup(int(attrs["lightPin" + str(x)]), GPIO.OUT)
for x in range(int(attrs["beds"])):
	GPIO.setup(int(attrs["waterPin" + str(x)]), GPIO.OUT)
GPIO.setup(int(attrs["pumpPin"]), GPIO.OUT)
theCamera = cv2.VideoCapture(0)

# More helpers ***********************************************************************************
def do_shutdown(*args,**kwargs):
	global mcp
	global theCamera
	try:#we shouldn't let crashes prevent the program from closing, so these must all be wrapped with try.
		mcp.close()#close down water control coms
	except Exception:
		print("Warning: we couldn't close down the water control communitcations.")
	try:
		theCamera.release()#turn off the damn camera
	except Exception:
		print("Warning: we couldn't close down the camera.")
	try:
		GPIO.cleanup()#knock the GPIO back to high-zed
	except Exception:
		print("Warning: we couldn't reset the GPIO.")
	sys.exit(0)#ensure the proghramme actually ends

# Postpostinitialization ***********************************************************************************

signal.signal(signal.SIGTERM,do_shutdown)
signal.signal(signal.SIGINT,do_shutdown)#I have no idea why these aren't the same signal. The program kicks the bucket either way.

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
	run_pump = False
	try:#my crummy mock of mcp3008.MCP3008 can't make sense of line 118, so this eyesore is trapped in a try-catch.
		for x in range(int(attrs["beds"])):
			moisture = mcp()[x]
			if (attrs["bed" + str(x)] == "False") and (moisture < int(attrs["MAX_VALUE"]) * (float(attrs["control_parameter" + str(x)]) - (float(attrs["deadband" + str(x)])/2))):#this if-else is basically an inelegant hysteresis controller. On the other hand, we're being rewarded for not destroying the pump, not for elegantly destroying the pump.
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
	except Exception:
		print("We failed at water control. This is probably because we aren't connected to an MCP3008, which is reasonable. If it isn't reasonable, check the dependencies.")

@app.command()
def light():#This code is a disaster area. Essentially, here's the logic:
	#If this code runs at night and before midnight, then it will be after sunset and after sunrise.
	#If this code runs at night and after midnight, then it will be before sunset and before sunrise.
	#If this code runs during the day, then it will be before sunset and after sunrise.
	#If this code runs and it is after sunset and before sunrise, time itself has crashed.
	#The problem comes when it's after midnight and we need to figure out when to turn the lights off: if we use the sunset time on the current day, we will never turn the lights off. Bad.
	#The solution I found is to calculate the time in UTC when we need to turn off the lights, do said calculation before midnight when the API is still talking about the correct sunset, and then just intentionally let this number get stale it's night and before midnight, at which point we will be talking about the right sunset again.
	#A consequence of this is that if you adjust the light length at any reasonable hour, it will only update the next day.
	#Another consequence of this is that if you run this code in Iceland or something where the sun won't rise on certain days of the year, this code will catch fire.
	#There must be a better solution than this, but I couldn't find it. Shrug emoji.
	global attrs
	global timesoff
	observer = Observer(float(attrs["latitude"]),float(attrs["longitude"]),float(attrs["elevation"]))
	theSun = sun.daylight(observer)#The sun is a deadly laser
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

#A command that captures a photograph, writes it to a file, and updates attrs accordingly.
@app.command()
def camera_capture():#updated to not badly reimplement last_file_name
	global attrs
	global theCamera
	ret, frame = theCamera.read()
	if not ret:
		assert False#this should maybe be changed later.
	else:
		cv2.imwrite(FileName(int(attrs["last_file_number"]) + 1),frame)
		attrs["last_file_number"] = str(int(attrs["last_file_number"]) + 1)
		setAttributes()

@app.command()
def create_video(output_video_path : str, fps : int = 24, size : str = None):
	image_paths = []
	for num in range(1,int(attrs["last_file_number"])+1):
		if cv2.imread(FileName(num)) is not None:
			image_paths.append(FileName(num))
		else:
			print("Warning: could not read " + FileName(num) + ", skipping.")
	if not image_paths:
		raise ValueError("Umm, we need images to make a video.")
	first_frame = cv2.imread(image_paths[0])
	if size is None:
		height, width, _ = first_frame.shape
		size = (width, height)
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter(output_video_path, fourcc, fps, size)
	for path in image_paths:
		frame = cv2.imread(path)
		frame_resized = cv2.resize(frame, size)
		out.write(frame_resized)
	out.release()
	print(f"Video saved to {output_video_path}")

#A command that lets you see the information flying through cyberspace.
@app.command()
def see_data():
	print(mcp())
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
		global hasGUI
		assert hasGUI#thou shalt not start the GUI without a GUI. See lines 54-60 for more info.
		self.lock = asyncio.Lock()
		self.Policy = GLibEventLoopPolicy()
		asyncio.set_event_loop_policy(self.Policy)
		self.loop = self.Policy.get_event_loop()
		self.tasks = []
		self.App = Gtk.Application(application_id="com.github.sp29174.GreenhousePython")
		if attrs["is_debug"]=="True":
			print("we have super")
		self.App.connect("activate",self.do_activate)
		if attrs["is_debug"]=="True":
			print("we can bind")
		self.App.run(None)
		if attrs["is_debug"]=="True":
			print("we get to the bloody twilight zone")
	def do_activate(self,useless):
		global attrs
		self.window = Gtk.ApplicationWindow(application=self.App)
		self.notebook = Gtk.Notebook()
		self.window.set_child(self.notebook)
		#stuff goes here
		self.CameraPage = Gtk.CenterBox()
		self.previewImage = Gtk.Image.new_from_file(FileName(int(attrs["last_file_number"])))
		self.CameraPage.set_start_widget(self.previewImage)
		self.cameraText = Gtk.Label(label="This text should vanish in a poof of smoke.")
		self.CameraPage.set_center_widget(self.cameraText)
		self.captureButton = Gtk.Button.new_with_label("Capture a photograph manually.")
		self.captureButton.connect("clicked", lambda button: self.tasks.append(self.loop.create_task(self.doForcedCapture())))
		self.notebook.append_page(self.CameraPage,Gtk.Label(label="Camera Control"))
		self.WaterPage = Gtk.Notebook()
		self.waterpages = []
		self.waterscales = []
		self.deadbandscales = []
		for n in range(int(attrs["beds"])):
			self.waterpages.append(Gtk.CenterBox())
			self.waterpages[n].set_start_widget(Gtk.Label(label="This text should vanish before you can read it."))#Namely, line 312 should cause autocontrol to await doUpdateGUI which should disappear this placeholder. If anything crashes between here and line 402, this text will live and we learn of a problem.
			self.waterscales.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,1,0.01))
			self.waterscales[n].set_value(float(attrs["control_parameter" + str(n)]))
			self.waterscales[n].set_hexpand(True)
			self.waterscales[n].set_vexpand(True)
			self.waterscales[n].connect("value-changed" , lambda scale, g=n : self.tasks.append(self.loop.create_task(self.doUpdateWaterControl(g,scale.get_value()))))#This line of code is the answer to a specific engineering question: how many obscure features of Python can fit in one line of code? It also makes the slider schedule a task when you move it, so that it neither blocks the GUI nor fails to do anything.
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
		self.SettingsPage.append(Gtk.Label(label="This window should allow you to adjust settings."))
		self.SettingsListBox = Gtk.ListBox()
		for key in attrs.keys():
			tmp = Gtk.ListBoxRow()
			tmp.set_child(Gtk.Label(label=key))
			self.SettingsListBox.append(tmp)
		self.SettingsPage.append(self.SettingsListBox)
		self.SettingsConfigBox = Gtk.CenterBox()
		self.SettingsConfigLabel = Gtk.Label(label="In order for you to change a setting, you must choose the setting to change.")
		self.SettingsConfigBox.set_start_widget(self.SettingsConfigLabel)
		self.SettingsTextBox = Gtk.Entry()
		self.SettingsConfigBox.set_center_widget(self.SettingsTextBox)
		self.SettingsEntryButton = Gtk.Button.new_with_label("Change the setting")
		self.SettingsEntryButton.connect("clicked", lambda button: self.tasks.append(self.loop.create_task(self.doUpdateSettings())))
		self.SettingsConfigBox.set_end_widget(self.SettingsEntryButton)
		self.SettingsPage.append(self.SettingsConfigBox)
		self.notebook.append_page(self.SettingsPage,Gtk.Label(label="Settigs"))
		self.window.present()
		self.tasks.append(self.loop.create_task(self.autocontrol()))
		self.tasks.append(self.loop.create_task(self.cameraControl()))
	async def doForcedCapture(self):
		global attrs
		await self.lock.acquire()
		camera_capture()
		await self.doUpdateGUI()
		self.lock.release()
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
	async def doUpdateSettings(self):
		global attrs
		await self.lock.acquire()
		row = self.SettingsListBox.get_selected_row()
		if row == None:
			self.lock.release()
			return None
		thingToChange = row.get_child().get_text()
		if ["file_name_prefix"].count(thingToChange) != 0:
			print("This part needs logic for automatically renaming files, which I haven't written yet. Sorry!")
			assert False
		elif ["interval","longitude","latitude","elevation"].count(thingToChange) != 0:
			try:
				new_val = str(float(self.SettingsTextBox.get_text()))
			except ValueError:
				print("We kinda need these to be floats.")
				self.lock.release()
				return None
		elif ["lights","pumpPin","beds","MAX_VALUE"].count(thingToChange) != 0 or thingToChange.startswith("lightPin") or thingToChange.startswith("waterPin"):
			if ["lights","beds"].count(thingToChange) != 0:
				print("When these are changed, the GUI needs to be rearranged, which I haven't coded yet.")
				assert False
			try:
				new_val = str(int(self.SettingsTextBox.get_text()))
			except ValueError:
				print("We kinda need these to be ints.")
				self.lock.release()
				return None
		elif ["is_debug"].count(thingToChange) != 0:
			if ["True","False"].count(self.SettingsTextBox.get_text()) == 0:
				print("We kinda need these to be bools.")
				self.lock.release()
				return None
		elif ["last_file_number"].count(thingToChange) != 0 or thingToChange.startswith("bed") or thingToChange.startswith("control_parameter") or thingToChange.startswith("deadband"):#this only doesn't catch beds because we already found it on line 356
			print("Changing this randomly will definitley break the software. If you know what you're doing, use the CLI, which is less picky")
			self.lock.release()
			return None
		attrs[thingToChange] = self.SettingsTextBox.get_text()
		setAttributes()
		self.lock.release()
	async def autocontrol(self):
		global attrs
		while True:
			await self.lock.acquire()
			water()
			light()
			self.lock.release()
			await self.doUpdateGUI()
			await asyncio.sleep(float(attrs["interval"]))
	async def cameraControl(self):
		global attrs
		while True:
			await self.lock.acquire()
			camera_capture()
			await self.doUpdateGUI()
			self.lock.release()
			await asyncio.sleep(float(attrs["camera_interval"]))
	async def doUpdateGUI(self):
		global attrs
		for n in range(int(attrs["beds"])):
			if (attrs["bed" + str(n)] == "True"):
				self.waterpages[n].get_start_widget().set_label("Bed " + str(n) + " is running.")
			else:
				self.waterpages[n].get_start_widget().set_label("Bed " + str(n) + " is not running.")
		self.previewImage.set_from_file(FileName(int(attrs["last_file_number"])))
		self.cameraText.set_label("Overall, " + attrs["last_file_number"] + " images have been captured by this device.\nCurrently, images will be captured every " + attrs["last_file_number"] + " seconds.")
		return None

# Finalization and execution ****************************************************************************************
app()


