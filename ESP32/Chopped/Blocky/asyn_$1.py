rce a coro should issue
# async with lock_instance:
#	access the locked resource

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
		await core.asyncio.sleep(0)

	async def acquire(self):
		while True:
			if self._locked:
				await core.asyncio.sleep_ms(self.delay_ms)
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
# it. The use of nowait promotes efficiency 