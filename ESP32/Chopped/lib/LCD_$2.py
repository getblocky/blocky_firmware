f.i2c_addr, bytearray([byte]))
		byte = (0x01 | (self.backlight << 3) | ((data & 0x0f) << 4))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x04]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
		
class LCD ():
	def __init__(self , port , addr = 56 , line = 2 , column = 16):
		self.p = port
		self.pin = core.getPort(self.p)
		self.line = line
		self.column = column
		self.addr = addr
		self.reinit = False
		self.i2c = core.machine.I2C(scl=core.machine.Pin(self.pin[0]),\
			sda=core.machine.Pin(self.pin[1]) ,freq = 100000)
		try :
			self.lcd = I2cLcd(self.i2c,self.addr,self.line,self.column)
			self.lcd.clear()
			self.lcd.backlight_on()
			self.lcd.display_on()
		except Exception as err:
			self.reinit = True 
			print("[LCD] " , err)
			pass
	
	def clear(self,line=None): #line = 1 , line = 2 , 1 based
		
		try :
			if self.reinit == True :
				self.lcd.init()
				self.reinit = False
			if line == None :
				self.lcd.clear()
			elif isinstance(line , int):
				if line <= self.line :
					self.lcd.move_to(0,line-1)
					self.lcd.putstr(' '*self.column)
		except Exception :
			self.reinit = True
			pass
	def display(self,line = 0 , left = '' , right = ''):
		try :
			if self.reinit == True :
				self.lcd.init()
				self.reinit = False
			if line <= self.line :
				self.lcd.move_to(0,line-1)
				right = str(right)
				left = str(left)
				
				if len(right) > 0:
					left =left[0:self.column-len(right)-1]
					string = left +':' + ' '*(self.column-len(left)-len(right)-1)+ right
				else :
					string = left + ' '*(self.column-len(left))
				
				if len(string) > self.column :
					string = string[0:self.column]
				self.lcd.putstr(string)
		except Exception :
			self.reinit = True
			pass
			
	def backlight(self , state = 'on'):
		try :
			if self.reinit == True :
				self.lcd.init()
				self.reinit = False
			if state == 'on' :
				self.lcd.backlight_on()
			if state == 'off' :
				self.lcd.backlight_off()
		except Exception:
			self.reinit = True
			pas