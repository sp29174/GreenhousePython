from gpiod.chip import Chip as c
from gpiod.line import Value as v

#A really dodgy hack. You can use this code in your project, but should you?

class gpio:
	def __init__(self, path : str = "/dev/gpiochip0", settings = None):
		self.BCM = None
		self.OUT = True
		self.IN = False
		self.HIGH = v.ACTIVE
		self.LOW = v.INACTIVE
		self.chip = c(path)
		self.lines = {}
	def setmode(self, *args):
		pass
	def setup(self,number,type):
		self.lines[number] = self.chip.request_lines({number : None})#Gimme all them lines
	def cleanup(self):
		self.chip.close()
	def output(self,number,value):
		self.lines[number].set_value(number,value)
