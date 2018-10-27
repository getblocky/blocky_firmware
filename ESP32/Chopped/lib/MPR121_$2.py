de if temporarily entered stop mode
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
			except Exce