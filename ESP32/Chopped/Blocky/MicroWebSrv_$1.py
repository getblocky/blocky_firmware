   = "/flash/www" ) :
		self._routeHandlers = routeHandlers
		self._srvAddr	   = (bindIP, port)
		self._webPath	   = webPath
		self._notFoundUrl   = None
		self._started	   = False
		self.MaxWebSocketRecvLen	 = 1024
		self.WebSocketThreaded	   = True
		self.AcceptWebSocketCallback = None
		
		self._socket = None 
		self.bootdone = False
	# ===( Server Process )=======================================================
	
	async def _socketProcess(self) :
		try :
			self._started = True
			wlan_ap = core.Network.WLAN(core.Network.AP_IF)
			wlan_ap.active(True)
			print('START AP')
			while core.flag.ONLINE == False :
				await core.asyncio.sleep_ms(200)
				if wlan_ap.isconnected():
					try :
						try :
							client, cliAddr = self._socket.accept()
							
						except :
							continue
						print(client , cliAddr)
						print('socket->Accepted')
						a = self._client(self, client, cliAddr)
						a._processRequest()
					except Exception as err :
						print('client->',err)
						core.sys.print_exception(err)
				
			self._started = False
			print('CLOSE AP')
		except Exception as err:
			print( ' _socket -> ' , err)
	
	# ===( Functions )============================================================
	
	async def Start(self, threaded=True) :
		if not self._started :
			reset_timer = core.machine.Timer(1)
			reset_timer.init(mode=core.machine.Timer.ONE_SHOT,period = 1800000,callback =lambda t:core.machine.reset)
			self._socket = core.socket.socket( core.socket.AF_INET,
										  core.socket.SOCK_STREAM,
										  core.socket.IPPROTO_TCP )
			self._socket.setsockopt( core.socket.SOL_SOCKET,
									 core.socket.SO_REUSEADDR,
									 1 )
									 
			self._socket.bind(self._srvAddr)
			self._socket.listen(1)
			self._socket.setblocking(False)
			await self._socketProcess ()
			
	def Stop(self) :
		if self._started :
			self._socket.close()

	def IsStarted(self) :
		return self._started

	def SetNotFoundPageUrl(self, url=None) :
		self._notFoundUrl = url

	def Get