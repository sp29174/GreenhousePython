#    The mock classes of the Greenhaus programme.
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

class Picamera2:
  def __init__(self):
    pass
  def start(self):
    pass
  def create_still_configuration(self):
    pass
  def configure(self,*args):
    pass

class GPIO:
  BCM = None
  OUT = None
  HIGH = None
  LOW = None
  def setmode(*args,**kwargs):
    pass
  def setup(*args,**kwargs):
    pass
  def output(*args,**kwargs):
    pass
  def cleanup(*args,**kwargs):
    pass

class MCP:
  CH0 = None
  CH1 = None
  CH2 = None
  CH3 = None
  CH4 = None
  CH5 = None
  CH6 = None
  CH7 = None

class MCP3008:
  def __init__(self):
    pass
  def __call__(self, *args, **kwargs):
    return [0,0,0,0,0,0,0,0]
  def fixed(*args,**kwargs):
    return MCP3008()
  def close(self):
    pass

class cv2:
  def __init__(self):
    pass
  def VideoCapture(*args,**kwargs):
    return cv2()
  def imwrite(*args,**kwargs):
    pass
  def imread(*args,**kwargs):
    pass
  def VideoWriter_fourcc(*args,**kwargs):
    pass
  def resize(*args,**kwargs):
    pass
  def release(self):
    pass
  def read(self):
    pass
