)
						loop.create_task(Cancellable(self.cb_temperature[0])(self.weather.humidity()))
						
				except Exception:
					print('weather-event-humd->',err)
					pass
				
	"""
		




