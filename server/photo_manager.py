import pymongo
import tincan
import datetime
import time
from flask import jsonify

import threading

PHOTO_NUM = 100
CATEGORIES = ['city','landscape','people']
DAYS = [1,3,7]

connection = pymongo.MongoClient('localhost', 27017, maxPoolSize=10)
mydb = connection.px500

photos = {}
for category in CATEGORIES:
	photos[category] = {}
	for day in DAYS:
		photos[category][day] = []


def get_requested_photos(category,day):

	return jsonify({'photos':photos[category][day]})


def scan_active_photos():
	temp = {}

	for category in CATEGORIES:
		temp[category] = {}
		for day in DAYS:
			temp[category][day] = []

	now = time.time()
	for category in CATEGORIES:
		items = list(mydb[category].find())
		for item in items:
			created_time = item['created_at']
			d = tincan.conversions.iso8601.make_datetime(created_time)
			created_in_seconds = time.mktime(d.timetuple())
			time_passed = now - created_in_seconds
			item = {x:item[x] for x in item if x in ['name']}
			#over one week, then not refresh at all, save to history
			if time_passed > 3600*24*DAYS[2]:
				spill_photos_to_history(category,item)
			elif time_passed < 3600*24*DAYS[1]:
				temp[category][DAYS[1]].append(item)
			elif time_passed < 3600*24*DAYS[0]:
				temp[category][DAYS[0]].append(item)
			temp[category][DAYS[2]].append(item)

	for category in CATEGORIES:
		for day in DAYS:
			photos[category][day] = temp[category][day]


def spill_photos_to_history(category,item):
	category_name = "history_"+category
	mydb[category_name].insert(item)
	mydb[category].remove(item)	


def start_photo_managing():
	while True:
		t = threading.Thread(target=scan_active_photos)
		t.start()
		t.join()
		time.sleep(300)

