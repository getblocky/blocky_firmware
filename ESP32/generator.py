import os 

# Get list of source file 
path = "Firmware/Blocky/"
LIMIT_SIZE = 5000
import glob, os , math
print(glob.glob(path))
list_src = os.listdir(path)

code = {}
for x in list_src :
	code[x] = open(path + '/' + x , 'r').read()
print(list(code))

for x in code :
	print(x , len(code[x]) , end = '')
	if len(code[x]) > LIMIT_SIZE :
		print('\t<<<<<<----------' , math.ceil(len(code[x])/LIMIT_SIZE ))
	else :
		print()
		
temp = os.listdir('Chopped/Blocky')
for x in temp :
	os.remove('Chopped/Blocky/' + x)
	print('Remove -> ' , 'Chopped/Blocky/' + x)
	
for x in code :
	if len(code[x]) <= LIMIT_SIZE :
		f = open('Chopped/Blocky/' + x , 'w')
		f.write(code[x])
		f.close()
		print('File -> ' , x , len(code[x]))

code_chopped = dict(code)
for x in code_chopped :
	code_chopped[x] = [code[x][i:i+LIMIT_SIZE] for i in range(0, len(code[x]), LIMIT_SIZE)]
	print(x , len(code_chopped[x]) , len(code[x]))

for x in code :
	if len(code[x]) > LIMIT_SIZE :
		temp = code[x]
		chop = []
		f = open('Chopped/Blocky/' + x , 'w')
		f.write(code[x][0:LIMIT_SIZE])
		f.close()
		for i in range( 1 , math.floor(len(code[x])/LIMIT_SIZE ) ):
			f = open('Chopped/Blocky/' + x.replace( '.' + x.split('.')[-1]   , 'p' + str(i) +  '.' + x.split('.')[-1]  ) , 'w')
			f.write(code[x][ LIMIT_SIZE*i :LIMIT_SIZE*(i+1)])
			f.close()
		i = math.ceil(len(code[x])/LIMIT_SIZE)
		f = open('Chopped/Blocky/' + x.replace( '.' + x.split('.')[-1]   , 'p' + str(i) +  '.' + x.split('.')[-1]  ) , 'w')
		f.write(code[x][ LIMIT_SIZE*i : len(code[x]) ])
		f.close()