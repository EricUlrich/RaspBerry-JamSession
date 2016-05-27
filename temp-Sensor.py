#!/usr/bin/python
# Add sources...
#
#
#

import os
import time
import glob
import json
import sys
import time
import datetime

import Adafruit_DHT # DHT sensor family
import gspread # Google docs
from oauth2client.client import SignedJwtAssertionCredentials # Required for Google docs API access and auth

# 1-wire
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT11

# Example of sensor connected to Raspberry Pi GPIO 23
DHT_PIN  = 4

GDOCS_OAUTH_JSON	   = '../RaspBerryJam-e443aed01834.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'RaspBerryJam'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS	  = 30


# build list of 1-wire devices
base_dir = '/sys/bus/w1/devices/'
devices = glob.glob(base_dir + '28*')
i = 0
for device in devices:
	devices[i] = device + '/w1_slave'
	i += 1

# Google sheets login	
def login_open_sheet(oauth_key_file, spreadsheet):
	"""Connect to Google Docs spreadsheet and return the first worksheet."""
	try:
		json_key = json.load(open(oauth_key_file))
		credentials = SignedJwtAssertionCredentials(json_key['client_email'],
													json_key['private_key'],
													['https://spreadsheets.google.com/feeds'])
		gc = gspread.authorize(credentials)
		worksheet = gc.open(spreadsheet).sheet1
		return worksheet
	except Exception as ex:
		print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
		print('Google sheet login failed with error:', ex)
		sys.exit(1)

# Read the 1-wire device data from file.
def read_temp_raw(device):
	f = open(device, 'r')
	lines = f.readlines()
	f.close()
	return lines

# Return temp data from raw data
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

#while True:
#	for device in devices:
#		reading = read_temp(device)
#		print("Sensor: " + str(reading[0]) + " Celsius: " + str(reading[1]) + " Fahrenheit: " + str(reading[2]))
#	time.sleep(30)

print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
	# Login if necessary.
	if worksheet is None:
		worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

	# Attempt to get sensor reading.
	humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

	# Skip to the next reading if a valid measurement couldn't be taken.
	# This might happen if the CPU is under a lot of load and the sensor
	# can't be reliably read (timing is critical to read the sensor).
	if humidity is None or temp is None:
		time.sleep(2)
		continue

	print('Ambient Temperature: {0:0.1f} F'.format(temp * 9.0 / 5.0 + 32.0))
	print('Ambient Humidity:	{0:0.1f} %'.format(humidity))

	for device in devices:
		reading = read_temp(device)
		print("Sensor: " + str(reading[0]) + " " + str(reading[2]) + " F" )
		str

	# Append the data in the spreadsheet, including a timestamp
	try:
 		worksheet.append_row((datetime.datetime.now(), temp * 9.0 / 5.0 + 32.0, humidity))
	except:
		# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the loop.
		print('Append error, logging in again')
		worksheet = None
		time.sleep(FREQUENCY_SECONDS)
		continue

	# Wait 30 seconds before continuing
	print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
	time.sleep(FREQUENCY_SECONDS)
	break
