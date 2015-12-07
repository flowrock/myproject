import pymongo
import tincan
import datetime
import time
import requests

import threading

CONSUMER_KEY = "evM04lzFCTjOLOO8V140JFbhnvxWFaI6H5Rz3mX5"
PHOTO_NUM = 100
CATEGORIES = ['city','landscape','people']
DAYS = [1,3,7]
PHOTO_FIELDS = ['id', 'name','camera','lens','focal_length','iso','shutter_speed','aperture','rating',
'latitude','longitude','tags','image_url','user']

connection = pymongo.MongoClient('localhost', 27017, maxPoolSize=10)
mydb = connection.px500

#this function runs periodically to update the photo database for instant server query
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

	save_active_photos(photos)


#this function is to put the outdated photos into history database
def spill_photos_to_history(category,item):
	col_name = "history_"+category
	mydb[col_name].insert(item)
	mydb[category].remove(item)	


#this function extracts active photos, sort them based on ratings, and save to photo database
def save_active_photos(photos):
	all_photos = {}
	for day in DAYS:
		all_photos[day] = []
		for category in CATEGORIES:
			all_photos[day].extend(save_for_category(photos[category][day], category, day))
		save_for_category(all_photos[day], 'all', day)

def save_for_category(pl, category, day):
	photo_list = sorted(pl, key=lambda p:p['rating'], reverse=True)
	top_photos = photo_list[:PHOTO_NUM]
	if category != 'all':
		top_photos = update_top_photos(top_photos, category)
	item = {'category':category,'day':day,'photos':top_photos}
	mydb.current.remove({'category':category,'day':day})
	mydb.current.insert(item)
	return top_photos


def update_top_photos(top_photos, category):
	for i in range(0,len(top_photos)):
		photo_id = top_photos[i]['id']
		record = mydb[category].find_one({'id':photo_id})
		if ('full_image_url' in record):
			top_photos[i]['full_image_url'] = record['full_image_url']
		else:
			full_image_url = request_full_image_url(photo_id, 0)
			top_photos[i]['full_image_url'] = full_image_url
			if full_image_url is not None:
				mydb[category].update_one({'id':photo_id},{
					"$set": {
					"full_image_url": full_image_url
					}})
	return top_photos


def request_full_image_url(photo_id,attempts):
	if attempts == 3:
		return None
	url = "https://api.500px.com/v1/photos/"+str(photo_id)
	payload = {'image_size':4, 'consumer_key':CONSUMER_KEY}
	full_image_url = None
	try:
		response = requests.get(url,params=payload)
		result = response.json()
		full_image_url = result['photo']['image_url']
	except:
		request_full_image_url(id,attempts+1)
	return full_image_url


def start_photo_managing():
	while True:
		t = threading.Thread(target=scan_active_photos)
		t.start()
		t.join()
		time.sleep(300)


if __name__ == '__main__':
	start_photo_managing()

