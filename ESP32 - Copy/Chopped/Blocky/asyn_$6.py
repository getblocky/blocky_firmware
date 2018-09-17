e()
		while not result:
			await self.wait()
			result = predicate()
		return result

# Provide functionality similar to core.asyncio.gather()

class Gather():
	
	def __init__(self, gatherables):
		ncoros = len(gatherables)
		self.barrier = Barrier(ncoros + 1)
		self.results = [None] * ncoros
		loop = core.asyncio.get_event_loop()
		for n, gatherable in enumerate(gatherables):
			loop.create_task(self.wrap(gatherable, n)())

	def __iter__(self):
		yield from self.barrier.__await__()
		return self.results

	def wrap(self, gatherable, idx):
		async def wrapped():
			coro, args, kwargs = gatherable()
			try:
				tim = kwargs.pop('timeout')
			except KeyError:
				self.results[idx] = await coro(*args, **kwargs)
			else:
				self.results[idx] = await core.asyncio.wait_for(coro(*args, **kwargs), tim)
			self.barrier.trigger()
		return wrapped

class Gatherable():
	def __init__(self, coro, *args, **kwargs):
		self.arguments = coro, args, kwargs

	def __call__(self):
		return self.arguments