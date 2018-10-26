
#version=1.0
import sys
core=sys.modules['Blocky.Core']
class Relay :
	def __init__(self , port):
		self.p = core.getPort(port)
		if self.p[0] == None :
			return 
		self.switch = core.machine.Pin(self.p[0] , core.machine.Pin.OUT)
		self.switch.value(0)
		
	def turn(self , state):
		if state == "flip" :
			self.switch.value(not self.switch.value())
		else :
			try :

				self.switch.value( state )
			except :
				pass


