#version=1.0
"""
MicroPython MPR121 capacitive touch keypad and breakout board driver
https://github.com/mcauser/micropython-mpr121

MIT License
Copyright (c) 2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sys
core = sys.modules['Blocky.Core']

def get_bit(byteval,idx):
	return ((byteval&(1<<idx))!=0)
	
class MPR121:
	def __init__(self, port, address=0x5A):
		self.p = core.getPort( port )
		self.i2c = core.machine.I2C ( scl = core.machine.Pin(self.p[0]) , sda = core.machine.Pin(self.p[1]) )
		self.address = address
		self.error = False
		self.prev = 0
		self.handler = [ [None,None] for x in range(12) ]
		self.reset()
		core.mainthread.call_soon(core.asyn.Cancellable(self.poller)())
	
	def _register8(self, register, value=None):
		if value is None:
			return self.i2c.readfrom_mem(self.address, register, 1)[0]
		self.i2c.writeto_mem(self.address, register, bytearray([value]))

	def _register16(self, register, value=None):
		if value is None:
			data = self.i2c.readfrom_mem(self.address, register, 2)
			return core.struct.unpack("<H", data)[0]
		self.i2c.writeto_mem(self.address, register, core.struct.pack("<H", value))

	def reset(self):
		try :
			# Soft reset of device.
			
			self._register8( 128, 0x63)
			core.time.sleep_ms(1)
			self._register8( 94, 0x00)
			# Check CDT, SFI, ESI configuration is at default values.
			c = self._register8( 93)
			if c != 0x24:
			   return False
			# Set threshold for touch and release to default values.
			self.set_thresholds(12, 6)
			# Configure baseline filtering control registers.
			self._register8( 43, 0x01)
			self._register8( 44, 0x01)
			self._register8( 45, 0x0E)
			self._register8( 46, 0x00)
			self._register8( 47, 0x01)
			self._register8( 48, 0x05)
			self._register8( 49, 0x01)
			self._register8( 50, 0x00)
			self._register8( 51, 0x00)
			self._register8( 52, 0x00)
			self._register8( 53, 0x00)
			# Set other configuration registers.
			self._register8( 91, 0)
			self._register8( 92, 0x10) # default, 16uA charge current
			self._register8( 93, 0x20) # 0.5uS encoding, 1ms period
			# Enable all electrodes.
			self._register8( 94, 0x8F) # start with first 5 bits of baseline tracking
			# All done, everything succeeded!
			print('[MPR121] -> Reset successful')
			self.error = False
		except Exception:
			pass 
		return True

	def set_thresholds(self, touch, release, electrode=None):
		"""Sets the touch and release thresholds (0-255) for a single electrode (0-11) or all electrodes"""
		if not 0 <= touch <= 255:
			raise ValueError('Touch must be in range 0-255.')
		if not 0 <= release <= 255:
			raise ValueError('Release must be in range 0-255.')
		f = 0 if electrode is None else electrode
		t = 12 if electrode is None else electrode + 1

		# you can only modify the thresholds when in stop mode
		config = self._register8(94)
		if config != 0:
			self._register8(94, 0)

		for i in range(f, t):
			self._register8(65 + i * 2, touch)
			self._register8(66 + i * 2, release)

		# return to previous mode if temporarily entered stop mode
		if config != 0:
			self._register8(94, config)

	def filtered_data(self, electrode):
		"""Returns filtered data value for the specified electrode (0-11)"""
		if not 0 <= electrode <= 11:
			raise ValueError('Electrode must be in range 0-11.')
		return self._register16(4 + electrode * 2)

	def baseline_data(self, electrode):
		"""Returns baseline data value for the specified electrode (0-11)"""
		if not 0 <= electrode <= 11:
			raise ValueError('Electrode must be in range 0-11.')
		return self._register8(30 + electrode) << 2

	def touched(self):
		"""Returns a 12-bit value representing which electrodes are touched. LSB = electrode 0"""
		try :
			value =  self._register16(0)
			return value
		except :
			self.error = True
			return 0

	def is_touched(self, electrode):
		"""Returns True when the specified electrode is being touched"""
		if not 0 <= electrode <= 11:
			raise ValueError('Electrode must be in range 0-11.')
		t = self.touched()
		return (t & (1 << electrode)) != 0
		
	def event ( self , type , pin , function ):
		self.handler[pin][0 if type=='touch' else 1] = function
	
	@core.asyn.cancellable
	async def poller (self):
		while True :
			if self.error == True :
				self.reset()
			try :
				now = self.touched()
				if now != self.prev :
					for x in range(11):
						if get_bit(self.prev,x) != get_bit(now,x):
							if get_bit(now , x):
								if self.handler[x][0] != None :
									if core.flag.duplicate == True :
										core.mainthread.call_soon ( core.asyn.Cancellable( self.handler[x][0] )() )
									else :
										await core.call_once('user_mpr121_{}.{}'.format(x,1),self.handler[x][0])
							else :
								if self.handler[x][1] != None :
									if core.flag.duplicate == True :
										core.mainthread.call_soon ( core.asyn.Cancellable( self.handler[x][1] )() )
									else :
										await core.call_once('user_mpr121_{}.{}'.format(x,0),self.handler[x][1])
										
				self.prev = now
			except Exception as err	:
				self.error = True
			await core.asyncio.sleep_ms(100)
	


