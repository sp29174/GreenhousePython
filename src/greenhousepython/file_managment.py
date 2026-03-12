import shelve
attrs = shelve.open("cfg.txt", writeback = True)
if not attrs:
	attrs["last_file_number"] = 0
	attrs["camera_interval"] = 3600
	attrs["interval"] = 1
	attrs["file_name_prefix"] = "gi"
	attrs["lights"] = 1
	attrs["light_length0"] = 0.5
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
