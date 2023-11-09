#!/usr/bin/env python3

import datetime
import requests
import pytz
from crontab import CronTab
import re

# Set the coordinates of Offenbach am Main
LATITUDE = 50.103151
LONGITUDE = 8.766111

# Get the current date and time
utc = pytz.timezone('UTC')
now = utc.localize(datetime.datetime.utcnow())

# Calculate the Fajr Azan time
fajr_azan_time = now + datetime.timedelta(hours=6)

# Make a request to the Islamic Prayer Times API to get the other Azan times
azan_times_api_url = "https://api.aladhan.com/v1/calendar"
params = {
	"latitude": LATITUDE,
	"longitude": LONGITUDE,
	"method": "3",  # Hanafi method
	"date": fajr_azan_time.strftime("%Y-%m-%d")
}
response = requests.get(azan_times_api_url, params=params)

# Parse the response and get the Azan times
azan_times = response.json()["data"][0]["timings"]

# Print the Azan times
print("Fajr:", azan_times["Fajr"])
print("Dhuhr:", azan_times["Dhuhr"])
print("Asr:", azan_times["Asr"])
print("Maghrib:", azan_times["Maghrib"])
print("Isha:", azan_times["Isha"])

# Update Crontab with Prayer Times
# ---------------------------------

system_cron = CronTab(user='mehedi')

strPlayAzaanMP3Command = 'mpg321 /home/mehedi/azan/Abdul-Basit.mp3 > /dev/null 2>&1'

jobs = system_cron.find_command(strPlayAzaanMP3Command)

for j in jobs:
	system_cron.remove(j)

# Function to add Azan time to cron
def addAzaanTime(strPrayerName, strPrayerTime, objCronTab, strCommand):
	job = objCronTab.new(command=strCommand, comment=strPrayerName)
	# Split the time and timezone parts
	time_part, timezone_part = re.search(r'(\d+:\d+) \(([^)]+)\)', strPrayerTime).groups()
	# Parse the time part
	hour, minute = map(int, time_part.split(':'))
	# Create the desired format for CronTab
	job.setall(minute, hour, '*', '*', '*')
	print(job)

# Iterate over the 5 daily Azan times and create Cron jobs for each
for prayer_name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
	addAzaanTime(prayer_name, azan_times[prayer_name], system_cron, strPlayAzaanMP3Command)

# Save the Cron configuration to a file
system_cron.write()

