#version=1.0
# AN2001 
from dht import *

class Weather:
	def __init__ (self , port,module='DHT11'):
		self.port = port
		self.p = core.getPort(port)
		if (self.pin[0] == None):
			return 
		if module == 'DHT11': 
			self.weather = DHT11(core.machine.Pin(pin[0]))
		else :
			raise NameError
		self.last_poll = core.Timer.runtime()
		#core.mainthread.create_task(self.handler())
		
	def temperature (self):
		if core.Timer.runtime() - self.last_poll > 2000:
			self.last_poll = core.Timer.runtime()
			try :
				self.weather.measure()
			except Exception:
				core.mainthread.call_soon(core.network.log('Your Weather Module on '+self.port+' is not working !')
				pass
		return self.weather.temperature()
	def humidity(self):
		if core.Timer.runtime() - self.last_poll > 2000:
			self.last_poll = core.Timer.runtime()
			try :
				self.weather.measure()
			except Exception:
				core.mainthread.call_soon(core.network.log('Your Weather Module on '+self.port+' is not working !')
				pass
		return self.weather.humidity()
	"""
	def event(self,type,function):
		if type == 'temperature':
			self.cb_temperature = [function,'g' if str(function).find('generator') >0 else 'f']
		if type == 'humidity':
			self.cb_humidity = [function,'g' if str(function).find('generator') >0 else 'f']
	"""	
	"""
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
				try 