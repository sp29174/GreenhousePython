#Things needed:
#attrs
#camera_capture
#change_setting
#lights
#water
#Basic idea: both systems simultaneously run identical logic to manage attrs, send it via socket.sendfile, and compare md5 hashes to sync.


attrs = {}
has_GUI = True
import socket
from typer import Typer, Argument, Option
app = Typer(rich_markup_mode="rich")
import asyncio
try:
	import gi
	gi.require_version("Gtk", "4.0")
	from gi.repository import GLib, Gtk
	from gi.events import GLibEventLoopPolicy
except Exception as e:
	print("WARNING: " + str(e))
	has_GUI = False

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
		for n in range(attrs["beds"]):
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
		for n in range(attrs["lights"]):
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
		attrs["is_recording"] = whermst
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
		global attrs
		await self.lock.acquire()
		row = self.settings_listbox.get_selected_row()
		if row == None:
			self.lock.release()
			return None
		setting_to_change = row.get_child().get_text()
		initial_val = self.settings_text_entry.get_text()
		change_setting(setting_to_change,initial_val)
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
			if attrs["is_recording"]:
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
		self.camera_text.set_label("Overall, " + str(attrs["last_file_number"]) + " images have been captured by this device.\nCurrently, images will be captured every " + str(attrs["last_file_number"]) + " seconds.")
		return None

@app.command(help="Connects to the main server thing.")
def connect(addr : Annotated[str, Argument(help="The ip address to connect to.")], port : Annotated[int, Argument(help="The port to look for a socket on.")], reverseport : Annotated[int, Argument(help="The port to return data from.")]):
	global attrs
	u = socket.socket()
	u.connect((addr,port))
	s = socket.socket()
	s.bind(('',reverseport))
	s.listen(1)
	conn, nuaddr = s.accept()
	assert addr = nuaddr
	
	#socket logic goes here
