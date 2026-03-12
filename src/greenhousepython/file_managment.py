import shelve
import hashlib
class wrapper_object:
	def __init__():
		self.attrs = shelve.open("cfg.txt", writeback = True)
		if not self.attrs:
			self.attrs["last_file_number"] = 0
			self.attrs["camera_interval"] = 3600
			self.attrs["interval"] = 1
			self.attrs["file_name_prefix"] = "gi"
			self.attrs["lights"] = 1
			self.attrs["light_length0"] = 0.5
			self.attrs["latitude"] = 43.0972
			self.attrs["longitude"] = -89.5043
			self.attrs["elevation"] = 355.0
			self.attrs["light_pin0"] = 21
			self.attrs["pump_pin"] = 15
			self.attrs["water_pin0"] = 16
			self.attrs["water_pin1"] = 17
			self.attrs["water_pin2"] = 18
			self.attrs["is_debug"] = True
			self.attrs["is_recording"] = True
			self.attrs["beds"] = 3
			self.attrs["bed0"] = False
			self.attrs["bed1"] = False
			self.attrs["bed2"] = False
			self.attrs["control_parameter0"] = 0.0
			self.attrs["deadband0"] = 0.0
			self.attrs["control_parameter1"] = 0.0
			self.attrs["deadband1"] = 0.0
			self.attrs["control_parameter2"] = 0.0
			self.attrs["deadband2"] = 0.0
			self.attrs.sync()
			#create default attrs
	def data():
		return attrs
	def hash():
		sha = hashlib.sha256()
		sha.update(open("cfg.txt").read())
		return sha.hexdigest()
	def force_writeback(new_data):
		attrs.close()
		with open("cfg.txt",'w') as file:
			file.write(new_data)
		attrs = shelve.open("cfg.txt", writeback = True)

#Helpers ****************************************************************************************

#figure out where the nth photo is (or at least should be)
def get_file_name(file_number):
    global attrs
    if (file_number == 0):
        return "../../images/placeholder.jpg"
    return "../../images/" + attrs["file_name_prefix"] + str(file_number) + ".jpg"
