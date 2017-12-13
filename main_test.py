import machine, ujson, time, network, neopixel, gcfrom machine import Pin, Timer

LED_PIN = 4
CONFIG_PIN = 25

config_btn = Pin(CONFIG_PIN, Pin.IN)
status_led = Pin(LED_PIN, Pin.OUT)

if config_btn.value() == 1: 
  print('config button is pressed')
  # turn on config led
  status_led.value(1)
  
  # start while loop until btn is released
  press_begin = time.ticks_ms()
  press_duration = 0
  while config_btn.value():
    press_end = time.ticks_ms()
    press_duration = time.ticks_diff(press_end, press_begin)
    print(press_duration)
    if press_duration > 2000:
      break
    time.sleep_ms(100)
  
  # check how long it was pressed
  if press_duration > 2000:    
    # if more than 3 seconds => flash led many times and copy original user code file and reset
    print('Config button pressed longer than 3 seconds')
    for i in range(10) :
      status_led.value(1)
      time.sleep_ms(100)
      status_led.value(0)
      time.sleep_ms(100)
    # read original code file
    original_user_code = ''
    for line in open('user_code_original.py', 'r'):
      original_user_code = original_user_code + line
    f = open('user_code.py', 'w')
    f.write(original_user_code)
    f.close()
    machine.reset()
  else: # in case pressed less than 1 seconds 
    print('Config button pressed less than 3 seconds')
    import config_manager

else: # config btn is not pressed
  # load config file
  config = {}
  try:
    f = open('config.json', 'r')
    config = ujson.loads(f.read())
    f.close()
  except Exception:
    print('Failed to load config file')

  #print(config)
  # if error found or missing information => start config mode
  if not config.get('device_name', False) \
    or not config.get('auth_key', False) \
    or not config.get('known_networks', False):
    print('Missing required info in config. Enter config mode')
    import config_manager
  else:
    print('Finish loading config file')
    #print(config)
    
    # connect to wifi using known network
    print('Connecting to WIFI')    
    wlan_sta = network.WLAN(network.STA_IF)    
    wlan_sta.active(True)
    
    # scan what WIFI network available
    available_wifi = []
    for wifi in wlan_sta.scan():
      available_wifi.append(wifi[0].decode("utf-8"))

    # Go over the preferred networks that are available, attempting first items or moving on if n/a
    for preference in [p for p in config['known_networks'] if p['ssid'] in available_wifi]:
      print("connecting to network {0}...".format(preference['ssid']))
      wlan_sta.connect(preference['ssid'], preference['password'])
      led_on = 1
      for check in range(0, 40):  # Wait a maximum of 10 times (10 * 500ms = 5 seconds) for success
        if wlan_sta.isconnected():
          break
        led_on = 1 - led_on
        status_led.value(led_on)
        time.sleep_ms(250)
      
      if wlan_sta.isconnected():
        break

    if wlan_sta.isconnected():
      status_led.value(0)
      print("Connected to Wifi. IP: " + str(wlan_sta.ifconfig()))
      # start blocky      
      from blocky import Blocky
      blocky = Blocky(config)
      if not blocky.connect(): # connect to server
        print('Failed to connect to broker. Enter config mode')
        gc.collect()
        import config_manager
      else: # run user code
        gc.collect()
        print(gc.mem_free())
        import user_code
        user_code.blocky = blocky
        user_code.setup()
        user_code.loop()
    else: # failed to connect to wifi
      import config_manager