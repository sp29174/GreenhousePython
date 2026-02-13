from gpiod import chip as ch

class GPIO:
	def __init__(self):
		self.BCM = None
		self.OUT = None
		self.HIGH = None
		self.LOW = None
		self.chip = ch.Chip("/dev/gpiochip0")
	def setmode(self, *args):
		pass
	def setup():
		pass
	def cleanup():
		self.chip.close()
	def output():
		pass
