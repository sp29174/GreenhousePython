# 11/11/2025
# 
# The main file.

#Preinitialization ****************************************************************************************

import socket
from typer import Typer, Argument, Option
app = Typer(rich_markup_mode="rich")

# Initialization ****************************************************************************************

import greenhousepython.file_management as fm
wrapper = fm.wrapper_object()
try:
	import cv2
	x = cv2.VideoCapture(0)
	x.read()
	x.release()#Fix bug where we crash because there's no camera
except ImportError:
	from greenhousepython.nonsense import cv2
try:
	import mcp3008 as MCP
	from mcp3008 import MCP3008
except ImportError as e:
	if wrapper.attrs["is_debug"]:
		print("WARNING: " + str(e))
	from greenhousepython.nonsense import MCP, MCP3008
try:
	from greenhousepython.gpio_wrapper import gpio as g
	GPIO = g()
except Exception as e:
	if wrapper.attrs["is_debug"]:
		print("WARNING: " + str(e))
	try:
		import RPi.GPIO as GPIO
	except ImportError as e:
		if wrapper.attrs["is_debug"]:
			print("WARNING: " + str(e))
		from greenhousepython.nonsense import GPIO
import sys
from datetime import datetime, timedelta, timezone
from astral import sun, Observer
import signal
from typing import Annotated

# Postinitialization ****************************************************************************************

times_off = []
for n in range(wrapper.attrs["lights"]):
	times_off.append(datetime.now(timezone.utc))
# create the mcp object
mcp = MCP3008.fixed([MCP.CH0, MCP.CH1, MCP.CH2, MCP.CH3, MCP.CH4, MCP.CH5, MCP.CH6, MCP.CH7])
# setup other GPIO
GPIO.setmode(GPIO.BCM)
for x in range(wrapper.attrs["lights"]):
	GPIO.setup(wrapper.attrs["light_pin" + str(x)], GPIO.OUT)
for x in range(wrapper.attrs["beds"]):
	GPIO.setup(wrapper.attrs["water_pin" + str(x)], GPIO.OUT)
GPIO.setup(wrapper.attrs["pump_pin"], GPIO.OUT)
the_camera = cv2.VideoCapture(0)

# More helpers ***********************************************************************************
def do_shutdown(*args,**kwargs):
	global mcp
	global the_camera
	global wrapper.attrs
	if wrapper.attrs["is_debug"]:
		print("Shutting down...")
	try:#we shouldn't let crashes prevent the program from closing, so these must all be wrapped with try.
		mcp.close()#close down water control coms
	except Exception as e:
		if wrapper.attrs["is_debug"]:
			print("WARNING: " + str(e))
		else:
			print("Warning: we couldn't close down the water control communitcations.")
	try:
		the_camera.release()#turn off the damn camera
	except Exception as e:
		if wrapper.attrs["is_debug"]:
			print("WARNING: " + str(e))
		else:
			print("Warning: we couldn't close down the camera.")
	try:
		GPIO.cleanup()#knock the GPIO back to high-zed
	except Exception as e:
		if wrapper.attrs["is_debug"]:
			print("WARNING: " + str(e))
		else:
			print("Warning: we couldn't reset the GPIO.")
	wrapper.attrs.close()
	sys.exit(0)#ensure the proghramme actually ends

# Postpostinitialization ***********************************************************************************

signal.signal(signal.SIGTERM,do_shutdown)
signal.signal(signal.SIGINT,do_shutdown)#I have no idea why these aren't the same signal. The program kicks the bucket either way.

# CLI commands   ***********************************************************************************

@app.command(help="Change the setting KEY to VALUE.")
def change_setting(key : Annotated[str, Argument(help="The exact name of the setting to change or create.")], value : Annotated[str, Argument(help="The exact value that the setting should be changed to.")]):
	if ["file_name_prefix"].count(key) != 0:
		print("This part needs logic for automatically renaming files, which I haven't written yet. Sorry!")
		assert False
	elif ["interval","camera_inteval","longitude","latitude","elevation"].count(key) != 0 or key.startswith("control_parameter") or key.startswith("deadband"):
		try:
			new_val = float(value)
		except ValueError:
			print("We kinda need these to be floats.")
			return None
	elif ["lights","pump_pin","beds","last_file_number"].count(key) != 0 or key.startswith("light_pin") or key.startswith("water_pin"):
		if ["lights","beds"].count(setting_to_change) != 0:
			print("When these are changed, the GUI needs to be rearranged, which I haven't coded yet.")
			assert False
		try:
			new_val = int(value)
		except ValueError:
			print("We kinda need these to be ints.")
			return None
	elif ["is_debug","is_recording"].count(key) != 0 or key.startswith("bed"):#this only doesn't catch beds because we already found it on line 160
		if "True" == value:
			new_val = True
		elif "False" == value:
			new_val = False
		else:
			print("We kinda need these to be bools.")
			return None
	else:
		print("Confusion noise: '" + key + "' is not actually a thing.")
		return None
	wrapper.attrs[setting_to_change] = new_val
	wrapper.attrs.sync()

