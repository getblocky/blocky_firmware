f._headers.get("Content-Length", 0))
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
			res	= { }
			data = self.ReadRequestContent()
			if len(data) > 0 :
				elements = data.decode().split('&')
				for s in elements :
					param = s.split('=', 1)
					if len(param) > 0 :
						value = MicroWebSrv._unquote(param[1]) if len(param) > 1 else ''
						res[MicroWebSrv._unquote(param[0])] = value
			return res
		
	
	# ===( Class Response	)======================================================
	
	class _response :
		
		def __init__(self, client) :
			self._client = client
		
		def _write(self, data) :
			try :
				
				if isinstance(data , str) or isinstance(data , bytes):
					print('socket_write' , data , len(data))
					return self._client._socket.write(data)
				elif isinstance(data , list):
					for x in data :
						self._client._socket.write(x)
					
				
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
			self._wri