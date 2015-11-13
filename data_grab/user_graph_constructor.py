from Queue import Queue
import time

from pxapi import api
from db_helper import mydb
from global_data import CONSUMER_KEY, CONSUMER_SECRET, user_bfs_queue, bloom_filter

class LoopedUserSearch(object):
	def __init__(self):
		self.unique_count = 0
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)

	#the user mining process is an infinite loop
	def retrieve_user_from_queue(self):
		while True:
			if not user_bfs_queue.empty():
				# print user_bfs_queue.qsize()
				self.unique_count += 1
				# print "Getting No.%d user" % self.unique_count
				user = user_bfs_queue.get()
				self._get_followers_of_user(user)
			break
			
	def _get_followers_of_user(self, user):
		results = self.client.get_followers(user_id=str(user), rpp=100, full_format=1)
		follower_list = []

		for follower in results:
			if not bloom_filter.is_user_seen(follower['id']):
				#print follower['id']
				bloom_filter.add_user(follower['id'])
				follower_list.append(follower)
				#put the new user into global bfs queue
				user_bfs_queue.put(follower['id'])
			#print follower_list

		self._save_follower_relation_to_db(user, follower_list)

	def _save_follower_relation_to_db(self, user, follower_list):
		follower_id_list = []

		#save users into users collection
		user_collection = mydb.users
		for follower in follower_list:
			user_collection.insert(follower)
			follower_id_list.append(follower['id'])

		#add the following relation of the given user into user relation collection
		user_relation_collection = mydb.user_relation
		relation = {}
		relation['user'] = user
		relation['followers'] = follower_id_list
		user_relation_collection.insert(relation)



