cheduling
        if __debug__ and DEBUG:
            log.debug("Sleeping for: %s", delay)
        time.sleep_ms(delay)

    def run_forever(self):
        cur_task = [0, 0, 0]
        while True:
            # Expire entries in waitq and move them to runq
            tnow = self.time()
            while self.waitq:
                t = self.waitq.peektime()
                delay = time.ticks_diff(t, tnow)
                if delay > 0:
                    break
                self.waitq.pop(cur_task)
                if __debug__ and DEBUG:
                    log.debug("Moving from waitq to runq: %s", cur_task[1])
                self.call_soon(cur_task[1], *cur_task[2])

            # Process runq
            l = len(self.runq)
            if __debug__ and DEBUG:
                log.debug("Entries in runq: %d", l)
            while l:
                cb = self.runq.popleft()
                l -= 1
                args = ()
                if not isinstance(cb, type_gen):
                    args = self.runq.popleft()
                    l -= 1
                    if __debug__ and DEBUG:
                        log.info("Next callback to run: %s", (cb, args))
                    cb(*args)
                    continue

                if __debug__ and DEBUG:
                    log.info("Next coroutine to run: %s", (cb, args))
                self.cur_task = cb
                delay = 0
                try:
                    if args is ():
                        ret = next(cb)
                    else:
                        ret = cb.send(*args)
                    if __debug__ and DEBUG:
                        log.info("Coroutine %s yield result: %s", cb, ret)
                    if isinstance(ret, SysCall1):
                        arg = ret.arg
                        if isinstance(ret, SleepMs):
                            delay = arg
                        elif isinstance(ret, IORead):
                            cb.pend_throw(False)
                      