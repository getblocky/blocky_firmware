try :
                elements = self._socket.readline().decode().strip().split()
                if len(elements) == 3 :
                    self._method  = elements[0].upper()
                    self._path    = elements[1]
                    self._httpVer = elements[2].upper()
                    elements      = self._path.split('?', 1)
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
    
        # ------------------------------------------------------------------------
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
        # ------------------------------------------------------------------------
        def _getConnUpgrade(self) :
            if 'upgrade' in self._headers.get('Connection', '').lower() :
                return self._headers.get('Upgrade', '').lower()
            return None
        # ------------------------------------------------------------------------
        def GetServer(self) :
            return self._microWebSrv
        # ------------------------------------------------------------------------
        def GetAddr(self) :
            return self._addr
        # ------------------------------------------------------------------------
        def GetIPAddr(self) :
            return self._addr[0]
        # ------------------------------------------------------------------------
        def GetPort(self) :
            return self._addr[1]
        # ------------------------------------------------------------------------
        def GetRequestMethod(self) :
            return self._method
        # ------------------------------------------------------------------------
        def GetRequestTotalPath(self) :
            return self._path
        # ------------------------------------------------------------------------
        def GetRequestPath(self) :
            return self._resPath
        # ------------------------------------------------------------------------
        def GetRequestQueryString(self) :
            return self._queryString
        # ------------------------------------------------------------------------
        def GetRequestQueryParams(self) :
            return self._queryParams
        # ------------------------------------------------------------------------
        def GetRequestHeaders(self) :
            return self._headers
        # ------------------------------------------------------------------------
        def GetRequestContentType(self) :
            return self._contentType
        # ------------------------------------------------------------------------
        def GetRequestContentLength(self) :
            return self._contentLength
        # ------------------------------------------------------------------------
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
        # ------------------------------------------------------------------------
        def ReadRequestPostedFormData(self) :
            res  = { }
            data = self.ReadRequestContent()
            if len(data) > 0 :
                elements = data.decode().split('&')
                for s in elements :
                    param = s.split('=', 1)
                    if len(param) > 0 :
                        value = MicroWebSrv._unquote(param[1]) if len(param) > 1 else ''
                        res[MicroWebSrv._unquote(para