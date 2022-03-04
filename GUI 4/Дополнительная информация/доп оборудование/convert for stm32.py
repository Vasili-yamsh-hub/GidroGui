

new_reading = ""
file = open('signal.txt','r')
reading = file.read()
file.close()
reading = reading.replace(' ','')
reading = reading.replace("'",'')
reading = reading[1:1560]

for i in range(0,len(reading),3):
	new_reading += ('0x'+ reading[i:i+3])
	
print(new_reading)
print('-------------------------------')







