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
			addr += 0x40	#