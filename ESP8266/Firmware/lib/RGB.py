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
		self.tar = list(self.rgb)
	def color(self , led = None, color = None):
		if isinstance(led,int) and color == None :
			if led > len(self.rgb.buf)//3 :
				return None 
			return self.rgb[led]
		if isinstance(color,str):
			color = color.lstrip('#')
			color = tuple(max(0,min(255,int(color[i:i+2], 16))) for i in (0, 2 ,4))
		try:
			if isinstance(led , list):
				for i in range(0,len(led)):
					self.rgb[led[i]-1] = color
				self.rgb.write()
			elif isinstance(led , tuple):
				for i in range(led[0] -1, led[1]):
					self.rgb[i] = color 
				self.rgb.write()
					
		except IndexError as err :
			temp = list(self.rgb)
			self.rgb = NeoPixel(Pin(self.p[0]) , max(led) , timing = True)
			for x in range(len(temp)):
				self.rgb[x] = temp[x]
				
			self.color( led,color)

class 