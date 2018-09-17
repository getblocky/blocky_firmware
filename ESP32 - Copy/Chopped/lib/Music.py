#version=1.0
#from blocky_utility import get_free_UART TODO
import sys
core = sys.modules['Blocky.Core']

class Music :
	def __init__ ( self , port ):
		self.port = port
		self.p = core.getPort(port)
		if (pin[0]==None or pin[1] == None):
			core.mainthread.call_soon(core.network.log("Your Music Module can't be used on  "+self.port)
			return
		self.bus = None
	
	def sendStack(self , cmd , param1 , param2):
		# plug and play
		self.bus = core.machine.UART(1 , 9600)
		self.bus.init(baudrate = 9600 , bits = 8 , parity = None , stop = 1 , rx = self.p[0] , tx = self.p[1] )
		# empty the buffer
		while self.bus.any():
			self.bus.read()
			
		buff = bytearray([0x7E, 0xFF, 0x06, cmd,0x01, param1, param2, 0xEF])
		if self.bus.write(buff) == len(buff):
			self.bus.deinit()
		nowTime = core.time.ticks_ms()
		
		
		# no ack 

	def _readRegister(self,cmd,param=None):
		# plug and play
		self.bus = core.machine.UART(1 , 9600)
		self.bus.init(baudrate = 9600 , bits = 8 , parity = None , stop = 1 , rx = self.p[0] , tx = self.p[1] )
		
		nowTime = core.time.ticks_ms()
		while self.bus.any() :
			self.bus.read()
			
		if param == None :
			self.sendStack(cmd,0x00,0x00)
		else :
			self.sendStack(cmd,param//256,param%256)
		while not self.bus.any():
			if core.time.ticks_diff(core.time.ticks_ms() , nowTime) > 200:
				return None
		buffer = self.bus.read(10)
		return buffer[5]*256 + buffer[6]
		
	#=====================================================
	def nextSong(self):
		self.sendStack(0x01,0x00,0x00)
	def previousSong(self):
		self.sendStack(0x02,0x00,0x00)
	def play( song , folder = None ):
		if folder == None :
			try :
				song = max(0,int(song))
				self.sendStack(0x03, song//256 , song%256)
			except :
				return 
			
		else :
			try :
				song = max(0,int(song))
				folder = max(0,int(folder))
				self.sendStack(0x0F, folder , song)
			except :
				return 
			
	
	def volume(self , volume = None ):
		if volume == None :
			return self._readRegister(0x43)
		else :
			try :
		