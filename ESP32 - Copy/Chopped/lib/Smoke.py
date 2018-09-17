#version=1.0
from machine import ADC , Pin 
from Blocky.Pin import getPin

class Smoke :
	def __init__ (self , port , atten = 4):
		self.p = getPin(port)
		if (self.p[2] == None):
			return 
		self.adc = ADC(Pin(self.p[2]))
		if (atten == 1) :self.adc.atten(ADC.ATTN_0DB)
		elif (atten == 2): self.adc.atten(ADC.ATTN_2_5DB)
		elif (atten == 3): self.adc.atten(ADC.ATTN_6DB)
		elif (atten == 4): self.adc.atten(ADC.ATTN_11DB)
	def read(self):
		return self.adc.read()
		
	


