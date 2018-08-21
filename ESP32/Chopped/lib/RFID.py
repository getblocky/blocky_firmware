#version=1.0
import Blocky.uasyncio as asyncio
from Blocky.asyn import cancellable , Cancellable
from Blocky.Pin import *
from Blocky.Network import network
from time import *
PN532_MIFARE_ISO14443A				= 0x00
PN532_ACK_STRING					= bytearray([0x00,0x00,0xFF,0x00,0xFF,0x00])
PN532_ACK_FRAME						= bytearray([0x00,0x00,0xFF,0x00,0xFF,0x00])
def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('reduce() of empty sequence with no initial value')
    accum_value = initializer
    for x in it:
        accum_value = function(accum_value, x)
    return accum_value

class RFID:
	def __init__ (self,port):
		self.last = None 
		self.status = False 
		self.message = None
		self.pin = getPin(port)
		self.cb = None
		from machine import UART 
		self.ser = UART ( 1 , tx = self.pin[0] , rx = self.pin[1] , baudrate = 115200 )
		self.status = True
		self.ser.write( '\x55\x55\x00\x00\x00') # wakeup babe
		self.SAM_configuration()
		
		loop = asyncio.get_event_loop()
		loop.call_soon(self._handler())
	def _uint8_add(self,a,b): return ((a & 0xFF) + (b & 0xFF)) & 0xFF
	def _write_frame(self,data):
		length = len(data)
		frame = bytearray(length+7)
		frame[0] = 0x00
		frame[1] = 0x00
		frame[2] = 0xFF
		frame[3] = length & 0xFF
		frame[4] = self._uint8_add(~length, 1)
		frame[5:-2] = data
		checksum = reduce(self._uint8_add,data,0xFF)
		frame[-2] = ~checksum & 0xFF
		frame[-1] = 0x00
		ack = False
		while not ack:
			self.ser.write(frame)
			ack = self._ack_wait(1000)
			sleep_ms(200)
		return ack 
	def _ack_wait(self , timeout):
		ack = False 
		rx_info = bytearray()
		start_time = ticks_ms()
		current_time = start_time
		while current_time-start_time<timeout and not ack :
			sleep_ms(120)
			while self.ser.any():
				rx_info.extend(self.ser.read())
			current_time = ticks_ms()
			if len(rx_info):
				ack = True 
		if ack:
			self.mess