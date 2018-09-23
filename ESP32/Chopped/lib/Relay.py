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
		val = 0
		if isinstance(state,list): # Blynk message is a list
			state = state[0]
		elif isinstance(state,str): # String based support
			state = state.lower()
			if state == "on":
				val = 1
			elif state == "flip":
				val = not self.switch.value()
		elif isinstance(state,int):
			if state > 0:
				val = 1
		
		self.switch.value(val)
		
	def state(self):
		return 'on' if self.switch.value() else 'off'

