# AN2001 
from machine import Pin
from dht import *
from Blocky.Pin import getPin
from Blocky.Timer import runtime
import Blocky.uasyncio as asyncio
from Blocky.asyn import  Cancellable

class Weather:
	def __init__ (self , port,module='DHT11'):
		pin = getPin(port)
		if (pin[0] == None):
			return 
		if module == 'DHT11': self.weather = DHT11(Pin(pin[0]))
		elif module == 'DHT22': self.weather = DHT22(Pin(pin[0]))
		elif module == 'DHTBase': self.weather = DHTBase(Pin(pin[0]))
		else :
			raise NameError
		self.last_poll = runtime()
		self.cb_humidity = []
		self.cb_temperature = []
		loop = asyncio.get_event_loop()
		loop.call_soon(self.handler())
		
	def temperature (self):
		if runtime() - self.last_poll > 2000:
			self.last_poll = runtime()
			try :
				self.weather.measure()
			except Exception:
				pass
		return self.weather.temperature()
	def humidity(self):
		if runtime() - self.last_poll > 2000:
			self.last_poll = runtime()
			try :
				self.weather.measure()
			except Exception:
				pass
		return self.weather.humidity()
	
	def event(self,type,function):
		if type == 'temperature':
			self.cb_temperature = [function,'g' if str(function).find('generator') >0 else 'f']
		if type == 'humidity':
			self.cb_humidity = [function,'g' if str(function).find('generator') >0 else 'f']
		
		
	async def handler(self):
		
		while True :
			temp = self.weather.temperature()
			humd = self.weather.humidity()
			
			await asyncio.sleep_ms(2500)
			try :
				self.weather.measure()
			except Exception:
				pass
			if self.weather.temperature() != temp and self.cb_temperature:
				try :
					if self.cb_temperature[1] == 'f':
						self.cb_temperature[0](self.weather.temperature())
					if self.cb_temperature[1] == 'g':
						loop = asyncio.get_event_loop()
						loop.create_task(Cancellable(self.cb_temperature[0])(self.weather.temperature()))
						
				except Exception as err:
					print('weather-event-temp->',err)
					pass
			if self.weather.humidity() != temp and self.cb_humidity:
				try :
					if self.cb_humidity[1] == 'f':
						self.cb_humidity[0](self.weather.humidity())
					if self.cb_humidity[1] == 'g':
						loop = asyncio.get_event_loop()
						loop.create_task(Cancellable(self.cb_temperature[0])(self.weather.humidity()))
						
				except Exception:
					print('weather-event-humd->',err)
					pass
				
			
		



