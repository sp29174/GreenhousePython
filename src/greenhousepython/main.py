# 11/11/2025
# 
# The main file.

#Preinitialization ****************************************************************************************

from typer import Typer, Argument, Option
import shelve
app = Typer(rich_markup_mode="rich")
attrs = shelve.open("cfg.txt", writeback = True)
if not attrs:
	attrs["last_file_number"] = 0
	attrs["camera_interval"] = 3600
	attrr["interval"] = 1
	attrs["file_name_prefix"] = "gi"
	attrs["lights"] = 1
	attrs["light_length"] = 0.5
	attrs["latitude"] = 43.0972
	attrs["longitude"] = -89.5043
	attrs["elevation"] = 355.0
	attrs["light_pin0"] = 21
	attrs["pump_pin"] = 15
	attrs["water_pin0"] = 16
	attrs["water_pin1"] = 17
	attrs["water_pin2"] = 18
	attrs["is_debug"] = True
	attrs["is_recording"] = True
	attrs["beds"] = 3
	attrs["bed0"] = False
	attrs["bed1"] = False
	attrs["bed2"] = False
	attrs["control_parameter0"] = 0.0
	attrs["deadband0"] = 0.0
	attrs["control_parameter1"] = 0.0
	attrs["deadband1"] = 0.0
	attrs["control_parameter2"] = 0.0
	attrs["deadband2"] = 0.0
	attrs.sync()
	#create default attrs

#Helpers ****************************************************************************************

#figure out where the nth photo is (or at least should be)
def get_file_name(file_number):
    global attrs
    if (file_number == 0):
        return "../../images/placeholder.jpg"
    return "../../images/" + attrs["file_name_prefix"] + str(file_number) + ".jpg"

# Initialization ****************************************************************************************

has_GUI = True
try:
	import cv2
	cv2.VideoCapture(0).release()#Fix bug where we crash because there's no camera
except ImportError:
	from greenhousepython.nonsense import cv2
try:
	import mcp3008 as MCP
	from mcp3008 import MCP3008
except ImportError as e:
	if attrs["is_debug"]:
		print("WARNING: " + str(e))
	from greenhousepython.nonsense import MCP, MCP3008
try:
	from greenhousepython.gpio_wrapper import gpio as g
	GPIO = g()
except Exception as e:
	if attrs["is_debug"]:
		print("WARNING: " + str(e))
	try:
		import RPi.GPIO as GPIO
	except ImportError as e:
		if attrs["is_debug"]:
			print("WARNING: " + str(e))
		from greenhousepython.nonsense import GPIO
import sys
import asyncio
try:
	import gi
	gi.require_version("Gtk", "4.0")
	from gi.repository import GLib, Gtk
	from gi.events import GLibEventLoopPolicy
except Exception as e:
	if attrs["is_debug"]:
		print("WARNING: " + str(e))
	has_GUI = False
from datetime import datetime, timedelta, timezone
from astral import sun, Observer
import signal
from typing import Annotated

# Postinitialization ****************************************************************************************

times_off = []
for n in range(attrs["lights"]):
	times_off.append(datetime.now(timezone.utc))
# create the mcp object
mcp = MCP3008.fixed([MCP.CH0, MCP.CH1, MCP.CH2, MCP.CH3, MCP.CH4, MCP.CH5, MCP.CH6, MCP.CH7])
# setup other GPIO
GPIO.setmode(GPIO.BCM)
for x in range(attrs["lights"]):
	GPIO.setup(attrs["light_pin" + str(x)], GPIO.OUT)
for x in range(attrs["beds"]):
	GPIO.setup(attrs["water_pin" + str(x)], GPIO.OUT)
GPIO.setup(attrs["pump_pin"], GPIO.OUT)
the_camera = cv2.VideoCapture(0)

# More helpers ***********************************************************************************
def do_shutdown(*args,**kwargs):
	global mcp
	global the_camera
	global attrs
	if attrs["is_debug"] == "True":
		print("Shutting down...")
	try:#we shouldn't let crashes prevent the program from closing, so these must all be wrapped with try.
		mcp.close()#close down water control coms
	except Exception as e:
		if attrs["is_debug"]:
			print("WARNING: " + str(e))
		else:
			print("Warning: we couldn't close down the water control communitcations.")
	try:
		the_camera.release()#turn off the damn camera
	except Exception as e:
		if attrs["is_debug"]:
			print("WARNING: " + str(e))
		else:
			print("Warning: we couldn't close down the camera.")
	try:
		GPIO.cleanup()#knock the GPIO back to high-zed
	except Exception as e:
		if attrs["is_debug"]:
			print("WARNING: " + str(e))
		else:
			print("Warning: we couldn't reset the GPIO.")
	attrs.close()
	sys.exit(0)#ensure the proghramme actually ends

