cb_humidity[1] == 'f':
						self.cb_humidity[0](self.weather.humidity())
					if self.cb_humidity[1] == 'g':
						loop = asyncio.get_event_loop()
						loop.create_task(Cancellable(self.cb_temperature[0])(self.weather.humidity()))
						
				except Exception:
					print('weather-event-humd->',err)
					pass
				
	"""
		




