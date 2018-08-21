re returned even if not requested, and
                    # are sticky, i.e. will be returned again and again.
                    # If the caller doesn't do proper error handling and
                    # unregister this sock, we'll busy-loop on it, so we
                    # as well can unregister it now "just in case".
                    self.remove_reader(sock)
                if DEBUG and __debug__:
                    log.debug("Calling IO callback: %r", cb)
                if isinstance(cb, tuple):
                    cb[0](*cb[1])
                else:
                    cb.pend_throw(None)
                    self.call_soon(cb)


class StreamReader:

    def __init__(self, polls, ios=None):
        if ios is None:
            ios = polls
        self.polls = polls
        self.ios = ios

    def read(self, n=-1):
        while True:
            yield IORead(self.polls)
            res = self.ios.read(n)
            if res is not None:
                break
            # This should not happen for real sockets, but can easily
            # happen for stream wrappers (ssl, websockets, etc.)
            #log.warn("Empty read")
        if not res:
            yield IOReadDone(self.polls)
        return res

    def readexactly(self, n):
        buf = b""
        while n:
            yield IORead(self.polls)
            res = self.ios.read(n)
            assert res is not None
            if not res:
                yield IOReadDone(self.polls)
                break
            buf += res
            n -= len(res)
        return buf

    def readline(self):
        if DEBUG and __debug__:
            log.debug("StreamReader.readline()")
        buf = b""
        while True:
            yield IORead(self.polls)
            res = self.ios.readline()
            assert res is not None
            if not res:
                yield IOReadDone(self.polls)
                break
            buf += res
            if buf[-1] == 0x0a:
                break
        if 