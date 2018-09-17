Semaphore(Semaphore):
	
	def __init__(self, value=1):
		super().__init__(value)
		self._initial_value = value

	def release(self):
		if self._count < self._initial_value:
			self._count += 1
		else:
			raise ValueError('Semaphore released more than acquired')
"""
# Task Cancellation
try:
	StopTask = core.asyncio.CancelledError  # More descriptive name
except AttributeError:
	raise OSError('asyn.py requires ucore.asyncio V1.7.1 or above.')
"""
class TaskId():
	
	def __init__(self, taskid):
		self.taskid = taskid

	def __call__(self):
		return self.taskid

# Sleep coro breaks up a sleep into shorter intervals to ensure a rapid
# response to StopTask exceptions
async def sleep(t, granularity=100):  # 100ms default
	
	if granularity <= 0:
		raise ValueError('sleep granularity must be > 0')
	t = int(t * 1000)  # ms
	if t <= granularity:
		await core.asyncio.sleep_ms(t)
	else:
		n, rem = divmod(t, granularity)
		for _ in range(n):
			await core.asyncio.sleep_ms(granularity)
		await core.asyncio.sleep_ms(rem)

# Anonymous cancellable tasks. These are members of a group which is identified
# by a user supplied name/number (default 0). Class method cancel_all() cancels
# all tasks in a group and awaits confirmation. Confirmation of ending (whether
# normally or by cancellation) is signalled by a task calling the _stopped()
# class method. Handled by the @cancellable decorator.


class Cancellable():
	
	task_no = 0  # Generated task ID, index of tasks dict
	tasks = {}  # Value is [coro, group, barrier] indexed by integer task_no

	@classmethod
	def _cancel(cls, task_no):
		task = cls.tasks[task_no][0]
		core.asyncio.cancel(task)

	@classmethod
	async def cancel_all(cls, group=0, nowait=False):
		tokill = cls._get_task_nos(group)
		barrier = Barrier(len(tokill) + 1)  # Include this task
		for task_no in tokill:
			cls.tasks[task_no][2] = barrier
			cls._cancel(task_no)
		if nowait:
			barrier.trigger()
		else:
			await barrier

	@classmethod
	def _is_running(cls, group=0):
		t