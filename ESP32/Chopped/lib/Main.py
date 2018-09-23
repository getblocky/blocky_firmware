#version=1.0
import Blocky.Core as core
from Blocky.Indicator import indicator

core.indicator = indicator
core.mainthread = core.asyncio.get_event_loop()


if 'user_code.py' not in core.os.listdir():
	f = open('user_code.py','w')
	f.close()
if 'config.json' not in core.os.listdir():
	f = open('config.json','w')
	f.close()

# This timer will trigger a reset
# if user code use the mainthread too long 
try :
	wdt_timer = core.machine.Timer(1)
except :
	pass
	
def failsafe(source):
	try :
		if core.Timer.runtime() - core.blynk.last_call > 10000 :
			print('Usercode is so bad')
			import os , machine 
			print('Removing')
			try :
				os.rename('user_code.py' , 'temp_code.py')
			except :
				pass
			print('Lastword')
			try :
				f = open('last_word.py' , 'w')
				f.write('Your code has been deleted because it use so many processing time')
				f.close()
			except:
				pass
			print('Reset')
			core.machine.reset()
	# Due to MemoryError or because reference has been deleted	
	except : 
		
		print('Blocky is now rebooting')
		import os , neopixel , time , machine 
		os.rename('user_code.py','temp_code.py')
		n = NeoPixel(Pin(5) , 1)
		for x in range(20):
			n[0] = (255,0,0);n.write();time.sleep_ms(50)
			n[0] = (0,0,0);n.write();time.sleep_ms(50)
		try :
			f = open('last_word.py' , 'w')
			f.write('Your code have some error,Blocky have to kill it')
			f.close()
		except:
			pass
		machine.reset()
		
		
async def run_user_code(direct = False):
	try:
		wdt_timer.deinit()
	except :
		pass
	
	await core.asyn.Cancellable.cancel_all()
		
	if direct == True :
		try :
			wdt_timer.init(mode=core.machine.Timer.PERIODIC,period=10000,callback = failsafe)
			print("User's watchdog initialized")
		except :
			pass
		
		core.user_code = __import__('user_code')
		return 
	
	print('Run User_code')
	
	
	print('Checking library file')
	
	# Why am I doing this huh ?
	# We can use readlines() or readline() right
	# uPython user continuous memory region for readlines() -> MemoryError
	# uPy