import os
import time
import glob

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#temp_sensor1 = '/sys/bus/w1/devices/28-021503b21eff/w1_slave'

#temp_sensor2 = '/sys/bus/w1/devices/28-021503b369ff/w1_slave'

base_dir = '/sys/bus/w1/devices/'
devices = glob.glob(base_dir + '28*')
i = 0
for device in devices:
	devices[i] = device + '/w1_slave'
	i += 1
	
#device_folder = glob.glob(base_dir + '28*')[0]
#device_file = device_folder + '/w1_slave'

def read_temp_raw(device):
	f = open(device, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp(device):
	lines = read_temp_raw(device)
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw(device)
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0
		return device, temp_c, temp_f

while True:
	for device in devices:
		reading = read_temp(device)
		print("Sensor: " + str(reading[0]) + " Celsius: " + str(reading[1]) + " Fahrenheit: " + str(reading[2]))
	time.sleep(30)

