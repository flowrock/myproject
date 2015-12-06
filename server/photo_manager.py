import pymongo
import tincan
import datetime
import time
from flask import jsonify

import threading

PHOTO_NUM = 100
CATEGORIES = ['city','landscape','people']
DAYS = [1,3,7]
PHOTO_FIELDS = ['name','camera','lens','focal_length','iso','shutter_speed','aperture','rating',
'latitude','longitude','tags','image_url','user']

connection = pymongo.MongoClient('localhost', 27017, maxPoolSize=10)
mydb = connection.px500

def scan_active_photos():
	photos = {}

	for category in CATEGORIES:
		photos[category] = {}
		for day in DAYS:
			photos[category][day] = []

	now = time.time()
	for category in CATEGORIES:
		items = list(mydb[category].find())
		for item in items:
			created_time = item['created_at']
			d = tincan.conversions.iso8601.make_datetime(created_time)
			created_in_seconds = time.mktime(d.timetuple())
			time_passed = now - created_in_seconds
			item = {x:item[x] for x in item if x in PHOTO_FIELDS}
			#over one week, then not refresh at all, save to history
			if time_passed > 3600*24*DAYS[2]:
				spill_photos_to_history(category,item)
			if time_passed < 3600*24*DAYS[1]:
				photos[category][DAYS[1]].append(item)
			if time_passed < 3600*24*DAYS[0]:
				photos[category][DAYS[0]].append(item)
			photos[category][DAYS[2]].append(item)

	mydb.current.remove()

	all_photos = {}
	for day in DAYS:
		all_photos[day] = []
		for category in CATEGORIES:
			all_photos[day].extend(photos[category][day])
			photo_list = sorted(photos[category][day], key=lambda p:p['rating'], reverse=True)
			item = {'category':category,'day':day,'photos':photo_list[:100]}
			mydb.current.insert(item)
		all_photos[day] = sorted(all_photos[day], key=lambda p:p['rating'], reverse=True)
		item = {'category':'all','day':day,'photos':all_photos[day][:100]}
		mydb.current.insert(item)		


def spill_photos_to_history(category,item):
	col_name = "history_"+category
	mydb[col_name].insert(item)
	mydb[category].remove(item)	


def start_photo_managing():
	while True:
		t = threading.Thread(target=scan_active_photos)
		t.start()
		t.join()
		time.sleep(300)

if __name__ == '__main__':
	start_photo_managing()