#control pumps using hysteresis based on the values returned from the MCP
@app.command(help="Force the system to run the automatic water control logic without starting the GUI.")
def water():
	global wrapper.attrs
	run_pump = False
	try:#my crummy mock of mcp3008.MCP3008 can't make sense of line 118, so this eyesore is trapped in a try-catch.
		for x in range(wrapper.attrs["beds"]):
			moisture = mcp(1)[x]#normalize values to one using mcp3008.MCP3008 (see https://github.com/luxedo/RPi_mcp3008/blob/master/mcp3008.py#L73)
			if (not wrapper.attrs["bed" + str(x)]) and (moisture < wrapper.attrs["control_parameter" + str(x)] - (wrapper.attrs["deadband" + str(x)]/2)):#this if-else is basically an inelegant hysteresis controller. On the other hand, we're being rewarded for not destroying the pump, not for elegantly destroying the pump.
				GPIO.output(int(wrapper.attrs["water_pin" + str(x)]), GPIO.HIGH)
				wrapper.attrs["bed" + str(x)] = "True"
				wrapper.attrs.sync()
			elif wrapper.attrs["bed" + str(x)] and (moisture > wrapper.attrs["control_parameter" + str(x)] + (wrapper.attrs["deadband" + str(x)]/2)):
				GPIO.output(wrapper.attrs["water_pin" + str(x)], GPIO.LOW)
				wrapper.attrs["bed" + str(x)] = False
				wrapper.attrs.sync()
			if (wrapper.attrs["bed" + str(x)] == "True"):
				run_pump = True#If any bed is on, then run the pump.
		if run_pump:
			GPIO.output(int(wrapper.attrs["pump_pin"]), GPIO.HIGH)
		else:
			GPIO.output(int(wrapper.attrs["pump_pin"]), GPIO.LOW)
	except Exception as e:
		if wrapper.attrs["is_debug"]:
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
	#Another consequence of this is that if you run this code in Iceland or something where the sun won't rise on certain days of the year, this code will have to bodge the sun.
	#There must be a better solution than this, but I couldn't find it. Shrug emoji.
	global wrapper.attrs
	global times_off
	observer = Observer(wrapper.attrs["latitude"],wrapper.attrs["longitude"],wrapper.attrs["elevation"])
	try:
		the_sun = sun.daylight(observer)#The sun is a deadly laser	
	except ValueError as e:#the sun doesn't rise/set today. We therefore need to fudge the sun. This means that, for our purposes, the sun rose at midnight and set a very long time ago.
		if wrapper.attrs["is_debug"]:
			print(str(e))
		the_sun = [datetime(datetime.year,datetime.month,datetime.day),datetime.min]
	if (datetime.now(timezone.utc) >= the_sun[1]):
		if wrapper.attrs["is_debug"]:
			print("We think that it's after sunset.")
		for n in range(wrapper.attrs["lights"]):
			times_off[n] = the_sun[0] + timedelta(days=wrapper.attrs["light_length" + str(n)])
	elif wrapper.attrs["is_debug"]:
		print("We think that it's before sunset.")
	for n in range(wrapper.attrs["lights"]):
		light_on = False
		if (datetime.now(timezone.utc) < times_off[n]):
			light_on = True
			if wrapper.attrs["is_debug"]:
				print("The light should be on.")
		elif wrapper.attrs["is_debug"]:
			print("The light should be off.")
		if light_on:
			GPIO.output(wrapper.attrs["light_pin" + str(n)], GPIO.HIGH)
		else:
			GPIO.output(wrapper.attrs["light_pin" + str(n)], GPIO.LOW)

#A command that captures a photograph, writes it to a file, and updates wrapper.attrs accordingly.
@app.command(help="Manually capture a photograph.")
def camera_capture():#updated to not badly reimplement last_file_name
	global wrapper.attrs
	global the_camera
	ret, frame = the_camera.read()
	if not ret:
		if not wrapper.attrs["is_debug"]:
			assert False#Fuck this!
		else:
			print("Warning: Image capture failed to complete.")
	else:
		cv2.imwrite(get_file_name(wrapper.attrs["last_file_number"] + 1), frame)
		wrapper.attrs["last_file_number"] = wrapper.attrs["last_file_number"] + 1
		wrapper.attrs.sync()

@app.command(help="Assemble the current collection of images into a mp4 video. This will:\n \n 1. Not include the placeholder image, ever. \n 2. Not recoginze images created with file numbers above last_file_number. \n 3. Pollute your shell with warnings if you have nonsequential image numbers. \n 4. Be unaware of the fact that manually captured images are not taken at regular intervals.")
def create_video(output_video_path : Annotated[str, Argument(help="An exact file name, which must be writable, must not have stuff in it, and should not be irrational. If you run this command with sudo and pass /, then it will replace your system with a video. Don't.")], fps : Annotated[int, Option(help="The framerate that the video will be displayed at. Defaults to 24.")] = 24, size : Annotated[str, Option(help="An override to resize your images to a different resolution. This is needed internally for technical reasons, and we saw no reason not to expose it to the commandline. Defaults to your camera resolution.")] = None):
	image_paths = []
	for num in range(1,wrapper.attrs["last_file_number"] + 1):
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
	global wrapper.attrs
	print(times_off)
	print(mcp())
	print(mcp(1))
	keys = wrapper.attrs.keys()#get all the settings
	for key in keys:
		print(key + ":" + str(wrapper.attrs[key]))#assemble key and values into new format

#A quick little command that just starts the GUI.
@app.command(help="Starts the main server thing.")
def open_socket(port : Annotated[int, Argument(help="The port to open a socket on.")], reverseport : Annotated[int, Argument(help="The port to recieve data from.")]):
	global wrapper.attrs
	s = socket.socket()
	s.bind(('',port))
	s.listen(1)
	conn, addr = s.accept()
	u = socket.socket()
	u.connect((addr,reverseport))
	#socket logic goes here

# Finalization and execution ****************************************************************************************
if wrapper.attrs["is_debug"]:
	print(__name__)
if __name__ == "__main__":
	app()