# Postpostinitialization ***********************************************************************************

signal.signal(signal.SIGTERM,do_shutdown)
signal.signal(signal.SIGINT,do_shutdown)#I have no idea why these aren't the same signal. The program kicks the bucket either way.

# CLI commands   ***********************************************************************************

#a simple command to allow the user to change settings-this lets them define nonsense parameters, but I could care less, because my get_attributes can ignore them.
#However, this almost certainly breaks if you pass in a thing that contains a newline, which we should fix later.
@app.command(help="Change the setting KEY to VALUE. Newlines and colons are not supported for technical reasons. BROKEN while we switch to Shelves.")
def change_setting(key : Annotated[str, Argument(help="The exact name of the setting to change or create.")], value : Annotated[str, Argument(help="The exact value that the setting should be changed to.")]):
	global attrs
	attrs[key] = value
	attrs.sync()

#control pumps using hysteresis based on the values returned from the MCP
@app.command(help="Force the system to run the automatic water control logic without starting the GUI.")
def water():
	global attrs
	run_pump = False
	try:#my crummy mock of mcp3008.MCP3008 can't make sense of line 118, so this eyesore is trapped in a try-catch.
		for x in range(attrs["beds"]):
			moisture = mcp(1)[x]#normalize values to one using mcp3008.MCP3008 (see https://github.com/luxedo/RPi_mcp3008/blob/master/mcp3008.py#L73)
			if (not attrs["bed" + str(x)]) and (moisture < attrs["control_parameter" + str(x)] - (attrs["deadband" + str(x)]/2)):#this if-else is basically an inelegant hysteresis controller. On the other hand, we're being rewarded for not destroying the pump, not for elegantly destroying the pump.
				GPIO.output(int(attrs["water_pin" + str(x)]), GPIO.HIGH)
				attrs["bed" + str(x)] = "True"
				attrs.sync()
			elif attrs["bed" + str(x)] and (moisture > attrs["control_parameter" + str(x)] + (attrs["deadband" + str(x)]/2)):
				GPIO.output(attrs["water_pin" + str(x)], GPIO.LOW)
				attrs["bed" + str(x)] = False
				attrs.sync()
			if (attrs["bed" + str(x)] == "True"):
				run_pump = True#If any bed is on, then run the pump.
		if run_pump:
			GPIO.output(int(attrs["pump_pin"]), GPIO.HIGH)
		else:
			GPIO.output(int(attrs["pump_pin"]), GPIO.LOW)
	except Exception as e:
		if attrs["is_debug"]:
			print("WARNING: " + str(e))
		else:
			print("We failed at water control. This is probably because we aren't connected to an MCP3008, which is reasonable. If it isn't reasonable, check the dependencies.")

@app.command(help="Force the system to run the automatic light control logic without starting the GUI. [bold red]This will not work if the sun will not rise and set today.[/bold red]")
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
	global times_off
	observer = Observer(attrs["latitude"],attrs["longitude"],attrs["elevation"])
	try:
		the_sun = sun.daylight(observer)#The sun is a deadly laser	
	except ValueError as e:#the sun doesn't rise/set today. We therefore need to fudge the sun. This means that, for our purposes, the sun rose at midnight and set a very long time ago.
		if attrs["is_debug"]:
			print(str(e))
		the_sun = [datetime(datetime.year,datetime.month,datetime.day),datetime.min]
	if (datetime.now(timezone.utc) >= the_sun[1]):
		if attrs["is_debug"]:
			print("We think that it's after sunset.")
		for n in range(attrs["lights"]):
			times_off[n] = the_sun[0] + timedelta(days=attrs["light_length" + str(n)])
	elif attrs["is_debug"]:
		print("We think that it's before sunset.")
	for n in range(attrs["lights"]):
		light_on = False
		if (datetime.now(timezone.utc) < times_off[n]):
			light_on = True
			if attrs["is_debug"]:
				print("The light should be on.")
		elif attrs["is_debug"]:
			print("The light should be off.")
		if light_on:
			GPIO.output(attrs["light_pin" + str(n)], GPIO.HIGH)
		else:
			GPIO.output(attrs["light_pin" + str(n)], GPIO.LOW)

