def SetNotFoundPageUrl(self, url=None) :
		self._notFoundUrl = url

	def GetMimeTypeFromFilename(self, filename) :
		filename = filename.lower()
		for ext in self._mimeTypes :
			if filename.endswith(ext) :
				return self._mimeTypes[ext]
		return None

	def GetRouteHandler(self, resUrl, method) :
		if self._routeHandlers :
			resUrl = resUrl.upper()
			method = method.upper()
			for route in self._routeHandlers :
				if len(route) == 3 and			\
					 route[0].upper() == resUrl and \
					 route[1].upper() == method :
					 return route[2]
		return None

	def _physPathFromURLPath(self, urlPath) :
		if urlPath == '/' :
			for idxPage in self._indexPages :
				physPath = self._webPath + '/' + idxPage
				if MicroWebSrv._fileExists(physPath) :
					return physPath
		else :
			physPath = self._webPath + urlPath
			if MicroWebSrv._fileExists(physPath) :
				return physPath
		return None
	
	# ===( Class Client	)========================================================
	
	class _client :
		
		def __init__(self, microWebSrv, socket, addr) :
			socket.settimeout(2)
			self._microWebSrv	 = microWebSrv
			self._socket		= socket
			self._addr			= addr
			self._method		= None
			self._path			= None
			self._httpVer		 = None
			self._resPath		 = "/"
			self._queryString	 = ""
			self._queryParams	 = { }
			self._headers		 = { }
			self._contentType	 = None
			self._contentLength = 0
			#await self._processRequest()
		
		def _processRequest(self) :
			try :
				response = MicroWebSrv._response(self)
				if self._parseFirstLine(response) :
					if self._parseHeader(response) :
						upg = self._getConnUpgrade()
						if not upg :
							routeHandler = self._microWebSrv.GetRouteHandler(self._resPath, self._method)
							if routeHandler :
								#routeHandler(self, response)
								#loop = asyncio.get_event_loop()
								#loop.create_task(routeHandler(self,response))
								routeHandler(self,response)
							
							else :
								response.WriteResponseMethodNotAllowed()
						eli