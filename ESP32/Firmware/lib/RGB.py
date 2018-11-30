#version=1.0
from machine import Pin
from neopixel import NeoPixel
from Blocky.Pin import getPin

class RGB:
	def __init__(self,port , num = 1):
		self.p = getPin(port)
		if self.p[0] == None :
			return 
		self.rgb = NeoPixel(Pin(self.p[0]) , num , timing = True)

	def colour(self,start,stop,colour,update=True):
		if start > stop :
			return
		if isinstance(colour,str):
			colour = colour.lstrip('#')
			colour = tuple(max(0,min(255,int(colour[i:i+2], 16))) for i in (0, 2 ,4))
		elif isinstance(colour,list):
			if len(list) < 3 :
				return
		else :
			return
		
		if start > len(self.rgb) or stop > len(self.rgb):
			temp = list(self.rgb)
			self.rgb = NeoPixel(Pin(self.p[0]) , max(start,stop) , timing = True)
			for x in range(len(temp)):
				self.rgb[x] = temp[x]
				
		for x in range(start,stop+1):
			self.rgb[x-1] = colour
			
		if update == True:
			self.rgb.write()
