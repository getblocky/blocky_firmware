#version=1.0
import sys;core = sys.modules['Blocky.Core']

# This library utilize NeoPixel->WS2811->L9110
class Motor:
	def __init__(self , port , num=2):
		self.p = port
		self.pin = core.getPort(self.p)[0]
		if self.pin == None :
			return
		self.ws2111 = core.neopixel.NeoPixel(core.machine.Pin(self.pin) , num , timing = True)
		self.ws2811.fill((0,0,0))
		self.ws2811.write()
	
	def speed (motor , speed):
		if motor <= len(self.ws2811):
			self.ws2811[motor] = ( 7   ,abs(speed))
		
		