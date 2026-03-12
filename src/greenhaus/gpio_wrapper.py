#    The GPIO wrapper of the Greenhaus programme.
#    Copyright (C) 2025 Frank J. Barth

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
