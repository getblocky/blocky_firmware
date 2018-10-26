#version=1.0
import sys;core = sys.modules['Blocky.Core']
class I2cLcd():
	def __init__(self, i2c, i2c_addr, num_lines, num_columns):
		self.i2c = i2c
		self.i2c_addr = i2c_addr
		self.num_lines = num_lines
		if self.num_lines > 4:
			self.num_lines = 4
		self.num_columns = num_columns
		if self.num_columns > 40:
			self.num_columns = 40
		self.cursor_x = 0
		self.cursor_y = 0
		self.backlight = True
		try :
			self.init() 
		except :
			pass
	def init(self):
		self.i2c.writeto(self.i2c_addr, bytearray([0]))
		core.time.sleep_ms(20)   # Allow LCD time to powerup
		# Send reset 3 times
		self.hal_write_init_nibble(0x30)
		core.time.sleep_ms(5)	# need to delay at least 4.1 msec
		self.hal_write_init_nibble(0x30)
		core.time.sleep_ms(1)
		self.hal_write_init_nibble(0x30)
		core.time.sleep_ms(1)
		# Put LCD into 4 bit mode
		self.hal_write_init_nibble(0x20)
		core.time.sleep_ms(1)
		#LcdApi.__init__(self, num_lines, num_columns)
		self.display_off()
		self.backlight_on()
		self.clear()
		self.hal_write_command(0x04 | 0x02)
		self.hide_cursor()
		self.display_on()
		cmd = 0x20
		if self.num_lines > 1:
			cmd |= 0x08
		self.hal_write_command(cmd)
			
	def clear(self):
		self.hal_write_command(0x01)
		self.hal_write_command(0x02)
		self.cursor_x = 0
		self.cursor_y = 0

	def show_cursor(self):
		self.hal_write_command(0x08 | 0x04 | 0x02)

	def hide_cursor(self):
		self.hal_write_command(0x08 | 0x04)

	def blink_cursor_on(self):
		self.hal_write_command(0x08 | 0x04 | 0x02 | 0x01)

	def blink_cursor_off(self):
		self.hal_write_command(0x08 | 0x04 |0x02)

	def display_on(self):
		self.hal_write_command(0x08 | 0x04)

	def display_off(self):
		self.hal_write_command(0x08)

	def backlight_on(self):
		self.backlight = True
		self.hal_backlight_on()

	def backlight_off(self):
		self.backlight = False
		self.hal_backlight_off()

	def move_to(self, cursor_x, cursor_y):
		self.cursor_x = cursor_x
		self.cursor_y = cursor_y
		addr = cursor_x & 0x3f
		if cursor_y & 1:
			addr += 0x40	# Lines 1 & 3 add 0x40
		if cursor_y & 2:
			addr += 0x14	# Lines 2 & 3 add 0x14
		self.hal_write_command(0x80 | addr)

	def putchar(self, char):
		if char != '\n':
			self.hal_write_data(ord(char))
			self.cursor_x += 1
		if self.cursor_x >= self.num_columns or char == '\n':
			self.cursor_x = 0
			self.cursor_y += 1
			if self.cursor_y >= self.num_lines:
				self.cursor_y = 0
			self.move_to(self.cursor_x, self.cursor_y)

	def putstr(self, string):
		for char in string:
			self.putchar(char)

	def custom_char(self, location, charmap):
		location &= 0x7
		self.hal_write_command(0x40 | (location << 3))
		core.time.sleep_us(40)
		for i in range(8):
			self.hal_write_data(charmap[i])
			core.time.sleep_us(40)
		self.move_to(self.cursor_x, self.cursor_y)

	def hal_backlight_on(self):
		pass

	def hal_backlight_off(self):
		pass

	def hal_write_command(self, cmd):
		raise NotImplementedError

	def hal_write_data(self, data):
		raise NotImplementedError
		
	def hal_write_init_nibble(self, nibble):
		byte = ((nibble >> 4) & 0x0f) << 4
		self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x04]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))

	def hal_backlight_on(self):
		self.i2c.writeto(self.i2c_addr, bytearray([1 << 3]))

	def hal_backlight_off(self):
		self.i2c.writeto(self.i2c_addr, bytearray([0]))

	def hal_write_command(self, cmd):
		byte = ((self.backlight << 3) | (((cmd >> 4) & 0x0f) << 4))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x04]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
		byte = ((self.backlight << 3) | ((cmd & 0x0f) << 4))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x04]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
		if cmd <= 3:
			# The home and clear commands require a worst case delay of 4.1 msec
			core.time.sleep_ms(5)

	def hal_write_data(self, data):
		byte = (0x01 | (self.backlight << 3) | (((data >> 4) & 0x0f) << 4))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x04]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
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
			pass

