from Queue import Queue
from pxapi import api

import global_data
from global_data import CONSUMER_KEY, CONSUMER_SECRET, PHOTO_GRAB_PER_TIME
# from db_helper import mydb

class PhotoStream(object):
	def __init__(self):
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)
		self.photo_queue = Queue()
		self.new_user_list = []

	def get_pop_photo_stream(self):
		count = 0
		results = self.client.get_photos(rpp=100, feature='popular', tags=1)
		for photo in results:
			self.photo_queue.put(photo)
			# print "get photo %d"%count
			count += 1
			if count==PHOTO_GRAB_PER_TIME:
				break

	def parse_photo_stream(self):
		while not self.photo_queue.empty():
			photo = self.photo_queue.get()
			self.save_photo_stream_to_db(photo)

	def save_photo_stream_to_db(self, photo):
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
		#add the authors of the popular photos into a list
		self._add_new_user_to_list(photo['user']['id'])

	#if user not seen in database, then it should be put to bfs queue for user relation graph
	def _add_new_user_to_list(self, user):
		self.new_user_list.append(user)
	#return new user list
	def get_new_user_list(self):
		return self.new_user_list
	def clear_new_user_list(self):
		self.new_user_list = []









