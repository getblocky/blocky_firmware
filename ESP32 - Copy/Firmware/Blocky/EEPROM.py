import sys
core = sys.modules['Blocky.Core']

# Is this a waste of flash ?
# No , this is use for long-term memory

if not "fuse.py" in core.os.listdir('Blocky'):
	f = open('Blocky/fuse.py','w')
	f.close()

def get(name):
	try :
		f = open('Blocky/fuse.py')
		b = core.json.loads(f.read())
		f.close()
		return b[name]
	except:
		return None
def set(name,value):
	print('[eeprom] set',name,'to',value ,end='')
	try :
		f = open('Blocky/fuse.py')
		try :
			b = core.json.loads(f.read())
		except :
			b = {}
		f.close()
		try :
			if b[name]==value:
				print('UnchangedValue')
				return
		except KeyError:
			pass
		print('3')
		b[name] = value
		f = open('Blocky/fuse.py','w')
		f.write(core.json.dumps(b))
		f.close()
		print('ChangedValue')
	except:
		return None