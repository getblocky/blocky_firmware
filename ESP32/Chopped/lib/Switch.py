#version=1.0
import sys
core=sys.modules['Blocky.Core']
class Relay :
	def __init__(self , port):
		self.p = core.getPort(port)
		if self.p[0] == None :
			core.mainthread.call_soon(core.network.log('Your Relay can be used on'+port))
			return 
		self.switch = Pin(self.p[0] , Pin.OUT)
		self.switch.value(0)
		
	def turn(self , state):
		if isinstance(state , int):
			self.switch.value(state)
		elif isinstance(state , str):
			if state == 'on':
				self.switch.value(1)
			elif state == 'off':
				self.switch.value(0)
			elif state == 'flip':
				self.switch.value(not self.switch.value())
	def state(self)::
		return 'on' if self.switch.value() else 'off'
	def flip(self):
		self.switch.value(not self.switch.value())

