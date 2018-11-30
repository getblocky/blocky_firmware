rstLine(101)
			self._writeHeader("Connection", "Upgrade")
			self._writeHeader("Upgrade",	upgrade)
			if isinstance(headers, dict) :
				for header in headers :
					self._writeHeader(header, headers[header])
		
		def WriteResponse(self, code, headers, contentType, contentCharset, content) :
			contentCharset = None
			try :
				if isinstance(content , str):
					contentLength = len(content) if content else 0
				elif isinstance(content , list):
					contentLength = 0
					for x in content :
						contentLength+= len(x)
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
				print('mwsr->wR',err)
				return False
		

		def WriteResponseOk(self, headers=None, contentType=None, contentCharset=None, content=None) :
			return self.WriteResponse(200, headers, contentType, contentCharset, content)
		


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
		
		def WriteRespons