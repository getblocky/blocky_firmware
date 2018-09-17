by enabling tasks which have been
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
			if direction != self._down:
				return
			yield

	__iter__ = __await__

	def trigger(self):
		self._update()
		if self._at_limit():  # All other threads are also at limit
			if self._func is not None:
				launch(self._func, self._args)
			self._reset(not self._down)  # Toggle direction to release others

	def _reset(self, down):
		self._down = down
		self._count = self._participants if down else 0

	def busy(self):
		if self._down:
			done = self._count == self._participants
		else:
			done = self._count == 0
		return not done

	def _at_limit(self):  # Has count reached up or down limit?
		limit = 0 if self._down else self._participants
		return self._count == limit

	def _update(self):
		self._count += -1 if self._down else 1
		if self._count < 0 or self._count > self._participants:
			raise ValueError('Too many tasks accessing Barrier')

# A Semaphore is typically used to limit the number of coros running a
# particular piece of code at once. The number is defined in the constructor.
class Semaphore():
	
	def __init__(self, value=1):
		self._count = value

	async def __aenter__(self):
		await self.acquire()
		return self

	async def __aexit__(self, *args):
		self.release()
		await core.asyncio.sleep(0)

	async def acquire(self):
		while self._count == 0:
			yield
		self._count -= 1

	def release(self):
		self._count += 1

class Bounded