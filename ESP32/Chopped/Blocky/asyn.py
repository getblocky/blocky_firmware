# asyn.py 'micro' synchronisation primitives for uasyncio
# Test/demo programs asyntest.py, barrier_test.py
# Provides Lock, Event, Barrier, Semaphore, BoundedSemaphore, Condition,
# NamedTask and Cancellable classes, also sleep coro.
# Uses low_priority where available and appropriate.
# Updated 31 Dec 2017 for uasyncio.core V1.6 and to provide task cancellation.

# The MIT License (MIT)
#
# Copyright (c) 2017 Peter Hinch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# CPython 3.5 compatibility
# (ignore RuntimeWarning: coroutine '_g' was never awaited)

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


async def _g():
    pass
type_coro = type(_g())

# If a callback is passed, run it and return.
# If a coro is passed initiate it and return.
# coros are passed by name i.e. not using function call syntax.
def launch(func, tup_args):
    res = func(*tup_args)
    if isinstance(res, type_coro):
        loop = asyncio.get_event_loop()
        loop.create_task(res)


# To access a lockable resource a coro should issue
# async with lock_instance:
#    access the locked resource

# Alternatively:
# await lock.acquire()
# try:
#   do stuff with locked resource
# finally:
#   lock.release
# Uses normal scheduling on assumption that locks are held briefly.
class Lock():
    def __init__(self, delay_ms=0):
        self._locked = False
        self.delay_ms = delay_ms

    def locked(self):
        return self._locked

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        self.release()
        await asyncio.sleep(0)

    async def acquire(self):
        while True:
            if self._locked:
                await asyncio.sleep_ms(self.delay_ms)
            else:
                self._locked = True
                break

    def release(self):
        if not self._locked:
            raise RuntimeError('Attempt to release a lock which has not been set')
        self._locked = False


# A coro waiting on an event issues await event
# A coro rasing the event issues event.set()
# When all waiting coros have run
# event.clear() should be issued
class Event():
    def __init__(self, lp=False):  # Redundant arg retained for compatibility
        self.clear()

    def clear(self):
        self._flag = False
        self._data = None

    def __await__(self):
        while not self._flag:
            yield

    __iter__ = __await__

    def is_set(self):
        return self._flag

    def set(self, data=None):
        self._flag = True
        self._data = data

    def value(self):
        return self._data

# A Barrier synchronises N coros. Each issues await barrier.
# Execution pauses until all other participant coros are waiting on it.
# At that point the callback is executed. Then the barrier is 'opened' and
# execution of all participants resumes.

# The nowait arg is to support task cancellation. It enables usage where one or
# more coros can register that they have reached the barrier without waiting
# for it. Any coros waiting normally on the barrier will pause until all
# non-waiting coros have passed the barrier and all waiting ones have reached
# it. The use of nowait promotes efficiency by enabling tasks which have been
# cancelled to leave the task queue as soon as possible.

# Uses low_priority if available

class Barrier():
    def __init__(self, participants, func=None, args=()):
        self._participants = participants
        self._func = func
        self._args = args
        self._reset(True)

    def __await__(self):
        self._update()
        if self._at_limit():  # All other threads are also at limit
            if self._func is not None:
                launch(self._func, self._args)
            self._reset(not self._down)  # Toggle direction to release others
            return

        direction = self._down
        while True:  # Wait until last waiting thread changes the direction
            if dir