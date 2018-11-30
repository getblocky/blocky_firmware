	 and self._microWebSrv.AcceptWebSocketCallback :
								MicroWebSocket( socket		 = self._socket,
												httpClient	 = self,
												httpResponse   = response,
												maxRecvLen	 = self._microWebSrv.MaxWebSocketRecvLen,
												threaded	   = self._microWebSrv.WebSocketThreaded,
												acceptCallback = self._microWebSrv.AcceptWebSocketCallback )
								return
						else :
							response.WriteResponseNotImplemented()
					else :
						response.WriteResponseBadRequest()
			except Exception as err:
				core.sys.print_exception(err)
				#response.WriteResponseInternalServerError()
			try :
				print('Socket Close')
				self._socket.close()
			except :
				pass
		
		def _parseFirstLine(self, response) :
			try :
				elements = self._socket.readline().decode().strip().split()
				if len(elements) == 3 :
					self._method  = elements[0].upper()
					self._path	= elements[1]
					self._httpVer = elements[2].upper()
					elements	  = self._path.split('?', 1)
					if len(elements) > 0 :
						self._resPath = MicroWebSrv._unquote_plus(elements[0])
						if len(elements) > 1 :
							self._queryString = elements[1]
							elements = self._queryString.split('&')
							for s in elements :
								param = s.split('=', 1)
								if len(param) > 0 :
									value = MicroWebSrv._unquote(param[1]) if len(param) > 1 else ''
									self._queryParams[MicroWebSrv._unquote(param[0])] = value
					return True
			except :
				pass
			return False
	
		
		def _parseHeader(self, response) :
			while True :
				elements = self._socket.readline().decode().strip().split(':', 1)
				if len(elements) == 2 :
					self._headers[elements[0].strip()] = elements[1].strip()
				elif len(elements) == 1 and len(elements[0]) == 0 :
					if self._method == 'POST' :
						self._contentType   = self._headers.get("Content-Type", None)
						self._contentLength = int(self._headers.get("Content-Length", 0))
					return True
				else :
					return False
		
		def _getConnUpgrade(self) :