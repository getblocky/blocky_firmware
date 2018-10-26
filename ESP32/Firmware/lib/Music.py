#version=1.0
#from blocky_utility import get_free_UART TODO
import machine , time
def getPort(a):
	return 25 , 26 , None 
class Music :
	def __init__ ( self , port ):
		self.port = port
		self.p = getPort(port)
		if (self.p[0]==None or self.p[1] == None):
			return
		self.bus = None
	
	def sendStack(self , cmd , param1 , param2):
		# plug and play
		self.bus = machine.UART(1 , 9600)
		self.bus.init(baudrate = 9600 , bits = 8 , parity = None , stop = 1 , rx = self.p[0] , tx = self.p[1] )
		# empty the buffer
		while self.bus.any():
			self.bus.read()
			
		buff = bytearray([0x7E, 0xFF, 0x06, cmd,0x00, param1, param2, 0xEF])
		#if self.bus.write(buff) == len(buff):
		#	self.bus.deinit()
		self.bus.write(buff) 
		nowTime = time.ticks_ms()
		print('SEND : ',end='')
		for x in buff:
			print(hex(x),end = '\t')
		print()
		
		# no ack 

	def _readRegister(self,cmd,param=None):
		# plug and play
		self.bus = machine.UART(1 , 9600)
		self.bus.init(baudrate = 9600 , bits = 8 , parity = None , stop = 1 , rx = self.p[0] , tx = self.p[1] )
		
		nowTime = time.ticks_ms()
		while self.bus.any() :
			self.bus.read()
			
		if param == None :
			self.sendStack(cmd,0x00,0x00)
		else :
			self.sendStack(cmd,param//256,param%256)
		while not self.bus.any():
			if time.ticks_diff(time.ticks_ms() , nowTime) > 200:
				return None
		buffer = self.bus.read(10)
		print('RECV : ',end='')
		for x in buffer:
			print(hex(x),end = '\t')
		print()
		
		return buffer[5]*256 + buffer[6]
		
	#=====================================================
	def nextSong(self):
		self.sendStack(0x01,0x00,0x00)
	def previousSong(self):
		self.sendStack(0x02,0x00,0x00)
	def play( self , song , folder = None ):
		if folder == None :
			try :
				song = max(0,int(song))
				self.sendStack(0x03, song//256 , song%256)
			except Exception as err:
				print(err)
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
				volume = max(0,min(30,int(volume)))
				self.sendStack(0x06 , 0x00 , volume)
			except :
				return 
	
	def loop ( self , song):
		try :
			song = max(0,int(song))
			self.sendStack(0x08, song//256 , song%256)
		except :
			pass
			
	def setEqualizer(self , eq):
		self.sendStack(0x07 , 0x00 , eq)
		
	def outputDevice( self , device):
		self.sendStack(0x09,0x00,device)
		time.sleep_ms(200)
	def sleep(self):
		self.sendStack(0x0A, 0x00,0x00)
	def reset(self):
		self.sendStack(0x0C,0x00,0x00)
		time.sleep_ms(2000)
	def start(self):
		self.sendStack(0x0D,0x00,0x00)
	def pause(self):
		self.sendStack(0x0E,0x00,0x00)
	def playFolder(self,folder,song):
		self.sendStack(0x0F,folder,song)
	def outputSetting(self,enable,gain):
		self.sendStack(0x10,enable,gain)
	def enableLoopAll(self):
		self.sendStack(0x11,0x00,0x01)
	def disableLoopAll(self):
		self.sendStack(0x11,0x00,0x00)
	def playMP3Folder(self,file):
		self.sendStack(0x12,file//256,file%256)
	def advertise( self,file):
		self.sendStack(0x13,file//256,file%256)
	def stopAdvertise(self):
		self.sendStack(0x15)
		self.sendStack(0x16,0x00,0x00)
	def stop(self):
		self.sendStack(0x16,0x00,0x00)
	def loopFolder(self,folderNumber):
		self.sendStack(0x17, folderNumber//256,folderNumber%256)
	def randomAll(self):
		self.sendStack(0x18,0x00,0x00)
	def enableLoop(self):
		self.sendStack(0x19, 0x00,0x00)
	def disableLoop(self):
		self.sendStack(0x19, 0x01,0x00)
	def enableDAC(self):
		self.sendStack(0x1A, 0x00,0x00)
	def disableDAC(self):
		self.sendStack(0x1A, 0x01,0x00)
	def readState(self):
		return self._readRegister(0x42)
	def readEQ(self):
		return self._readRegister(0x44)
	def readFileCounts(self):
		return self._readRegister(0x48)
	def readCurrentFileNumber(self):
		return self._readRegister(0x4C)
	def readFileCountsInFolder(self,folder):
		return self._readRegister(0x4E,folder)
	def readFolderCounts(self):
		return self._readRegister(0x4F)
		
m = Music ( 'PORT1') 