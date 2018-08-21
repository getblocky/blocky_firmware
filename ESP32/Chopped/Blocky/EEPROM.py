def get(name):
	t = None
	f = None
	try :
		f = open('Blocky/FUSE.txt')
		while True :
			data = f.readline()
			if len(data) < 3 :
				break 
			var , val = data.split('=')
			var.replace(' ','');val.replace(' ','')
			if var == name:
				if val.find('"') == -1:
					if val.find('.') == 0:
						val = float(val)
					else:
						val = int(val)
				break 
		return val
	except :
		pass
		
def set(var,val):
	if isinstance(val,str):
		val = '"' + val + '"'
	elif isinstance(val,int) or isinstance(val,float):
		val = str(val)
	else :
		return 
	try :
		f = open('Blocky/FUSE.txt')
	except :
		import os
		f = open('Blocky/FUSE.txt' , 'w')
		f.close()
		f = open('Blocky/FUSE.txt')
	t = f.readlines()
	found = False
	for i in range(len(t)):
		x = t[i]
		if len(x) > 3 :
			name , value = x.split('=')
			name.replace(' ','');value.replace(' ','')
			if name == var :
				t[i] = var + '=' + val 
				found = True
				break
	f.close()
	f = open('Blocky/FUSE.txt','w')
	for x in t :
		f.write(x)
	if found == False :
		f.write(var + '=' + val)
		f.write('\n')
	f.close()


