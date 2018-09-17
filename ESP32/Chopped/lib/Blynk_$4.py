f._format_msg(MSG_EMAIL, to, subject, body))

    def virtual_write(self, pin, val):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW, 'vw', pin, val))

    def set_property(self, pin, prop, val):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_PROPERTY, pin, prop, val))

    def log_event(self, event, descr=None):
        if self.state == AUTHENTICATED:
            if descr==None:
                self._send(self._format_msg(MSG_EVENT_LOG, event))
            else:
                self._send(self._format_msg(MSG_EVENT_LOG, event, descr))

    def sync_all(self):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW_SYNC))

    def sync_virtual(self, pin):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW_SYNC, 'vr', pin))

    def add_virtual_pin(self, pin, read=None, write=None):
        if isinstance(pin, int) and pin in range(0, MAX_VIRTUAL_PINS):
            self._vr_pins[pin] = VrPin(read, write)
        else:
            raise ValueError('the pin must be an integer between 0 and %d' % (MAX_VIRTUAL_PINS - 1))

    def VIRTUAL_READ(blynk, pin):
        class Decorator():
            def __init__(self, func):
                self.func = func
                blynk._vr_pins[pin] = VrPin(func, None)
                #print(blynk, func, pin)
            def __call__(self):
                return self.func()
        return Decorator

    def VIRTUAL_WRITE(blynk, pin):
        class Decorator():
            def __init__(self, func):
                self.func = func
                blynk._vr_pins[pin] = VrPin(None, func)
            def __call__(self):
                return self.func()
        return Decorator

    def on_connect(self, func):
        self._on_connect = func

    def set_user_task(self, task, ms_period):
        if ms_period % TASK_PERIOD_RES != 0:
            raise ValueError('the user task period must be a mult