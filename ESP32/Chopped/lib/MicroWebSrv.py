import sys 
core = sys.modules['Blocky.Core']

class MicroWebSrv :
	
	# ===( Constants )============================================================
	
	_indexPages = [
		"index.html",
		"index.htm",
	]
	_mimeTypes = {
		".txt"	 : "text/plain",
		".htm"	 : "text/html",
		".html"	: "text/html",
		".css"	 : "text/css",
		".csv"	 : "text/csv",
		".js"	: "application/javascript",
		".xml"	 : "application/xml",
		".xhtml" : "application/xhtml+xml",
		".json"	: "application/json",
		".zip"	 : "application/zip",
		".pdf"	 : "application/pdf",
		".jpg"	 : "image/jpeg",
		".jpeg"	: "image/jpeg",
		".png"	 : "image/png",
		".gif"	 : "image/gif",
		".svg"	 : "image/svg+xml",
		".ico"	 : "image/x-icon"
	}
	_html_escape_chars = {
		"&" : "&amp;",
		'"' : "&quot;",
		"'" : "&apos;",
		">" : "&gt;",
		"<" : "&lt;"
	}
	_pyhtmlPagesExt = '.pyhtml'
	
	# ===( Utils	)===============================================================
	
	def HTMLEscape(s) :
		return ''.join(MicroWebSrv._html_escape_chars.get(c, c) for c in s)

	def _tryAllocByteArray(size) :
		for x in range(10) :
			try :
				core.gc.collect()
				return bytearray(size)
			except :
				pass
		return None

	def _tryStartThread(func, args=()) :
		for x in range(10) :
			try :
				core.gc.collect()
				core.start_new_thread(func, args)
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
					port			= 80,
					bindIP		= '0.0.0.0',
					webPath		 = "/flash/www" ) :
