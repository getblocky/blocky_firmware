
                        pass
                    elif ret is False:
                        # Don't reschedule
                        continue
                    else:
                        assert False, "Unsupported coroutine yield value: %r (of type %r)" % (ret, type(ret))
                except StopIteration as e:
                    if __debug__ and DEBUG:
                        log.debug("Coroutine finished: %s", cb)
                    continue
                except CancelledError as e:
                    if __debug__ and DEBUG:
                        log.debug("Coroutine cancelled: %s", cb)
                    continue
                # Currently all syscalls don't return anything, so we don't
                # need to feed anything to the next invocation of coroutine.
                # If that changes, need to pass that value below.
                if delay:
                    self.call_later_ms(delay, cb)
                else:
                    self.call_soon(cb)

            # Wait until next waitq task or I/O availability
            delay = 0
            if not self.runq:
                delay = -1
                if self.waitq:
                    tnow = self.time()
                    t = self.waitq.peektime()
                    delay = time.ticks_diff(t, tnow)
                    if delay < 0:
                        delay = 0
            self.wait(delay)

    def run_until_complete(self, coro):
        def _run_and_stop():
            yield from coro
            yield StopLoop(0)
        self.call_soon(_run_and_stop())
        self.run_forever()

    def stop(self):
        self.call_soon((lambda: (yield StopLoop(0)))())

    def close(self):
        pass


class SysCall:

    def __init__(self, *args):
        self.args = args

    def handle(self):
        raise NotImplementedError

# Optimized syscall with 1 arg
class SysCall1(SysCall):

    def __init__(self, arg):
        self.arg = arg

class StopLoop(SysCall1):
    pass

class IORead(SysCall1):
    pass

class IOWrite(SysCall1):
    pass

class IOReadDone(SysCall1):
    pass

class IOWriteDone(SysCall1):
    pass


_event_loop = None
_event_loop_class = EventLoop
def get_event_loop(runq_len=16, waitq_len=16):
    global _event_loop
    if _event_loop is None:
        _event_loop = _event_loop_class(runq_len, waitq_len)
    return _event_loop

def sleep(secs):
    yield int(secs * 1000)

# Implementation of sleep_ms awaitable with zero heap memory usage
class SleepMs(SysCall1):

    def __init__(self):
        self.v = None
        self.arg = None

    def __call__(self, arg):
        self.v = arg
        #print("__call__")
        return self

    def __iter__(self):
        #print("__iter__")
        return self

    def __next__(self):
        if self.v is not None:
            #print("__next__ syscall enter")
            self.arg = self.v
            self.v = None
            return self
        #print("__next__ syscall exit")
        _stop_iter.__traceback__ = None
        raise _stop_iter

_stop_iter = StopIteration()
sleep_ms = SleepMs()


def cancel(coro):
    prev = coro.pend_throw(CancelledError())
    if prev is False:
        _event_loop.call_soon(coro)


class TimeoutObj:
    def __init__(self, coro):
        self.coro = coro


def wait_for_ms(coro, timeout):

    def waiter(coro, timeout_obj):
        res = yield from coro
        if __debug__ and DEBUG:
            log.debug("waiter: cancelling %s", timeout_obj)
        timeout_obj.coro = None
        return res

    def timeout_func(timeout_obj):
        if timeout_obj.coro:
            if __debug__ and DEBUG:
                log.debug("timeout_func: cancelling %s", timeout_obj.coro)
            prev = timeout_obj.coro.pend_throw(TimeoutError())
            #print("prev pend", prev)
            if prev is False:
                _event_loop.call_soon(timeout_obj.coro)

    timeout_obj = TimeoutObj(_event_loop.cur_task)
    _event_loop.call_later_ms(timeout, timeout_func, timeout_obj)
    return (yield from waiter(coro, timeout_obj))


def wait_for(coro, timeout):
    return wait_for_ms(coro, int(timeout * 1000))


def coroutine(f):
    return f

#
# The functions below are deprecated in uasyncio, and provided only
# for compatibility with CPython asyncio
#

def ensure_future(coro, loop=_event_loop):
    _event_loop.call_soon(coro)
    # CPython asyncio incompatibility: we don't return Task object
    return coro


# CPython asyncio incompatibility: Task is a function, not a class (for efficiency)
def Task(coro, loop=_event_loop):
    # Same as async()
    _event_loop.call_soon(coro)



DEBUG = 0
log = None

def set_debug(val):
    global DEBUG, log
    DEBUG = val
    if val:
        import logging
        log = logging.getLogger("uasyncio")


class PollEventLoop(EventLoop):

    def __init__(self, runq_len=16, waitq_len=16):
        EventLoop.__init__(self, runq_len, waitq_len)
        self.poller = select.poll()
        self.objmap = {}

    def add_reader