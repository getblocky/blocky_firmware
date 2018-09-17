:
			os.stat('Remote')
		except:
			os.mkdir('Remote')  
		f = open('Remote/' + str(name) + '.json','w')
		f.write(dumps({'data':list,'freq':freq}))
		f.close()
		# Feedback
		self.recv = Pin(self.p[0],Pin.OUT)
		for x in range(10):
			self.recv.value(0)
			sleep_us(30000)
			self.recv.value(1)
			sleep_us(30000)
		self.recv = Pin(self.p[0],Pin.IN)
		
	def event(**kwargs):
		from Blocky.Network import network
		network.log('Remote event not implemeted')
		

