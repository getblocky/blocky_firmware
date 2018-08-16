m[0])] = value
            return res
        
    
    # ===( Class Response  )======================================================
    
    class _response :
        # ------------------------------------------------------------------------
        def __init__(self, client) :
            self._client = client
        # ------------------------------------------------------------------------
        def _write(self, data) :
            return self._client._socket.write(data)
        # ------------------------------------------------------------------------
        def _writeFirstLine(self, code) :
            reason = self._responseCodes.get(code, ('Unknown reason', ))[0]
            self._write("HTTP/1.0 %s %s\r\n" % (code, reason))
        # ------------------------------------------------------------------------
        def _writeHeader(self, name, value) :
            self._write("%s: %s\r\n" % (name, value))
        # ------------------------------------------------------------------------
        def _writeContentTypeHeader(self, contentType, charset=None) :
            if contentType :
                ct = contentType \
                   + (("; charset=%s" % charset) if charset else "")
            else :
                ct = "application/octet-stream"
            self._writeHeader("Content-Type", ct)
        # ------------------------------------------------------------------------
        def _writeEndHeader(self) :
            self._write("\r\n")
        # ------------------------------------------------------------------------
        def _writeBeforeContent(self, code, headers, contentType, contentCharset, contentLength) :
            self._writeFirstLine(code)
            if isinstance(headers, dict) :
                for header in headers :
                    self._writeHeader(header, headers[header])
            if contentLength > 0 :
                self._writeContentTypeHeader(contentType, contentCharset)
                self._writeHeader("Content-Length", contentLength)
            self._writeHeader("Server", "MicroWebSrv by JC`zic")
            self._writeHeader("Connection", "close")
            self._writeEndHeader()        
        # ------------------------------------------------------------------------
        def WriteSwitchProto(self, upgrade, headers=None) :
            self._writeFirstLine(101)
            self._writeHeader("Connection", "Upgrade")
            self._writeHeader("Upgrade",    upgrade)
            if isinstance(headers, dict) :
                for header in headers :
                    self._writeHeader(header, headers[header])
        # ------------------------------------------------------------------------
        def WriteResponse(self, code, headers, contentType, contentCharset, content) :
            try :
                contentLength = len(content) if content else 0
                self._writeBeforeContent(code, headers, contentType, contentCharset, contentLength)
                if contentLength > 0 :
                    self._write(content)
                return True
            except :
                return False
        # ------------------------------------------------------------------------
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
        # ------------------------------------------------------------------------
        def WriteResponseFile(self, filepath, contentType=None, headers=None) :
            try :
                size = stat(filepath)[6]
                if size > 0 :
                    with open(filepath, 'rb') as file :
                        self._writeBeforeContent(200, headers, contentType, None, size)
                        buf = MicroWebSrv._tryAllocByteArray(1024)
                        if buf :
                            while size > 0 :
                                x = file.readinto(buf)
                                if x < len(buf) :
                                    buf = memoryview(buf)[:x]
                                self._write(buf)
                                size -= x
    