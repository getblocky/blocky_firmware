#version=1.0
import sys
core = sys.modules['Blocky.Core']
class Potentiometer :
	def __init__ (self , port , range = 3.3):
		self.pin = core.getPort(port)
		if (self.pin[2] == None):
			return 
		
		self.adc = core.machine.ADC(core.machine.Pin(self.pin[2],core.machine.Pin.IN))
		if self.pin[0] != self.pin[2]:
			core.machine.PWM(core.machine.Pin(self.pin[0],core.machine.Pin.IN)).deinit()
			core.machine.Pin(self.pin[0] , core.machine.Pin.IN)
		if (range == 1.1):		self.adc.atten(core.machine.ADC.ATTN_0DB)
		elif (range == 1.5):	self.adc.atten(core.machine.ADC.ATTN_2_5DB)
		elif (range == 2.2):	self.adc.atten(core.machine.ADC.ATTN_6DB)
		elif (range == 3.3):	self.adc.atten(core.machine.ADC.ATTN_11DB)
		
	def value(self):
		return self.adc.read()
