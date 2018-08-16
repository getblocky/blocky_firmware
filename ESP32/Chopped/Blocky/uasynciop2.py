(self, sock, cb, *args):
        if DEBUG and __debug__:
            log.debug("add_reader%s", (sock, cb, args))
        if args:
            self.poller.register(sock, select.POLLIN)
            self.objmap[id(sock)] = (cb, args)
        else:
            self.poller.register(sock, select.POLLIN)
            self.objmap[id(sock)] = cb

    def remove_reader(self, sock):
        if DEBUG and __debug__:
            log.debug("remove_reader(%s)", sock)
        self.poller.unregister(sock)
        del self.objmap[id(sock)]

    def add_writer(self, sock, cb, *args):
        if DEBUG and __debug__:
            log.debug("add_writer%s", (sock, cb, args))
        if args:
            self.poller.register(sock, select.POLLOUT)
            self.objmap[id(sock)] = (cb, args)
        else:
            self.poller.register(sock, select.POLLOUT)
            self.objmap[id(sock)] = cb

    def remove_writer(self, sock):
        if DEBUG and __debug__:
            log.debug("remove_writer(%s)", sock)
        try:
            self.poller.unregister(sock)
            self.objmap.pop(id(sock), None)
        except OSError as e:
            # StreamWriter.awrite() first tries to write to a socket,
            # and if that succeeds, yield IOWrite may never be called
            # for that socket, and it will never be added to poller. So,
            # ignore such error.
            if e.args[0] != uerrno.ENOENT:
                raise

    def wait(self, delay):
        if DEBUG and __debug__:
            log.debug("poll.wait(%d)", delay)
        # We need one-shot behavior (second arg of 1 to .poll())
        res = self.poller.ipoll(delay, 1)
        #log.debug("poll result: %s", res)
        # Remove "if res" workaround after
        # https://github.com/micropython/micropython/issues/2716 fixed.
        if res:
            for sock, ev in res:
                cb = self.objmap[id(sock)]
                if ev & (select.POLLHUP | select.POLLERR):
                    # These events are returned even if not requested, and
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
        if DEBUG and __debug__:
            log.debug("StreamReader.readline(): %s", buf)
        return buf

    def aclose(self):
        yield IOReadDone(self.polls)
        self.ios.close()

    def __repr__(self):
        return "<StreamReader %r %r>" % (self.polls, self.ios)


class StreamWriter:

    def __init__(self, s, extra):
        self.s = s
        self.extra = extra

    def awrite(self, buf, off=0, sz=-1):
        # This method is called awrite (async write) to not proliferate
        # incompatibility with original asyncio. Unlike original asyncio
        # whose .write() method is both not a coroutine and guaranteed
        # to return immediately (which means it has to buffer all the
        # data), this method is a coroutine.
        if sz == -1:
            sz = len(buf) - off
        if DEBUG and __debug__:
            log.debug("StreamWriter.awrite(): spooling %d bytes", sz)
        while True:
            res = self.s.write(buf, off, sz)
            # If we spooled everyth