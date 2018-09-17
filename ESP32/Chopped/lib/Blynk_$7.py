lse:
                    self._start_time = sleep_from_until(self._start_time, IDLE_TIME_MS)
                if not self._server_alive():
                    self._close('Blynk server is offline')
                    break
                self._run_task()

            if not self._do_connect:
                self._close()
                print('Blynk disconnection requested by the user')