#A command that captures a photograph, writes it to a file, and updates attrs accordingly.
@app.command(help="Manually capture a photograph.")
def camera_capture():#updated to not badly reimplement last_file_name
	global attrs
	global the_camera
	ret, frame = the_camera.read()
	if not ret:
		if not attrs["is_debug"]:
			assert False#Fuck this!
		else:
			print("Warning: Image capture failed to complete.")
	else:
		cv2.imwrite(get_file_name(attrs["last_file_number"] + 1, frame)
		attrs["last_file_number"] = attrs["last_file_number"] + 1
		attrs.sync()

@app.command(help="Assemble the current collection of images into a mp4 video. This will:\n \n 1. Not include the placeholder image, ever. \n 2. Not recoginze images created with file numbers above last_file_number. \n 3. Pollute your shell with warnings if you have nonsequential image numbers. \n 4. Be unaware of the fact that manually captured images are not taken at regular intervals.")
def create_video(output_video_path : Annotated[str, Argument(help="An exact file name, which must be writable, must not have stuff in it, and should not be irrational. If you run this command with sudo and pass /, then it will replace your system with a video. Don't.")], fps : Annotated[int, Option(help="The framerate that the video will be displayed at. Defaults to 24.")] = 24, size : Annotated[str, Option(help="An override to resize your images to a different resolution. This is needed internally for technical reasons, and we saw no reason not to expose it to the commandline. Defaults to your camera resolution.")] = None):
	image_paths = []
	for num in range(1,attrs["last_file_number"] + 1):
		if cv2.imread(get_file_name(num)) is not None:
			image_paths.append(get_file_name(num))
		else:
			print("Warning: could not read " + get_file_name(num) + ", skipping.")
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
@app.command(help="Prints the internal state of the program into your shell, and does nothing else.")
def see_data():
	global times_off
	global mcp
	global attrs
	print(times_off)
	print(mcp())
	keys = attrs.keys()#get all the settings
	for key in keys:
		print(key + ":" + attrs[key])#assemble key and values into new format

#A quick little command that just starts the GUI.
@app.command(help="Starts the GUI. Will fail if your system has no way to render it.")
def start_gui():
	global attrs
	gui = GUI()

# GUI ****************************************************************************************	

class GUI:
	def __init__(self):
		global has_GUI
		assert has_GUI#thou shalt not start the GUI without a GUI. See lines 54-60 for more info.
		self.lock = asyncio.Lock()
		self.policy = GLibEventLoopPolicy()
		asyncio.set_event_loop_policy(self.policy)
		self.loop = self.policy.get_event_loop()
		self.tasks = []
		self.gui_app = Gtk.Application(application_id="com.github.sp29174.GreenhousePython")
		if attrs["is_debug"]:
			print("we have super")
		self.gui_app.connect("activate",self.do_activate)
		if attrs["is_debug"]:
			print("we can bind")
		self.gui_app.run(None)
		if attrs["is_debug"]:
			print("we get to the bloody twilight zone")
		do_shutdown()
	def do_activate(self,useless):
		global attrs
		self.window = Gtk.ApplicationWindow(application=self.gui_app)
		self.notebook = Gtk.Notebook()
		self.window.set_child(self.notebook)
		#stuff goes here
		self.camera_page = Gtk.CenterBox()
		self.preview_image = Gtk.Image.new_from_file(get_file_name(attrs["last_file_number"]))
		self.preview_image.set_vexpand(True)#Allow the preview image to not be two pixels tall
		self.preview_image.set_hexpand(True)
		self.camera_page.set_start_widget(self.preview_image)
		self.camera_text = Gtk.Label(label="This text should vanish in a poof of smoke.")
		self.camera_page.set_center_widget(self.camera_text)
		self.capture_box = Gtk.Box()
		self.capture_button = Gtk.Button.new_with_label("Capture a photograph manually.")
		self.capture_button.connect("clicked", lambda button: self.tasks.append(self.loop.create_task(self.force_capture())))
		self.capture_box.append(self.capture_button)
		self.record_button = Gtk.ToggleButton(label="Toggle recording.")
		if attrs["is_recording"]:
			self.record_button.set_active(True)
		else:
			self.record_button.set_active(False)
		self.record_button.connect("toggled", lambda button: self.tasks.append(self.loop.create_task(self.toggle_recording(button.props.active))))
		self.capture_box.append(self.record_button)
		self.camera_page.set_end_widget(self.capture_box)
		self.notebook.append_page(self.camera_page,Gtk.Label(label="Camera Control"))
		self.water_page = Gtk.Notebook()
		self.water_pages = []
		self.water_scales = []
		self.deadband_scales = []
		for n in range(int(attrs["beds"])):
			self.water_pages.append(Gtk.CenterBox())
			self.water_pages[n].set_start_widget(Gtk.Label(label="This text should vanish before you can read it."))#Namely, line 312 should cause automatic_control to await update_GUI which should disappear this placeholder. If anything crashes between here and line 402, this text will live and we learn of a problem.
			self.water_scales.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,1,0.01))
			self.water_scales[n].set_value(attrs["control_parameter" + str(n)])
			self.water_scales[n].set_hexpand(True)
			self.water_scales[n].set_vexpand(True)
			self.water_scales[n].connect("value-changed" , lambda scale, g=n : self.tasks.append(self.loop.create_task(self.update_water_threshold(g,scale.get_value()))))#This line of code is the answer to a specific engineering question: how many obscure features of Python can fit in one line of code? It also makes the slider schedule a task when you move it, so that it neither blocks the GUI nor fails to do anything.
			self.water_pages[n].set_center_widget(self.water_scales[n])
			self.deadband_scales.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,1,0.01))
			self.deadband_scales[n].set_value(attrs["deadband" + str(n)])
			self.deadband_scales[n].set_hexpand(True)
			self.deadband_scales[n].set_vexpand(True)
			self.deadband_scales[n].connect("value-changed" , lambda scale, g=n : self.tasks.append(self.loop.create_task(self.update_water_deadband(g,scale.get_value()))))
			self.water_pages[n].set_end_widget(self.deadband_scales[n])
			self.water_page.append_page(self.water_pages[n],Gtk.Label(label="Bed " + str(n)))
		self.notebook.append_page(self.water_page,Gtk.Label(label="Water Control"))
		self.light_page = Gtk.Notebook()
		self.light_pages = []
		self.light_scales = []
		for n in range(int(attrs["lights"])):
			self.light_pages.append(Gtk.Box())
			self.light_pages[n].append(Gtk.Label(label="This is a test of the light control interface."))
			self.light_pages[n].append(Gtk.Label(label="This will eventually display an indicator of if the light is running and a slider to control hours."))
			self.light_scales.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,1,0.01))
			self.light_scales[n].set_value(attrs["light_length" + str(n)])
			self.light_scales[n].set_hexpand(True)
			self.light_scales[n].set_vexpand(True)
			self.light_scales[n].connect("value-changed" , lambda scale, g=n : self.tasks.append(self.loop.create_task(self.update_light_length(g,scale.get_value()))))
			self.light_pages[n].append(self.light_scales[n])
			self.light_page.append_page(self.light_pages[n],Gtk.Label(label="Light" + str(n)))
		self.notebook.append_page(self.light_page,Gtk.Label(label="Light Control"))
		self.help_page = Gtk.Box()
		self.help_page.append(Gtk.Label(label="This is a test of whether buttons work."))
		self.help_page.append(Gtk.Button.new_with_label("this is a button."))
		self.notebook.append_page(self.help_page,Gtk.Label(label="Help"))
		self.settings_page = Gtk.Box()
		self.settings_page.append(Gtk.Label(label="This window should allow you to adjust settings."))
		self.settings_listbox = Gtk.ListBox()
		for key in attrs.keys():
			tmp = Gtk.ListBoxRow()
			tmp.set_child(Gtk.Label(label=key))
			self.settings_listbox.append(tmp)
		self.settings_page.append(self.settings_listbox)
		self.settings_config_box = Gtk.CenterBox()
		self.settings_config_label = Gtk.Label(label="In order for you to change a setting, you must choose the setting to change.")
		self.settings_config_box.set_start_widget(self.settings_config_label)
		self.settings_text_entry = Gtk.Entry()
		self.settings_config_box.set_center_widget(self.settings_text_entry)
		self.settings_enter_button = Gtk.Button.new_with_label("Change the setting")
		self.settings_enter_button.connect("clicked", lambda button: self.tasks.append(self.loop.create_task(self.update_settings())))
		self.settings_config_box.set_end_widget(self.settings_enter_button)
		self.settings_page.append(self.settings_config_box)
		self.notebook.append_page(self.settings_page,Gtk.Label(label="Settigs"))
		self.window.present()
		self.tasks.append(self.loop.create_task(self.automatic_control()))
		self.tasks.append(self.loop.create_task(self.camera_control()))
	async def toggle_recording(self,whermst):
		global attrs
		await self.lock.acquire()
		attrs["recording_status"] = whermst
		attrs.sync()
		self.lock.release()
	async def force_capture(self):
		global attrs
		await self.lock.acquire()
		camera_capture()
		await self.update_GUI()
		self.lock.release()
	async def update_water_threshold(self,n,value):
		global attrs
		await self.lock.acquire()
		attrs["control_parameter" + str(n)] = value
		attrs.sync()
		self.lock.release()
	async def update_water_deadband(self,n,value):
		global attrs
		await self.lock.acquire()
		attrs["deadband" + str(n)] = value
		attrs.sync()
		self.lock.release()
	async def update_light_length(self,n,value):
		global attrs
		await self.lock.acquire()
		attrs["light_length" + str(n)] = value
		attrs.sync()
		self.lock.release()
	async def update_settings(self):
		assert False#This is BROKEN until we finish migrating to shelves
		global attrs
		await self.lock.acquire()
		row = self.settings_listbox.get_selected_row()
		if row == None:
			self.lock.release()
			return None
		setting_to_change = row.get_child().get_text()
		if ["file_name_prefix"].count(setting_to_change) != 0:
			print("This part needs logic for automatically renaming files, which I haven't written yet. Sorry!")
			assert False
		elif ["interval","longitude","latitude","elevation"].count(setting_to_change) != 0:
			try:
				new_val = str(float(self.settings_text_entry.get_text()))
			except ValueError:
				print("We kinda need these to be floats.")
				self.lock.release()
				return None
		elif ["lights","pump_pin","beds"].count(setting_to_change) != 0 or setting_to_change.startswith("light_pin") or setting_to_change.startswith("water_pin"):
			if ["lights","beds"].count(setting_to_change) != 0:
				print("When these are changed, the GUI needs to be rearranged, which I haven't coded yet.")
				assert False
			try:
				new_val = str(int(self.settings_text_entry.get_text()))
			except ValueError:
				print("We kinda need these to be ints.")
				self.lock.release()
				return None
		elif ["is_debug"].count(setting_to_change) != 0:
			if ["True","False"].count(self.settings_text_entry.get_text()) == 0:
				print("We kinda need these to be bools.")
				self.lock.release()
				return None
		elif ["last_file_number"].count(setting_to_change) != 0 or setting_to_change.startswith("bed") or setting_to_change.startswith("control_parameter") or setting_to_change.startswith("deadband"):#this only doesn't catch beds because we already found it on line 356
			print("Changing this randomly will definitley break the software. If you know what you're doing, use the CLI, which is less picky")
			self.lock.release()
			return None
		attrs[setting_to_change] = self.settings_text_entry.get_text()
		set_attributes()
		self.lock.release()
	async def automatic_control(self):
		global attrs
		while True:
			await self.lock.acquire()
			water()
			light()
			self.lock.release()
			await self.update_GUI()
			await asyncio.sleep(attrs["interval"])
	async def camera_control(self):
		global attrs
		while True:
			await self.lock.acquire()
			if attrs["recording_status"]:
				camera_capture()
			await self.update_GUI()
			self.lock.release()
			await asyncio.sleep(attrs["camera_interval"])
	async def update_GUI(self):
		global attrs
		for n in range(attrs["beds"]):
			if attrs["bed" + str(n)]:
				self.water_pages[n].get_start_widget().set_label("Bed " + str(n) + " is running.")
			else:
				self.water_pages[n].get_start_widget().set_label("Bed " + str(n) + " is not running.")
		self.preview_image.set_from_file(get_file_name(attrs["last_file_number"]))
		self.camera_text.set_label("Overall, " + attrs["last_file_number"] + " images have been captured by this device.\nCurrently, images will be captured every " + attrs["last_file_number"] + " seconds.")
		return None

# Finalization and execution ****************************************************************************************
if attrs["is_debug"] == "True":
	print(__name__)
if __name__ == "__main__":
	app()
