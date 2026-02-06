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
  def setmode(thing):
    pass
  def setup(pin,mode):
    pass
  def output(pin,thing):
    pass

class MCP:
  P0 = None
  P1 = None
  P2 = None
  def MCP3008(spi, cs):
    return None
