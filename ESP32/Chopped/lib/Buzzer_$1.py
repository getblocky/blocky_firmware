 >= len(self.sequence):
			self.timer.deinit()
			self.pwm.deinit()
			self.playing = False
		else :
			try :
				self.timer.deinit()
			except :
				pass
				
			try :
				self.timer = None
				self.timer = core.machine.Timer(-1)
				self.timer.init(mode=core.machine.Timer.ONE_SHOT,period=self.sequence[self.pos-1][1],callback=self.isr_handler)
			except :
				pass
			
		
