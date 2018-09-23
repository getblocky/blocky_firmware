#version=1.0
import sys;core = sys.modules['Blocky.Core']

"""Implements a HD44780 character LCD connected via PCF8574 on I2C.
   This was tested with: https://www.wemos.cc/product/d1-mini.html"""
   
DEFAULT_I2C_ADDR = 56
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

LCD_CLR = 0x01			  # DB0: clear display
LCD_HOME = 0x02			 # DB1: return to home position
LCD_ENTRY_MODE = 0x04	   # DB2: set entry mode
LCD_ENTRY_INC = 0x02		# --DB1: increment
LCD_ENTRY_SHIFT = 0x01	  # --DB0: shift
LCD_ON_CTRL = 0x08		  # DB3: turn lcd/cursor on
LCD_ON_DISPLAY = 0x04	   # --DB2: turn display on
LCD_ON_CURSOR = 0x02		# --DB1: turn cursor on
LCD_ON_BLINK = 0x01		 # --DB0: blinking cursor
LCD_MOVE = 0x10			 # DB4: move cursor/display
LCD_MOVE_DISP = 0x08		# --DB3: move display (0-> move cursor)
LCD_MOVE_RIGHT = 0x04	   # --DB2: move right (0-> left)
LCD_FUNCTION = 0x20		 # DB5: function set
LCD_FUNCTION_8BIT = 0x10	# --DB4: set 8BIT mode (0->4BIT mode)
LCD_FUNCTION_2LINES = 0x08  # --DB3: two lines (0->one line)
LCD_FUNCTION_10DOTS = 0x04  # --DB2: 5x10 font (0->5x7 font)
LCD_FUNCTION_RESET = 0x30   # See "Initializing by Instruction" section
LCD_CGRAM = 0x40			# DB6: set CG RAM address
LCD_DDRAM = 0x80			# DB7: set DD RAM address
LCD_RS_CMD = 0
LCD_RS_DATA = 1
LCD_RW_WRITE = 0
LCD_RW_READ = 1


class I2cLcd():
	"""Implements a HD44780 character LCD connected via PCF8574 on I2C."""

	def __init__(self, i2c, i2c_addr, num_lines, num_columns):
		self.i2c = i2c
		self.i2c_addr = i2c_addr
		self.i2c.writeto(self.i2c_addr, bytearray([0]))
		core.time.sleep_ms(20)   # Allow LCD time to powerup
		# Send reset 3 times
		self.hal_write_init_nibble(LCD_FUNCTION_RESET)
		core.time.sleep_ms(5)	# need to delay at least 4.1 msec
		self.hal_write_init_nibble(LCD_FUNCTION_RESET)
		core.time.sleep_ms(1)
		self.hal_write_init_nibble(LCD_FUNCTION_RESET)
		core.time.sleep_ms(1)
		# Put LCD into 4 bit mode
		self.hal_write_init_nibble(LCD_FUNCTION)
		core.time.sleep_ms(1)
