#!/usr/bin/python
#  
# Parts of this code were taken from source below for the DHT family of sensors and the
# google docs API interface exmaple
#
# https://github.com/adafruit/Adafruit_Python_DHT.git
# examples/google_spreadsheet.py
# https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/overview
#
# Google Spreadsheet DHT Sensor Data-logging Example

# Depends on the 'gspread' and 'oauth2client' package being installed.  If you
# have pip installed execute:
#   sudo pip install gspread oauth2client

# Also it's _very important_ on the Raspberry Pi to install the python-openssl
# package because the version of Python is a bit old and can fail with Google's
# new OAuth2 based authentication.  Run the following command to install the
# the package:
#   sudo apt-get update
#   sudo apt-get install python-openssl

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Other examples and tutorials used for the DS18B20 family of sensors
# http://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi
# http://www.d3noob.org/2015/02/raspberry-pi-multiple-temperature.html
#
# OAuth2 from google
# http://gspread.readthedocs.io/en/latest/oauth2.html
# had to install this version to work on my Raspberry pi
# pip install oauth2client==1.5.2
# https://github.com/burnash/gspread/issues/357

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
FREQUENCY_SECONDS	  = 300


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

print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
	# Login if necessary.
	if worksheet is None:
		worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

	results_list = []
	# Attempt to get sensor reading.
	humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
	# 
	# Skip to the next reading if a valid measurement couldn't be taken.
	# This might happen if the CPU is under a lot of load and the sensor
	# can't be reliably read (timing is critical to read the sensor).
	if humidity is None or temp is None:
		time.sleep(2)
		continue
	results_list.append(temp * 9.0 / 5.0 + 32.0)
	results_list.append(humidity)
	#print(results_list)
	#print(len(results_list))

	print('Ambient Temperature: {0:0.1f} F'.format(results_list[0]))
	print('Ambient Humidity:	{0:0.1f} %'.format(results_list[1]))
	#device_count = len(devices)

	for device in devices:
		reading = read_temp(device)
		#print("Sensor: " + str(reading[0][20:35]))
		try:
			results_list1.extend([str(reading[0][20:35]), str(reading[2])])
		except:
			results_list1 = [str(reading[0][20:35]), str(reading[2])]

		#print(results_list1)
		#print(len(results_list1))

	results_list.extend(results_list1)
	#print(results_list)
	#print(len(results_list))
	print('Sensor: ' + results_list[2] + ' {0:0.1f} F'.format(float(results_list[3])))
	print('Sensor: ' + results_list[4] + ' {0:0.1f} F'.format(float(results_list[5])))
	print('Sensor: ' + results_list[6] + ' {0:0.1f} F'.format(float(results_list[7])))
	print('Sensor: ' + results_list[8] + ' {0:0.1f} F'.format(float(results_list[9])))
	#print(float("{0:0.1f}".format(float(results_list[3]))))

	# Append the data in the spreadsheet, including a timestamp
	try:
		worksheet.append_row((datetime.datetime.now(), results_list[0], results_list[1], results_list[2], float("{0:0.1f}".format(float(results_list[3]))), results_list[4], float("{0:0.1f}".format(float(results_list[5]))), results_list[6], float("{0:0.1f}".format(float(results_list[7]))), results_list[8], float("{0:0.1f}".format(float(results_list[9])))))
	except:
		# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the loop.
		print('Append error, logging in again')
		worksheet = None
		time.sleep(FREQUENCY_SECONDS)
		continue

	# Wait 30 seconds before continuing
	print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
	del results_list1
	time.sleep(FREQUENCY_SECONDS)
