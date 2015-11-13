import sys
import threading
import time

from Queue import Queue
from photo import api

import global_data
from global_data import CONSUMER_KEY, CONSUMER_SECRET, PHOTO_GRAB_PER_TIME
from db_helper import mydb

class PhotoStream(object):
	def __init__(self):
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)
		self.photo_queue = Queue()
		self.new_user_list = []

	def get_pop_photo_stream(self):
		count = 0
		results = self.client.get_photos(rpp=100, feature='popular')
		for photo in results:
			self.photo_queue.put(photo)
			print "get photo %d"%count
			count += 1
			if count==PHOTO_GRAB_PER_TIME:
				break
		print '\n'
		print '\n'

	def parse_photo_stream(self):
		while not self.photo_queue.empty():
			photo = self.photo_queue.get(0)
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

		#save users into users collection
		user_collection = mydb.users
		#check if the user exists
		user_check = user_collection.find_one({'id':photo['user']['id']})
		if user_check is None:
			user_collection.insert(photo['user'])
			self._add_new_user_to_list(photo['user']['id'])

	#if user not seen in database, then it should be put to bfs queue for user relation graph
	def _add_new_user_to_list(self, user):
		self.new_user_list.append(user)
	#return new user list
	def get_new_user_list(self)
		return self.new_user_list











			
