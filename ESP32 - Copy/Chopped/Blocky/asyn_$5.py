return True
		return False

	@classmethod
	def is_running(cls, name):
		return cls._is_running(group=name)

	@classmethod
	def _stopped(cls, task_id):  # On completion remove it
		name = cls._get_group(task_id())  # Convert task_id to task_no
		if name in cls.instances:
			instance = cls.instances[name]
			barrier = instance.barrier
			if barrier is not None:
				barrier.trigger()
			del cls.instances[name]
		Cancellable._stopped(task_id())

	def __init__(self, name, gf, *args, barrier=None, **kwargs):
		if name in self.instances:
			raise ValueError('Task name "{}" already exists.'.format(name))
		super().__init__(gf, *args, group=name, **kwargs)
		self.barrier = barrier
		self.instances[name] = self


# @namedtask
namedtask = cancellable  # compatibility with old code

# Condition class

class Condition():
	def __init__(self, lock=None):
		self.lock = Lock() if lock is None else lock
		self.events = []

	async def acquire(self):
		await self.lock.acquire()

# enable this syntax:
# with await condition [as cond]:
	def __await__(self):
		yield from self.lock.acquire()
		return self

	__iter__ = __await__

	def __enter__(self):
		return self

	def __exit__(self, *_):
		self.lock.release()

	def locked(self):
		return self.lock.locked()

	def release(self):
		self.lock.release()  # Will raise RuntimeError if not locked

	def notify(self, n=1):  # Caller controls lock
		if not self.lock.locked():
			raise RuntimeError('Condition notify with lock not acquired.')
		for _ in range(min(n, len(self.events))):
			ev = self.events.pop()
			ev.set()

	def notify_all(self):
		self.notify(len(self.events))

	async def wait(self):
		if not self.lock.locked():
			raise RuntimeError('Condition wait with lock not acquired.')
		ev = Event()
		self.events.append(ev)
		self.lock.release()
		await ev
		await self.lock.acquire()
		assert ev not in self.events, 'condition wait assertion fail'
		return True  # CPython compatibility

	async def wait_for(self, predicate):
		result = predicat