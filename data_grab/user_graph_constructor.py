import time
import threading
from threading import current_thread
import os
import requests

from pxapi import api
from db_helper import mydb
from user_manager import UserManager
from bfs_queue_manager import BfsQueueManager
from global_data import CONSUMER_KEY, CONSUMER_SECRET

class LoopedUserSearch(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)
		self.bm = BfsQueueManager()

	def run(self):
		self.retrieve_user_from_queue()

	#the user mining process is an infinite loop
	def retrieve_user_from_queue(self):
		enter_time = time.time()

		# while True:
		# 	if not self.bm.is_empty():
		# 		user = self.bm.get_user()
		print "user process: ", os.getpid()
		self._get_followers_of_user(9149967)
			#set break for test
			# if time.time() > enter_time+30:
			# 	break
			
	def _get_followers_of_user(self, user):
		um = UserManager()
		path = "https://api.500px.com/v1/users/9149967/followers?fullformat=1&page=1&rpp=50"
		# results = self.client.get_followers(user_id=str(user), rpp=100, full_format=1)
		results = requests.get(path)
		print results.status_code
		print results.json()
		follower_list = []

		# for follower in results:
		# 	if not um.user_seen(follower['id']):
		# 		um.add_user(follower['id'])
		# 		follower_list.append(follower)
		# 		self.bm.put_user(follower['id'])
		# print follower_list
		# self._save_follower_relation_to_db(user, follower_list)

	#may want to spawn to separate threads
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


def user_search_start_running():
	#create 5 threads for requesting users
	thread_list = []
	for i in range(1):
		thread = LoopedUserSearch()
		thread_list.append(thread)
		thread.start()

	for t in thread_list:
		t.join()

