#version=1.0
import sys

core = sys.modules['Blocky.Core']
wifi_list = None
connected = False

wlan_sta  = core.network.WLAN(core.network.STA_IF)


async def connect(ap=None):
	print('[WIFI] -> Connecting')
	await core.indicator.show('wifi-connecting')
	wlan_sta.active(True)
	if ap == None :
		while not wlan_sta.isconnected() :
			await core.asyncio.sleep_ms(100)
			
	else :
		#core.mainthread.call_soon(core.indicator.heartbeat( (0,50,50) , 1 , wlan_sta.isconnected ))
		while not wlan_sta.isconnected():
			
			l = []
			core.wifi_list = wlan_sta.scan()
			for x in core.wifi_list:
				l.append(x[0].decode('utf-8'))
			print(l , sep = '\r\n')
			for preference in [p for p in core.config.get('known_networks') if p['ssid'] in l]:
				print('[',core.Timer.runtime(),'] Connecting to network {0}...'.format(preference['ssid']))
				print(preference)
				wlan_sta.connect(preference['ssid'],preference['password'])
				for check in range(50):
					if wlan_sta.isconnected():
						break
					print('.',end='')
					await core.asyncio.sleep_ms(250)
				if wlan_sta.isconnected():
					print('Connected to ' ,  preference)
					break
			if wlan_sta.isconnected():
				core.flag.wifi = True
				core.Timer.sync_ntp()
				break
			await core.asyncio.sleep_ms(10000)
			print('[WIFI] -> Reconneting')