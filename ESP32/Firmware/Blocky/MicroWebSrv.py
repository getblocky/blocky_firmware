import socket,json,ustruct,gc
import Blocky.uasyncio as asyncio 

class MicroWebSrv :
	
	# ===( Constants )============================================================
	
	_indexPages = [
		"index.html",
		"index.htm",
	]
	_mimeTypes = {
		".txt"   : "text/plain",
		".htm"   : "text/html",
		".html"  : "text/html",
		".css"   : "text/css",
		".csv"   : "text/csv",
		".js"	: "application/javascript",
		".xml"   : "application/xml",
		".xhtml" : "application/xhtml+xml",
		".json"  : "application/json",
		".zip"   : "application/zip",
		".pdf"   : "application/pdf",
		".jpg"   : "image/jpeg",
		".jpeg"  : "image/jpeg",
		".png"   : "image/png",
		".gif"   : "image/gif",
		".svg"   : "image/svg+xml",
		".ico"   : "image/x-icon"
	}
	_html_escape_chars = {
		"&" : "&amp;",
		'"' : "&quot;",
		"'" : "&apos;",
		">" : "&gt;",
		"<" : "&lt;"
	}
	_pyhtmlPagesExt = '.pyhtml'
	
	# ===( Utils  )===============================================================
	
	def HTMLEscape(s) :
		return ''.join(MicroWebSrv._html_escape_chars.get(c, c) for c in s)

	def _tryAllocByteArray(size) :
		for x in range(10) :
			try :
				gc.collect()
				return bytearray(size)
			except :
				pass
		return None

	def _tryStartThread(func, args=()) :
		for x in range(10) :
			try :
				gc.collect()
				start_new_thread(func, args)
				return True
			except :
				pass
		return False

	def _unquote(s) :
		r = s.split('%')
		for i in range(1, len(r)) :
			s = r[i]
			try :
				r[i] = chr(int(s[:2], 16)) + s[2:]
			except :
				r[i] = '%' + s
		return ''.join(r)

	def _unquote_plus(s) :
		return MicroWebSrv._unquote(s.replace('+', ' '))

	def _fileExists(path) :
		try :
			stat(path)
			return True
		except :
			return False

	def _isPyHTMLFile(filename) :
		return filename.lower().endswith(MicroWebSrv._pyhtmlPagesExt)
	
	# ===( Constructor )==========================================================
	
	def __init__( self,
				  routeHandlers = None,
				  port		  = 80,
				  bindIP		= '0.0.0.0',
				  webPath	   = "/flash/www" ) :
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
			import network as Network
			self._started = True
			wlan_ap = Network.WLAN(Network.AP_IF)
			wlan_ap.active(True)
			print('START AP')
			import Blocky.Global
			while Blocky.Global.flag_ONLINE == False :
				await asyncio.sleep_ms(200)
				if wlan_ap.isconnected():
					try :
						try :
							client, cliAddr = self._socket.accept()
							
						except :
							continue
						print(client , cliAddr)
						print('socket->Accepted')
						a = self._client(self, client, cliAddr)
						await a._processRequest()
					except Exception as err :
						import sys
						print('client->',err)
						sys.print_exception(err)
				
			self._started = False
			print('CLOSE AP')
		except Exception as err:
			print( ' _socket -> ' , err)
	
	# ===( Functions )============================================================
	
	async def Start(self, threaded=True) :
		if not self._started :
			self._socket = socket.socket( socket.AF_INET,
										  socket.SOCK_STREAM,
										  socket.IPPROTO_TCP )
			self._socket.setsockopt( socket.SOL_SOCKET,
									 socket.SO_REUSEADDR,
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
	
	# ===( Class Client  )========================================================
	
	class _client :
		
		def __init__(self, microWebSrv, socket, addr) :
			socket.settimeout(2)
			self._microWebSrv   = microWebSrv
			self._socket		= socket
			self._addr		  = addr
			self._method		= None
			self._path		  = None
			self._httpVer	   = None
			self._resPath	   = "/"
			self._queryString   = ""
			self._queryParams   = { }
			self._headers	   = { }
			self._contentType   = None
			self._contentLength = 0
			#await self._processRequest()
		
		async def _processRequest(self) :
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
								await routeHandler(self,response)
							elif self._method.upper() == "GET" :
								filepath = self._microWebSrv._physPathFromURLPath(self._resPath)
								if filepath :
									if MicroWebSrv._isPyHTMLFile(filepath) :
										response.WriteResponsePyHTMLFile(filepath)
									else :
										contentType = self._microWebSrv.GetMimeTypeFromFilename(filepath)
										if contentType :
											response.WriteResponseFile(filepath, contentType)
										else :
											response.WriteResponseForbidden()
								else :
									response.WriteResponseNotFound()
							else :
								response.WriteResponseMethodNotAllowed()
						elif upg == 'websocket' and 'MicroWebSocket' in globals() \
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
				import sys 
				sys.print_exception(err)
				#response.WriteResponseInternalServerError()
			try :
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
			if 'upgrade' in self._headers.get('Connection', '').lower() :
				return self._headers.get('Upgrade', '').lower()
			return None
		
		def ReadRequestContent(self, size=None) :
			self._socket.setblocking(False)
			b = None
			try :
				if not size :
					b = self._socket.read(self._contentLength)
				elif size > 0 :
					b = self._socket.read(size)
			except :
				pass
			self._socket.setblocking(True)
			return b if b else b''
		
		def ReadRequestPostedFormData(self) :
			res  = { }
			data = self.ReadRequestContent()
			if len(data) > 0 :
				elements = data.decode().split('&')
				for s in elements :
					param = s.split('=', 1)
					if len(param) > 0 :
						value = MicroWebSrv._unquote(param[1]) if len(param) > 1 else ''
						res[MicroWebSrv._unquote(param[0])] = value
			return res
		
	
	# ===( Class Response  )======================================================
	
	class _response :
		
		def __init__(self, client) :
			self._client = client
		
		def _write(self, data) :
			try :
				return self._client._socket.write(data)
			except Exception as err:
				print('socket->_write->' , err)
		
		def _writeFirstLine(self, code) :
			reason = self._responseCodes.get(code, ('Unknown reason', ))[0]
			self._write("HTTP/1.0 %s %s\r\n" % (code, reason))
		
		def _writeHeader(self, name, value) :
			self._write("%s: %s\r\n" % (name, value))
		
		# delete
		def _writeContentTypeHeader(self, contentType, charset=None) :
			if contentType :
				ct = contentType \
				   + (("; charset=%s" % charset) if charset else "")
			else :
				ct = "application/octet-stream"
			self._writeHeader("Content-Type", ct)
		
		def _writeEndHeader(self) :
			self._write("\r\n")
		
		#def _writeBeforeContent(self, code, headers, contentType, contentCharset, contentLength) :
		#	pass		
		
		def WriteSwitchProto(self, upgrade, headers=None) :
			self._writeFirstLine(101)
			self._writeHeader("Connection", "Upgrade")
			self._writeHeader("Upgrade",	upgrade)
			if isinstance(headers, dict) :
				for header in headers :
					self._writeHeader(header, headers[header])
		
		def WriteResponse(self, code, headers, contentType, contentCharset, content) :
			contentCharset = None
			try :
				contentLength = len(content) if content else 0
				#self._writeBeforeContent(code, headers, contentType, contentCharset, contentLength)
				
				self._writeFirstLine(code)
				if isinstance(headers, dict) :
					for header in headers :
						self._writeHeader(header, headers[header])
				if contentLength > 0 :
					#self._writeContentTypeHeader(contentType, contentCharset)
					if contentType :
						ct = contentType \
						   + (("; charset=%s" % contentCharset) if contentCharset else "")
					else :
						ct = "application/octet-stream"
					self._writeHeader("Content-Type", ct)
					self._writeHeader("Content-Length", contentLength)
				self._writeHeader("Server", "MicroWebSrv by JC`zic")
				self._writeHeader("Connection", "close")
				self._write("\r\n")	#self._writeEndHeader()
				
				if contentLength > 0 :
					self._write(content)
				return True
			except MemoryError as err:
				print(err)
				return False
		
		def WriteResponsePyHTMLFile(self, filepath, headers=None) :
			if 'MicroWebTemplate' in globals() :
				with open(filepath, 'r') as file :
					code = file.read()
				mWebTmpl = MicroWebTemplate(code, escapeStrFunc=MicroWebSrv.HTMLEscape)
				try :
					return self.WriteResponseOk(headers, "text/html", "UTF-8", mWebTmpl.Execute())
				except Exception as ex :
					return self.WriteResponse( 500,
											   None,
											   "text/html",
											   "UTF-8",
											   self._execErrCtnTmpl % {
													'module'  : 'PyHTML',
													'message' : str(ex)
											   } )
			return self.WriteResponseNotImplemented()
		

		def WriteResponseFileAttachment(self, filepath, attachmentName, headers=None) :
			if not isinstance(headers, dict) :
				headers = { }
			headers["Content-Disposition"] = "attachment; filename=\"%s\"" % attachmentName
			return self.WriteResponseFile(filepath, None, headers)
		
		def WriteResponseOk(self, headers=None, contentType=None, contentCharset=None, content=None) :
			return self.WriteResponse(200, headers, contentType, contentCharset, content)
		
		def WriteResponseJSONOk(self, obj=None, headers=None) :
			return self.WriteResponseOk(headers, "application/json", "UTF-8", dumps(obj))
		
		def WriteResponseRedirect(self, location) :
			headers = { "Location" : location }
			return self.WriteResponse(302, headers, None, None, None)
		
		def WriteResponseError(self, code) :
			responseCode = self._responseCodes.get(code, ('Unknown reason', ''))
			return self.WriteResponse( code,
									   None,
									   "text/html",
									   "UTF-8",
									   self._errCtnTmpl % {
											'code'	: code,
											'reason'  : responseCode[0],
											'message' : responseCode[1]
									   } )
		
		def WriteResponseJSONError(self, code, obj=None) :
			return self.WriteResponse( code,
									   None,
									   "application/json",
									   "UTF-8",
									   dumps(obj if obj else { }) )
		
		def WriteResponseBadRequest(self) :
			return self.WriteResponseError(400)
		
		def WriteResponseForbidden(self) :
			return self.WriteResponseError(403)
		
		def WriteResponseNotFound(self) :
			if self._client._microWebSrv._notFoundUrl :
				self.WriteResponseRedirect(self._client._microWebSrv._notFoundUrl)
			else :
				return self.WriteResponseError(404)
		
		def WriteResponseMethodNotAllowed(self) :
			return self.WriteResponseError(405)
		
		def WriteResponseInternalServerError(self) :
			return self.WriteResponseError(500)
		
		def WriteResponseNotImplemented(self) :
			return self.WriteResponseError(501)
		
		_errCtnTmpl = """\
		<html>
			<head>
				<title>Error</title>
			</head>
			<body>
				<h1>%(code)d %(reason)s</h1>
				%(message)s
			</body>
		</html>
		"""
		
		_execErrCtnTmpl = """\
		<html>
			<head>
				<title>Page execution error</title>
			</head>
			<body>
				<h1>%(module)s page execution error</h1>
				%(message)s
			</body>
		</html>
		"""
		
		_responseCodes = {
			
		}



