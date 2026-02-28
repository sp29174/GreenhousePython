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
