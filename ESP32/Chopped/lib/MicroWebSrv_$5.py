te("\r\n")
		
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
			try :
				
				if isinstance(content , str) or isinstance(content , bytes):
					contentLength = len(content) if content else 0
					print('LEN ' , contentLength , contentCharset , contentType )
				elif isinstance(content , list):
					contentLength = 0
					for x in content :
						contentLength+= len(x)
				else :
					contentLength = 0
				#self._writeBeforeContent(code, headers, contentType, contentCharset, contentLength)
				
				self._writeFirstLine(code)
				if isinstance(headers, dict) :
					for header in headers :
						self._writeHeader(header, headers[header])
				
				if contentLength > 0 :
					#self._writeContentTypeHeader(contentType, contentCharset)
					ct = None
					
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
					print('_write',len(content))
				
				return True
			except MemoryError as err:
				print('mwsr->wR',err)
				return False
			except Exception as err :
				import sys
				sys.print_exception(err)
				
		

		def WriteResponseOk(self, headers=None, contentType=None, contentCharset=None, content=None) :
			return se