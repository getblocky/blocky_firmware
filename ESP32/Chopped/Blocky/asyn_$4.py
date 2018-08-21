asks = cls._get_task_nos(group)
		if tasks == []:
			return False
		for task_no in tasks:
			barrier = cls.tasks[task_no][2]
			if barrier is None:  # Running, not yet cancelled
				return True
			if barrier.busy():
				return True
		return False

	@classmethod
	def _get_task_nos(cls, group):  # Return task nos in a group
		return [task_no for task_no in cls.tasks if cls.tasks[task_no][1] == group]

	@classmethod
	def _get_group(cls, task_no):  # Return group given a task_no
		return cls.tasks[task_no][1]

	@classmethod
	def _stopped(cls, task_no):
		if task_no in cls.tasks:
			barrier = cls.tasks[task_no][2]
			if barrier is not None:  # Cancellation in progress
				barrier.trigger()
			del cls.tasks[task_no]

	def __init__(self, gf, *args, group=0, **kwargs):
		task = gf(TaskId(Cancellable.task_no), *args, **kwargs)
		if task in self.tasks:
			raise ValueError('Task already exists.')
		self.tasks[Cancellable.task_no] = [task, group, None]
		self.task_no = Cancellable.task_no  # For subclass
		Cancellable.task_no += 1
		self.task = task

	def __call__(self):
		return self.task

	def __await__(self):  # Return any value returned by task.
		return (yield from self.task)

	__iter__ = __await__


# @cancellable decorator

def cancellable(f):
	
	def new_gen(*args, **kwargs):
		if isinstance(args[0], TaskId):  # Not a bound method
			task_id = args[0]
			g = f(*args[1:], **kwargs)
		else:  # Task ID is args[1] if a bound method
			task_id = args[1]
			args = (args[0],) + args[2:]
			g = f(*args, **kwargs)
		try:
			res = await g
			return res
		finally:
			NamedTask._stopped(task_id)
	return new_gen

# The NamedTask class enables a coro to be identified by a user defined name.
# It constrains Cancellable to allow groups of one coro only.
# It maintains a dict of barriers indexed by name.
class NamedTask(Cancellable):
	instances = {}

	@classmethod
	async def cancel(cls, name, nowait=True):
		if name in cls.instances:
			await cls.cancel_all(group=name, nowait=nowait)
			