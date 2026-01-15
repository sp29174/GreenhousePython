class Picamera2:
  def __init__(self):
    pass
  def start(self):
    pass
  def create_still_configuration(self):
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

class busio:
  def SPI(clock, MSIO, MOSI):
    pass

class digitalio:
  def DigitalInOut(thing):
    pass

class board:
  SCK = None
  MISO = None
  MOSI = None
  CE0 = None

class MCP:
  P0 = None
  P1 = None
  P2 = None
  def MCP3008(spi, cs):
    return None

class AnalogIn:
  def __init__(self,mcp,pin):
    self.value = None
    self.voltage = None    
