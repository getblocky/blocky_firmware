# (c) 2014-2018 Paul Sokolovsky. MIT license.
import uerrno
import uselect as select
import usocket as _socket
import utime as time
import utimeq
import ucollections
type_gen = type((lambda: (yield))())

DEBUG = 0
log = None

def set_debug(val):
    global DEBUG, log
    DEBUG = val
    if val:
        import logging
        log = logging.getLogger("uasyncio.core")


class CancelledError(Exception):
    pass


class TimeoutError(CancelledError):
    pass


class EventLoop:

    def __init__(self, runq_len=100, waitq_len=100):
        self.runq = ucollections.deque((), runq_len, True)
        self.waitq = utimeq.utimeq(waitq_len)
        # Current task being run. Task is a top-level coroutine scheduled
        # in the event loop (sub-coroutines executed transparently by
        # yield from/await, event loop "doesn't see" them).
        self.cur_task = None

    def time(self):
        return time.ticks_ms()

    def create_task(self, coro):
        # CPython 3.4.2
        self.call_later_ms(0, coro)
        # CPython asyncio incompatibility: we don't return Task object

    def call_soon(self, callback, *args):
        if __debug__ and DEBUG:
            log.debug("Scheduling in runq: %s", (callback, args))
        self.runq.append(callback)
        if not isinstance(callback, type_gen):
            self.runq.append(args)

    def call_later(self, delay, callback, *args):
        self.call_at_(time.ticks_add(self.time(), int(delay * 1000)), callback, args)

    def call_later_ms(self, delay, callback, *args):
        if not delay:
            return self.call_soon(callback, *args)
        self.call_at_(time.ticks_add(self.time(), delay), callback, args)

    def call_at_(self, time, callback, args=()):
        if __debug__ and DEBUG:
            log.debug("Scheduling in waitq: %s", (time, callback, args))
        self.waitq.push(time, callback, args)

    def wait(self, delay):
        # Default wait implementation, to be overriden in subclasses
        # with IO s