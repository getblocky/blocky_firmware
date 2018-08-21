#version=1.0
import sys
core = sys.modules['Blocky.Core']
class WaterSensor :
	def __init__ (self , port , scale = 3.3):
		pin = core.getPort(port)
		if (pin[2] == None):
			core.mainthread.call_soon(core.network.log("Your Water Sensor module can't be used on "+port))
			return 
		
		self.adc = core.machine.ADC(core.machine.Pin(pin[2]))
		if (atten == 1.1):		self.adc.atten(core.machine.ADC.ATTN_0DB)
		elif (atten == 1.5):	self.adc.atten(core.machine.ADC.ATTN_2_5DB)
		elif (atten == 2.2):	self.adc.atten(core.machine.ADC.ATTN_6DB)
		elif (atten == 3.3):	self.adc.atten(core.machine.ADC.ATTN_11DB)
	def read(self):
		return 4095 - self.adc.read()
		

