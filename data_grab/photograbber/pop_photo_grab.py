from Queue import Queue
import api

import global_data
from global_data import CONSUMER_KEY, CONSUMER_SECRET, PHOTO_GRAB_PER_TIME
from db_helper import mydb

class PhotoStream(object):
	def __init__(self):
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)
		self.photo_list = []

	def get_pop_photo_stream(self, category):
		results = self.client.get_photos(rpp=100, feature='popular', only=category, sort=rating, tags=1)
		for photo in results:
			self.photo_list.append(photo)

	def parse_photo_stream(self):
		pass
		
	def save_photo_stream_to_db(self):
		#save popular photos into photos collection
		photo_collection = mydb.photos
		#check if the photo exists
		photo_check = photo_collection.find_one({'id':photo['id']})
		#photo has not seen before, insert
		if photo_check is None:
			photo_collection.insert(photo)
		#has seen, update time varying fields
		else:
			photo_collection.update({'id':photo['id']},photo)










