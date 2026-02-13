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
	def setup(self):
		pass
	def cleanup(self):
		self.chip.close()
	def output(self):
		pass
