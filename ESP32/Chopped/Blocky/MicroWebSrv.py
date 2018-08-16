import socket,json,ustruct,gc
from _thread import start_new_thread
class MicroWebSrv :
    
    # ===( Constants )============================================================
    
    _indexPages = [
        "index.pyhtml",
        "index.html",
        "index.htm",
        "default.pyhtml",
        "default.html",
        "default.htm"
    ]
    _mimeTypes = {
        ".txt"   : "text/plain",
        ".htm"   : "text/html",
        ".html"  : "text/html",
        ".css"   : "text/css",
        ".csv"   : "text/csv",
        ".js"    : "application/javascript",
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
    # ----------------------------------------------------------------------------
    def _tryAllocByteArray(size) :
        for x in range(10) :
            try :
                gc.collect()
                return bytearray(size)
            except :
                pass
        return None
    # ----------------------------------------------------------------------------
    def _tryStartThread(func, args=()) :
        for x in range(10) :
            try :
                gc.collect()
                start_new_thread(func, args)
                return True
            except :
                pass
        return False
    # ----------------------------------------------------------------------------
    def _unquote(s) :
        r = s.split('%')
        for i in range(1, len(r)) :
            s = r[i]
            try :
                r[i] = chr(int(s[:2], 16)) + s[2:]
            except :
                r[i] = '%' + s
        return ''.join(r)
    # ----------------------------------------------------------------------------
    def _unquote_plus(s) :
        return MicroWebSrv._unquote(s.replace('+', ' '))
    # ----------------------------------------------------------------------------
    def _fileExists(path) :
        try :
            stat(path)
            return True
        except :
            return False
    # ----------------------------------------------------------------------------
    def _isPyHTMLFile(filename) :
        return filename.lower().endswith(MicroWebSrv._pyhtmlPagesExt)
    
    # ===( Constructor )==========================================================
    
    def __init__( self,
                  routeHandlers = None,
                  port          = 80,
                  bindIP        = '0.0.0.0',
                  webPath       = "/flash/www" ) :
        self._routeHandlers = routeHandlers
        self._srvAddr       = (bindIP, port)
        self._webPath       = webPath
        self._notFoundUrl   = None
        self._started       = False
        self.MaxWebSocketRecvLen     = 1024
        self.WebSocketThreaded       = True
        self.AcceptWebSocketCallback = None
    
    # ===( Server Process )=======================================================
    
    def _serverProcess(self) :
        self._started = True
        while True :
            try :
                client, cliAddr = self._server.accept()
            except :
                break
            self._client(self, client, cliAddr)
        self._started = False
    
    # ===( Functions )============================================================
    
    def Start(self, threaded=True) :
        if not self._started :
            self._server = socket.socket( socket.AF_INET,
                                          socket.SOCK_STREAM,
                                          socket.IPPROTO_TCP )
            self._server.setsockopt( socket.SOL_SOCKET,
                                     socket.SO_REUSEADDR,
                                     1 )
            self._server.bind(self._srvAddr)
            self._server.listen(1)
            if threaded :
                MicroWebSrv._tryStartThread(self._serverProcess)
            else :
                self._serverProcess()
    # ----------------------------------------------------------------------------
    def Stop(self) :
        if self._started :
            self._server.close()
    # ----------------------------------------------------------------------------
    def IsStarted(self) :
        return self._started
    # ----------------------------------------------------------------------------
    def SetNotFoundPag