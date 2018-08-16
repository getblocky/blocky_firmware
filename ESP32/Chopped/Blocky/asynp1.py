ection != self._down:
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
        await asyncio.sleep(0)

    async def acquire(self):
        while self._count == 0:
            yield
        self._count -= 1

    def release(self):
        self._count += 1

class BoundedSemaphore(Semaphore):
    def __init__(self, value=1):
        super().__init__(value)
        self._initial_value = value

    def release(self):
        if self._count < self._initial_value:
            self._count += 1
        else:
            raise ValueError('Semaphore released more than acquired')

# Task Cancellation
try:
    StopTask = asyncio.CancelledError  # More descriptive name
except AttributeError:
    raise OSError('asyn.py requires uasyncio V1.7.1 or above.')

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
        await asyncio.sleep_ms(t)
    else:
        n, rem = divmod(t, granularity)
        for _ in range(n):
            await asyncio.sleep_ms(granularity)
        await asyncio.sleep_ms(rem)

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
        asyncio.cancel(task)

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
        tasks = cls._get_task_nos(group)
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
   