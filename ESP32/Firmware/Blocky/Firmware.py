
list = ['Blocky/Alarm.py', 'Blocky/Button.py', 'Blocky/Buzzer.py', 'Blocky/ConfigManager.py', 'Blocky/deque.py', 'Blocky/Firmware.py', 'Blocky/IFTTT.py', 'Blocky/index.html', 'Blocky/Indicator.py', 'Blocky/Light.py', 'Blocky/Main.py', 'Blocky/MicroWebSrv.py', 'Blocky/MQTT.py', 'Blocky/Music.py', 'Blocky/Network.py', 'Blocky/Pin.py', 'Blocky/Remote.py', 'Blocky/RFID.py', 'Blocky/RGB.py', 'Blocky/Servo.py', 'Blocky/Smoke.py', 'Blocky/Stepper.py', 'Blocky/Switch.py', 'Blocky/system.json', 'Blocky/Timer.py', 'Blocky/uasyncio.py', 'Blocky/WaterSensor.py', 'Blocky/Weather.py', 'main.py']



from Blocky.Indicator import indicator
import urequests , ujson
error = False 
board = 'TheShield'
try :
	f = open('Blocky/system.json')
	system = ujson.loads(f.read())
	firmware = system.firmware
	board = system.board 
except Exception:
	pass

try :
	latest = int(urequests.get('https://raw.githubusercontent.com/curlyz/Firmware/master/branch/'+board+'/latest.md').text)
except ValueError:
	error = True 

if not error :
	if latest > firmware:
		import os 
		list = (urequests.get('https://raw.githubusercontent.com/curlyz/Firmware/master/branch/'+board+'/' + str(latest_version) + '/list.json').text)
		
		print(list)
		list = ujson.loads(list)
		for x in list['update_list']:
			if x != 'Blocky/system.json':
				try :
					f = open(x , 'w')
					f.write( urequests.get('https://raw.githubusercontent.com/curlyz/Firmware/master/branch/TheShield/' + str(latest_version) + "/" + x).text)
					f.close()
					print('File' , x , 'updated')
					indicator.animate('pulse',(0,0,100),20)
				except Exception as err:
					print(err)
		f = open('Blocky/system.json','w')
		f.write( urequests.get('https://raw.githubusercontent.com/curlyz/Firmware/master/branch/TheShield/' + str(latest_version) + "/" + x).text)
		f.close()
		print('File' , x , 'updated');
		print('Done +>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
		indicator.animate('pulse',(0,100,0),50)