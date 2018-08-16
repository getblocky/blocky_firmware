from Blocky.Pin import getPin
from machine import Pin

class Switch :
	def __init__(self , port):
		self.p = getPin(port)
		if self.p[0] == None :
			network.log('sw-declare->' , 'Wrong Pin')
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
			
	def flip(self):
		self.switch.value(not self.switch.value())

